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

    def create_share(self, access_token: str, user_urn: str, text: str) -> dict:
        """
        Create a share (post) on LinkedIn.

        Args:
            access_token: Valid LinkedIn access token
            user_urn: The user's URN (may be just ID or full URN format)
            text: The post content

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


# Singleton instance
linkedin_service = LinkedInService()
