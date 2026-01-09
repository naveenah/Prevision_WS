from django.db.models.signals import post_save
from django.dispatch import receiver
from django_tenants.utils import schema_context
from .models import Tenant, Domain


@receiver(post_save, sender=Tenant)
def create_tenant_schema(sender, instance, created, **kwargs):
    """
    Create schema and domain when a new tenant is created.
    """
    if created:
        # Create the tenant schema
        from django_tenants.utils import get_tenant_model
        tenant_model = get_tenant_model()

        # Create domain if it doesn't exist
        domain, created = Domain.objects.get_or_create(
            domain=instance.domain,
            defaults={'tenant': instance, 'is_primary': True}
        )

        # Additional tenant setup can be done here
        print(f"Tenant {instance.name} created with schema and domain {instance.domain}")


@receiver(post_save, sender=Tenant)
def update_tenant_schema(sender, instance, **kwargs):
    """
    Handle tenant updates that might affect schema.
    """
    # Handle domain changes
    if instance.domain:
        Domain.objects.filter(tenant=instance).update(domain=instance.domain)