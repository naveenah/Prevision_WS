"""
Stripe service wrapper for payment operations.
"""
import stripe
import logging
from django.conf import settings
from django.utils import timezone
from datetime import datetime

from .models import Subscription, SubscriptionPlan, PaymentHistory

logger = logging.getLogger(__name__)


class StripeService:
    """Service for interacting with Stripe API"""

    def __init__(self):
        self.api_key = getattr(settings, "STRIPE_SECRET_KEY", None)
        if self.api_key:
            stripe.api_key = self.api_key
        else:
            logger.warning("STRIPE_SECRET_KEY not configured")

    def create_customer(self, tenant, email):
        """Create a Stripe customer for a tenant"""
        if not self.api_key:
            logger.error("Stripe not configured")
            return None

        try:
            customer = stripe.Customer.create(
                email=email,
                metadata={
                    "tenant_id": str(tenant.id),
                    "tenant_name": tenant.name,
                },
            )
            # Update tenant with Stripe customer ID
            tenant.stripe_customer_id = customer.id
            tenant.save(update_fields=["stripe_customer_id"])
            return customer
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create Stripe customer: {e}")
            raise

    def get_or_create_customer(self, tenant, email):
        """Get existing customer or create new one"""
        if tenant.stripe_customer_id:
            try:
                return stripe.Customer.retrieve(tenant.stripe_customer_id)
            except stripe.error.InvalidRequestError:
                # Customer doesn't exist, create new one
                pass
        return self.create_customer(tenant, email)

    def create_checkout_session(self, tenant, plan, success_url, cancel_url, email):
        """Create a Stripe Checkout session for subscription"""
        if not self.api_key:
            logger.error("Stripe not configured")
            return None

        try:
            customer = self.get_or_create_customer(tenant, email)

            session = stripe.checkout.Session.create(
                customer=customer.id,
                payment_method_types=["card"],
                line_items=[
                    {
                        "price": plan.stripe_price_id,
                        "quantity": 1,
                    }
                ],
                mode="subscription",
                success_url=success_url,
                cancel_url=cancel_url,
                metadata={
                    "tenant_id": str(tenant.id),
                    "plan_id": str(plan.id),
                },
            )
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create checkout session: {e}")
            raise

    def create_portal_session(self, tenant, return_url):
        """Create a Stripe Customer Portal session"""
        if not self.api_key:
            logger.error("Stripe not configured")
            return None

        if not tenant.stripe_customer_id:
            raise ValueError("Tenant has no Stripe customer ID")

        try:
            session = stripe.billing_portal.Session.create(
                customer=tenant.stripe_customer_id,
                return_url=return_url,
            )
            return session
        except stripe.error.StripeError as e:
            logger.error(f"Failed to create portal session: {e}")
            raise

    def cancel_subscription(self, subscription, at_period_end=True):
        """Cancel a subscription"""
        if not self.api_key:
            logger.error("Stripe not configured")
            return None

        try:
            if at_period_end:
                stripe_sub = stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True,
                )
            else:
                stripe_sub = stripe.Subscription.delete(
                    subscription.stripe_subscription_id
                )

            subscription.cancel_at_period_end = at_period_end
            subscription.save(update_fields=["cancel_at_period_end"])
            return stripe_sub
        except stripe.error.StripeError as e:
            logger.error(f"Failed to cancel subscription: {e}")
            raise

    def handle_webhook_event(self, payload, sig_header):
        """Process Stripe webhook events"""
        webhook_secret = getattr(settings, "STRIPE_WEBHOOK_SECRET", None)

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except ValueError:
            logger.error("Invalid webhook payload")
            raise
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid webhook signature")
            raise

        return self._process_event(event)

    def _process_event(self, event):
        """Process different webhook event types"""
        event_type = event["type"]
        data = event["data"]["object"]

        handlers = {
            "checkout.session.completed": self._handle_checkout_completed,
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
        }

        handler = handlers.get(event_type)
        if handler:
            return handler(data)
        else:
            logger.info(f"Unhandled webhook event type: {event_type}")
            return {"status": "ignored", "event_type": event_type}

    def _handle_checkout_completed(self, session):
        """Handle successful checkout session"""
        from tenants.models import Tenant

        tenant_id = session.get("metadata", {}).get("tenant_id")
        plan_id = session.get("metadata", {}).get("plan_id")

        if not tenant_id or not plan_id:
            logger.error("Missing metadata in checkout session")
            return {"status": "error", "message": "Missing metadata"}

        try:
            tenant = Tenant.objects.get(id=tenant_id)
            plan = SubscriptionPlan.objects.get(id=plan_id)

            # Retrieve the subscription from Stripe
            stripe_sub = stripe.Subscription.retrieve(session["subscription"])

            # Create or update subscription
            subscription, created = Subscription.objects.update_or_create(
                tenant=tenant,
                defaults={
                    "plan": plan,
                    "stripe_subscription_id": stripe_sub.id,
                    "stripe_customer_id": session["customer"],
                    "status": stripe_sub.status,
                    "current_period_start": datetime.fromtimestamp(
                        stripe_sub.current_period_start, tz=timezone.utc
                    ),
                    "current_period_end": datetime.fromtimestamp(
                        stripe_sub.current_period_end, tz=timezone.utc
                    ),
                },
            )

            # Update tenant's Stripe customer ID
            tenant.stripe_customer_id = session["customer"]
            tenant.subscription_status = "active"
            tenant.save(update_fields=["stripe_customer_id", "subscription_status"])

            return {"status": "success", "subscription_id": subscription.id}

        except (Tenant.DoesNotExist, SubscriptionPlan.DoesNotExist) as e:
            logger.error(f"Error processing checkout: {e}")
            return {"status": "error", "message": str(e)}

    def _handle_payment_succeeded(self, invoice):
        """Handle successful payment"""
        from tenants.models import Tenant

        customer_id = invoice.get("customer")

        try:
            tenant = Tenant.objects.get(stripe_customer_id=customer_id)
            subscription = Subscription.objects.get(tenant=tenant)

            # Record payment
            PaymentHistory.objects.create(
                tenant=tenant,
                subscription=subscription,
                stripe_invoice_id=invoice.get("id", ""),
                stripe_payment_intent_id=invoice.get("payment_intent", ""),
                amount=invoice.get("amount_paid", 0) / 100,  # Convert from cents
                currency=invoice.get("currency", "usd").upper(),
                status="succeeded",
                description=(
                    f"Subscription payment for {subscription.plan.display_name}"
                ),
            )

            return {"status": "success", "tenant_id": tenant.id}

        except (Tenant.DoesNotExist, Subscription.DoesNotExist) as e:
            logger.warning(f"Payment succeeded but tenant/subscription not found: {e}")
            return {"status": "warning", "message": str(e)}

    def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        from tenants.models import Tenant

        customer_id = invoice.get("customer")

        try:
            tenant = Tenant.objects.get(stripe_customer_id=customer_id)
            subscription = Subscription.objects.filter(tenant=tenant).first()

            # Record failed payment
            PaymentHistory.objects.create(
                tenant=tenant,
                subscription=subscription,
                stripe_invoice_id=invoice.get("id", ""),
                amount=invoice.get("amount_due", 0) / 100,
                currency=invoice.get("currency", "usd").upper(),
                status="failed",
                description="Payment failed",
            )

            # Update subscription status
            if subscription:
                subscription.status = "past_due"
                subscription.save(update_fields=["status"])

            return {"status": "recorded", "tenant_id": tenant.id}

        except Tenant.DoesNotExist:
            logger.warning(f"Payment failed for unknown customer: {customer_id}")
            return {"status": "warning", "message": "Tenant not found"}

    def _handle_subscription_updated(self, stripe_sub):
        """Handle subscription update"""
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=stripe_sub["id"]
            )

            subscription.status = stripe_sub["status"]
            subscription.current_period_start = datetime.fromtimestamp(
                stripe_sub["current_period_start"], tz=timezone.utc
            )
            subscription.current_period_end = datetime.fromtimestamp(
                stripe_sub["current_period_end"], tz=timezone.utc
            )
            subscription.cancel_at_period_end = stripe_sub.get(
                "cancel_at_period_end", False
            )
            subscription.save()

            return {"status": "updated", "subscription_id": subscription.id}

        except Subscription.DoesNotExist:
            logger.warning(f"Subscription not found for update: {stripe_sub['id']}")
            return {"status": "warning", "message": "Subscription not found"}

    def _handle_subscription_deleted(self, stripe_sub):
        """Handle subscription cancellation"""
        try:
            subscription = Subscription.objects.get(
                stripe_subscription_id=stripe_sub["id"]
            )

            subscription.status = "canceled"
            subscription.save(update_fields=["status"])

            # Update tenant status
            subscription.tenant.subscription_status = "canceled"
            subscription.tenant.save(update_fields=["subscription_status"])

            return {"status": "canceled", "subscription_id": subscription.id}

        except Subscription.DoesNotExist:
            logger.warning(f"Subscription not found for deletion: {stripe_sub['id']}")
            return {"status": "warning", "message": "Subscription not found"}


# Singleton instance
stripe_service = StripeService()
