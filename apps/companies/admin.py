from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.conf import settings
from django.utils.html import format_html
import stripe

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
        "verified",
        "stripe_subscription_id",
        "onboarded_at",
        "website",
        "created_by",
        "created_at",
    )
    search_fields = ("name", "legal_name", "stripe_customer_id", "stripe_subscription_id")
    list_filter = ("life_cycle", "plan", "industry", "timezone", "verified", InGracePeriodFilter)

    inlines = [AuditLogInline]

    actions = ["impersonate", "login_as", "activate_basic", "activate_pro"]

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

    def activate_basic(self, request, queryset):
        for company in queryset:
            company.plan = "basic"
            company.verified = True
            company.life_cycle = Company.LifeCycle.ACTIVE
            company.save(update_fields=["plan", "verified", "life_cycle"])
        self.message_user(request, "Activated Basic plan for selected companies")
    activate_basic.short_description = "Activate Basic"

    def activate_pro(self, request, queryset):
        for company in queryset:
            company.plan = "pro"
            company.verified = True
            company.life_cycle = Company.LifeCycle.ACTIVE
            company.save(update_fields=["plan", "verified", "life_cycle"])
        self.message_user(request, "Activated Pro plan for selected companies")
    activate_pro.short_description = "Activate Pro"

    def get_readonly_fields(self, request, obj=None):
        fields = super().get_readonly_fields(request, obj)
        if not request.user.is_superuser:
            fields = list(fields) + ["ignore_subscription"]
        return fields


@admin.register(Subscription)
class SubscriptionAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = (
        "company",
        "plan",
        "colored_status",
        "next_charge",
        "amount",
    )
    list_filter = ("plan", "status")
    search_fields = ("stripe_subscription_id", "company__name")
    readonly_fields = ("stripe_subscription_id",)
    actions = [
        "cancel_at_period_end",
        "reactivate",
        "sync_with_stripe",
    ]

    def colored_status(self, obj):
        color = {
            "active": "success",
            "trialing": "info",
            "past_due": "warning",
            "canceled": "danger",
        }.get(obj.status, "secondary")
        return format_html(
            '<span class="badge bg-{}">{}</span>', color, obj.get_status_display()
        )

    colored_status.short_description = "status"

    def next_charge(self, obj):
        return obj.end_date

    def cancel_at_period_end(self, request, queryset):
        for sub in queryset:
            sub.cancel_at_period_end = True
            sub.save(update_fields=["cancel_at_period_end"])
        self.message_user(request, "Subscription will cancel at period end")

    def reactivate(self, request, queryset):
        for sub in queryset:
            sub.cancel_at_period_end = False
            sub.status = Subscription.Status.ACTIVE
            sub.save(update_fields=["cancel_at_period_end", "status"])
        self.message_user(request, "Subscription reactivated")

    def sync_with_stripe(self, request, queryset):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        for sub in queryset:
            try:
                data = stripe.Subscription.retrieve(sub.stripe_subscription_id)
            except Exception as exc:
                self.message_user(request, f"Stripe error: {exc}", level=messages.ERROR)
                continue
            sub.status = data.get("status", sub.status)
            sub.plan = data.get("items", {}).get("data", [{}])[0].get("price", {}).get("nickname", sub.plan)
            sub.end_date = timezone.datetime.fromtimestamp(
                data.get("current_period_end"), tz=timezone.utc
            )
            sub.start_date = timezone.datetime.fromtimestamp(
                data.get("current_period_start"), tz=timezone.utc
            )
            sub.amount = data.get("plan", {}).get("amount", sub.amount)
            sub.currency = data.get("plan", {}).get("currency", sub.currency)
            sub.stripe_data = data
            sub.save()
        self.message_user(request, "Subscription synced")


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
