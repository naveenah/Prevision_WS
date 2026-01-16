"""
LinkedIn OAuth and API service.
"""
import requests
import logging
from typing import Optional, List
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
        image_urns: Optional[List[str]] = None,
        video_urn: Optional[str] = None,
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

    def get_organization_followers(self, access_token: str, org_id: str = None) -> dict:
        """
        Get follower statistics for the user's network.
        
        Note: For personal profiles, LinkedIn API v2 doesn't expose follower counts
        directly. This method provides what's available through the API.
        
        Args:
            access_token: Valid LinkedIn access token
            org_id: Optional organization ID for company page metrics
            
        Returns:
            Dictionary with follower/connection information
        """
        # For personal profiles, we can get 1st-degree connections count
        # through the connections API (if authorized)
        try:
            # Get network size (connections)
            network_url = "https://api.linkedin.com/v2/networkSizes/urn:li:person:me?edgeType=CompanyFollowedByMember"
            
            response = requests.get(
                network_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                timeout=30,
            )
            
            if response.ok:
                data = response.json()
                return {
                    "first_degree_size": data.get("firstDegreeSize", 0),
                }
            else:
                # API might not be available for this user/scope
                return {"first_degree_size": 0, "note": "Network size unavailable"}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn network size fetch failed: {e}")
            return {"first_degree_size": 0, "error": str(e)}

    def get_share_statistics(self, access_token: str, share_urn: str) -> dict:
        """
        Get engagement statistics for a specific share/post.
        
        Args:
            access_token: Valid LinkedIn access token
            share_urn: The share URN (e.g., urn:li:share:12345 or urn:li:ugcPost:12345)
            
        Returns:
            Dictionary with engagement metrics (likes, comments, shares, impressions)
        """
        # LinkedIn API v2 uses organizationalEntityShareStatistics for org pages
        # For personal shares, we use socialActions API
        
        try:
            # Get social actions (likes, comments) for the post
            # URL encode the URN
            encoded_urn = share_urn.replace(":", "%3A")
            
            # Get likes count
            likes_url = f"https://api.linkedin.com/v2/socialActions/{encoded_urn}/likes?count=0"
            comments_url = f"https://api.linkedin.com/v2/socialActions/{encoded_urn}/comments?count=0"
            
            likes_count = 0
            comments_count = 0
            
            # Fetch likes
            likes_response = requests.get(
                likes_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                timeout=30,
            )
            if likes_response.ok:
                likes_data = likes_response.json()
                # The paging total gives us the count
                likes_count = likes_data.get("paging", {}).get("total", 0)
            
            # Fetch comments
            comments_response = requests.get(
                comments_url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                timeout=30,
            )
            if comments_response.ok:
                comments_data = comments_response.json()
                comments_count = comments_data.get("paging", {}).get("total", 0)
            
            return {
                "share_urn": share_urn,
                "likes": likes_count,
                "comments": comments_count,
                "shares": 0,  # Reshares not easily accessible via v2 API
                "impressions": 0,  # Impressions require organization analytics
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn share statistics fetch failed: {e}")
            return {
                "share_urn": share_urn,
                "likes": 0,
                "comments": 0,
                "shares": 0,
                "impressions": 0,
                "error": str(e),
            }

    def get_user_posts(self, access_token: str, user_urn: str, count: int = 20) -> list:
        """
        Get recent posts by the user.
        
        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN
            count: Number of posts to fetch (max 100)
            
        Returns:
            List of post dictionaries with basic info
        """
        # Normalize URN format
        if user_urn.startswith("urn:li:person:"):
            author_urn = user_urn
        else:
            author_urn = f"urn:li:person:{user_urn}"
        
        encoded_author = author_urn.replace(":", "%3A")
        
        try:
            # Fetch UGC posts by the author
            url = f"https://api.linkedin.com/v2/ugcPosts?q=authors&authors=List({encoded_author})&count={min(count, 100)}"
            
            response = requests.get(
                url,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0",
                },
                timeout=30,
            )
            
            if response.ok:
                data = response.json()
                posts = []
                
                for element in data.get("elements", []):
                    post_urn = element.get("id", "")
                    specific_content = element.get("specificContent", {})
                    share_content = specific_content.get("com.linkedin.ugc.ShareContent", {})
                    commentary = share_content.get("shareCommentary", {})
                    
                    posts.append({
                        "post_urn": post_urn,
                        "text": commentary.get("text", ""),
                        "created_time": element.get("created", {}).get("time"),
                        "lifecycle_state": element.get("lifecycleState"),
                    })
                
                return posts
            else:
                logger.error(f"Failed to fetch user posts: {response.status_code}")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"LinkedIn user posts fetch failed: {e}")
            return []

    def get_analytics_summary(self, access_token: str, user_urn: str) -> dict:
        """
        Get a summary of analytics for the user including profile and post metrics.
        
        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN
            
        Returns:
            Dictionary with user metrics and recent post performance
        """
        # Get user profile info
        profile = self.get_user_profile(access_token)
        
        # Get recent posts
        posts = self.get_user_posts(access_token, user_urn, count=20)
        
        # Get metrics for each post
        posts_with_metrics = []
        total_likes = 0
        total_comments = 0
        
        for post in posts[:10]:  # Limit to 10 to avoid rate limits
            post_urn = post.get("post_urn")
            if post_urn:
                metrics = self.get_share_statistics(access_token, post_urn)
                post["metrics"] = metrics
                posts_with_metrics.append(post)
                total_likes += metrics.get("likes", 0)
                total_comments += metrics.get("comments", 0)
        
        # Get network info
        network = self.get_organization_followers(access_token)
        
        return {
            "profile": {
                "name": profile.get("name"),
                "email": profile.get("email"),
                "picture": profile.get("picture"),
            },
            "network": {
                "connections": network.get("first_degree_size", 0),
            },
            "posts": posts_with_metrics,
            "totals": {
                "total_posts": len(posts),
                "total_likes": total_likes,
                "total_comments": total_comments,
                "engagement_rate": round(
                    ((total_likes + total_comments) / max(len(posts_with_metrics), 1)) * 100, 2
                ) if posts_with_metrics else 0,
            },
        }


