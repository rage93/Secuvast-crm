import json
import stripe
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django_redis import get_redis_connection
from datetime import timedelta

from .models import (
    Subscription,
    AuditLog,
    Company,
    StripeEvent,
    StripeWebhookLog,
)

@shared_task
def verify_subscriptions():
    """Check subscription status in Stripe and update companies."""
    lock_key = f"verify_subscriptions_lock:{settings.ENVIRONMENT}"
    if not cache.add(lock_key, "1", timeout=60 * 60):
        return
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        remote_data = {}
        for sub in stripe.Subscription.list(limit=100).auto_paging_iter():
            remote_data[sub["id"]] = sub

        for sub in Subscription.objects.select_related("company").all():
            company = sub.company
            if not company or company.ignore_subscription:
                continue
            data = remote_data.get(sub.stripe_subscription_id)
            if not data:
                try:
                    data = stripe.Subscription.retrieve(sub.stripe_subscription_id)
                except Exception:
                    continue
            status = data.get("status", "")
            updates = {}
            if sub.status != status:
                updates["status"] = status
            new_end = timezone.datetime.fromtimestamp(data.get("current_period_end"), tz=timezone.utc)
            if sub.end_date != new_end:
                updates["end_date"] = new_end
            new_start = timezone.datetime.fromtimestamp(data.get("current_period_start"), tz=timezone.utc)
            if sub.start_date != new_start:
                updates["start_date"] = new_start
            updates["cancel_at_period_end"] = data.get("cancel_at_period_end", False)
            updates["amount"] = data.get("plan", {}).get("amount", sub.amount)
            updates["currency"] = data.get("plan", {}).get("currency", sub.currency)
            updates["stripe_data"] = data
            if updates:
                for k, v in updates.items():
                    setattr(sub, k, v)
                sub.save()
            if status not in ["active", "trialing"]:
                if company.grace_until and company.grace_until > timezone.now():
                    continue
                if company.life_cycle == Company.LifeCycle.ACTIVE:
                    company.life_cycle = Company.LifeCycle.SUSPENDED
                    company.save(update_fields=["life_cycle"])
            else:
                update_fields = []
                if company.life_cycle != Company.LifeCycle.ACTIVE:
                    company.life_cycle = Company.LifeCycle.ACTIVE
                    update_fields.append("life_cycle")
                if company.grace_until:
                    company.grace_until = None
                    update_fields.append("grace_until")
                if update_fields:
                    company.save(update_fields=update_fields)

        grace_warning()
    finally:
        cache.delete(lock_key)


@shared_task
def grace_warning():
    """Send reminder emails about expiring grace periods."""
    remind_qs = Company.objects.filter(
        grace_until__gt=timezone.now(),
        grace_until__lte=timezone.now() + timedelta(days=1),
    ).select_related("created_by")
    for company in remind_qs:
        if company.created_by and company.created_by.email:
            html = render_to_string(
                "companies/email_grace_warning.html", {"company": company}
            )
            send_mail(
                "Subscription expiring soon",
                "",
                settings.DEFAULT_FROM_EMAIL,
                [company.created_by.email],
                html_message=html,
                fail_silently=True,
            )
            AuditLog.objects.create(
                company=company,
                user=company.created_by,
                ip=None,
                path="grace_warning_email",
                method="SYSTEM",
                status=0,
                ms=0,
            )


@shared_task
def log_request(data: dict):
    """Buffer request logs in Redis to insert in bulk."""
    conn = get_redis_connection("default")
    length = conn.rpush("audit_log_buffer", json.dumps(data))
    if length == 1:
        conn.set("audit_log_buffer_first_ts", int(timezone.now().timestamp()))


@shared_task
def flush_audit_logs():
    conn = get_redis_connection("default")
    length = conn.llen("audit_log_buffer")
    first_ts = conn.get("audit_log_buffer_first_ts")
    if length < 500:
        if not first_ts or (timezone.now().timestamp() - float(first_ts)) < 5:
            return
    items = []
    while True:
        raw = conn.lpop("audit_log_buffer")
        if not raw:
            break
        items.append(json.loads(raw))
    if items:
        AuditLog.objects.bulk_create(
            [
                AuditLog(
                    company_id=i.get("company_id"),
                    user_id=i.get("user_id"),
                    ip=i.get("ip"),
                    path=i.get("path"),
                    method=i.get("method"),
                    status=i.get("status"),
                    ms=i.get("ms"),
                )
                for i in items
            ]
        )
    conn.delete("audit_log_buffer_first_ts")


@shared_task
def purge_audit_logs():
    """Remove logs older than 90 days."""
    cutoff = timezone.now() - timedelta(days=90)
    AuditLog.objects.filter(timestamp__lt=cutoff).delete()


@shared_task
def purge_stripe_events():
    """Delete StripeEvent records older than one year."""
    cutoff = timezone.now() - timedelta(days=365)
    StripeEvent.objects.filter(created_at__lt=cutoff).delete()


def _handle_webhook(log):
    from .views import handle_stripe_event

    try:
        handle_stripe_event(log.payload)
        log.status = log.Status.PROCESSED
        log.error = ""
    except Exception as exc:  # pragma: no cover - safeguard
        log.status = log.Status.FAILED
        log.error = str(exc)
    log.save(update_fields=["status", "error"])


@shared_task
def retry_failed_webhooks():
    """Reprocess any failed Stripe webhooks."""
    for log in StripeWebhookLog.objects.filter(status=StripeWebhookLog.Status.FAILED)[:10]:
        _handle_webhook(log)
