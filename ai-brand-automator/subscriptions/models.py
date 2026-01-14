"""
Subscription models for Stripe payment integration.
"""
from django.db import models
from django.utils import timezone


class SubscriptionPlan(models.Model):
    """Available subscription plans"""

    PLAN_CHOICES = [
        ("basic", "Basic"),
        ("pro", "Pro"),
        ("enterprise", "Enterprise"),
    ]

    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    stripe_price_id = models.CharField(max_length=255, unique=True)

    # Plan features
    max_brands = models.IntegerField(default=1)
    max_team_members = models.IntegerField(default=1)
    ai_generations_per_month = models.IntegerField(default=10)
    automation_enabled = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["price"]

    def __str__(self):
        return f"{self.display_name} - ${self.price}/mo"


class Subscription(models.Model):
    """Active subscriptions for tenants"""

    STATUS_CHOICES = [
        ("active", "Active"),
        ("past_due", "Past Due"),
        ("canceled", "Canceled"),
        ("incomplete", "Incomplete"),
        ("trialing", "Trialing"),
        ("unpaid", "Unpaid"),
    ]

    tenant = models.OneToOneField(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="subscription",
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )
    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    stripe_customer_id = models.CharField(max_length=255)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    current_period_start = models.DateTimeField()
    current_period_end = models.DateTimeField()
    cancel_at_period_end = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tenant.name} - {self.plan.display_name} ({self.status})"

    @property
    def is_active(self):
        return self.status in ["active", "trialing"]

    @property
    def days_until_renewal(self):
        if self.current_period_end:
            delta = self.current_period_end - timezone.now()
            return max(0, delta.days)
        return 0


class PaymentHistory(models.Model):
    """Payment history for auditing"""

    STATUS_CHOICES = [
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("pending", "Pending"),
        ("refunded", "Refunded"),
    ]

    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="payments",
    )
    subscription = models.ForeignKey(
        Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )

    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)
    stripe_invoice_id = models.CharField(max_length=255, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    description = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Payment histories"

    def __str__(self):
        return f"{self.tenant.name} - ${self.amount} ({self.status})"
