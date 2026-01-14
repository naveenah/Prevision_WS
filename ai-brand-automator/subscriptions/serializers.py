"""
Serializers for subscription models.
"""
from rest_framework import serializers
from .models import SubscriptionPlan, Subscription, PaymentHistory


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    """Serializer for subscription plans"""

    class Meta:
        model = SubscriptionPlan
        fields = [
            "id",
            "name",
            "display_name",
            "description",
            "price",
            "currency",
            "max_brands",
            "max_team_members",
            "ai_generations_per_month",
            "automation_enabled",
            "priority_support",
            "is_active",
        ]


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions"""

    plan = SubscriptionPlanSerializer(read_only=True)
    is_active = serializers.ReadOnlyField()
    days_until_renewal = serializers.ReadOnlyField()

    class Meta:
        model = Subscription
        fields = [
            "id",
            "plan",
            "status",
            "current_period_start",
            "current_period_end",
            "cancel_at_period_end",
            "is_active",
            "days_until_renewal",
            "created_at",
        ]


class PaymentHistorySerializer(serializers.ModelSerializer):
    """Serializer for payment history"""

    class Meta:
        model = PaymentHistory
        fields = [
            "id",
            "amount",
            "currency",
            "status",
            "description",
            "created_at",
        ]


class CreateCheckoutSessionSerializer(serializers.Serializer):
    """Serializer for checkout session creation"""

    plan_id = serializers.IntegerField()
    success_url = serializers.URLField()
    cancel_url = serializers.URLField()


class CreatePortalSessionSerializer(serializers.Serializer):
    """Serializer for portal session creation"""

    return_url = serializers.URLField()
