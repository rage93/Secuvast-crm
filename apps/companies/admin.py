from django.contrib import admin
from .models import Company, Subscription, AuditLog, StripeEvent


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug_subdomain",
        "plan",
        "is_active",
        "stripe_customer_id",
        "ignore_subscription",
        "grace_until",
        "created_by",
    )
    search_fields = ("name", "slug_subdomain")

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            fields = list(fields) + ["ignore_subscription"]
        return fields


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("company", "stripe_subscription_id", "status")
    search_fields = ("stripe_subscription_id",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "user",
        "path",
        "method",
        "status",
        "ms",
        "timestamp",
    )
    search_fields = ("path",)


@admin.register(StripeEvent)
class StripeEventAdmin(admin.ModelAdmin):
    list_display = ("event_id", "created_at")
