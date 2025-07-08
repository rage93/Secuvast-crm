from django.db.models.signals import post_save, pre_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.conf import settings
import yaml
from pathlib import Path
from django.core.exceptions import ValidationError

from .models import Company, AuditLog
from .group_permissions import GROUP_PERMISSIONS
from .threadlocals import get_current_user, get_current_ip

@receiver(post_save, sender=Company)
def create_default_groups(sender, instance, created, **kwargs):
    if created:
        for group_name, perms in GROUP_PERMISSIONS.items():
            group, _ = Group.objects.get_or_create(
                name=f"{instance.slug_subdomain}-{group_name}"
            )
            for perm_code in perms:
                app_label, codename = perm_code.split(".")
                try:
                    perm = Permission.objects.get(
                        content_type__app_label=app_label, codename=codename
                    )
                except Permission.DoesNotExist:
                    continue
                group.permissions.add(perm)


@receiver(post_migrate)
def load_role_fixtures(sender, **kwargs):
    if sender.name != 'companies':
        return
    fixture_path = Path(settings.BASE_DIR) / 'fixtures' / 'role_matrix.yml'
    if not fixture_path.exists():
        return
    with open(fixture_path) as f:
        mapping = yaml.safe_load(f)
    for name, perms in mapping.items():
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.clear()
        for perm_code in perms:
            app_label, codename = perm_code.split('.')
            try:
                perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
            except Permission.DoesNotExist:
                continue
            group.permissions.add(perm)


@receiver(pre_save, sender=Company)
def audit_skip_billing_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = Company.objects.get(pk=instance.pk)
    except Company.DoesNotExist:
        return
    instance._old_state = {
        "life_cycle": previous.life_cycle,
        "ignore_subscription": previous.ignore_subscription,
    }
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
            company_state_before=instance._old_state,
            company_state_after={"ignore_subscription": instance.ignore_subscription},
        )


@receiver(post_save, sender=Company)
def audit_lifecycle_change(sender, instance, created, **kwargs):
    if created or not hasattr(instance, "_old_state"):
        return
    if instance.life_cycle != instance._old_state.get("life_cycle"):
        user = get_current_user()
        AuditLog.objects.create(
            company=instance,
            user=user,
            ip=get_current_ip(),
            path="company.life_cycle",
            method="ADMIN",
            status=0,
            ms=0,
            company_state_before=instance._old_state,
            company_state_after={"life_cycle": instance.life_cycle},
        )


RESERVED_SUBDOMAINS = {"www", "admin", "api"}


@receiver(pre_save, sender=Company)
def validate_slug_unique(sender, instance, **kwargs):
    """Ensure unique, non-reserved subdomains."""
    slug = instance.slug_subdomain.lower()
    if slug in RESERVED_SUBDOMAINS:
        raise ValidationError("Subdominio reservado")
    qs = Company.objects.filter(slug_subdomain__iexact=slug)
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)
    if qs.exists():
        raise ValidationError("Subdominio ya existe")
