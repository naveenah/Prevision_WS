#!/usr/bin/env python
"""
Test script to validate multi-tenancy configuration.
This tests:
1. Tenant creation
2. Domain assignment
3. Schema creation
4. Tenant-specific data isolation
"""

import os
import django
import pytest

# Setup Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "brand_automator.settings")
django.setup()

from tenants.models import Tenant, Domain  # noqa: E402
from django.db import connection  # noqa: E402
from django_tenants.utils import schema_context  # noqa: E402


@pytest.fixture
def tenant(db):
    """Fixture to create a test tenant"""
    tenant = Tenant.objects.create(
        name="Test Company Inc",
        description="A test company for multi-tenancy validation",
        subscription_status="trial",
    )
    yield tenant
    # Cleanup
    tenant.delete()


@pytest.mark.django_db
def test_tenant_creation():
    """Test creating a new tenant with auto-generated schema name"""
    print("=" * 80)
    print("TEST 1: Tenant Creation")
    print("=" * 80)

    # Create a test tenant
    tenant = Tenant.objects.create(
        name="Test Company Inc",
        description="A test company for multi-tenancy validation",
        subscription_status="trial",
    )

    print("✅ Tenant created successfully!")
    print(f"   - ID: {tenant.id}")
    print(f"   - Name: {tenant.name}")
    print(f"   - Schema Name: {tenant.schema_name}")
    print(f"   - Subscription Status: {tenant.subscription_status}")
    print(f"   - Created At: {tenant.created_at}")
    print()

    assert tenant.id is not None
    assert tenant.schema_name.startswith("tenant_")
    tenant.delete()


@pytest.mark.django_db
def test_domain_creation(tenant):
    """Test creating a domain for the tenant"""
    print("=" * 80)
    print("TEST 2: Domain Creation")
    print("=" * 80)

    # Create a domain for localhost testing
    domain = Domain.objects.create(
        domain=f"{tenant.schema_name}.localhost",
        tenant=tenant,
        is_primary=True,
    )

    print("✅ Domain created successfully!")
    print(f"   - Domain: {domain.domain}")
    print(f"   - Tenant: {domain.tenant.name}")
    print(f"   - Is Primary: {domain.is_primary}")
    print()

    assert domain.domain == f"{tenant.schema_name}.localhost"
    assert domain.is_primary is True


@pytest.mark.django_db
def test_schema_creation(tenant):
    """Test that schema was created in database"""
    print("=" * 80)
    print("TEST 3: Schema Verification")
    print("=" * 80)

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name = %s
        """,
            [tenant.schema_name],
        )
        result = cursor.fetchone()

    if result:
        print("✅ Schema exists in database!")
        print(f"   - Schema Name: {result[0]}")
    else:
        print("❌ Schema NOT found in database!")
        print(f"   - Expected: {tenant.schema_name}")
    print()

    assert result is not None, f"Schema {tenant.schema_name} not found"


@pytest.mark.django_db
def test_tenant_data_isolation(tenant):
    """Test that tenant-specific data is isolated"""
    print("=" * 80)
    print("TEST 4: Tenant Data Isolation")
    print("=" * 80)

    from django.contrib.auth.models import User

    # Create user in public schema
    public_user = User.objects.create_user(
        username="public_user",
        email="public@example.com",
        password="testpass123",
    )
    print(f"✅ Created user in PUBLIC schema: {public_user.username}")

    # Switch to tenant schema and create user there
    with schema_context(tenant.schema_name):
        tenant_user = User.objects.create_user(
            username="tenant_user",
            email="tenant@example.com",
            password="testpass123",
        )
        print(
            f"✅ Created user in TENANT schema "
            f"({tenant.schema_name}): {tenant_user.username}"
        )

        # Count users in tenant schema
        tenant_users_count = User.objects.count()
        print(f"   - Users in tenant schema: {tenant_users_count}")

    # Count users in public schema
    public_users_count = User.objects.count()
    print(f"   - Users in public schema: {public_users_count}")

    # Verify isolation
    if tenant_users_count == 1 and public_users_count >= 1:
        print("✅ Data isolation working correctly!")
    else:
        print("❌ Data isolation NOT working!")
    print()


@pytest.mark.django_db
def test_tenant_listing():
    """List all existing tenants"""
    print("=" * 80)
    print("TEST 5: List All Tenants")
    print("=" * 80)

    tenants = Tenant.objects.all()
    print(f"Total tenants: {tenants.count()}")
    for tenant in tenants:
        domains = Domain.objects.filter(tenant=tenant)
        print(f"\n  Tenant: {tenant.name}")
        print(f"  - Schema: {tenant.schema_name}")
        print(f"  - Status: {tenant.subscription_status}")
        print(f"  - Domains: {', '.join([d.domain for d in domains])}")
    print()


def cleanup_test_data():
    """Clean up test data"""
    print("=" * 80)
    print("CLEANUP: Removing test data")
    print("=" * 80)

    # Remove test tenant
    test_tenants = Tenant.objects.filter(name__icontains="Test Company")
    count = test_tenants.count()
    test_tenants.delete()

    # Remove test users
    from django.contrib.auth.models import User

    User.objects.filter(username__in=["public_user", "tenant_user"]).delete()

    print(f"✅ Cleaned up {count} test tenant(s) and test users")
    print()
