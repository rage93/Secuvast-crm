from rest_framework.permissions import BasePermission
from django.utils import timezone

class TenantActivePermission(BasePermission):
    """Allow access only for active or grace-period companies."""

    def has_permission(self, request, view):
        company = getattr(request, "company", None)
        if not company:
            return False
        if company.life_cycle == company.LifeCycle.ACTIVE or company.ignore_subscription:
            return True
        if company.grace_until and company.grace_until > timezone.now():
            return True
        return False
