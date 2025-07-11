from django.db.models import Q
from customers.models import Customer
from .models import Subscription, UserSubscription, SubscriptionStatus

try:
    from helpers import billing
except Exception:
    class billing:
        @staticmethod
        def get_subscription(*args, **kwargs):
            return {}
        @staticmethod
        def get_customer_active_subscriptions(*args, **kwargs):
            return []
        @staticmethod
        def cancel_subscription(*args, **kwargs):
            return None


def refresh_active_users_subscriptions(
    user_ids=None,
    active_only=True,
    days_left=-1,
    days_ago=-1,
    day_start=-1,
    day_end=-1,
    verbose=False,
):
    qs = UserSubscription.objects.all()
    if active_only:
        qs = qs.by_active_trialing()
    if user_ids is not None:
        qs = qs.by_user_ids(user_ids=user_ids)
    if days_ago > -1:
        qs = qs.by_days_ago(days_ago=days_ago)
    if days_left > -1:
        qs = qs.by_days_left(days_left=days_left)
    if day_start > -1 and day_end > -1:
        qs = qs.by_range(days_start=day_start, days_end=day_end, verbose=verbose)
    complete_count = 0
    qs_count = qs.count()
    for obj in qs:
        if verbose:
            print("Updating user", obj.user, obj.subscription, obj.current_period_end)
        if obj.stripe_id:
            sub_data = billing.get_subscription(obj.stripe_id, raw=False)
            for k, v in sub_data.items():
                setattr(obj, k, v)
            obj.save()
            complete_count += 1
    return complete_count == qs_count


def clear_dangling_subs():
    qs = Customer.objects.filter(stripe_id__isnull=False)
    for customer_obj in qs:
        company = customer_obj.company
        customer_stripe_id = customer_obj.stripe_id
        print(f"Sync {company} - {customer_stripe_id} subs and remove old ones")
        subs = billing.get_customer_active_subscriptions(customer_stripe_id)
        for sub in subs:
            existing_user_subs_qs = UserSubscription.objects.filter(
                stripe_id__iexact=f"{sub.id}".strip()
            )
            if existing_user_subs_qs.exists():
                continue
            billing.cancel_subscription(
                sub.id, reason="Dangling active subscription", cancel_at_period_end=False
            )


def sync_subs_group_permissions():
    qs = Subscription.objects.filter(active=True)
    for obj in qs:
        sub_perms = obj.permissions.all()
        for group in obj.groups.all():
            group.permissions.set(sub_perms)
