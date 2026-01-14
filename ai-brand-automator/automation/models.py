"""
Automation models for social media integration and content scheduling.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class SocialProfile(models.Model):
    """
    Stores connected social media accounts (LinkedIn, Twitter, Instagram, etc.)
    """
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
    ]
    
    STATUS_CHOICES = [
        ('connected', 'Connected'),
        ('disconnected', 'Disconnected'),
        ('expired', 'Token Expired'),
        ('error', 'Error'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='social_profiles'
    )
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    
    # OAuth tokens (encrypted in production)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField(blank=True, null=True)
    token_expires_at = models.DateTimeField(blank=True, null=True)
    
    # Profile information from the platform
    profile_id = models.CharField(max_length=255, blank=True, null=True)
    profile_name = models.CharField(max_length=255, blank=True, null=True)
    profile_url = models.URLField(blank=True, null=True)
    profile_image_url = models.URLField(blank=True, null=True)
    
    # Connection status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='disconnected'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_synced_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'platform']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_platform_display()}"
    
    @property
    def is_token_valid(self):
        """Check if the access token is still valid."""
        if not self.token_expires_at:
            return False
        return timezone.now() < self.token_expires_at
    
    def disconnect(self):
        """Disconnect the social profile."""
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        self.status = 'disconnected'
        self.save()


class AutomationTask(models.Model):
    """
    Tracks automated tasks like posting, profile creation, etc.
    """
    TASK_TYPE_CHOICES = [
        ('social_post', 'Social Media Post'),
        ('profile_sync', 'Profile Sync'),
        ('content_schedule', 'Content Scheduling'),
        ('analytics_fetch', 'Analytics Fetch'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='automation_tasks'
    )
    social_profile = models.ForeignKey(
        SocialProfile,
        on_delete=models.CASCADE,
        related_name='tasks',
        blank=True,
        null=True
    )
    
    task_type = models.CharField(max_length=30, choices=TASK_TYPE_CHOICES)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
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
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_task_type_display()} - {self.status}"


class ContentCalendar(models.Model):
    """
    Scheduled content for social media posting.
    """
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('scheduled', 'Scheduled'),
        ('published', 'Published'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scheduled_content'
    )
    
    title = models.CharField(max_length=255)
    content = models.TextField()
    media_urls = models.JSONField(default=list, blank=True)  # Array of media URLs
    
    # Target platforms and profiles
    platforms = models.JSONField(default=list)  # ['linkedin', 'twitter']
    social_profiles = models.ManyToManyField(
        SocialProfile,
        related_name='scheduled_posts',
        blank=True
    )
    
    # Scheduling
    scheduled_date = models.DateTimeField()
    published_at = models.DateTimeField(blank=True, null=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft'
    )
    
    # Results from posting
    post_results = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_date']
        verbose_name_plural = 'Content Calendar'
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date}"


class OAuthState(models.Model):
    """
    Temporary storage for OAuth state tokens.
    Used to validate OAuth callbacks since JWT-based apps don't use sessions.
    """
    state = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='oauth_states'
    )
    platform = models.CharField(max_length=20)  # 'linkedin', 'twitter', etc.
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'OAuth State'
        verbose_name_plural = 'OAuth States'
    
    def is_expired(self):
        """State tokens expire after 10 minutes."""
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(minutes=10)
    
    def __str__(self):
        return f"{self.platform} OAuth for {self.user.email}"
