from functools import wraps
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone


def company_active_required(view_func):
    """Ensure the current company has an active subscription."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        company = getattr(request, "company", None)
        if company and (
            company.life_cycle == company.LifeCycle.ACTIVE
            or company.ignore_subscription
            or (company.grace_until and company.grace_until > timezone.now())
        ):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden()

    return _wrapped


def active_user_required(view_func):
    """Block access if user profile is suspended."""

    check = user_passes_test(
        lambda u: getattr(getattr(u, "profile", None), "role", "user") != "suspended"
    )
    return check(view_func)
