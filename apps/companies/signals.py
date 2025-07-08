from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import Group

from .models import Company, AuditLog
from .threadlocals import get_current_user, get_current_ip

@receiver(post_save, sender=Company)
def create_default_groups(sender, instance, created, **kwargs):
    if created:
        Group.objects.get_or_create(name=f"{instance.slug_subdomain}-Admin")
        Group.objects.get_or_create(name=f"{instance.slug_subdomain}-User")


@receiver(pre_save, sender=Company)
def audit_skip_billing_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = Company.objects.get(pk=instance.pk)
    except Company.DoesNotExist:
        return
    if previous.ignore_subscription != instance.ignore_subscription:
        user = get_current_user()
        if not user or not user.is_superuser:
            instance.ignore_subscription = previous.ignore_subscription
            return
        AuditLog.objects.create(
            company=instance,
            user=user,
            ip=get_current_ip(),
            path="company.ignore_subscription",
            method="ADMIN",
            status=0,
            ms=0,
        )
