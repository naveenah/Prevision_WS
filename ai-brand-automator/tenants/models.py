from django.db import models
# from django_tenants.models import TenantMixin, DomainMixin  # Disabled for SQLite development
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class Tenant(models.Model):
    """
    Tenant model for multi-tenancy.
    Simplified version for SQLite development.
    """
    name = models.CharField(max_length=100, help_text="Company/Organization name")
    description = models.TextField(blank=True, help_text="Brief description of the company")
    domain = models.CharField(max_length=255, unique=True, help_text="Primary domain for the tenant")

    # Subscription information
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ('trial', 'Trial'),
            ('active', 'Active'),
            ('past_due', 'Past Due'),
            ('canceled', 'Canceled'),
            ('unpaid', 'Unpaid'),
        ],
        default='trial'
    )
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Tenant-specific settings
    max_users = models.PositiveIntegerField(default=10, help_text="Maximum number of users allowed")
    storage_limit_gb = models.PositiveIntegerField(default=5, help_text="Storage limit in GB")

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self):
        return self.name

    @property
    def is_subscription_active(self):
        return self.subscription_status in ['active', 'trial']


class Domain(models.Model):
    """
    Domain model for tenant domains.
    Simplified version for SQLite development.
    """
    domain = models.CharField(max_length=255, unique=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='domains')
    is_primary = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Domain"
        verbose_name_plural = "Domains"

    def __str__(self):
        return self.domain


# Custom User model disabled for initial SQLite development
# Will be enabled when multi-tenancy is properly configured
# class User(AbstractUser):
#     """
#     Custom user model for tenants.
#     """
#     tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users')
#
#     # Role-based access
#     ROLE_CHOICES = [
#         ('admin', 'Admin'),
#         ('editor', 'Editor'),
#         ('viewer', 'Viewer'),
#     ]
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='admin')
#
#     # Profile information
#     avatar = models.URLField(blank=True, null=True, help_text="Profile picture URL")
#     phone = models.CharField(max_length=20, blank=True, help_text="Phone number")
#
#     class Meta:
#         verbose_name = "User"
#         verbose_name_plural = "Users"
#
#     def __str__(self):
#         return f"{self.username} ({self.tenant.name})"
#
#     @property
#     def full_name(self):
#         return f"{self.first_name} {self.last_name}".strip() or self.username
