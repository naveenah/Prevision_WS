from django.contrib import admin
from .models import Company, BrandAsset, OnboardingProgress


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "tenant", "industry", "created_at")
    list_filter = ("industry", "brand_voice", "created_at")
    search_fields = ("name", "tenant__name", "description")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("tenant", "name", "description", "industry")},
        ),
        (
            "Target & Problem",
            {"fields": ("target_audience", "core_problem", "brand_voice")},
        ),
        (
            "AI-Generated Content",
            {
                "fields": (
                    "vision_statement",
                    "mission_statement",
                    "values",
                    "positioning_statement",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Brand Messaging",
            {
                "fields": ("tagline", "value_proposition", "elevator_pitch"),
                "classes": ("collapse",),
            },
        ),
        (
            "Brand Identity",
            {
                "fields": (
                    "color_palette_desc",
                    "font_recommendations",
                    "messaging_guide",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(BrandAsset)
class BrandAssetAdmin(admin.ModelAdmin):
    list_display = ("file_name", "company", "file_type", "file_size", "uploaded_at")
    list_filter = ("file_type", "uploaded_at", "processed")
    search_fields = ("file_name", "company__name", "company__tenant__name")
    readonly_fields = ("uploaded_at",)

    fieldsets = (
        (
            "File Information",
            {"fields": ("tenant", "company", "file_name", "file_type", "file_size")},
        ),
        ("Storage", {"fields": ("gcs_path", "gcs_bucket", "processed")}),
        ("Metadata", {"fields": ("uploaded_at",), "classes": ("collapse",)}),
    )


@admin.register(OnboardingProgress)
class OnboardingProgressAdmin(admin.ModelAdmin):
    list_display = (
        "tenant",
        "company",
        "current_step",
        "completion_percentage",
        "is_completed",
    )
    list_filter = ("current_step", "is_completed", "started_at")
    search_fields = ("tenant__name", "company__name")
    readonly_fields = ("started_at", "last_updated")

    fieldsets = (
        (
            "Progress Tracking",
            {
                "fields": (
                    "tenant",
                    "company",
                    "current_step",
                    "completed_steps",
                    "is_completed",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("started_at", "completed_at", "last_updated"),
                "classes": ("collapse",),
            },
        ),
    )