# Singleton instance
linkedin_service = LinkedInService()


class TwitterService:
    """
    Service for Twitter/X OAuth 2.0 authentication and API interactions.

    Twitter API v2 with OAuth 2.0 + PKCE (Proof Key for Code Exchange)
    Documentation:
    https://developer.twitter.com/en/docs/authentication/oauth-2-0/authorization-code
    """

    AUTHORIZATION_URL = "https://twitter.com/i/oauth2/authorize"
    TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
    REVOKE_URL = "https://api.twitter.com/2/oauth2/revoke"
    USER_INFO_URL = "https://api.twitter.com/2/users/me"
    TWEET_URL = "https://api.twitter.com/2/tweets"

    # Scopes for Twitter API v2
    # tweet.read - View Tweets
    # tweet.write - Post Tweets
    # users.read - View user profile
    # offline.access - Get refresh token
    SCOPES = [
        "tweet.read",
        "tweet.write",
        "users.read",
        "offline.access",
    ]

    def __init__(self):
        self.client_id = getattr(settings, "TWITTER_CLIENT_ID", None)
        self.client_secret = getattr(settings, "TWITTER_CLIENT_SECRET", None)
        self.redirect_uri = getattr(
            settings,
            "TWITTER_REDIRECT_URI",
            "http://localhost:8000/api/v1/automation/twitter/callback/",
        )

    @property
    def is_configured(self) -> bool:
        """Check if Twitter credentials are configured."""
        return bool(self.client_id and self.client_secret)

    def generate_pkce_pair(self) -> tuple:
        """
        Generate PKCE code verifier and code challenge.

        Returns:
            Tuple of (code_verifier, code_challenge)
        """
        import hashlib
        import base64
        import secrets

        # Generate code verifier (43-128 characters, URL-safe)
        code_verifier = secrets.token_urlsafe(64)[:128]

        # Generate code challenge (SHA256 hash of verifier, base64url encoded)
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode()).digest()
        ).decode().rstrip("=")

        return code_verifier, code_challenge

    def get_authorization_url(self, state: str, code_challenge: str) -> str:
        """
        Generate the Twitter OAuth 2.0 authorization URL with PKCE.

        Args:
            state: A unique state token to prevent CSRF attacks
            code_challenge: PKCE code challenge

        Returns:
            The full authorization URL to redirect the user to
        """
        if not self.is_configured:
            raise ValueError("Twitter credentials not configured")

        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.SCOPES),
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
        }

        return f"{self.AUTHORIZATION_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code: str, code_verifier: str) -> dict:
        """
        Exchange the authorization code for access and refresh tokens.

        Args:
            code: The authorization code from Twitter callback
            code_verifier: The PKCE code verifier

        Returns:
            Dictionary with access_token, expires_in, refresh_token, etc.
        """
        if not self.is_configured:
            raise ValueError("Twitter credentials not configured")

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "code_verifier": code_verifier,
        }

        # Twitter requires Basic Auth with client_id:client_secret
        import base64
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        try:
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {credentials}",
                },
                timeout=30,
            )
            response.raise_for_status()
            token_data = response.json()

            # Calculate token expiration time
            expires_in = token_data.get("expires_in", 7200)  # Default 2 hours
            token_data["expires_at"] = timezone.now() + timedelta(seconds=expires_in)

            return token_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter token exchange failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
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
            raise ValueError("Twitter credentials not configured")

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        import base64
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        try:
            response = requests.post(
                self.TOKEN_URL,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {credentials}",
                },
                timeout=30,
            )
            response.raise_for_status()
            token_data = response.json()

            # Calculate token expiration time
            expires_in = token_data.get("expires_in", 7200)
            token_data["expires_at"] = timezone.now() + timedelta(seconds=expires_in)

            return token_data

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter token refresh failed: {e}")
            raise Exception(f"Failed to refresh token: {str(e)}")

    def revoke_token(self, token: str, token_type: str = "access_token") -> bool:
        """
        Revoke an access or refresh token.

        Args:
            token: The token to revoke
            token_type: Either 'access_token' or 'refresh_token'

        Returns:
            True if revocation was successful
        """
        if not self.is_configured:
            raise ValueError("Twitter credentials not configured")

        data = {
            "token": token,
            "token_type_hint": token_type,
        }

        import base64
        credentials = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()

        try:
            response = requests.post(
                self.REVOKE_URL,
                data=data,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Authorization": f"Basic {credentials}",
                },
                timeout=30,
            )
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter token revocation failed: {e}")
            return False

    def get_user_info(self, access_token: str) -> dict:
        """
        Get the authenticated user's profile information.

        Args:
            access_token: Valid Twitter access token

        Returns:
            Dictionary with user profile data (id, name, username, etc.)
        """
        try:
            response = requests.get(
                self.USER_INFO_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                params={
                    "user.fields": "id,name,username,profile_image_url,description",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("data", {})

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter user info fetch failed: {e}")
            raise Exception(f"Failed to fetch user info: {str(e)}")

    def create_tweet(
        self,
        access_token: str,
        text: str,
        reply_to_id: Optional[str] = None,
        quote_tweet_id: Optional[str] = None,
        media_ids: Optional[List[str]] = None,
    ) -> dict:
        """
        Create a tweet (post) on Twitter/X.

        Args:
            access_token: Valid Twitter access token
            text: The tweet content (max 280 chars for regular, 25000 for Premium)
            reply_to_id: Optional tweet ID to reply to
            quote_tweet_id: Optional tweet ID to quote
            media_ids: Optional list of media IDs for attachments

        Returns:
            Dictionary with the created tweet information
        """
        payload = {"text": text}

        # Add reply settings if replying to a tweet
        if reply_to_id:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to_id}

        # Add quote tweet settings
        if quote_tweet_id:
            payload["quote_tweet_id"] = quote_tweet_id

        # Add media if provided
        if media_ids:
            payload["media"] = {"media_ids": media_ids}

        try:
            response = requests.post(
                self.TWEET_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            logger.info(f"Tweet created successfully: {data.get('data', {})}")
            return data.get("data", {})

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter tweet creation failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Failed to create tweet: {str(e)}")

    def delete_tweet(self, access_token: str, tweet_id: str) -> bool:
        """
        Delete a tweet.

        Args:
            access_token: Valid Twitter access token
            tweet_id: The ID of the tweet to delete

        Returns:
            True if deletion was successful
        """
        try:
            response = requests.delete(
                f"{self.TWEET_URL}/{tweet_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                timeout=30,
            )
            response.raise_for_status()
            return True

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter tweet deletion failed: {e}")
            return False

    def get_tweet_metrics(self, access_token: str, tweet_id: str) -> dict:
        """
        Get public metrics for a specific tweet.

        Args:
            access_token: Valid Twitter access token
            tweet_id: The ID of the tweet to get metrics for

        Returns:
            Dictionary with tweet metrics (impressions, likes, retweets, replies, quotes)
        """
        try:
            response = requests.get(
                f"{self.TWEET_URL}/{tweet_id}",
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                params={
                    "tweet.fields": "public_metrics,created_at,text",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            tweet_data = data.get("data", {})
            metrics = tweet_data.get("public_metrics", {})

            return {
                "tweet_id": tweet_id,
                "text": tweet_data.get("text", ""),
                "created_at": tweet_data.get("created_at"),
                "metrics": {
                    "impressions": metrics.get("impression_count", 0),
                    "likes": metrics.get("like_count", 0),
                    "retweets": metrics.get("retweet_count", 0),
                    "replies": metrics.get("reply_count", 0),
                    "quotes": metrics.get("quote_count", 0),
                    "bookmarks": metrics.get("bookmark_count", 0),
                },
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get tweet metrics: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Failed to get tweet metrics: {str(e)}")

    def get_multiple_tweet_metrics(self, access_token: str, tweet_ids: list) -> list:
        """
        Get public metrics for multiple tweets at once.

        Args:
            access_token: Valid Twitter access token
            tweet_ids: List of tweet IDs to get metrics for (max 100)

        Returns:
            List of tweet metrics dictionaries
        """
        if not tweet_ids:
            return []

        # Twitter API allows max 100 tweets per request
        tweet_ids = tweet_ids[:100]

        try:
            response = requests.get(
                self.TWEET_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                params={
                    "ids": ",".join(tweet_ids),
                    "tweet.fields": "public_metrics,created_at,text",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for tweet_data in data.get("data", []):
                metrics = tweet_data.get("public_metrics", {})
                results.append({
                    "tweet_id": tweet_data.get("id"),
                    "text": tweet_data.get("text", ""),
                    "created_at": tweet_data.get("created_at"),
                    "metrics": {
                        "impressions": metrics.get("impression_count", 0),
                        "likes": metrics.get("like_count", 0),
                        "retweets": metrics.get("retweet_count", 0),
                        "replies": metrics.get("reply_count", 0),
                        "quotes": metrics.get("quote_count", 0),
                        "bookmarks": metrics.get("bookmark_count", 0),
                    },
                })

            return results

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get multiple tweet metrics: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Failed to get tweet metrics: {str(e)}")

    def get_user_metrics(self, access_token: str) -> dict:
        """
        Get the authenticated user's profile metrics.

        Args:
            access_token: Valid Twitter access token

        Returns:
            Dictionary with user metrics (followers, following, tweet count)
        """
        try:
            response = requests.get(
                self.USER_INFO_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                params={
                    "user.fields": "public_metrics,created_at,description,profile_image_url",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            user_data = data.get("data", {})
            metrics = user_data.get("public_metrics", {})

            return {
                "user_id": user_data.get("id"),
                "username": user_data.get("username"),
                "name": user_data.get("name"),
                "description": user_data.get("description"),
                "profile_image_url": user_data.get("profile_image_url"),
                "created_at": user_data.get("created_at"),
                "metrics": {
                    "followers": metrics.get("followers_count", 0),
                    "following": metrics.get("following_count", 0),
                    "tweets": metrics.get("tweet_count", 0),
                    "listed": metrics.get("listed_count", 0),
                },
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get user metrics: {e}")
            if hasattr(e, "response") and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Failed to get user metrics: {str(e)}")

    def validate_tweet_length(self, text: str, is_premium: bool = False) -> dict:
        """
        Validate tweet length against Twitter's limits.

        Args:
            text: The tweet text to validate
            is_premium: Whether the user has Twitter/X Premium

        Returns:
            Dictionary with is_valid, length, max_length, remaining
        """
        max_length = 25000 if is_premium else 280
        length = len(text)

        return {
            "is_valid": length <= max_length,
            "length": length,
            "max_length": max_length,
            "remaining": max_length - length,
        }

    def upload_media(
        self,
        access_token: str,
        media_data: bytes,
        media_type: str,
        media_category: str = "tweet_image",
    ) -> dict:
        """
        Upload media to Twitter for use in tweets.

        Twitter uses v1.1 media upload endpoint (still required for v2 tweets).
        Documentation: https://developer.twitter.com/en/docs/twitter-api/v1/media/upload-media/overview

        Args:
            access_token: Valid Twitter access token
            media_data: The raw bytes of the media file
            media_type: The MIME type (e.g., "image/jpeg", "image/png", "video/mp4")
            media_category: One of "tweet_image", "tweet_gif", "tweet_video"

        Returns:
            Dictionary with media_id and media_id_string
        """
        import base64

        MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"

        # For images under 5MB, use simple upload
        if media_category == "tweet_image" and len(media_data) <= 5 * 1024 * 1024:
            # Simple upload (base64 encoded)
            media_b64 = base64.b64encode(media_data).decode()

            try:
                response = requests.post(
                    MEDIA_UPLOAD_URL,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "media_data": media_b64,
                        "media_category": media_category,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                data = response.json()

                logger.info(f"Twitter media uploaded: {data.get('media_id_string')}")
                return {
                    "media_id": data.get("media_id"),
                    "media_id_string": data.get("media_id_string"),
                    "type": data.get("type"),
                    "expires_after_secs": data.get("expires_after_secs"),
                }

            except requests.exceptions.RequestException as e:
                logger.error(f"Twitter media upload failed: {e}")
                if hasattr(e, "response") and e.response is not None:
                    logger.error(f"Response: {e.response.text}")
                    # Check for 403 Forbidden - usually means missing permissions
                    if e.response.status_code == 403:
                        raise Exception(
                            "Twitter media upload forbidden (403). Your Twitter Developer app "
                            "needs 'Basic' tier ($100/mo) or ensure 'Read and Write' permissions "
                            "are enabled in the Twitter Developer Portal."
                        )
                raise Exception(f"Failed to upload media: {str(e)}")

        # For larger files or videos, use chunked upload
        return self._chunked_media_upload(
            access_token, media_data, media_type, media_category
        )

    def _chunked_media_upload(
        self,
        access_token: str,
        media_data: bytes,
        media_type: str,
        media_category: str,
    ) -> dict:
        """
        Chunked media upload for large files and videos.

        Uses INIT, APPEND, FINALIZE flow.
        """
        import base64

        MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"
        total_bytes = len(media_data)

        # INIT phase
        try:
            init_response = requests.post(
                MEDIA_UPLOAD_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                data={
                    "command": "INIT",
                    "total_bytes": total_bytes,
                    "media_type": media_type,
                    "media_category": media_category,
                },
                timeout=30,
            )
            init_response.raise_for_status()
            init_data = init_response.json()
            media_id = init_data["media_id_string"]

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter media INIT failed: {e}")
            if hasattr(e, "response") and e.response is not None:
                if e.response.status_code == 403:
                    raise Exception(
                        "Twitter media upload forbidden (403). Your Twitter Developer app "
                        "needs 'Basic' tier ($100/mo) or ensure 'Read and Write' permissions "
                        "are enabled in the Twitter Developer Portal."
                    )
            raise Exception(f"Failed to initialize media upload: {str(e)}")

        # APPEND phase - upload in chunks
        chunk_size = 4 * 1024 * 1024  # 4MB chunks
        segment_index = 0

        for i in range(0, total_bytes, chunk_size):
            chunk = media_data[i:i + chunk_size]
            chunk_b64 = base64.b64encode(chunk).decode()

            try:
                append_response = requests.post(
                    MEDIA_UPLOAD_URL,
                    headers={
                        "Authorization": f"Bearer {access_token}",
                    },
                    data={
                        "command": "APPEND",
                        "media_id": media_id,
                        "media_data": chunk_b64,
                        "segment_index": segment_index,
                    },
                    timeout=120,
                )
                append_response.raise_for_status()
                segment_index += 1

            except requests.exceptions.RequestException as e:
                logger.error(f"Twitter media APPEND failed at segment {segment_index}: {e}")
                raise Exception(f"Failed to upload media chunk: {str(e)}")

        # FINALIZE phase
        try:
            finalize_response = requests.post(
                MEDIA_UPLOAD_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                data={
                    "command": "FINALIZE",
                    "media_id": media_id,
                },
                timeout=30,
            )
            finalize_response.raise_for_status()
            finalize_data = finalize_response.json()

            # Check for async processing (videos/GIFs)
            processing_info = finalize_data.get("processing_info")
            if processing_info:
                logger.info(
                    f"Twitter media {media_id} is processing: {processing_info}"
                )
                return {
                    "media_id": finalize_data.get("media_id"),
                    "media_id_string": media_id,
                    "processing_info": processing_info,
                    "status": "PROCESSING",
                }

            logger.info(f"Twitter media uploaded and ready: {media_id}")
            return {
                "media_id": finalize_data.get("media_id"),
                "media_id_string": media_id,
                "status": "READY",
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter media FINALIZE failed: {e}")
            raise Exception(f"Failed to finalize media upload: {str(e)}")

    def get_media_status(self, access_token: str, media_id: str) -> dict:
        """
        Check the processing status of uploaded media.

        Args:
            access_token: Valid Twitter access token
            media_id: The media_id_string from upload

        Returns:
            Dictionary with processing status
        """
        MEDIA_UPLOAD_URL = "https://upload.twitter.com/1.1/media/upload.json"

        try:
            response = requests.get(
                MEDIA_UPLOAD_URL,
                headers={
                    "Authorization": f"Bearer {access_token}",
                },
                params={
                    "command": "STATUS",
                    "media_id": media_id,
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            processing_info = data.get("processing_info", {})
            state = processing_info.get("state", "succeeded")

            return {
                "media_id": media_id,
                "state": state,
                "check_after_secs": processing_info.get("check_after_secs"),
                "progress_percent": processing_info.get("progress_percent"),
                "error": processing_info.get("error"),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Twitter media status check failed: {e}")
            raise Exception(f"Failed to get media status: {str(e)}")


# Singleton instance
twitter_service = TwitterService()
