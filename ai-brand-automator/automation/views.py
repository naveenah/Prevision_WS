"""
Views for the automation app - social media integrations and content scheduling.
"""
import uuid
import logging
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import SocialProfile, AutomationTask, ContentCalendar, OAuthState
from .serializers import (
    SocialProfileSerializer,
    AutomationTaskSerializer,
    ContentCalendarSerializer,
)
from .services import linkedin_service

logger = logging.getLogger(__name__)

User = get_user_model()


class SocialProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing social media profiles.
    """
    serializer_class = SocialProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SocialProfile.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """Disconnect a social profile."""
        profile = self.get_object()
        profile.disconnect()
        return Response({
            'message': f'{profile.get_platform_display()} disconnected successfully'
        })
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """Get connection status for all platforms."""
        profiles = self.get_queryset()
        
        # Build status for each supported platform
        platforms = ['linkedin', 'twitter', 'instagram', 'facebook']
        status_dict = {}
        
        for platform in platforms:
            profile = profiles.filter(platform=platform).first()
            if profile:
                status_dict[platform] = {
                    'connected': profile.status == 'connected',
                    'profile_name': profile.profile_name,
                    'profile_url': profile.profile_url,
                    'profile_image_url': profile.profile_image_url,
                    'status': profile.status,
                    'is_token_valid': profile.is_token_valid,
                }
            else:
                status_dict[platform] = {
                    'connected': False,
                    'profile_name': None,
                    'profile_url': None,
                    'profile_image_url': None,
                    'status': 'disconnected',
                    'is_token_valid': False,
                }
        
        return Response(status_dict)


class LinkedInConnectView(APIView):
    """
    Initiates LinkedIn OAuth flow.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Redirect user to LinkedIn authorization page."""
        if not linkedin_service.is_configured:
            return Response(
                {'error': 'LinkedIn integration not configured'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Generate a unique state token and store it in database
        # This is more reliable than sessions for JWT-based apps
        state = str(uuid.uuid4())
        
        # Clean up any old states for this user/platform
        OAuthState.objects.filter(user=request.user, platform='linkedin').delete()
        
        # Create new state
        OAuthState.objects.create(
            state=state,
            user=request.user,
            platform='linkedin'
        )
        
        # Get the authorization URL
        auth_url = linkedin_service.get_authorization_url(state)
        
        return Response({
            'authorization_url': auth_url
        })


class LinkedInCallbackView(APIView):
    """
    Handles LinkedIn OAuth callback.
    """
    # No authentication required - this is called by LinkedIn redirect
    permission_classes = []
    
    def get(self, request):
        """Handle the OAuth callback from LinkedIn."""
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        error = request.query_params.get('error')
        error_description = request.query_params.get('error_description')
        
        # Debug logging
        logger.info(f"LinkedIn callback received - code: {bool(code)}, state: {state}, error: {error}")
        
        # Get frontend URL for redirects
        frontend_url = getattr(
            settings,
            'FRONTEND_URL',
            'http://localhost:3000'
        )
        
        # Handle errors from LinkedIn
        if error:
            logger.error(f"LinkedIn OAuth error: {error} - {error_description}")
            return HttpResponseRedirect(
                f"{frontend_url}/automation?error={error}&message={error_description}"
            )
        
        # Validate state token from database (more reliable than sessions for JWT apps)
        try:
            oauth_state = OAuthState.objects.get(state=state, platform='linkedin')
        except OAuthState.DoesNotExist:
            logger.error(f"LinkedIn OAuth state not found: {state}")
            return HttpResponseRedirect(
                f"{frontend_url}/automation?error=invalid_state&message=State+token+not+found+or+expired"
            )
        
        # Check if state is expired (10 min limit)
        if oauth_state.is_expired():
            oauth_state.delete()
            logger.error("LinkedIn OAuth state expired")
            return HttpResponseRedirect(
                f"{frontend_url}/automation?error=state_expired&message=Authorization+timed+out"
            )
        
        user = oauth_state.user
        
        try:
            # Exchange code for tokens
            token_data = linkedin_service.exchange_code_for_token(code)
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token')
            expires_at = token_data.get('expires_at')
            
            # Get user profile from LinkedIn
            profile_data = linkedin_service.get_user_profile(access_token)
            
            social_profile, created = SocialProfile.objects.update_or_create(
                user=user,
                platform='linkedin',
                defaults={
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'token_expires_at': expires_at,
                    'profile_id': profile_data.get('id'),
                    'profile_name': profile_data.get('name'),
                    'profile_url': f"https://www.linkedin.com/in/{profile_data.get('id')}",
                    'profile_image_url': profile_data.get('picture'),
                    'status': 'connected',
                }
            )
            
            # Clean up the OAuth state
            oauth_state.delete()
            
            logger.info(f"LinkedIn connected for user {user.email}")
            
            return HttpResponseRedirect(
                f"{frontend_url}/automation?success=linkedin&name={profile_data.get('name', '')}"
            )
            
        except Exception as e:
            logger.error(f"LinkedIn OAuth callback error: {e}")
            # Clean up the OAuth state even on error
            oauth_state.delete()
            return HttpResponseRedirect(
                f"{frontend_url}/automation?error=connection_failed&message={str(e)}"
            )


class LinkedInTestConnectView(APIView):
    """
    Creates a TEST LinkedIn connection for development/testing purposes.
    This bypasses OAuth and creates a mock profile - NO real LinkedIn data is used.
    Only available in DEBUG mode.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a test LinkedIn connection."""
        if not settings.DEBUG:
            return Response(
                {'error': 'Test connections only available in DEBUG mode'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create a mock LinkedIn profile
        from django.utils import timezone
        from datetime import timedelta
        
        social_profile, created = SocialProfile.objects.update_or_create(
            user=request.user,
            platform='linkedin',
            defaults={
                'access_token': 'test_access_token_not_real',
                'refresh_token': 'test_refresh_token_not_real',
                'token_expires_at': timezone.now() + timedelta(days=60),
                'profile_id': f'test_user_{request.user.id}',
                'profile_name': request.user.get_full_name() or request.user.email.split('@')[0],
                'profile_url': 'https://www.linkedin.com/in/test-profile',
                'profile_image_url': None,
                'status': 'connected',
            }
        )
        
        action = 'created' if created else 'updated'
        logger.info(f"Test LinkedIn profile {action} for user {request.user.email}")
        
        return Response({
            'message': f'Test LinkedIn connection {action} successfully',
            'profile_name': social_profile.profile_name,
            'is_test': True,
        })


class LinkedInDisconnectView(APIView):
    """
    Disconnects LinkedIn account.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Disconnect LinkedIn account."""
        try:
            profile = SocialProfile.objects.get(
                user=request.user,
                platform='linkedin'
            )
            profile.disconnect()
            return Response({
                'message': 'LinkedIn disconnected successfully'
            })
        except SocialProfile.DoesNotExist:
            return Response(
                {'error': 'LinkedIn account not connected'},
                status=status.HTTP_404_NOT_FOUND
            )


class AutomationTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing automation tasks.
    """
    serializer_class = AutomationTaskSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AutomationTask.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ContentCalendarViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing content calendar.
    """
    serializer_class = ContentCalendarSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ContentCalendar.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Manually publish a scheduled post immediately."""
        content = self.get_object()
        
        if content.status == 'published':
            return Response(
                {'error': 'Content already published'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # TODO: Implement actual publishing logic
        # This would iterate through connected platforms and post
        
        return Response({
            'message': 'Publishing initiated',
            'status': 'in_progress'
        })
