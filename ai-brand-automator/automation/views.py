"""
Views for the automation app - social media integrations and content scheduling.
"""
import uuid
import logging
from django.http import HttpResponseRedirect
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
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
from .constants import TEST_ACCESS_TOKEN, TEST_REFRESH_TOKEN, LINKEDIN_TITLE_MAX_LENGTH

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

    @action(detail=True, methods=["post"])
    def disconnect(self, request, pk=None):
        """Disconnect a social profile."""
        profile = self.get_object()
        profile.disconnect()
        return Response(
            {"message": f"{profile.get_platform_display()} disconnected successfully"}
        )

    @action(detail=False, methods=["get"])
    def status(self, request):
        """Get connection status for all platforms."""
        profiles = self.get_queryset()

        # Build status for each supported platform
        platforms = ["linkedin", "twitter", "instagram", "facebook"]
        status_dict = {}

        for platform in platforms:
            profile = profiles.filter(platform=platform).first()
            if profile:
                status_dict[platform] = {
                    "connected": profile.status == "connected",
                    "profile_name": profile.profile_name,
                    "profile_url": profile.profile_url,
                    "profile_image_url": profile.profile_image_url,
                    "status": profile.status,
                    "is_token_valid": profile.is_token_valid,
                }
            else:
                status_dict[platform] = {
                    "connected": False,
                    "profile_name": None,
                    "profile_url": None,
                    "profile_image_url": None,
                    "status": "disconnected",
                    "is_token_valid": False,
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
                {"error": "LinkedIn integration not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Generate a unique state token and store it in database
        # This is more reliable than sessions for JWT-based apps
        state = str(uuid.uuid4())

        # Clean up any old states for this user/platform
        OAuthState.objects.filter(user=request.user, platform="linkedin").delete()

        # Create new state
        OAuthState.objects.create(state=state, user=request.user, platform="linkedin")

        # Get the authorization URL
        auth_url = linkedin_service.get_authorization_url(state)

        return Response({"authorization_url": auth_url})


class LinkedInCallbackView(APIView):
    """
    Handles LinkedIn OAuth callback.
    """

    # No authentication required - this is called by LinkedIn redirect
    permission_classes = []

    def get(self, request):
        """Handle the OAuth callback from LinkedIn."""
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")
        error_description = request.query_params.get("error_description")

        # Debug logging
        logger.info(
            f"LinkedIn callback received - code: {bool(code)}, "
            f"state: {state}, error: {error}"
        )

        # Get frontend URL for redirects
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")

        # Handle errors from LinkedIn
        if error:
            logger.error(f"LinkedIn OAuth error: {error} - {error_description}")
            return HttpResponseRedirect(
                f"{frontend_url}/automation?error={error}&message={error_description}"
            )

        # Validate state token from database (more reliable than sessions for JWT apps)
        try:
            oauth_state = OAuthState.objects.get(state=state, platform="linkedin")
        except OAuthState.DoesNotExist:
            logger.error(f"LinkedIn OAuth state not found: {state}")
            redirect_url = (
                f"{frontend_url}/automation?error=invalid_state"
                "&message=State+token+not+found+or+expired"
            )
            return HttpResponseRedirect(redirect_url)

        # Check if state is expired (10 min limit)
        if oauth_state.is_expired():
            oauth_state.delete()
            logger.error("LinkedIn OAuth state expired")
            redirect_url = (
                f"{frontend_url}/automation?error=state_expired"
                "&message=Authorization+timed+out"
            )
            return HttpResponseRedirect(redirect_url)

        user = oauth_state.user

        try:
            # Exchange code for tokens
            token_data = linkedin_service.exchange_code_for_token(code)
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            expires_at = token_data.get("expires_at")

            # Get user profile from LinkedIn
            profile_data = linkedin_service.get_user_profile(access_token)

            # Extract profile ID - the 'sub' field may be full URN or just ID
            # Store the full ID for API calls (create_share handles both formats)
            profile_id = profile_data.get("id", "")

            # LinkedIn profile URLs require vanity name which isn't available
            # from userinfo endpoint, so we link to the generic profile page
            # Note: profile_id may be in URN format, not suitable for /in/ URLs
            profile_url = "https://www.linkedin.com/feed/"

            _social_profile, _created = SocialProfile.objects.update_or_create(
                user=user,
                platform="linkedin",
                defaults={
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_expires_at": expires_at,
                    "profile_id": profile_id,
                    "profile_name": profile_data.get("name"),
                    "profile_url": profile_url,
                    "profile_image_url": profile_data.get("picture"),
                    "status": "connected",
                },
            )

            # Clean up the OAuth state
            oauth_state.delete()

            logger.info(f"LinkedIn connected for user {user.email}")

            profile_name = profile_data.get("name", "")
            redirect_url = (
                f"{frontend_url}/automation?success=linkedin&name={profile_name}"
            )
            return HttpResponseRedirect(redirect_url)

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
                {"error": "Test connections only available in DEBUG mode"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Create a mock LinkedIn profile
        from django.utils import timezone
        from datetime import timedelta

        social_profile, created = SocialProfile.objects.update_or_create(
            user=request.user,
            platform="linkedin",
            defaults={
                "access_token": TEST_ACCESS_TOKEN,
                "refresh_token": TEST_REFRESH_TOKEN,
                "token_expires_at": timezone.now() + timedelta(days=60),
                "profile_id": f"test_user_{request.user.id}",
                "profile_name": request.user.get_full_name()
                or request.user.email.split("@")[0],
                "profile_url": "https://www.linkedin.com/in/test-profile",
                "profile_image_url": None,
                "status": "connected",
            },
        )

        action = "created" if created else "updated"
        logger.info(f"Test LinkedIn profile {action} for user {request.user.email}")

        return Response(
            {
                "message": f"Test LinkedIn connection {action} successfully",
                "profile_name": social_profile.profile_name,
                "is_test": True,
            }
        )


class LinkedInDisconnectView(APIView):
    """
    Disconnects LinkedIn account.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Disconnect LinkedIn account."""
        try:
            profile = SocialProfile.objects.get(user=request.user, platform="linkedin")
            profile.disconnect()
            return Response({"message": "LinkedIn disconnected successfully"})
        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "LinkedIn account not connected"},
                status=status.HTTP_404_NOT_FOUND,
            )


class LinkedInPostView(APIView):
    """
    Create a post on LinkedIn.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Create a LinkedIn post."""
        title = request.data.get("title", "").strip()
        text = request.data.get("text", "").strip()
        media_urns = request.data.get("media_urns", [])  # List of asset URNs from media upload

        if not text:
            return Response(
                {"error": "Post text is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if len(text) > 3000:
            return Response(
                {"error": "Post text cannot exceed 3000 characters"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate title length if provided
        if title and len(title) > LINKEDIN_TITLE_MAX_LENGTH:
            return Response(
                {"error": f"Title cannot exceed {LINKEDIN_TITLE_MAX_LENGTH} chars"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate media_urns is a list
        if media_urns and not isinstance(media_urns, list):
            media_urns = [media_urns]

        try:
            profile = SocialProfile.objects.get(
                user=request.user, platform="linkedin", status="connected"
            )
        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "LinkedIn account not connected"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check if this is a test profile
        if profile.access_token == TEST_ACCESS_TOKEN:
            # Simulate posting for test mode
            logger.info(f"Test LinkedIn post by {request.user.email}: {text[:50]}...")

            # Create a ContentCalendar entry for the published post
            post_title = (
                title
                if title
                else f"LinkedIn Post - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            )
            content = ContentCalendar.objects.create(
                user=request.user,
                title=post_title,
                content=text,
                media_urls=media_urns,  # Store media URNs
                platforms=["linkedin"],
                scheduled_date=timezone.now(),
                published_at=timezone.now(),
                status="published",
                post_results={
                    "test_mode": True,
                    "message": "Post simulated in test mode",
                    "has_media": len(media_urns) > 0,
                },
            )
            content.social_profiles.add(profile)

            # Create an automation task record
            task = AutomationTask.objects.create(
                user=request.user,
                task_type="social_post",
                status="completed",
                payload={"text": text, "platform": "linkedin", "media_count": len(media_urns)},
                result={"test_mode": True, "message": "Post simulated in test mode"},
            )

            return Response(
                {
                    "message": "Post created successfully (Test Mode)",
                    "test_mode": True,
                    "task_id": task.id,
                    "content_id": content.id,
                }
            )

        try:
            # Get valid access token (auto-refresh if needed)
            access_token = profile.get_valid_access_token()

            # Create the post (with optional media)
            result = linkedin_service.create_share(
                access_token=access_token, 
                user_urn=profile.profile_id, 
                text=text,
                image_urns=media_urns if media_urns else None,
            )

            # Create a ContentCalendar entry for the published post
            post_title = (
                title
                if title
                else f"LinkedIn Post - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            )
            content = ContentCalendar.objects.create(
                user=request.user,
                title=post_title,
                content=text,
                media_urls=media_urns,  # Store media URNs
                platforms=["linkedin"],
                scheduled_date=timezone.now(),
                published_at=timezone.now(),
                status="published",
                post_results=result,
            )
            content.social_profiles.add(profile)

            # Create an automation task record
            task = AutomationTask.objects.create(
                user=request.user,
                task_type="social_post",
                status="completed",
                payload={"text": text, "platform": "linkedin", "media_count": len(media_urns)},
                result=result,
            )

            logger.info(f"LinkedIn post created by {request.user.email} (media: {len(media_urns)})")

            return Response(
                {
                    "message": "Post created successfully",
                    "post_id": result.get("id"),
                    "task_id": task.id,
                    "content_id": content.id,
                    "has_media": len(media_urns) > 0,
                }
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"LinkedIn post failed: {e}")

            # Create a failed task record
            AutomationTask.objects.create(
                user=request.user,
                task_type="social_post",
                status="failed",
                payload={"text": text, "platform": "linkedin", "media_count": len(media_urns)},
                result={"error": str(e)},
            )

            return Response(
                {"error": f"Failed to create post: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LinkedInMediaUploadView(APIView):
    """
    Upload media (images, videos, or documents) to LinkedIn for use in posts.
    """

    permission_classes = [IsAuthenticated]

    # Supported media types (LinkedIn officially supports MP4 only for video)
    IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]
    VIDEO_TYPES = ["video/mp4"]  # LinkedIn standard: MP4 only
    DOCUMENT_TYPES = [
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # docx
        "application/vnd.ms-powerpoint",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation",  # pptx
    ]
    
    # Size limits (LinkedIn standards: images 8MB, videos 75KB-500MB, documents 100MB)
    MAX_IMAGE_SIZE = 8 * 1024 * 1024  # 8MB
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB (LinkedIn max for organic posts)
    MAX_DOCUMENT_SIZE = 100 * 1024 * 1024  # 100MB (LinkedIn max for documents)

    def post(self, request):
        """
        Upload an image or video to LinkedIn.
        
        Accepts either:
        - A file upload (multipart/form-data with 'media' or 'image' field)
        - An image URL (JSON with 'image_url' field)
        
        Returns the asset URN to use when creating a post with media.
        """
        try:
            profile = SocialProfile.objects.get(
                user=request.user, platform="linkedin", status="connected"
            )
        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "LinkedIn account not connected"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check for file upload (try 'media' first, then 'image' for backward compatibility)
        media_file = request.FILES.get("media") or request.FILES.get("image")
        
        if media_file:
            content_type = media_file.content_type
            is_video = content_type in self.VIDEO_TYPES
            is_image = content_type in self.IMAGE_TYPES
            is_document = content_type in self.DOCUMENT_TYPES
            
            if not is_video and not is_image and not is_document:
                return Response(
                    {"error": f"Invalid file type: {content_type}. Allowed: JPEG, PNG, GIF, MP4, PDF, DOC, DOCX, PPT, PPTX"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            # Validate file size
            if is_video:
                max_size = self.MAX_VIDEO_SIZE
                size_label = "500MB"
            elif is_document:
                max_size = self.MAX_DOCUMENT_SIZE
                size_label = "100MB"
            else:
                max_size = self.MAX_IMAGE_SIZE
                size_label = "8MB"
                
            if media_file.size > max_size:
                return Response(
                    {"error": f"File too large. Maximum size is {size_label}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check if test mode
            if profile.access_token == TEST_ACCESS_TOKEN:
                if is_video:
                    media_type = "video"
                elif is_document:
                    media_type = "document"
                else:
                    media_type = "image"
                test_asset_urn = f"urn:li:digitalmediaAsset:test-{media_type}-{uuid.uuid4().hex[:12]}"
                logger.info(f"Test LinkedIn {media_type} upload by {request.user.email}")
                return Response({
                    "asset_urn": test_asset_urn,
                    "media_type": media_type,
                    "test_mode": True,
                    "status": "PROCESSING" if (is_video or is_document) else "READY",
                    "message": f"{media_type.capitalize()} upload simulated in test mode",
                })

            try:
                access_token = profile.get_valid_access_token()
                file_data = media_file.read()
                
                if is_video:
                    # Video upload
                    result = linkedin_service.upload_video_file(
                        access_token, profile.profile_id, file_data, content_type
                    )
                    logger.info(f"LinkedIn video uploaded by {request.user.email}: {result['asset_urn']}")
                    return Response({
                        "asset_urn": result["asset_urn"],
                        "media_type": "video",
                        "status": result["status"],
                        "message": "Video uploaded successfully. Processing may take a few minutes.",
                    })
                elif is_document:
                    # Document upload
                    result = linkedin_service.upload_document_file(
                        access_token, profile.profile_id, file_data, content_type,
                        filename=media_file.name
                    )
                    logger.info(f"LinkedIn document uploaded by {request.user.email}: {result['document_urn']}")
                    return Response({
                        "asset_urn": result["document_urn"],
                        "media_type": "document",
                        "status": result["status"],
                        "message": "Document uploaded successfully. Processing may take a few minutes.",
                    })
                else:
                    # Image upload
                    upload_info = linkedin_service.register_image_upload(
                        access_token, profile.profile_id
                    )
                    upload_url = upload_info.get("upload_url")
                    asset_urn = upload_info.get("asset_urn")

                    if not upload_url or not asset_urn:
                        return Response(
                            {"error": "Failed to get upload URL from LinkedIn"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )

                    linkedin_service.upload_image(upload_url, file_data, content_type)
                    logger.info(f"LinkedIn image uploaded by {request.user.email}: {asset_urn}")
                    
                    return Response({
                        "asset_urn": asset_urn,
                        "media_type": "image",
                        "status": "READY",
                        "message": "Image uploaded successfully",
                    })

            except Exception as e:
                logger.error(f"LinkedIn media upload failed: {e}")
                return Response(
                    {"error": f"Failed to upload media: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # Handle URL-based upload (images only)
        image_url = request.data.get("image_url")
        if image_url:
            # Check if test mode
            if profile.access_token == TEST_ACCESS_TOKEN:
                test_asset_urn = f"urn:li:digitalmediaAsset:test-url-{uuid.uuid4().hex[:12]}"
                logger.info(f"Test LinkedIn URL upload by {request.user.email}")
                return Response({
                    "asset_urn": test_asset_urn,
                    "media_type": "image",
                    "test_mode": True,
                    "status": "READY",
                    "message": "Image upload simulated in test mode",
                })
            
            try:
                access_token = profile.get_valid_access_token()
                asset_urn = linkedin_service.upload_image_from_url(
                    access_token, profile.profile_id, image_url
                )

                logger.info(f"LinkedIn image uploaded from URL by {request.user.email}: {asset_urn}")

                return Response({
                    "asset_urn": asset_urn,
                    "media_type": "image",
                    "status": "READY",
                    "message": "Image uploaded successfully",
                })

            except Exception as e:
                logger.error(f"LinkedIn media upload from URL failed: {e}")
                return Response(
                    {"error": f"Failed to upload image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"error": "No media provided. Send 'media' file, 'image' file, or 'image_url'"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LinkedInVideoStatusView(APIView):
    """
    Check the processing status of an uploaded video.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, asset_urn):
        """
        Check video processing status.
        
        Args:
            asset_urn: The asset URN returned from video upload
        
        Returns:
            Status: PROCESSING, READY, or FAILED
        """
        try:
            profile = SocialProfile.objects.get(
                user=request.user, platform="linkedin", status="connected"
            )
        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "LinkedIn account not connected"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Test mode
        if profile.access_token == TEST_ACCESS_TOKEN:
            return Response({
                "asset_urn": asset_urn,
                "status": "READY",
                "test_mode": True,
                "message": "Video ready (test mode)",
            })

        try:
            access_token = profile.get_valid_access_token()
            result = linkedin_service.check_video_status(access_token, asset_urn)
            
            return Response({
                "asset_urn": result["asset_urn"],
                "status": result["status"],
                "message": f"Video status: {result['status']}",
            })

        except Exception as e:
            logger.error(f"LinkedIn video status check failed: {e}")
            return Response(
                {"error": f"Failed to check video status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LinkedInDocumentStatusView(APIView):
    """
    Check the processing status of an uploaded document.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, document_urn):
        """
        Check document processing status.
        
        Args:
            document_urn: The document URN returned from document upload
        
        Returns:
            Status: PROCESSING, AVAILABLE, or FAILED
        """
        try:
            profile = SocialProfile.objects.get(
                user=request.user, platform="linkedin", status="connected"
            )
        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "LinkedIn account not connected"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Test mode
        if profile.access_token == TEST_ACCESS_TOKEN:
            return Response({
                "document_urn": document_urn,
                "status": "AVAILABLE",
                "test_mode": True,
                "message": "Document ready (test mode)",
            })

        try:
            access_token = profile.get_valid_access_token()
            result = linkedin_service.check_document_status(access_token, document_urn)
            
            return Response({
                "document_urn": result["document_urn"],
                "status": result["status"],
                "download_url": result.get("download_url"),
                "message": f"Document status: {result['status']}",
            })

        except Exception as e:
            logger.error(f"LinkedIn document status check failed: {e}")
            return Response(
                {"error": f"Failed to check document status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        queryset = ContentCalendar.objects.filter(user=self.request.user)

        # Filter by status
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by platform
        platform = self.request.query_params.get("platform")
        if platform:
            queryset = queryset.filter(platforms__contains=[platform])

        # Filter by date range
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date:
            queryset = queryset.filter(scheduled_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_date__lte=end_date)

        queryset = queryset.order_by("-updated_at")

        # Apply limit if specified
        limit = self.request.query_params.get("limit")
        if limit:
            try:
                limit_int = int(limit)
                if limit_int > 0:
                    queryset = queryset[:limit_int]
            except ValueError:
                # If limit is not a valid integer, ignore it and return full queryset
                pass

        return queryset

    def perform_create(self, serializer):
        # Auto-link LinkedIn profile if platform is selected
        instance = serializer.save(user=self.request.user)

        if "linkedin" in instance.platforms:
            linkedin_profile = SocialProfile.objects.filter(
                user=self.request.user, platform="linkedin", status="connected"
            ).first()
            if linkedin_profile:
                instance.social_profiles.add(linkedin_profile)

    def update(self, request, *args, **kwargs):
        """Update a scheduled post. Only draft/scheduled posts can be edited."""
        instance = self.get_object()

        # Prevent editing published, failed, or cancelled posts
        if instance.status not in ["draft", "scheduled"]:
            return Response(
                {"error": f"Cannot edit a post with status '{instance.status}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Handle platform changes when updating a post."""
        instance = serializer.save()

        # Re-link LinkedIn profile if platforms changed
        if "linkedin" in instance.platforms:
            linkedin_profile = SocialProfile.objects.filter(
                user=self.request.user, platform="linkedin", status="connected"
            ).first()
            if (
                linkedin_profile
                and linkedin_profile not in instance.social_profiles.all()
            ):
                instance.social_profiles.add(linkedin_profile)

    @action(detail=False, methods=["get"])
    def upcoming(self, request):
        """Get all scheduled posts (pending and overdue) ordered by date."""
        # Show all scheduled posts - both upcoming and overdue ones
        # that haven't been published
        upcoming = ContentCalendar.objects.filter(
            user=request.user,
            status="scheduled",
        ).order_by("scheduled_date")

        serializer = self.get_serializer(upcoming, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        """Manually publish a scheduled post immediately."""
        content = self.get_object()

        if content.status == "published":
            return Response(
                {"error": "Content already published"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = {}
        errors = []

        # Get media URNs if any
        media_urns = content.media_urls if content.media_urls else []

        # Publish to each connected platform
        for profile in content.social_profiles.all():
            if profile.platform == "linkedin" and profile.status == "connected":
                try:
                    # Check if test mode
                    if profile.access_token == TEST_ACCESS_TOKEN:
                        results["linkedin"] = {
                            "test_mode": True,
                            "message": "Post simulated in test mode",
                            "has_media": len(media_urns) > 0,
                        }
                        logger.info(f"Test publish to LinkedIn: {content.title}")
                    else:
                        access_token = profile.get_valid_access_token()
                        result = linkedin_service.create_share(
                            access_token=access_token,
                            user_urn=profile.profile_id,
                            text=content.content,
                            image_urns=media_urns if media_urns else None,
                        )
                        results["linkedin"] = result
                except Exception as e:
                    errors.append(f"LinkedIn: {str(e)}")
                    logger.error(f"Failed to publish to LinkedIn: {e}")

        # Update content status
        if errors and not results:
            content.status = "failed"
            content.post_results = {"errors": errors}
        else:
            content.status = "published"
            content.published_at = timezone.now()
            content.post_results = results

        content.save()

        return Response(
            {
                "message": "Publishing completed"
                if not errors
                else "Publishing completed with some errors",
                "status": content.status,
                "results": results,
                "errors": errors,
            }
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a scheduled post."""
        content = self.get_object()

        if content.status == "published":
            return Response(
                {"error": "Cannot cancel a published post"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content.status = "cancelled"
        content.save()

        return Response(
            {"message": "Post cancelled successfully", "status": content.status}
        )
