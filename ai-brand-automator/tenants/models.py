from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
from django.utils import timezone


class Tenant(TenantMixin):
    """
    Tenant model for multi-tenancy.
    Each tenant represents an enterprise customer.
    """

    name = models.CharField(max_length=100, help_text="Company/Organization name")
    description = models.TextField(
        blank=True, help_text="Brief description of the company"
    )

    # Schema name will be auto-generated from name
    schema_name = models.CharField(
        max_length=63,
        unique=True,
        blank=True,
        help_text="Database schema name",
    )

    # Subscription information
    subscription_status = models.CharField(
        max_length=20,
        choices=[
            ("trial", "Trial"),
            ("active", "Active"),
            ("past_due", "Past Due"),
            ("canceled", "Canceled"),
            ("unpaid", "Unpaid"),
        ],
        default="trial",
    )
    stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    # Tenant-specific settings
    max_users = models.PositiveIntegerField(
        default=10, help_text="Maximum number of users allowed"
    )
    storage_limit_gb = models.PositiveIntegerField(
        default=5, help_text="Storage limit in GB"
    )

    def save(self, *args, **kwargs):
        # Auto-generate schema_name from name if not provided
        if not self.schema_name:
            # Create a valid schema name from the tenant name
            import re

            schema_name = re.sub(r"[^a-zA-Z0-9_]", "_", self.name.lower())
            schema_name = f"tenant_{schema_name}"
            # Ensure it's unique
            counter = 1
            original_schema = schema_name
            while Tenant.objects.filter(schema_name=schema_name).exists():
                schema_name = f"{original_schema}_{counter}"
                counter += 1
            self.schema_name = schema_name
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Tenant"
        verbose_name_plural = "Tenants"

    def __str__(self):
        return self.name

    @property
    def is_subscription_active(self):
        return self.subscription_status in ["active", "trial"]


class Domain(DomainMixin):
    """
    Domain model for tenant domains.
    """

    pass


# Temporarily removed custom User model to allow migrations
# Will be re-added after initial setup
# class User(AbstractUser):
#     """
#     Custom user model for tenants.
#     """
#     # Role-based access
#     ROLE_CHOICES = [
#         ('admin', 'Admin'),
#         ('editor', 'Editor'),
#         ('viewer', 'Viewer'),
#     ]
#     role = models.CharField(
#         max_length=20, choices=ROLE_CHOICES, default='admin'
#     )
#
#     # Profile information
#     avatar = models.URLField(
#         blank=True, null=True, help_text="Profile picture URL"
#     )
#     phone = models.CharField(
#         max_length=20, blank=True, help_text="Phone number"
#     )
#
#     class Meta:
#         verbose_name = "User"
#         verbose_name_plural = "Users"
#
#     def __str__(self):
#         return f"{self.username}"
#
#     @property
#     def full_name(self):
#         return f"{self.first_name} {self.last_name}".strip() or self.username
