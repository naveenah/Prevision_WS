"""
LinkedIn OAuth and API service.
"""
import requests
import logging
from datetime import timedelta
from urllib.parse import urlencode
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class LinkedInService:
    """
    Service for LinkedIn OAuth 2.0 authentication and API interactions.

    LinkedIn API v2 with OAuth 2.0 (3-legged)
    Documentation:
    https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow
    """

    AUTHORIZATION_URL = "https://www.linkedin.com/oauth/v2/authorization"
    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    PROFILE_URL = "https://api.linkedin.com/v2/userinfo"

    # Scopes for basic profile access
    SCOPES = [
        "openid",
        "profile",
        "email",
        "w_member_social",  # For posting content
    ]

    def __init__(self):
        self.client_id = getattr(settings, "LINKEDIN_CLIENT_ID", None)
        self.client_secret = getattr(settings, "LINKEDIN_CLIENT_SECRET", None)
        self.redirect_uri = getattr(
            settings,
            "LINKEDIN_REDIRECT_URI",
            "http://localhost:8000/api/v1/automation/linkedin/callback/",
        )

    @property
    def is_configured(self) -> bool:
        """Check if LinkedIn credentials are configured."""
        return bool(self.client_id and self.client_secret)

    def get_authorization_url(self, state: str) -> str:
        """
        Generate the LinkedIn OAuth authorization URL.

        Args:
            state: A unique state token to prevent CSRF attacks

        Returns:
            The full authorization URL to redirect the user to
        """
        if not self.is_configured:
            raise ValueError("LinkedIn credentials not configured")

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "state": state,
            "scope": " ".join(self.SCOPES),
        }

        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str) -> dict:
        """
        Exchange the authorization code for access and refresh tokens.

        Args:
            code: The authorization code from LinkedIn callback

        Returns:
            Dictionary with access_token, expires_in, refresh_token, etc.
        """
        if not self.is_configured:
            raise ValueError("LinkedIn credentials not configured")

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            response.raise_for_status()
            token_data = response.json()

            # Calculate token expiration time
            expires_in = token_data.get("expires_in", 3600)
            token_data["expires_at"] = timezone.now() + timedelta(seconds=expires_in)

            return token_data

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn token exchange failed: {e}")
            raise Exception(f"Failed to exchange code for token: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh an expired access token.

        Args:
            refresh_token: The refresh token from the original OAuth flow

        Returns:
            Dictionary with new access_token, expires_in, etc.
        """
        if not self.is_configured:
            raise ValueError("LinkedIn credentials not configured")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }

        try:
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=30,
            )
            response.raise_for_status()
            token_data = response.json()

            # Calculate token expiration time
            expires_in = token_data.get("expires_in", 3600)
            token_data["expires_at"] = timezone.now() + timedelta(seconds=expires_in)

            return token_data

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn token refresh failed: {e}")
            raise Exception(f"Failed to refresh token: {str(e)}")

    def get_user_profile(self, access_token: str) -> dict:
        """
        Fetch the user's LinkedIn profile.

        Args:
            access_token: Valid LinkedIn access token

        Returns:
            Dictionary with user profile information
        """
        try:
            response = requests.get(
                self.PROFILE_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                timeout=30,
            )
            response.raise_for_status()
            profile_data = response.json()

            # Normalize the profile data
            return {
                "id": profile_data.get("sub"),
                "name": profile_data.get("name"),
                "email": profile_data.get("email"),
                "picture": profile_data.get("picture"),
                "given_name": profile_data.get("given_name"),
                "family_name": profile_data.get("family_name"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn profile fetch failed: {e}")
            raise Exception(f"Failed to fetch profile: {str(e)}")

    def create_share(
        self,
        access_token: str,
        user_urn: str,
        text: str,
        image_urns: list = None,
        video_urn: str = None,
    ) -> dict:
        """
        Create a share (post) on LinkedIn.

        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN (may be just ID or full URN format)
            text: The post content
            image_urns: Optional list of image asset URNs for media posts
            video_urn: Optional video asset URN for video posts
                (takes precedence over images)

        Returns:
            Dictionary with the created post information
        """
        share_url = "https://api.linkedin.com/v2/ugcPosts"

        # Handle URN format: user_urn may be just ID or full URN
        # Normalize to full URN format
        if user_urn.startswith("urn:li:person:"):
            author_urn = user_urn
        else:
            author_urn = f"urn:li:person:{user_urn}"

        # Video takes precedence over images
        if video_urn:
            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "VIDEO",
                        "media": [
                            {
                                "status": "READY",
                                "media": video_urn,
                            }
                        ],
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }
        # Build media content if images provided
        elif image_urns and len(image_urns) > 0:
            # Build media array for the share
            media_items = []
            for urn in image_urns:
                media_items.append(
                    {
                        "status": "READY",
                        "media": urn,
                    }
                )

            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "IMAGE",
                        "media": media_items,
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }
        else:
            payload = {
                "author": author_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": text},
                        "shareMediaCategory": "NONE",
                    }
                },
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }

        try:
            response = requests.post(
                share_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                timeout=30,
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn share creation failed: {e}")
            raise Exception(f"Failed to create share: {str(e)}")

    def register_image_upload(self, access_token: str, user_urn: str) -> dict:
        """
        Register an image upload with LinkedIn to get an upload URL.

        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN

        Returns:
            Dictionary with upload URL and asset URN
        """
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"

        # Normalize URN format
        if user_urn.startswith("urn:li:person:"):
            owner_urn = user_urn
        else:
            owner_urn = f"urn:li:person:{user_urn}"

        payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                "owner": owner_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
            }
        }

        try:
            response = requests.post(
                register_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Extract upload URL and asset URN
            value = data.get("value", {})
            upload_mechanism = value.get("uploadMechanism", {})
            media_artifact = upload_mechanism.get(
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}
            )

            return {
                "upload_url": media_artifact.get("uploadUrl"),
                "asset_urn": value.get("asset"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn image registration failed: {e}")
            raise Exception(f"Failed to register image upload: {str(e)}")

    def upload_image(
        self, upload_url: str, image_data: bytes, content_type: str = "image/jpeg"
    ) -> bool:
        """
        Upload image binary data to LinkedIn's upload URL.

        Args:
            upload_url: The upload URL from register_image_upload
            image_data: Binary image data
            content_type: MIME type of the image

        Returns:
            True if upload was successful
        """
        try:
            response = requests.put(
                upload_url,
                data=image_data,
                headers={
                    "Content-Type": content_type,
                },
                timeout=60,  # Longer timeout for uploads
            )
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn image upload failed: {e}")
            raise Exception(f"Failed to upload image: {str(e)}")

    def upload_image_from_url(
        self, access_token: str, user_urn: str, image_url: str
    ) -> str:
        """
        Upload an image from a URL to LinkedIn.

        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN
            image_url: URL of the image to upload

        Returns:
            The asset URN for the uploaded image
        """
        # Download the image
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            image_data = response.content
            content_type = response.headers.get("Content-Type", "image/jpeg")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download image from URL: {e}")
            raise Exception(f"Failed to download image: {str(e)}")

        # Register the upload
        upload_info = self.register_image_upload(access_token, user_urn)
        upload_url = upload_info.get("upload_url")
        asset_urn = upload_info.get("asset_urn")

        if not upload_url or not asset_urn:
            raise Exception("Failed to get upload URL from LinkedIn")

        # Upload the image
        self.upload_image(upload_url, image_data, content_type)

        return asset_urn

    # ==================== VIDEO UPLOAD METHODS ====================

    def register_video_upload(
        self, access_token: str, user_urn: str, file_size: int
    ) -> dict:
        """
        Register a video upload with LinkedIn to get upload instructions.

        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN
            file_size: Size of the video file in bytes

        Returns:
            Dictionary with upload URLs and asset URN
        """
        register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"

        # Normalize URN format
        if user_urn.startswith("urn:li:person:"):
            owner_urn = user_urn
        else:
            owner_urn = f"urn:li:person:{user_urn}"

        payload = {
            "registerUploadRequest": {
                "recipes": ["urn:li:digitalmediaRecipe:feedshare-video"],
                "owner": owner_urn,
                "serviceRelationships": [
                    {
                        "relationshipType": "OWNER",
                        "identifier": "urn:li:userGeneratedContent",
                    }
                ],
                "supportedUploadMechanism": ["SINGLE_REQUEST_UPLOAD"],
            }
        }

        try:
            response = requests.post(
                register_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            # Extract upload URL and asset URN
            value = data.get("value", {})
            upload_mechanism = value.get("uploadMechanism", {})
            media_artifact = upload_mechanism.get(
                "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}
            )

            return {
                "upload_url": media_artifact.get("uploadUrl"),
                "asset_urn": value.get("asset"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn video registration failed: {e}")
            raise Exception(f"Failed to register video upload: {str(e)}")

    def upload_video(
        self, upload_url: str, video_data: bytes, content_type: str = "video/mp4"
    ) -> bool:
        """
        Upload video binary data to LinkedIn's upload URL.

        Args:
            upload_url: The upload URL from register_video_upload
            video_data: Binary video data
            content_type: MIME type of the video

        Returns:
            True if upload was successful
        """
        try:
            response = requests.put(
                upload_url,
                data=video_data,
                headers={
                    "Content-Type": content_type,
                },
                timeout=300,  # 5 minutes timeout for video uploads
            )
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn video upload failed: {e}")
            raise Exception(f"Failed to upload video: {str(e)}")

    def check_video_status(self, access_token: str, asset_urn: str) -> dict:
        """
        Check the processing status of an uploaded video.

        Args:
            access_token: Valid LinkedIn access token
            asset_urn: The asset URN from video registration

        Returns:
            Dictionary with status information
        """
        # URL-encode the asset URN
        encoded_urn = asset_urn.replace(":", "%3A")
        status_url = f"https://api.linkedin.com/v2/assets/{encoded_urn}"

        try:
            response = requests.get(
                status_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            recipes = data.get("recipes", [])
            status = "PROCESSING"

            for recipe in recipes:
                recipe_status = recipe.get("status")
                if recipe_status == "AVAILABLE":
                    status = "READY"
                    break
                elif recipe_status == "PROCESSING":
                    status = "PROCESSING"
                elif recipe_status == "FAILED":
                    status = "FAILED"
                    break

            return {
                "status": status,
                "asset_urn": asset_urn,
                "raw_response": data,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn video status check failed: {e}")
            raise Exception(f"Failed to check video status: {str(e)}")

    def upload_video_file(
        self,
        access_token: str,
        user_urn: str,
        video_data: bytes,
        content_type: str = "video/mp4",
    ) -> dict:
        """
        Upload a video file to LinkedIn.

        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN
            video_data: Binary video data
            content_type: MIME type of the video

        Returns:
            Dictionary with asset_urn and initial status
        """
        file_size = len(video_data)

        # Register the upload
        upload_info = self.register_video_upload(access_token, user_urn, file_size)
        upload_url = upload_info.get("upload_url")
        asset_urn = upload_info.get("asset_urn")

        if not upload_url or not asset_urn:
            raise Exception("Failed to get upload URL from LinkedIn")

        # Upload the video
        self.upload_video(upload_url, video_data, content_type)

        return {
            "asset_urn": asset_urn,
            "status": "PROCESSING",  # Videos start in processing state
        }

    # ==================== DOCUMENT UPLOAD METHODS ====================

    def register_document_upload(self, access_token: str, user_urn: str) -> dict:
        """
        Register a document upload with LinkedIn to get upload URL.

        LinkedIn Documents API: https://api.linkedin.com/rest/documents

        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN

        Returns:
            Dictionary with upload_url and document_urn
        """
        register_url = "https://api.linkedin.com/rest/documents?action=initializeUpload"

        # Normalize URN format
        if user_urn.startswith("urn:li:person:"):
            owner_urn = user_urn
        else:
            owner_urn = f"urn:li:person:{user_urn}"

        payload = {
            "initializeUploadRequest": {
                "owner": owner_urn,
            }
        }

        try:
            response = requests.post(
                register_url,
                json=payload,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0",
                    "LinkedIn-Version": "202501",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            value = data.get("value", {})
            return {
                "upload_url": value.get("uploadUrl"),
                "document_urn": value.get("document"),
                "upload_url_expires_at": value.get("uploadUrlExpiresAt"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn document registration failed: {e}")
            raise Exception(f"Failed to register document upload: {str(e)}")

    def upload_document(
        self, upload_url: str, document_data: bytes, content_type: str
    ) -> bool:
        """
        Upload document binary data to LinkedIn's upload URL.

        Args:
            upload_url: The upload URL from register_document_upload
            document_data: Binary document data
            content_type: MIME type of the document

        Returns:
            True if upload was successful
        """
        try:
            response = requests.put(
                upload_url,
                data=document_data,
                headers={
                    "Content-Type": content_type,
                },
                timeout=120,  # 2 minutes timeout for document uploads
            )
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn document upload failed: {e}")
            raise Exception(f"Failed to upload document: {str(e)}")

    def check_document_status(self, access_token: str, document_urn: str) -> dict:
        """
        Check the processing status of an uploaded document.

        Args:
            access_token: Valid LinkedIn access token
            document_urn: The document URN from registration

        Returns:
            Dictionary with status information
        """
        # URL-encode the document URN
        encoded_urn = document_urn.replace(":", "%3A")
        status_url = f"https://api.linkedin.com/rest/documents/{encoded_urn}"

        try:
            response = requests.get(
                status_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                    "LinkedIn-Version": "202501",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            status = data.get("status", "PROCESSING")

            return {
                "status": status,
                "document_urn": document_urn,
                "download_url": data.get("downloadUrl"),
                "raw_response": data,
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn document status check failed: {e}")
            raise Exception(f"Failed to check document status: {str(e)}")

    def upload_document_file(
        self,
        access_token: str,
        user_urn: str,
        document_data: bytes,
        content_type: str,
        filename: str = None,
    ) -> dict:
        """
        Upload a document file to LinkedIn.

        Supported formats: PDF, DOC, DOCX, PPT, PPTX
        Max size: 100MB, Max pages: 300

        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN
            document_data: Binary document data
            content_type: MIME type of the document
            filename: Optional filename for the document

        Returns:
            Dictionary with document_urn and initial status
        """
        # Register the upload
        upload_info = self.register_document_upload(access_token, user_urn)
        upload_url = upload_info.get("upload_url")
        document_urn = upload_info.get("document_urn")

        if not upload_url or not document_urn:
            raise Exception("Failed to get upload URL from LinkedIn")

        # Upload the document
        self.upload_document(upload_url, document_data, content_type)

        return {
            "document_urn": document_urn,
            "status": "PROCESSING",  # Documents start in processing state
            "filename": filename,
        }


# Singleton instance
linkedin_service = LinkedInService()
