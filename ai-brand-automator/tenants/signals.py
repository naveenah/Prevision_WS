from django.db.models.signals import post_save
from django.dispatch import receiver
from django_tenants.utils import schema_context
from .models import Tenant, Domain


@receiver(post_save, sender=Tenant)
def create_tenant_schema(sender, instance, created, **kwargs):
    """
    Create schema when a new tenant is created.
    Note: Domain must be created separately.
    """
    if created:
        print(f"✅ Tenant {instance.name} created with schema '{instance.schema_name}'")
        print(f"   Remember to create a Domain for this tenant")
