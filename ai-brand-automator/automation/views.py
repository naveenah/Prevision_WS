"""
Views for the automation app - social media integrations and content scheduling.
"""
import uuid
import logging
from datetime import timedelta
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
from .services import linkedin_service, twitter_service
from .constants import (
    TEST_ACCESS_TOKEN,
    TEST_REFRESH_TOKEN,
    LINKEDIN_TITLE_MAX_LENGTH,
    EDITABLE_STATUSES,
    IMAGE_TYPES,
    VIDEO_TYPES,
    DOCUMENT_TYPES,
    MAX_IMAGE_SIZE,
    MAX_VIDEO_SIZE,
    MAX_DOCUMENT_SIZE,
    TWITTER_TEST_ACCESS_TOKEN,
    TWITTER_TEST_REFRESH_TOKEN,
    TWITTER_POST_MAX_LENGTH,
    TWITTER_IMAGE_TYPES,
    TWITTER_VIDEO_TYPES,
    TWITTER_MEDIA_MAX_IMAGE_SIZE,
    TWITTER_MEDIA_MAX_VIDEO_SIZE,
    TWITTER_MEDIA_MAX_GIF_SIZE,
)

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
        media_urns = request.data.get(
            "media_urns", []
        )  # List of asset URNs from media upload

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
                payload={
                    "text": text,
                    "platform": "linkedin",
                    "media_count": len(media_urns),
                },
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
                payload={
                    "text": text,
                    "platform": "linkedin",
                    "media_count": len(media_urns),
                },
                result=result,
            )

            logger.info(
                f"LinkedIn post created by {request.user.email} "
                f"(media: {len(media_urns)})"
            )

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
                payload={
                    "text": text,
                    "platform": "linkedin",
                    "media_count": len(media_urns),
                },
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

        # Check for file upload
        # Try 'media' first, then 'image' for backward compatibility
        media_file = request.FILES.get("media") or request.FILES.get("image")

        if media_file:
            content_type = media_file.content_type
            is_video = content_type in VIDEO_TYPES
            is_image = content_type in IMAGE_TYPES
            is_document = content_type in DOCUMENT_TYPES

            if not is_video and not is_image and not is_document:
                allowed = "JPEG, PNG, GIF, MP4, PDF, DOC, DOCX, PPT, PPTX"
                return Response(
                    {"error": f"Invalid file type: {content_type}. Allowed: {allowed}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate file size
            if is_video:
                max_size = MAX_VIDEO_SIZE
                size_label = "500MB"
            elif is_document:
                max_size = MAX_DOCUMENT_SIZE
                size_label = "100MB"
            else:
                max_size = MAX_IMAGE_SIZE
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
                asset_id = f"test-{media_type}-{uuid.uuid4().hex[:12]}"
                test_asset_urn = f"urn:li:digitalmediaAsset:{asset_id}"
                logger.info(
                    f"Test LinkedIn {media_type} upload by {request.user.email}"
                )
                return Response(
                    {
                        "asset_urn": test_asset_urn,
                        "media_type": media_type,
                        "test_mode": True,
                        "status": "PROCESSING"
                        if (is_video or is_document)
                        else "READY",
                        "message": f"{media_type.capitalize()} upload simulated",
                    }
                )

            try:
                access_token = profile.get_valid_access_token()
                file_data = media_file.read()

                if is_video:
                    # Video upload
                    result = linkedin_service.upload_video_file(
                        access_token, profile.profile_id, file_data, content_type
                    )
                    logger.info(
                        f"LinkedIn video uploaded by {request.user.email}: "
                        f"{result['asset_urn']}"
                    )
                    return Response(
                        {
                            "asset_urn": result["asset_urn"],
                            "media_type": "video",
                            "status": result["status"],
                            "message": "Video uploaded. Processing may take a few min.",
                        }
                    )
                elif is_document:
                    # Document upload
                    result = linkedin_service.upload_document_file(
                        access_token,
                        profile.profile_id,
                        file_data,
                        content_type,
                        filename=media_file.name,
                    )
                    logger.info(
                        f"LinkedIn document uploaded by {request.user.email}: "
                        f"{result['document_urn']}"
                    )
                    return Response(
                        {
                            "asset_urn": result["document_urn"],
                            "media_type": "document",
                            "status": result["status"],
                            "message": "Document uploaded. Processing.",
                        }
                    )
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
                    logger.info(
                        f"LinkedIn image uploaded by {request.user.email}: {asset_urn}"
                    )

                    return Response(
                        {
                            "asset_urn": asset_urn,
                            "media_type": "image",
                            "status": "READY",
                            "message": "Image uploaded successfully",
                        }
                    )

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
                asset_id = f"test-url-{uuid.uuid4().hex[:12]}"
                test_asset_urn = f"urn:li:digitalmediaAsset:{asset_id}"
                logger.info(f"Test LinkedIn URL upload by {request.user.email}")
                return Response(
                    {
                        "asset_urn": test_asset_urn,
                        "media_type": "image",
                        "test_mode": True,
                        "status": "READY",
                        "message": "Image upload simulated in test mode",
                    }
                )

            try:
                access_token = profile.get_valid_access_token()
                asset_urn = linkedin_service.upload_image_from_url(
                    access_token, profile.profile_id, image_url
                )

                logger.info(
                    f"LinkedIn image uploaded from URL by {request.user.email}: "
                    f"{asset_urn}"
                )

                return Response(
                    {
                        "asset_urn": asset_urn,
                        "media_type": "image",
                        "status": "READY",
                        "message": "Image uploaded successfully",
                    }
                )

            except Exception as e:
                logger.error(f"LinkedIn media upload from URL failed: {e}")
                return Response(
                    {"error": f"Failed to upload image: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"error": "No media provided. Send 'media', 'image', or 'image_url'"},
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
            return Response(
                {
                    "asset_urn": asset_urn,
                    "status": "READY",
                    "test_mode": True,
                    "message": "Video ready (test mode)",
                }
            )

        try:
            access_token = profile.get_valid_access_token()
            result = linkedin_service.check_video_status(access_token, asset_urn)

            return Response(
                {
                    "asset_urn": result["asset_urn"],
                    "status": result["status"],
                    "message": f"Video status: {result['status']}",
                }
            )

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
            return Response(
                {
                    "document_urn": document_urn,
                    "status": "AVAILABLE",
                    "test_mode": True,
                    "message": "Document ready (test mode)",
                }
            )

        try:
            access_token = profile.get_valid_access_token()
            result = linkedin_service.check_document_status(access_token, document_urn)

            return Response(
                {
                    "document_urn": result["document_urn"],
                    "status": result["status"],
                    "download_url": result.get("download_url"),
                    "message": f"Document status: {result['status']}",
                }
            )

        except Exception as e:
            logger.error(f"LinkedIn document status check failed: {e}")
            return Response(
                {"error": f"Failed to check document status: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TwitterMediaUploadView(APIView):
    """
    Upload media (images, videos, or GIFs) to Twitter for use in tweets.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Upload an image, video, or GIF to Twitter.

        Accepts a file upload (multipart/form-data with 'media' field).

        Returns the media_id to use when creating a tweet with media.
        """
        try:
            profile = SocialProfile.objects.get(
                user=request.user, platform="twitter", status="connected"
            )
        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "Twitter account not connected"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check for file upload
        media_file = request.FILES.get("media")

        if not media_file:
            return Response(
                {"error": "No media file provided. Use 'media' field."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        content_type = media_file.content_type
        is_image = content_type in TWITTER_IMAGE_TYPES
        is_video = content_type in TWITTER_VIDEO_TYPES
        is_gif = content_type == "image/gif"

        if not is_image and not is_video:
            allowed = "JPEG, PNG, GIF, WEBP (images); MP4, MOV (video)"
            return Response(
                {"error": f"Invalid file type: {content_type}. Allowed: {allowed}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Determine media category and size limit
        if is_video:
            media_category = "tweet_video"
            max_size = TWITTER_MEDIA_MAX_VIDEO_SIZE
            size_label = "512MB"
        elif is_gif:
            media_category = "tweet_gif"
            max_size = TWITTER_MEDIA_MAX_GIF_SIZE
            size_label = "15MB"
        else:
            media_category = "tweet_image"
            max_size = TWITTER_MEDIA_MAX_IMAGE_SIZE
            size_label = "5MB"

        if media_file.size > max_size:
            return Response(
                {"error": f"File too large. Maximum size is {size_label}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if test mode
        if profile.access_token == TWITTER_TEST_ACCESS_TOKEN:
            media_type = "video" if is_video else ("gif" if is_gif else "image")
            test_media_id = f"test-{media_type}-{uuid.uuid4().hex[:12]}"
            logger.info(f"Test Twitter {media_type} upload by {request.user.email}")
            return Response(
                {
                    "media_id": test_media_id,
                    "media_id_string": test_media_id,
                    "media_type": media_type,
                    "test_mode": True,
                    "status": "PROCESSING" if is_video else "READY",
                    "message": f"{media_type.capitalize()} upload simulated",
                }
            )

        try:
            access_token = profile.get_valid_access_token()
            file_data = media_file.read()

            result = twitter_service.upload_media(
                access_token=access_token,
                media_data=file_data,
                media_type=content_type,
                media_category=media_category,
            )

            media_type = "video" if is_video else ("gif" if is_gif else "image")
            processing_msg = (
                "Processing may take a few minutes."
                if result.get("status") == "PROCESSING"
                else ""
            )

            logger.info(
                f"Twitter {media_type} uploaded by {request.user.email}: "
                f"{result.get('media_id_string')}"
            )

            return Response(
                {
                    "media_id": result.get("media_id"),
                    "media_id_string": result.get("media_id_string"),
                    "media_type": media_type,
                    "status": result.get("status", "READY"),
                    "message": f"{media_type.capitalize()} uploaded. {processing_msg}",
                }
            )

        except Exception as e:
            logger.error(f"Twitter media upload failed: {e}")
            return Response(
                {"error": f"Failed to upload media: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TwitterMediaStatusView(APIView):
    """
    Check the processing status of uploaded Twitter media.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, media_id):
        """
        Check media processing status.

        Args:
            media_id: The media_id_string returned from media upload

        Returns:
            Status: pending, in_progress, succeeded, failed
        """
        try:
            profile = SocialProfile.objects.get(
                user=request.user, platform="twitter", status="connected"
            )
        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "Twitter account not connected"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Test mode
        if profile.access_token == TWITTER_TEST_ACCESS_TOKEN:
            return Response(
                {
                    "media_id": media_id,
                    "state": "succeeded",
                    "test_mode": True,
                    "message": "Media ready (test mode)",
                }
            )

        try:
            access_token = profile.get_valid_access_token()
            result = twitter_service.get_media_status(access_token, media_id)

            return Response(
                {
                    "media_id": result["media_id"],
                    "state": result["state"],
                    "check_after_secs": result.get("check_after_secs"),
                    "progress_percent": result.get("progress_percent"),
                    "error": result.get("error"),
                    "message": f"Media status: {result['state']}",
                }
            )

        except Exception as e:
            logger.error(f"Twitter media status check failed: {e}")
            return Response(
                {"error": f"Failed to check media status: {str(e)}"},
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

    def _sync_platform_profiles(self, instance):
        """
        Sync social profiles with selected platforms.

        Adds or removes social profiles based on the platforms list.
        """
        # Handle LinkedIn platform
        linkedin_profiles_on_instance = instance.social_profiles.filter(
            platform="linkedin"
        )

        if "linkedin" in instance.platforms:
            # Ensure the user's connected LinkedIn profile is attached
            linkedin_profile = SocialProfile.objects.filter(
                user=self.request.user, platform="linkedin", status="connected"
            ).first()

            if linkedin_profile:
                # Add if not already linked
                if not linkedin_profiles_on_instance.filter(
                    id=linkedin_profile.id
                ).exists():
                    instance.social_profiles.add(linkedin_profile)
        else:
            # LinkedIn removed from platforms - remove any LinkedIn profiles
            if linkedin_profiles_on_instance.exists():
                instance.social_profiles.remove(*linkedin_profiles_on_instance)

        # Handle Twitter platform
        twitter_profiles_on_instance = instance.social_profiles.filter(
            platform="twitter"
        )

        if "twitter" in instance.platforms:
            # Ensure the user's connected Twitter profile is attached
            twitter_profile = SocialProfile.objects.filter(
                user=self.request.user, platform="twitter", status="connected"
            ).first()

            if twitter_profile:
                # Add if not already linked
                if not twitter_profiles_on_instance.filter(
                    id=twitter_profile.id
                ).exists():
                    instance.social_profiles.add(twitter_profile)
        else:
            # Twitter removed from platforms - remove any Twitter profiles
            if twitter_profiles_on_instance.exists():
                instance.social_profiles.remove(*twitter_profiles_on_instance)

    def perform_create(self, serializer):
        """Auto-link social profiles based on selected platforms."""
        instance = serializer.save(user=self.request.user)
        self._sync_platform_profiles(instance)

    def update(self, request, *args, **kwargs):
        """Update a scheduled post. Only draft/scheduled posts can be edited."""
        instance = self.get_object()

        # Prevent editing published, failed, or cancelled posts
        if instance.status not in EDITABLE_STATUSES:
            return Response(
                {"error": f"Cannot edit a post with status '{instance.status}'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        """Handle platform changes when updating a post."""
        instance = serializer.save()
        self._sync_platform_profiles(instance)

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

            elif profile.platform == "twitter" and profile.status == "connected":
                try:
                    # Check if test mode
                    if profile.access_token == TWITTER_TEST_ACCESS_TOKEN:
                        results["twitter"] = {
                            "test_mode": True,
                            "message": "Tweet simulated in test mode",
                            "has_media": len(media_urns) > 0,
                        }
                        logger.info(f"Test publish to Twitter: {content.title}")
                    else:
                        access_token = profile.get_valid_access_token()
                        # Twitter uses media_ids instead of URNs
                        result = twitter_service.create_tweet(
                            access_token=access_token,
                            text=content.content,
                            media_ids=media_urns if media_urns else None,
                        )
                        results["twitter"] = result
                except Exception as e:
                    errors.append(f"Twitter: {str(e)}")
                    logger.error(f"Failed to publish to Twitter: {e}")

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


# =============================================================================
# Twitter/X Integration Views
# =============================================================================


class TwitterConnectView(APIView):
    """
    Initiate Twitter OAuth 2.0 flow with PKCE.

    Returns the authorization URL that the frontend should redirect to.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        from .services import twitter_service

        if not twitter_service.is_configured:
            return Response(
                {"error": "Twitter OAuth not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Generate PKCE code verifier and challenge
        code_verifier, code_challenge = twitter_service.generate_pkce_pair()

        # Generate unique state for CSRF protection
        state = str(uuid.uuid4())

        # Store state and code_verifier in session/database
        OAuthState.objects.create(
            user=request.user,
            platform="twitter",
            state=state,
            code_verifier=code_verifier,  # Store for token exchange
        )

        try:
            auth_url = twitter_service.get_authorization_url(state, code_challenge)
            return Response({"authorization_url": auth_url})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TwitterCallbackView(APIView):
    """
    Handle Twitter OAuth 2.0 callback.

    Exchanges authorization code for tokens and creates/updates SocialProfile.
    """

    # No authentication required - this is a callback from Twitter
    permission_classes = []

    def get(self, request):
        from .services import twitter_service

        code = request.GET.get("code")
        state = request.GET.get("state")
        error = request.GET.get("error")

        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")

        if error:
            logger.error(f"Twitter OAuth error: {error}")
            return HttpResponseRedirect(
                f"{frontend_url}/automation?error=twitter_auth_failed"
            )

        if not code or not state:
            return HttpResponseRedirect(
                f"{frontend_url}/automation?error=missing_params"
            )

        # Validate state and get code_verifier
        try:
            oauth_state = OAuthState.objects.get(
                state=state,
                platform="twitter",
                used=False,
            )
        except OAuthState.DoesNotExist:
            return HttpResponseRedirect(
                f"{frontend_url}/automation?error=invalid_state"
            )

        # Mark state as used
        oauth_state.used = True
        oauth_state.save()

        # Check if state is expired (5 minutes)
        if (timezone.now() - oauth_state.created_at).total_seconds() > 300:
            return HttpResponseRedirect(f"{frontend_url}/automation?error=state_expired")

        try:
            # Exchange code for tokens with PKCE verifier
            token_data = twitter_service.exchange_code_for_token(
                code, oauth_state.code_verifier
            )

            # Get user info
            user_info = twitter_service.get_user_info(token_data["access_token"])

            # Create or update social profile
            profile, created = SocialProfile.objects.update_or_create(
                user=oauth_state.user,
                platform="twitter",
                defaults={
                    "access_token": token_data["access_token"],
                    "refresh_token": token_data.get("refresh_token"),
                    "token_expires_at": token_data.get("expires_at"),
                    "profile_id": user_info.get("id"),
                    "profile_name": user_info.get("name"),
                    "profile_url": f"https://twitter.com/{user_info.get('username')}",
                    "profile_image_url": user_info.get("profile_image_url"),
                    "status": "connected",
                },
            )

            logger.info(
                f"Twitter connected for user {oauth_state.user.email}: "
                f"@{user_info.get('username')}"
            )

            return HttpResponseRedirect(
                f"{frontend_url}/automation?success=true&platform=twitter"
            )

        except Exception as e:
            logger.error(f"Twitter OAuth callback failed: {e}")
            return HttpResponseRedirect(
                f"{frontend_url}/automation?error=twitter_token_exchange_failed"
            )


class TwitterDisconnectView(APIView):
    """Disconnect Twitter account."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .services import twitter_service

        try:
            profile = SocialProfile.objects.get(
                user=request.user, platform="twitter"
            )

            # Revoke token if possible
            if profile.access_token:
                try:
                    twitter_service.revoke_token(profile.access_token)
                except Exception as e:
                    logger.warning(f"Failed to revoke Twitter token: {e}")

            # Clear tokens and mark as disconnected
            profile.access_token = None
            profile.refresh_token = None
            profile.token_expires_at = None
            profile.status = "disconnected"
            profile.save()

            return Response({"message": "Twitter account disconnected successfully"})

        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "No Twitter account connected"},
                status=status.HTTP_404_NOT_FOUND,
            )


class TwitterTestConnectView(APIView):
    """
    Create a mock Twitter connection for testing (DEBUG mode only).

    This allows testing the Twitter integration without real OAuth.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not settings.DEBUG:
            return Response(
                {"error": "Test connect only available in DEBUG mode"},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Create mock profile
        profile, created = SocialProfile.objects.update_or_create(
            user=request.user,
            platform="twitter",
            defaults={
                "access_token": TWITTER_TEST_ACCESS_TOKEN,
                "refresh_token": TWITTER_TEST_REFRESH_TOKEN,
                "token_expires_at": timezone.now() + timedelta(days=60),
                "profile_id": f"test_twitter_{request.user.id}",
                "profile_name": f"Test User ({request.user.email})",
                "profile_url": f"https://twitter.com/test_user_{request.user.id}",
                "profile_image_url": None,
                "status": "connected",
            },
        )

        return Response(
            {
                "message": "Test Twitter connection created",
                "profile_name": profile.profile_name,
                "is_test_mode": True,
            }
        )


class TwitterPostView(APIView):
    """
    Create a tweet on Twitter/X.

    Requires a connected Twitter account.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .services import twitter_service
        from .constants import TWITTER_POST_MAX_LENGTH

        title = request.data.get("title", "").strip()
        text = request.data.get("text", "").strip()
        media_ids = request.data.get("media_ids", [])

        if not text:
            return Response(
                {"error": "Tweet text is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate length
        validation = twitter_service.validate_tweet_length(text)
        if not validation["is_valid"]:
            return Response(
                {
                    "error": f"Tweet exceeds max length of {validation['max_length']} "
                    f"characters (current: {validation['length']})"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate media_ids is a list
        if media_ids and not isinstance(media_ids, list):
            media_ids = [media_ids]

        try:
            profile = SocialProfile.objects.get(
                user=request.user, platform="twitter", status="connected"
            )
        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "Twitter account not connected"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check for test mode
        if profile.access_token == TWITTER_TEST_ACCESS_TOKEN:
            logger.info(f"Test mode tweet by {request.user.email}: {text[:50]}...")

            # Create a ContentCalendar entry for the published tweet
            post_title = (
                title
                if title
                else f"Twitter Post - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            )
            content = ContentCalendar.objects.create(
                user=request.user,
                title=post_title,
                content=text,
                media_urls=media_ids,
                platforms=["twitter"],
                scheduled_date=timezone.now(),
                published_at=timezone.now(),
                status="published",
                post_results={
                    "test_mode": True,
                    "message": "Tweet simulated in test mode",
                    "has_media": len(media_ids) > 0,
                },
            )
            content.social_profiles.add(profile)

            # Create an automation task record
            task = AutomationTask.objects.create(
                user=request.user,
                task_type="social_post",
                status="completed",
                payload={
                    "text": text,
                    "platform": "twitter",
                    "media_count": len(media_ids),
                },
                result={"test_mode": True, "message": "Tweet simulated in test mode"},
            )

            return Response(
                {
                    "message": "Tweet simulated (test mode)",
                    "test_mode": True,
                    "task_id": task.id,
                    "content_id": content.id,
                    "tweet": {
                        "id": f"test_tweet_{uuid.uuid4().hex[:12]}",
                        "text": text,
                    },
                }
            )

        try:
            # Get valid access token (refresh if needed)
            access_token = profile.get_valid_access_token()

            # Create tweet
            result = twitter_service.create_tweet(
                access_token=access_token,
                text=text,
                reply_to_id=request.data.get("reply_to_id"),
                quote_tweet_id=request.data.get("quote_tweet_id"),
                media_ids=media_ids if media_ids else None,
            )

            # Create a ContentCalendar entry for the published tweet
            post_title = (
                title
                if title
                else f"Twitter Post - {timezone.now().strftime('%Y-%m-%d %H:%M')}"
            )
            content = ContentCalendar.objects.create(
                user=request.user,
                title=post_title,
                content=text,
                media_urls=media_ids,
                platforms=["twitter"],
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
                payload={
                    "text": text,
                    "platform": "twitter",
                    "media_count": len(media_ids),
                },
                result=result,
            )

            logger.info(
                f"Twitter tweet created by {request.user.email} "
                f"(media: {len(media_ids)})"
            )

            return Response(
                {
                    "message": "Tweet posted successfully",
                    "tweet_id": result.get("id"),
                    "task_id": task.id,
                    "content_id": content.id,
                    "has_media": len(media_ids) > 0,
                    "tweet": result,
                }
            )

        except Exception as e:
            logger.error(f"Failed to post tweet: {e}")
            return Response(
                {"error": f"Failed to post tweet: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TwitterValidateTweetView(APIView):
    """
    Validate tweet text without posting.

    Used for real-time validation in the UI.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        from .services import twitter_service

        text = request.data.get("text", "")
        is_premium = request.data.get("is_premium", False)

        validation = twitter_service.validate_tweet_length(text, is_premium)

        return Response(validation)


class TwitterDeleteTweetView(APIView):
    """
    Delete a tweet by its ID.
    
    Requires a connected Twitter account.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, tweet_id):
        from .services import twitter_service
        from .constants import TWITTER_TEST_ACCESS_TOKEN

        try:
            profile = SocialProfile.objects.get(
                user=request.user, platform="twitter", status="connected"
            )
        except SocialProfile.DoesNotExist:
            return Response(
                {"error": "Twitter account not connected"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check for test mode
        if profile.access_token == TWITTER_TEST_ACCESS_TOKEN:
            logger.info(f"Test mode tweet deletion by {request.user.email}: {tweet_id}")
            
            # Update ContentCalendar if exists
            ContentCalendar.objects.filter(
                user=request.user,
                post_results__tweet__id=tweet_id,
            ).update(status="cancelled")
            
            return Response({
                "message": "Tweet deleted (test mode)",
                "test_mode": True,
                "tweet_id": tweet_id,
            })

        try:
            access_token = profile.get_valid_access_token()
            success = twitter_service.delete_tweet(access_token, tweet_id)

            if success:
                # Update ContentCalendar if exists
                ContentCalendar.objects.filter(
                    user=request.user,
                    post_results__id=tweet_id,
                ).update(status="cancelled")

                logger.info(f"Tweet deleted by {request.user.email}: {tweet_id}")
                return Response({
                    "message": "Tweet deleted successfully",
                    "tweet_id": tweet_id,
                })
            else:
                return Response(
                    {"error": "Failed to delete tweet"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        except Exception as e:
            logger.error(f"Failed to delete tweet: {e}")
            return Response(
                {"error": f"Failed to delete tweet: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
