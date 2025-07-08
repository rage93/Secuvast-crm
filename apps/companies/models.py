from django.db import models
from django.contrib.auth.models import User
from .threadlocals import get_current_company


class TenantQuerySet(models.QuerySet):
    """QuerySet with helper for company scoping."""

    def for_company(self, company):
        return self.filter(company=company)


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    """Manager using ``TenantQuerySet`` as base."""

    def get_queryset(self):
        qs = super().get_queryset()
        company = get_current_company()
        if company and hasattr(self.model, "company"):
            qs = qs.filter(company=company)
        return qs

    def for_company(self, company):
        return super().get_queryset().for_company(company)

class Company(models.Model):
    name = models.CharField(max_length=255)
    slug_subdomain = models.SlugField(unique=True)
    plan = models.CharField(max_length=50, default='free')
    trial_ends = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    primary_color = models.CharField(max_length=7, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    ignore_subscription = models.BooleanField(
        default=False,
        help_text="Keep company active even if Stripe subscription is inactive",
    )
    grace_until = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_companies',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    objects = TenantManager()

    def __str__(self):
        return self.name


class CompanyScopedModel(models.Model):
    """Abstract model to add company FK and tenant-aware manager."""

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        null=True,
        blank=True,
    )

    objects = TenantManager()

    class Meta:
        abstract = True

class Subscription(CompanyScopedModel):
    """Track Stripe subscription for a company."""

    stripe_subscription_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company} - {self.status}"

class AuditLog(models.Model):
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status = models.PositiveSmallIntegerField()
    ms = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class StripeEvent(models.Model):
    """Store processed Stripe event IDs to ensure idempotency."""

    event_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
