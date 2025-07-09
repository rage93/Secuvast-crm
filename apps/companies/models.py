from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from .threadlocals import get_current_company, get_current_user


class TenantQuerySet(models.QuerySet):
    """QuerySet with helper for company scoping."""

    def for_company(self, company):
        return self.filter(company=company)


class TenantManager(models.Manager.from_queryset(TenantQuerySet)):
    """Manager using ``TenantQuerySet`` as base."""

    def get_queryset(self):
        qs = super().get_queryset()
        company = get_current_company()
        user = get_current_user()
        if (
            company
            and hasattr(self.model, "company")
            and not getattr(user, "is_superuser", False)
        ):
            qs = qs.filter(company=company)
        if hasattr(self.model, "is_deleted"):
            qs = qs.filter(is_deleted=False)
        return qs

    def for_company(self, company):
        qs = super().get_queryset().for_company(company)
        if hasattr(self.model, "is_deleted"):
            qs = qs.filter(is_deleted=False)
        return qs

class Company(models.Model):
    class LifeCycle(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        PAST_DUE = "PAST_DUE", "Past Due"
        SUSPENDED = "SUSPENDED", "Suspended"
        DELETED = "DELETED", "Deleted"

    name = models.CharField(max_length=255)
    plan = models.CharField(max_length=50, default="free")
    trial_ends = models.DateField(null=True, blank=True)
    life_cycle = models.CharField(
        max_length=10,
        choices=LifeCycle.choices,
        default=LifeCycle.ACTIVE,
    )
    logo = models.ImageField(upload_to="company_logos/", null=True, blank=True)
    legal_name = models.CharField(max_length=255, null=True, blank=True)
    primary_color = models.CharField(max_length=7, null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    db_shard = models.CharField(max_length=50, default="default")
    industry = models.CharField(max_length=255, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    timezone = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    address_line1 = models.CharField(max_length=255, null=True, blank=True)
    address_line2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    billing_email = models.EmailField(null=True, blank=True)
    onboarded_at = models.DateTimeField(null=True, blank=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
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
    row_version = models.PositiveIntegerField(default=0)

    objects = TenantManager()

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=
                (
                    models.Q(primary_color__regex=r"^#[0-9A-Fa-f]{6}$")
                    | models.Q(primary_color__isnull=True)
                    | models.Q(primary_color="")
                ),
                name="company_color_hex",
            ),
            models.CheckConstraint(
                check=
                (
                    models.Q(billing_email__regex=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
                    | models.Q(billing_email__isnull=True)
                    | models.Q(billing_email="")
                ),
                name="company_billing_email_valid",
            ),
        ]
        permissions = (
            ("bypass_tenant_scope", "Can bypass tenant scoping"),
        )

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.life_cycle == self.LifeCycle.ACTIVE

    def activate(self):
        self.life_cycle = self.LifeCycle.ACTIVE
        self.save(update_fields=["life_cycle"])

    def suspend(self):
        self.life_cycle = self.LifeCycle.SUSPENDED
        self.save(update_fields=["life_cycle"])

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def save(self, *args, **kwargs):
        if self.pk:
            current = Company.objects.filter(pk=self.pk).values("row_version").first()
            if current and current["row_version"] != self.row_version:
                raise ValidationError("Row version mismatch")
            self.row_version += 1
        super().save(*args, **kwargs)

    @property
    def settings(self):
        from django.core.cache import cache
        key = f"company_settings_{self.id}"
        data = cache.get(key)
        if data is None:
            data = {s.key: s.value for s in self.companysettings.all()}
            cache.set(key, data, 60)
        return data


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


class CompanySetting(CompanyScopedModel):
    key = models.CharField(max_length=100)
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ("company", "key")

    def __str__(self):
        return f"{self.company}:{self.key}"

class AuditLog(models.Model):
    company = models.ForeignKey(Company, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField(null=True, blank=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    status = models.PositiveSmallIntegerField()
    ms = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    company_state_before = models.JSONField(null=True, blank=True)
    company_state_after = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']


class StripeEvent(models.Model):
    """Store processed Stripe event IDs to ensure idempotency."""

    event_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class StripeWebhookLog(models.Model):
    """Persist incoming webhook payloads for troubleshooting and retries."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSED = "processed", "Processed"
        FAILED = "failed", "Failed"

    event_id = models.CharField(max_length=255, unique=True)
    payload = models.JSONField()
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_id} ({self.status})"
