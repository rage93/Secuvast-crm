from django.http import HttpResponseRedirect
from django.conf import settings

class EnsureSubdomainMiddleware:
    """Redirect authenticated users to their company subdomain."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        company = getattr(getattr(user, "profile", None), "company", None)

        if (
            user
            and user.is_authenticated
            and company
            and not getattr(request, "company", None)
            and not user.is_superuser
            and not user.has_perm("companies.bypass_tenant_scope")
        ):

            host = request.get_host()
            port = ""
            if ":" in host:
                port = ":" + host.split(":", 1)[1]

            base_domain = settings.SAAS_ROOT_DOMAIN
            new_host = f"{company.slug_subdomain}.{base_domain}{port}"
            return HttpResponseRedirect(f"//{new_host}{request.get_full_path()}")
        return self.get_response(request)

