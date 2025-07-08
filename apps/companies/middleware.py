from django.core.cache import cache
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.db import OperationalError, ProgrammingError

from .models import Company
from .threadlocals import set_current_company


class SubdomainCompanyMiddleware:
    """Attach company object based on subdomain."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        cache_key = f"missing_slug_{subdomain}"
        if cache.get(cache_key):
            request.company = None
            set_current_company(None)
            if subdomain not in ("www", ""):
                return HttpResponseRedirect(reverse("company_not_found"))
            return self.get_response(request)
        try:
            if request.path == reverse("company_healthz"):
                request.company = Company.objects.filter(slug_subdomain=subdomain).first()
            else:
                request.company = Company.objects.get(
                    slug_subdomain=subdomain,
                    life_cycle=Company.LifeCycle.ACTIVE,
                )
        except Company.DoesNotExist:
            cache.set(cache_key, True, 300)
            request.company = None
            if subdomain not in ("www", ""):
                set_current_company(None)
                return HttpResponseRedirect(reverse("company_not_found"))
        except (OperationalError, ProgrammingError):
            # Database isn't ready yet (e.g. migrations pending)
            request.company = None
        set_current_company(request.company)
        return self.get_response(request)
