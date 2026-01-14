"""
Views for subscription management.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

from .models import SubscriptionPlan, Subscription, PaymentHistory
from .serializers import (
    SubscriptionPlanSerializer,
    SubscriptionSerializer,
    PaymentHistorySerializer,
    CreateCheckoutSessionSerializer,
    CreatePortalSessionSerializer,
)
from .services import stripe_service

logger = logging.getLogger(__name__)


class SubscriptionPlanViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing subscription plans"""

    queryset = SubscriptionPlan.objects.filter(is_active=True)
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]  # Plans are public


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_subscription_status(request):
    """Get current subscription status for the tenant"""
    tenant = getattr(request, "tenant", None)

    if not tenant:
        # MVP mode - try to get tenant from user
        from tenants.models import Tenant

        try:
            tenant = Tenant.objects.get(schema_name="public")
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Tenant not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    try:
        subscription = Subscription.objects.get(tenant=tenant)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)
    except Subscription.DoesNotExist:
        return Response(
            {
                "status": "none",
                "message": "No active subscription",
                "plans_url": "/api/v1/subscriptions/plans/",
            }
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_checkout_session(request):
    """Create a Stripe Checkout session for subscription"""
    serializer = CreateCheckoutSessionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    tenant = getattr(request, "tenant", None)
    if not tenant:
        from tenants.models import Tenant

        try:
            tenant = Tenant.objects.get(schema_name="public")
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Tenant not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    try:
        plan = SubscriptionPlan.objects.get(
            id=serializer.validated_data["plan_id"],
            is_active=True,
        )
    except SubscriptionPlan.DoesNotExist:
        return Response(
            {"error": "Plan not found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        session = stripe_service.create_checkout_session(
            tenant=tenant,
            plan=plan,
            success_url=serializer.validated_data["success_url"],
            cancel_url=serializer.validated_data["cancel_url"],
            email=request.user.email,
        )

        if session:
            return Response(
                {
                    "checkout_url": session.url,
                    "session_id": session.id,
                }
            )
        else:
            return Response(
                {"error": "Stripe not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    except Exception as e:
        logger.error(f"Checkout session creation failed: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_portal_session(request):
    """Create a Stripe Customer Portal session"""
    serializer = CreatePortalSessionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    tenant = getattr(request, "tenant", None)
    if not tenant:
        from tenants.models import Tenant

        try:
            tenant = Tenant.objects.get(schema_name="public")
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Tenant not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    if not tenant.stripe_customer_id:
        return Response(
            {"error": "No billing account found. Please subscribe first."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        session = stripe_service.create_portal_session(
            tenant=tenant,
            return_url=serializer.validated_data["return_url"],
        )

        if session:
            return Response({"portal_url": session.url})
        else:
            return Response(
                {"error": "Stripe not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

    except Exception as e:
        logger.error(f"Portal session creation failed: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cancel_subscription(request):
    """Cancel the current subscription"""
    tenant = getattr(request, "tenant", None)
    if not tenant:
        from tenants.models import Tenant

        try:
            tenant = Tenant.objects.get(schema_name="public")
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Tenant not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    try:
        subscription = Subscription.objects.get(tenant=tenant)
    except Subscription.DoesNotExist:
        return Response(
            {"error": "No subscription found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    at_period_end = request.data.get("at_period_end", True)

    try:
        stripe_service.cancel_subscription(subscription, at_period_end=at_period_end)
        return Response(
            {
                "message": "Subscription will be canceled"
                + (" at period end" if at_period_end else " immediately"),
                "cancel_at_period_end": at_period_end,
            }
        )
    except Exception as e:
        logger.error(f"Subscription cancellation failed: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_payment_history(request):
    """Get payment history for the tenant"""
    tenant = getattr(request, "tenant", None)
    if not tenant:
        from tenants.models import Tenant

        try:
            tenant = Tenant.objects.get(schema_name="public")
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Tenant not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    payments = PaymentHistory.objects.filter(tenant=tenant)[:20]
    serializer = PaymentHistorySerializer(payments, many=True)
    return Response(serializer.data)


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    try:
        result = stripe_service.handle_webhook_event(payload, sig_header)
        return Response(result)
    except ValueError as e:
        logger.error(f"Webhook error: {e}")
        return Response(
            {"error": "Invalid payload"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        logger.error(f"Webhook processing error: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def sync_subscription(request):
    """Sync subscription status from Stripe (for after checkout)"""
    import stripe
    from datetime import datetime
    from django.utils import timezone as django_timezone

    stripe.api_key = settings.STRIPE_SECRET_KEY

    tenant = getattr(request, "tenant", None)
    if not tenant:
        from tenants.models import Tenant

        try:
            tenant = Tenant.objects.get(schema_name="public")
        except Tenant.DoesNotExist:
            return Response(
                {"error": "Tenant not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

    if not tenant.stripe_customer_id:
        return Response(
            {"error": "No Stripe customer associated with this account"},
            status=status.HTTP_404_NOT_FOUND,
        )

    try:
        # Fetch subscriptions from Stripe for this customer
        subscriptions = stripe.Subscription.list(
            customer=tenant.stripe_customer_id,
            status="all",
            limit=1,
        )

        if not subscriptions.data:
            return Response(
                {"error": "No subscription found in Stripe"},
                status=status.HTTP_404_NOT_FOUND,
            )

        stripe_sub = subscriptions.data[0]

        # Find the plan by matching the price ID
        price_id = stripe_sub["items"]["data"][0]["price"]["id"]
        try:
            plan = SubscriptionPlan.objects.get(stripe_price_id=price_id)
        except SubscriptionPlan.DoesNotExist:
            return Response(
                {"error": f"Plan not found for price: {price_id}"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Create or update local subscription
        subscription, created = Subscription.objects.update_or_create(
            tenant=tenant,
            defaults={
                "plan": plan,
                "stripe_subscription_id": stripe_sub.id,
                "stripe_customer_id": tenant.stripe_customer_id,
                "status": stripe_sub.status,
                "current_period_start": datetime.fromtimestamp(
                    stripe_sub.current_period_start, tz=django_timezone.utc
                ),
                "current_period_end": datetime.fromtimestamp(
                    stripe_sub.current_period_end, tz=django_timezone.utc
                ),
                "cancel_at_period_end": stripe_sub.cancel_at_period_end,
            },
        )

        serializer = SubscriptionSerializer(subscription)
        return Response({
            "message": "Subscription synced successfully",
            "subscription": serializer.data,
        })

    except stripe.error.StripeError as e:
        logger.error(f"Stripe error during sync: {e}")
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
