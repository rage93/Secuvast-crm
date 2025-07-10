from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta
import json

from apps.companies.models import Company, AuditLog
from apps.companies.tasks import purge_audit_logs
from apps.users.models import Profile
from apps.users.forms import TenantUserCreationForm


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class StripeWebhookTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="TestCo",
            plan="pro",
            life_cycle=Company.LifeCycle.ACTIVE,
        )
        user = User.objects.create_user(username="admin", password="pass")
        user.profile.company = self.company
        user.profile.role = "admin"
        user.profile.save()
        self.client.login(username="admin", password="pass")

    @override_settings(STRIPE_WEBHOOK_SECRET="whsec")
    @patch("apps.companies.audit_middleware.conn")
    @patch("stripe.WebhookSignature.verify_header", return_value=True)
    def test_grace_period(self, mock_verify, mock_conn):
        payload = json.dumps({
            "id": "evt_1",
            "type": "invoice.payment_failed",
            "data": {"object": {"customer": "cus_test"}},
        })
        self.company.stripe_customer_id = "cus_test"
        self.company.save()
        self.client.post(
            reverse("stripe_webhook"),
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t",
            HTTP_HOST="localhost",
        )
        self.company.refresh_from_db()
        self.assertTrue(self.company.grace_until is not None)
        self.assertTrue(self.company.life_cycle == Company.LifeCycle.ACTIVE)
        resp = self.client.get(reverse("smart_home"), HTTP_HOST="localhost")
        self.assertEqual(resp.status_code, 200)
        self.company.grace_until = timezone.now() - timedelta(days=1)
        self.company.life_cycle = Company.LifeCycle.SUSPENDED
        self.company.save()
        resp = self.client.get(reverse("smart_home"), HTTP_HOST="localhost")
        self.assertEqual(resp.status_code, 403)

    @override_settings(STRIPE_WEBHOOK_SECRET="whsec")
    @patch("apps.companies.audit_middleware.conn")
    @patch("stripe.WebhookSignature.verify_header", return_value=True)
    def test_dedup_webhook(self, mock_verify, mock_conn):
        self.company.stripe_customer_id = "cus_dedup"
        self.company.save()
        payload = json.dumps({
            "id": "evt_dup",
            "type": "invoice.payment_failed",
            "data": {"object": {"customer": "cus_dedup"}},
        })
        resp1 = self.client.post(
            reverse("stripe_webhook"),
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t",
            HTTP_HOST="localhost",
        )
        self.assertEqual(resp1.status_code, 200)
        resp2 = self.client.post(
            reverse("stripe_webhook"),
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="t",
            HTTP_HOST="localhost",
        )
        self.assertEqual(resp2.status_code, 409)


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class PlanLimitTests(TestCase):
    def test_user_limit_basic_plan(self):
        company = Company.objects.create(name="FreeCo", plan="basic")
        for i in range(3):
            user = User.objects.create_user(username=f"u{i}")
            user.profile.company = company
            user.profile.save()
        form = TenantUserCreationForm(
            data={
                "username": "u4",
                "email": "u4@example.com",
                "password1": "pass123",
                "password2": "pass123",
                "role": "user",
            },
            company=company,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("limit", str(form.errors))


@override_settings(CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}})
class AuditTasksTests(TestCase):
    def test_prune_audit(self):
        company = Company.objects.create(name="C")
        user = User.objects.create_user(username="u")
        log = AuditLog.objects.create(
            company=company,
            user=user,
            path="/x",
            method="GET",
            status=200,
            ms=1,
        )
        log.timestamp = timezone.now() - timedelta(days=100)
        log.save(update_fields=["timestamp"])
        self.assertEqual(AuditLog.objects.count(), 1)
        purge_audit_logs()
        self.assertEqual(AuditLog.objects.count(), 0)


class SignupFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="new", password="pass")

    def test_signup_requires_auth(self):
        resp = self.client.get(reverse("signup_company"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("basic_login"), resp["Location"])

    def test_create_company_assigns_admin(self):
        self.client.login(username="new", password="pass")
        resp = self.client.post(reverse("signup_company"), {"company_name": "NewCo"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/dashboard/", resp["Location"])
        company = Company.objects.get(name="NewCo")
        self.user.refresh_from_db()
        self.assertEqual(self.user.profile.company, company)
        self.assertEqual(self.user.profile.role, "admin")
        self.assertFalse(company.verified)
        self.assertEqual(company.life_cycle, Company.LifeCycle.SUSPENDED)
