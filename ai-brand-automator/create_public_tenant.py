#!/usr/bin/env python
"""
Create the public tenant required for django-tenants.
This must be run once before the application can function.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brand_automator.settings')
django.setup()

from tenants.models import Tenant, Domain

def create_public_tenant():
    """Create the public tenant if it doesn't exist"""
    # Check if public tenant already exists
    if Tenant.objects.filter(schema_name='public').exists():
        print("✅ Public tenant already exists")
        return
    
    # Create public tenant
    public_tenant = Tenant.objects.create(
        schema_name='public',
        name='Public',
        description='Public schema for authentication and shared data'
    )
    print(f"✅ Created public tenant: {public_tenant.name} ({public_tenant.schema_name})")
    
    # Create domain for public tenant
    # In development, use localhost
    domain = Domain.objects.create(
        domain='localhost',
        tenant=public_tenant,
        is_primary=True
    )
    print(f"✅ Created domain: {domain.domain}")
    
    print("\n🎉 Public tenant setup complete!")
    print("   You can now create customer tenants via user registration")

if __name__ == '__main__':
    create_public_tenant()
