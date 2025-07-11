import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from allauth.account.models import EmailAddress
from allauth.account.signals import email_confirmed
from unittest.mock import patch
from django.utils import timezone

from apps.customers.models import Customer


@pytest.mark.django_db
def test_customer_created_and_confirmed(client):
    user = User.objects.create_user(
        username="admin", email="admin@example.com", password="pass"
    )
    client.login(username="admin", password="pass")
    resp = client.post(reverse("signup_company"), {"company_name": "ACME"})
    assert resp.status_code == 302
    user.refresh_from_db()
    company = user.profile.company
    customer = Customer.objects.get(company=company)
    assert customer.init_email == "admin@example.com"
    assert not customer.init_email_confirmed
    assert customer.stripe_id is None

    email_address = EmailAddress.objects.create(
        user=user, email="admin@example.com", verified=True
    )
    with patch(
        "apps.customers.models.billing.create_customer", return_value="cus_123"
    ) as mock_create:
        email_confirmed.send(
            sender=EmailAddress, request=None, email_address=email_address
        )
    customer.refresh_from_db()
    assert customer.init_email_confirmed
    assert customer.stripe_id == "cus_123"
    assert mock_create.called
