"""
URL patterns for subscription endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SubscriptionPlanViewSet,
    get_subscription_status,
    create_checkout_session,
    create_portal_session,
    cancel_subscription,
    get_payment_history,
    stripe_webhook,
    sync_subscription,
)

router = DefaultRouter()
router.register(r"plans", SubscriptionPlanViewSet, basename="subscriptionplan")

urlpatterns = [
    path("", include(router.urls)),
    path("status/", get_subscription_status, name="subscription_status"),
    path(
        "create-checkout-session/",
        create_checkout_session,
        name="create_checkout_session",
    ),
    path(
        "create-portal-session/",
        create_portal_session,
        name="create_portal_session",
    ),
    path("cancel/", cancel_subscription, name="cancel_subscription"),
    path("payments/", get_payment_history, name="payment_history"),
    path("webhook/", stripe_webhook, name="stripe_webhook"),
    path("sync/", sync_subscription, name="sync_subscription"),
]
