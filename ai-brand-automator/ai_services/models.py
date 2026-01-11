from django.db import models
from django.utils import timezone
from tenants.models import Tenant


class ChatSession(models.Model):
    """
    AI chat sessions for brand strategy conversations
    """

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="chat_sessions"
    )
    session_id = models.CharField(
        max_length=255,
        unique=True,
        help_text="Unique session identifier",
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        help_text="Session title",
    )

    # Chat data
    messages = models.JSONField(default=list, help_text="List of chat messages")
    context = models.JSONField(
        default=dict, help_text="Session context (company info, etc.)"
    )

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Chat Session"
        verbose_name_plural = "Chat Sessions"
        ordering = ["-last_activity"]

    def __str__(self):
        return f"{self.title or 'Chat Session'} ({self.tenant.name})"

    def add_message(self, role, content, metadata=None):
        """Add a message to the session"""
        message = {
            "role": role,
            "content": content,
            "timestamp": timezone.now().isoformat(),
            "metadata": metadata or {},
        }
        self.messages.append(message)
        self.last_activity = timezone.now()
        self.save()


class AIGeneration(models.Model):
    """
    Track AI content generations
    """

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="ai_generations"
    )

    content_type = models.CharField(
        max_length=50,
        choices=[
            ("brand_strategy", "Brand Strategy"),
            ("brand_identity", "Brand Identity"),
            ("content", "Content Generation"),
            ("analysis", "Market Analysis"),
        ],
        help_text="Type of AI-generated content",
    )

    prompt = models.TextField(help_text="AI prompt used")
    response = models.TextField(help_text="AI response generated")
    tokens_used = models.PositiveIntegerField(
        default=0, help_text="API tokens consumed"
    )

    # Metadata
    model_used = models.CharField(max_length=100, default="gemini-2.0-flash-exp")
    created_at = models.DateTimeField(default=timezone.now)
    processing_time = models.FloatField(
        default=0.0, help_text="Processing time in seconds"
    )

    class Meta:
        verbose_name = "AI Generation"
        verbose_name_plural = "AI Generations"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.content_type} - {self.tenant.name} ({self.created_at.date()})"
