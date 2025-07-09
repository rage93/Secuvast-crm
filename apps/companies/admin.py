from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.conf import settings

from .models import Company, Subscription, AuditLog, StripeEvent


class AuditLogInline(admin.TabularInline):
    model = AuditLog
    extra = 0
    fields = ("user", "path", "method", "status", "ms", "timestamp")
    readonly_fields = fields
    can_delete = False


class TenantAdminMixin:
    """Filter objects by request.company for non-superusers."""

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        company = getattr(request, "company", None)
        if company and hasattr(qs.model, "company"):
            return qs.filter(company=company)
        elif company and qs.model is Company:
            return qs.filter(id=company.id)
        return qs.none()


class InGracePeriodFilter(admin.SimpleListFilter):
    title = "In grace period"
    parameter_name = "grace"

    def lookups(self, request, model_admin):
        return (("yes", "Yes"), ("no", "No"))

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(grace_until__gt=timezone.now())
        if self.value() == "no":
            return queryset.exclude(grace_until__gt=timezone.now())
        return queryset


@admin.register(Company)
class CompanyAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "plan",
        "life_cycle",
        "onboarded_at",
        "website",
        "created_by",
        "created_at",
    )
    search_fields = ("name", "legal_name", "stripe_customer_id")
    list_filter = ("life_cycle", "plan", "industry", "timezone", InGracePeriodFilter)

    inlines = [AuditLogInline]

    actions = ["impersonate", "login_as"]

    def impersonate(self, request, queryset):
        company = queryset.first()
        if company:
            url = reverse('admin:index') + f"?company={company.id}"
            return HttpResponseRedirect(url)
    impersonate.short_description = "Entrar como compañía"

    def login_as(self, request, queryset):
        company = queryset.first()
        if not company or not company.created_by:
            self.message_user(request, "No admin user", level=messages.ERROR)
            return
        login(request, company.created_by, backend="django.contrib.auth.backends.ModelBackend")
        return HttpResponseRedirect("/")
    login_as.short_description = "Login as admin"

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            fields = list(fields) + ["ignore_subscription"]
        return fields


@admin.register(Subscription)
class SubscriptionAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ("company", "stripe_subscription_id", "status")
    search_fields = ("stripe_subscription_id",)


@admin.register(AuditLog)
class AuditLogAdmin(TenantAdminMixin, admin.ModelAdmin):
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
class StripeEventAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ("event_id", "created_at")
