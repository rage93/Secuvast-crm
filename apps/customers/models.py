from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

from apps.companies.models import Company

try:
    from helpers import billing
except Exception:
    class billing:
        @staticmethod
        def create_customer(*args, **kwargs):
            return None


class Customer(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE)
    stripe_id = models.CharField(max_length=120, null=True, blank=True)
    init_email = models.EmailField(blank=True, null=True)
    init_email_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.company.name}"

    def save(self, *args, **kwargs):
        if not self.stripe_id and self.init_email_confirmed and self.init_email:
            email = self.init_email
            if email:
                stripe_id = billing.create_customer(
                    email=email,
                    metadata={"company_id": self.company.id, "company": self.company.name},
                    raw=False,
                )
                self.stripe_id = stripe_id
        super().save(*args, **kwargs)

from allauth.account.signals import email_confirmed
from django.dispatch import receiver


@receiver(email_confirmed)
def allauth_email_confirmed_handler(request, email_address, **kwargs):
    user = email_address.user
    company = getattr(user.profile, 'company', None)
    if not company:
        return
    try:
        customer = Customer.objects.get(company=company)
    except Customer.DoesNotExist:
        return
    if customer.init_email == email_address.email and not customer.init_email_confirmed:
        customer.init_email_confirmed = True
        customer.save()
