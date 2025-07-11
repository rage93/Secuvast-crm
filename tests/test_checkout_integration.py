import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch

from apps.customers.models import Customer
from apps.subscriptions.models import (
    Subscription,
    SubscriptionPrice,
    UserSubscription,
    SubscriptionStatus,
)
from apps.companies.models import Company


@pytest.mark.django_db
def test_checkout_finalize_creates_user_subscription(client):
    user = User.objects.create_user(username="admin", password="pass")
    company = Company.objects.create(name="ACME", created_by=user)
    user.profile.company = company
    user.profile.role = "admin"
    user.profile.save()
    Customer.objects.create(
        company=company,
        stripe_id="cus_1",
        init_email="admin@example.com",
        init_email_confirmed=True,
    )
    with patch(
        "apps.subscriptions.models.billing.create_product", return_value="prod_1"
    ), patch(
        "apps.subscriptions.models.billing.create_price",
        return_value="price_1",
    ):
        sub = Subscription.objects.create(name="Basic")
        price = SubscriptionPrice.objects.create(subscription=sub, stripe_id="price_1")

    checkout_data = {
        "plan_id": "price_1",
        "customer_id": "cus_1",
        "sub_stripe_id": "sub_1",
        "current_period_start": timezone.now(),
        "current_period_end": timezone.now() + timezone.timedelta(days=30),
        "status": SubscriptionStatus.ACTIVE,
    }

    with patch(
        "apps.checkouts.views.helpers.billing.get_checkout_customer_plan",
        return_value=checkout_data,
    ):
        resp = client.get(reverse("stripe-checkout-end") + "?session_id=sess")
    assert resp.status_code == 200
    user_sub = UserSubscription.objects.get(user=user)
    assert user_sub.subscription == sub
    assert user_sub.stripe_id == "sub_1"
    assert user_sub.status == SubscriptionStatus.ACTIVE
