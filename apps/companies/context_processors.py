from django.core.cache import cache
from django.conf import settings
from .models import Company
from .plans import PLAN_LIMITS

def company_brand(request):
    company = getattr(request, "company", None)
    if not company:
        return {"company_brand": None, "plan_usage": None}
    limit = PLAN_LIMITS.get(company.plan, {}).get("users")
    cache_key = f"company_user_count:{company.id}"
    used = cache.get(cache_key)
    if used is None:
        used = company.profiles.count()
        cache.set(cache_key, used, timeout=300)
    return {
        "company_brand": {
            "logo": company.logo.url if company.logo else "",
            "primary_color": company.primary_color,
        },
        "plan_usage": {"used": used, "limit": limit},
    }


def root_domain(request):
    return {"root_domain": settings.SAAS_ROOT_DOMAIN}
