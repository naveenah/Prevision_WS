"""
Automation models for social media integration and content scheduling.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

from .encryption import encrypt_token, decrypt_token

User = get_user_model()


class SocialProfile(models.Model):
    """
    Stores connected social media accounts (LinkedIn, Twitter, Instagram, etc.)

    OAuth tokens are encrypted at rest for security.
    """

    PLATFORM_CHOICES = [
        ("linkedin", "LinkedIn"),
        ("twitter", "Twitter/X"),
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
    ]

    STATUS_CHOICES = [
        ("connected", "Connected"),
        ("disconnected", "Disconnected"),
        ("expired", "Token Expired"),
        ("error", "Error"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="social_profiles"
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)

    # OAuth tokens (encrypted at rest)
    _access_token = models.TextField(blank=True, null=True, db_column="access_token")
    _refresh_token = models.TextField(blank=True, null=True, db_column="refresh_token")
    token_expires_at = models.DateTimeField(blank=True, null=True)

    # Profile information from the platform
    profile_id = models.CharField(max_length=255, blank=True, null=True)
    profile_name = models.CharField(max_length=255, blank=True, null=True)
    profile_url = models.URLField(blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)

    # Connection status
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="disconnected"
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ["user", "platform"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} - {self.get_platform_display()}"

    # Encrypted token properties
    @property
    def access_token(self):
        """Get the decrypted access token."""
        return decrypt_token(self._access_token) if self._access_token else None

    @access_token.setter
    def access_token(self, value):
        """Set and encrypt the access token."""
        self._access_token = encrypt_token(value) if value else None

    @property
    def refresh_token(self):
        """Get the decrypted refresh token."""
        return decrypt_token(self._refresh_token) if self._refresh_token else None

    @refresh_token.setter
    def refresh_token(self, value):
        """Set and encrypt the refresh token."""
        self._refresh_token = encrypt_token(value) if value else None

    @property
    def is_token_valid(self):
        """Check if the access token is still valid."""
        if not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at

    @property
    def is_token_expiring_soon(self):
        """Check if the token will expire within 5 minutes."""
        if not self.token_expires_at:
            return True
        from datetime import timedelta

        return timezone.now() + timedelta(minutes=5) >= self.token_expires_at

    def refresh_token_if_needed(self):
        """
        Refresh the access token if it's expired or expiring soon.
        Returns the current (or refreshed) access token.
        """
        if self.status != "connected":
            raise ValueError("Profile is not connected")

        if not self.is_token_expiring_soon:
            return self.access_token

        if not self.refresh_token:
            self.status = "expired"
            self.save()
            raise ValueError("No refresh token available")

        # Import here to avoid circular imports
        from .services import linkedin_service, twitter_service

        try:
            if self.platform == "linkedin":
                token_data = linkedin_service.refresh_access_token(self.refresh_token)
                self.access_token = token_data.get("access_token")
                self.token_expires_at = token_data.get("expires_at")
                if token_data.get("refresh_token"):
                    self.refresh_token = token_data.get("refresh_token")
                self.save()
                return self.access_token
            elif self.platform == "twitter":
                token_data = twitter_service.refresh_access_token(self.refresh_token)
                self.access_token = token_data.get("access_token")
                self.token_expires_at = token_data.get("expires_at")
                if token_data.get("refresh_token"):
                    self.refresh_token = token_data.get("refresh_token")
                self.save()
                return self.access_token
            else:
                raise ValueError(f"Token refresh not implemented for {self.platform}")
        except Exception as e:
            self.status = "error"
            self.save()
            raise ValueError(f"Failed to refresh token: {str(e)}")

    def get_valid_access_token(self):
        """
        Get a valid access token, refreshing if necessary.
        This is the main method to use before making API calls.
        """
        return self.refresh_token_if_needed()

    def disconnect(self):
        """Disconnect the social profile."""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.status = "disconnected"
        self.save()


class AutomationTask(models.Model):
    """
    Tracks automated tasks like posting, profile creation, etc.
    """

    TASK_TYPE_CHOICES = [
        ("social_post", "Social Media Post"),
        ("profile_sync", "Profile Sync"),
        ("content_schedule", "Content Scheduling"),
        ("analytics_fetch", "Analytics Fetch"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="automation_tasks"
    )
    social_profile = models.ForeignKey(
        SocialProfile,
        on_delete=models.CASCADE,
        related_name="tasks",
        blank=True,
        null=True,
    )

    task_type = models.CharField(max_length=30, choices=TASK_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Task data and results
    payload = models.JSONField(default=dict, blank=True)
    result = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True, null=True)

    # Scheduling
    scheduled_at = models.DateTimeField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.status}"


class ContentCalendar(models.Model):
    """
    Scheduled content for social media posting.
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("scheduled", "Scheduled"),
        ("published", "Published"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="scheduled_content"
    )

    title = models.CharField(max_length=255)
    content = models.TextField()
    media_urls = models.JSONField(default=list, blank=True)  # Array of media URLs

    # Target platforms and profiles
    platforms = models.JSONField(default=list)  # ['linkedin', 'twitter']
    social_profiles = models.ManyToManyField(
        SocialProfile, related_name="scheduled_posts", blank=True
    )

    # Scheduling
    scheduled_date = models.DateTimeField()
    published_at = models.DateTimeField(blank=True, null=True)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")

    # Results from posting
    post_results = models.JSONField(default=dict, blank=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["scheduled_date"]
        verbose_name_plural = "Content Calendar"

    def __str__(self):
        return f"{self.title} - {self.scheduled_date}"


class OAuthState(models.Model):
    """
    Temporary storage for OAuth state tokens.
    Used to validate OAuth callbacks since JWT-based apps don't use sessions.
    """

    state = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="oauth_states"
    )
    platform = models.CharField(max_length=20)  # 'linkedin', 'twitter', etc.
    code_verifier = models.CharField(
        max_length=256, blank=True, null=True
    )  # PKCE code verifier for Twitter
    used = models.BooleanField(default=False)  # Mark as used after callback
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "OAuth State"
        verbose_name_plural = "OAuth States"

    def is_expired(self):
        """State tokens expire after 10 minutes."""
        from datetime import timedelta

        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.platform} OAuth for {self.user.email}"


