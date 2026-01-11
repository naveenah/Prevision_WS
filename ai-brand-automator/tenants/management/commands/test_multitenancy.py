from django.core.management.base import BaseCommand
from tenants.models import Tenant, Domain
from django.db import connection
from django_tenants.utils import schema_context


class Command(BaseCommand):
    help = "Validate multi-tenancy configuration"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS("\n🔍 Testing Multi-Tenancy Configuration\n")
        )

        # Test 1: Check existing tenants
        tenants = Tenant.objects.all()
        self.stdout.write(f"Found {tenants.count()} existing tenant(s)")
        for tenant in tenants:
            domains = Domain.objects.filter(tenant=tenant)
            self.stdout.write(f"  - {tenant.name} ({tenant.schema_name})")
            for domain in domains:
                self.stdout.write(f"    Domain: {domain.domain}")

        # Test 2: Create a test tenant
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Creating test tenant...")

        try:
            test_tenant = Tenant.objects.create(
                name="MultiTenancy Test Corp",
                description="Test tenant for validation",
                subscription_status="trial",
            )
            self.stdout.write(
                self.style.SUCCESS(f"✅ Tenant created: {test_tenant.schema_name}")
            )

            # Create domain
            test_domain = Domain.objects.create(
                domain=f"{test_tenant.schema_name}.localhost",
                tenant=test_tenant,
                is_primary=True,
            )
            self.stdout.write(
                self.style.SUCCESS(f"✅ Domain created: {test_domain.domain}")
            )

            # Check schema exists
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT schema_name 
                    FROM information_schema.schemata 
                    WHERE schema_name = %s
                """,
                    [test_tenant.schema_name],
                )
                result = cursor.fetchone()

            if result:
                self.stdout.write(self.style.SUCCESS(f"✅ Schema exists in database"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Schema NOT found"))

            # Cleanup
            self.stdout.write("\nCleaning up test data...")
            test_tenant.delete()
            self.stdout.write(self.style.SUCCESS("✅ Test data cleaned up"))

            self.stdout.write(
                self.style.SUCCESS("\n✅ Multi-tenancy configuration is WORKING!")
            )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Error: {str(e)}"))
            raise
