"""Minimal Stripe billing helpers used by subscriptions app."""

import stripe
from django.conf import settings
from django.utils import timezone

stripe.api_key = getattr(settings, "STRIPE_SECRET_KEY", "")


def create_customer(*args, **kwargs):
    try:
        obj = stripe.Customer.create(*args, **kwargs)
        return obj.id
    except Exception:
        return None


def create_product(*args, **kwargs):
    try:
        obj = stripe.Product.create(*args, **kwargs)
        return obj.id
    except Exception:
        return None


def create_price(*args, **kwargs):
    try:
        obj = stripe.Price.create(*args, **kwargs)
        return obj.id
    except Exception:
        return None


def get_subscription(sub_id, raw=True):
    try:
        obj = stripe.Subscription.retrieve(sub_id)
        return obj if raw else obj.to_dict()
    except Exception:
        return {}


def get_customer_active_subscriptions(customer_id):
    try:
        return list(
            stripe.Subscription.list(customer=customer_id, status="active").auto_paging_iter()
        )
    except Exception:
        return []


def cancel_subscription(sub_id, reason="", cancel_at_period_end=True):
    try:
        return stripe.Subscription.delete(sub_id)
    except Exception:
        return None


def start_checkout_session(
    customer_id,
    success_url,
    cancel_url,
    price_stripe_id,
    raw=True,
    **kwargs,
):
    """Create a Stripe Checkout session for subscriptions."""
    try:
        session = stripe.checkout.Session.create(
            mode="subscription",
            customer=customer_id,
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            line_items=[{"price": price_stripe_id, "quantity": 1}],
            **kwargs,
        )
        return session if raw else session.url
    except Exception:
        return None


def get_checkout_customer_plan(session_id):
    """Return key subscription details from a Checkout session."""
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        sub_id = session.subscription
        subscription = stripe.Subscription.retrieve(sub_id)
        return {
            "plan_id": subscription.get("plan", {}).get("id"),
            "customer_id": session.customer,
            "sub_stripe_id": subscription.get("id"),
            "current_period_start": timezone.datetime.fromtimestamp(
                subscription.get("current_period_start"), tz=timezone.utc
            ),
            "current_period_end": timezone.datetime.fromtimestamp(
                subscription.get("current_period_end"), tz=timezone.utc
            ),
            "status": subscription.get("status"),
        }
    except Exception:
        return {}
