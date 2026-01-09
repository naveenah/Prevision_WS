from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin
# from django_tenants.admin import TenantAdminMixin
from .models import Tenant, Domain
# from .models import User


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):  # TenantAdminMixin disabled for SQLite development
    list_display = ('name', 'domain', 'subscription_status', 'created_at')
    list_filter = ('subscription_status', 'created_at')
    search_fields = ('name', 'domain')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'domain')
        }),
        ('Subscription', {
            'fields': ('subscription_status', 'stripe_customer_id')
        }),
        ('Limits', {
            'fields': ('max_users', 'storage_limit_gb')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'tenant', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('domain', 'tenant__name')

# Custom User admin disabled for initial development
# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     list_display = ('username', 'email', 'role', 'is_active')
#     list_filter = ('role', 'is_active', 'is_staff')
#     search_fields = ('username', 'email', 'first_name', 'last_name')
#
#     fieldsets = UserAdmin.fieldsets + (
#         ('Additional Information', {
#             'fields': ('role', 'avatar', 'phone')
#         }),
#     )
#
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         ('Additional Information', {
#             'fields': ('role', 'avatar', 'phone')
#         }),
#     )
