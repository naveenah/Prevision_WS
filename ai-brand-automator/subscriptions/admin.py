from django.contrib import admin
from .models import SubscriptionPlan, Subscription, PaymentHistory


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ["name", "price", "stripe_price_id", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "stripe_price_id"]


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["tenant", "plan", "status", "current_period_end"]
    list_filter = ["status", "plan"]
    search_fields = ["tenant__name", "stripe_subscription_id"]


@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ["tenant", "amount", "status", "created_at"]
    list_filter = ["status"]
    search_fields = ["tenant__name", "stripe_payment_intent_id"]
