"""
Management command to seed initial subscription plans from Stripe.
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import stripe

from subscriptions.models import SubscriptionPlan


class Command(BaseCommand):
    help = "Seed the database with subscription plans from Stripe"

    def handle(self, *args, **options):
        # Configure Stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY

        if not stripe.api_key:
            self.stdout.write(self.style.ERROR("STRIPE_SECRET_KEY not configured"))
            return

        # Validate required price ID settings
        price_ids = [
            ("STRIPE_PRICE_BASIC", getattr(settings, "STRIPE_PRICE_BASIC", "")),
            ("STRIPE_PRICE_PRO", getattr(settings, "STRIPE_PRICE_PRO", "")),
            (
                "STRIPE_PRICE_ENTERPRISE",
                getattr(settings, "STRIPE_PRICE_ENTERPRISE", ""),
            ),
        ]
        missing_settings = [name for name, value in price_ids if not value]
        if missing_settings:
            self.stdout.write(
                self.style.ERROR(
                    f"Missing Stripe price settings: {', '.join(missing_settings)}"
                )
            )
            return

        # Map of Stripe price IDs to plan metadata
        plan_config = {
            settings.STRIPE_PRICE_BASIC: {
                "name": "basic",
                "display_name": "Basic",
                "description": "Perfect for individuals starting their brand journey",
                "max_brands": 1,
                "max_team_members": 1,
                "ai_generations_per_month": 10,
                "automation_enabled": False,
                "priority_support": False,
            },
            settings.STRIPE_PRICE_PRO: {
                "name": "pro",
                "display_name": "Pro",
                "description": "For growing businesses with multiple brands",
                "max_brands": 5,
                "max_team_members": 5,
                "ai_generations_per_month": 50,
                "automation_enabled": True,
                "priority_support": True,
            },
            settings.STRIPE_PRICE_ENTERPRISE: {
                "name": "enterprise",
                "display_name": "Enterprise",
                "description": "Unlimited features for large organizations",
                "max_brands": SubscriptionPlan.UNLIMITED,
                "max_team_members": SubscriptionPlan.UNLIMITED,
                "ai_generations_per_month": SubscriptionPlan.UNLIMITED,
                "automation_enabled": True,
                "priority_support": True,
            },
        }

        success_count = 0
        failure_count = 0

        for stripe_price_id, config in plan_config.items():
            try:
                # Fetch price from Stripe
                price = stripe.Price.retrieve(stripe_price_id)

                # Get the amount (Stripe stores in cents)
                amount = price.unit_amount / 100 if price.unit_amount else 0
                currency = price.currency.upper()

                self.stdout.write(
                    f"Fetched {config['display_name']}: ${amount} {currency}"
                )

                # Create or update the plan
                plan, created = SubscriptionPlan.objects.update_or_create(
                    name=config["name"],
                    defaults={
                        **config,
                        "stripe_price_id": stripe_price_id,
                        "price": amount,
                        "currency": currency,
                        "is_active": price.active,
                    },
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created plan: {plan.display_name} - ${amount}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Updated plan: {plan.display_name} - ${amount}"
                        )
                    )
                success_count += 1

            except stripe.error.StripeError as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to fetch {config['display_name']}: {e}")
                )
                failure_count += 1

        # Show accurate summary based on results
        if failure_count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully synced all {success_count} subscription plans"
                )
            )
        elif success_count > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Synced {success_count} plans, {failure_count} failed"
                )
            )
        else:
            self.stdout.write(self.style.ERROR("Failed to sync any subscription plans"))