class TwitterWebhookEvent(models.Model):
    """
    Stores incoming webhook events from Twitter Account Activity API.

    Events include likes, retweets, mentions, follows, and DMs.
    """

    EVENT_TYPE_CHOICES = [
        ("tweet_create", "Tweet Created"),
        ("favorite", "Like/Favorite"),
        ("follow", "New Follower"),
        ("unfollow", "Unfollowed"),
        ("direct_message", "Direct Message"),
        ("tweet_delete", "Tweet Deleted"),
        ("mention", "Mentioned"),
        ("retweet", "Retweeted"),
        ("quote", "Quote Tweet"),
    ]

    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    for_user_id = models.CharField(
        max_length=50, db_index=True, help_text="Twitter user ID this event is for"
    )
    payload = models.JSONField(
        default=dict, help_text="Full event payload from Twitter"
    )
    read = models.BooleanField(
        default=False, help_text="Whether user has seen this event"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Twitter Webhook Event"
        verbose_name_plural = "Twitter Webhook Events"
        indexes = [
            models.Index(fields=["for_user_id", "-created_at"]),
            models.Index(fields=["for_user_id", "read"]),
        ]

    def __str__(self):
        return f"{self.event_type} for {self.for_user_id} at {self.created_at}"


class LinkedInWebhookEvent(models.Model):
    """
    Stores incoming webhook events from LinkedIn.

    LinkedIn webhooks can notify about:
    - Share reactions (likes)
    - Share comments
    - Profile mentions
    - Connection updates
    - Organization updates (for company pages)

    Docs: https://learn.microsoft.com/en-us/linkedin/
        marketing/integrations/community-management/webhooks
    """

    EVENT_TYPE_CHOICES = [
        ("share_reaction", "Share Reaction (Like)"),
        ("share_comment", "Comment on Share"),
        ("mention", "Mentioned"),
        ("connection_update", "Connection Update"),
        ("organization_update", "Organization Update"),
        ("share_update", "Share/Post Update"),
        ("message", "Message Received"),
    ]

    event_type = models.CharField(max_length=30, choices=EVENT_TYPE_CHOICES)
    for_user_id = models.CharField(
        max_length=100, db_index=True, help_text="LinkedIn member URN this event is for"
    )
    resource_urn = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="URN of the resource (share, comment, etc.)",
    )
    payload = models.JSONField(
        default=dict, help_text="Full event payload from LinkedIn"
    )
    read = models.BooleanField(
        default=False, help_text="Whether user has seen this event"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "LinkedIn Webhook Event"
        verbose_name_plural = "LinkedIn Webhook Events"
        indexes = [
            models.Index(fields=["for_user_id", "-created_at"]),
            models.Index(fields=["for_user_id", "read"]),
        ]

    def __str__(self):
        return f"{self.event_type} for {self.for_user_id} at {self.created_at}"
