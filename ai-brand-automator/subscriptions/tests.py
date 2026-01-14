"""
Tests for the subscriptions app.
"""
import pytest
from decimal import Decimal
from rest_framework import status
from unittest.mock import patch, MagicMock

from subscriptions.models import SubscriptionPlan, Subscription, PaymentHistory
from subscriptions.services import StripeService


# Use the api_client fixture from conftest.py which has SERVER_NAME set


@pytest.fixture
def subscription_plan(db):
    """Create a test subscription plan."""
    return SubscriptionPlan.objects.create(
        name="basic",
        display_name="Basic Test",
        description="Test plan description",
        price=Decimal("29.00"),
        stripe_price_id="price_test_123",
        max_brands=1,
        max_team_members=1,
        ai_generations_per_month=10,
        automation_enabled=False,
        priority_support=False,
        is_active=True,
    )


@pytest.fixture
def mock_tenant():
    """Create a mock tenant object."""
    tenant = MagicMock()
    tenant.id = 1
    tenant.name = "Test Tenant"
    tenant.stripe_customer_id = None
    return tenant


@pytest.mark.django_db
class TestSubscriptionPlanModel:
    """Tests for SubscriptionPlan model."""

    def test_create_subscription_plan(self, subscription_plan):
        """Test creating a subscription plan."""
        assert subscription_plan.name == "basic"
        assert subscription_plan.display_name == "Basic Test"
        assert subscription_plan.price == Decimal("29.00")
        assert subscription_plan.stripe_price_id == "price_test_123"
        assert subscription_plan.is_active is True

    def test_subscription_plan_str(self, subscription_plan):
        """Test string representation."""
        expected = "Basic Test - $29.00/mo"
        assert str(subscription_plan) == expected


@pytest.mark.django_db
class TestSubscriptionPlanAPI:
    """Tests for subscription plan API endpoints."""

    def test_list_plans(self, api_client, subscription_plan):
        """Test listing subscription plans."""
        url = "/api/v1/subscriptions/plans/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] >= 1

    def test_retrieve_plan(self, api_client, subscription_plan):
        """Test retrieving a specific plan."""
        url = f"/api/v1/subscriptions/plans/{subscription_plan.id}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "basic"
        assert response.data["display_name"] == "Basic Test"

    def test_plans_are_read_only(self, api_client, subscription_plan):
        """Test that plans cannot be created via API."""
        url = "/api/v1/subscriptions/plans/"
        data = {
            "name": "test",
            "display_name": "Test Plan",
            "price": "99.00",
            "stripe_price_id": "price_new",
        }
        response = api_client.post(url, data)

        # Should be method not allowed (read-only viewset)
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestStripeService:
    """Tests for StripeService."""

    def test_service_initialization(self):
        """Test that the service can be instantiated."""
        service = StripeService()
        assert service is not None

    @patch("subscriptions.services.stripe.Customer.create")
    def test_create_customer(self, mock_create, mock_tenant):
        """Test creating a Stripe customer."""
        mock_create.return_value = MagicMock(id="cus_test123")

        service = StripeService()
        customer = service.create_customer(mock_tenant, "test@example.com")

        assert customer.id == "cus_test123"
        mock_create.assert_called_once()
        mock_tenant.save.assert_called_once()

    @patch("subscriptions.services.stripe.checkout.Session.create")
    @patch("subscriptions.services.stripe.Customer.retrieve")
    def test_create_checkout_session(
        self, mock_retrieve, mock_create, subscription_plan, mock_tenant
    ):
        """Test creating a checkout session."""
        mock_tenant.stripe_customer_id = "cus_existing"
        mock_retrieve.return_value = MagicMock(id="cus_existing")
        mock_create.return_value = MagicMock(
            id="cs_test123",
            url="https://checkout.stripe.com/test",
        )

        service = StripeService()
        session = service.create_checkout_session(
            tenant=mock_tenant,
            plan=subscription_plan,
            success_url="https://example.com/success",
            cancel_url="https://example.com/cancel",
            email="test@example.com",
        )

        assert session.id == "cs_test123"
        assert session.url == "https://checkout.stripe.com/test"

    @patch("subscriptions.services.stripe.billing_portal.Session.create")
    def test_create_portal_session(self, mock_create, mock_tenant):
        """Test creating a billing portal session."""
        mock_tenant.stripe_customer_id = "cus_test123"
        mock_create.return_value = MagicMock(
            url="https://billing.stripe.com/portal",
        )

        service = StripeService()
        session = service.create_portal_session(
            tenant=mock_tenant,
            return_url="https://example.com/billing",
        )

        assert session.url == "https://billing.stripe.com/portal"

    @patch("subscriptions.services.stripe.Subscription.modify")
    def test_cancel_subscription(self, mock_modify):
        """Test canceling a subscription."""
        mock_subscription = MagicMock()
        mock_subscription.stripe_subscription_id = "sub_test123"

        mock_modify.return_value = MagicMock(
            id="sub_test123",
            cancel_at_period_end=True,
        )

        service = StripeService()
        result = service.cancel_subscription(mock_subscription)

        assert result.cancel_at_period_end is True
        mock_modify.assert_called_once_with(
            "sub_test123",
            cancel_at_period_end=True,
        )
        mock_subscription.save.assert_called_once()
