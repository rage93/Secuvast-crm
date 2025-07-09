from django.http import HttpResponseRedirect

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
            host_parts = host.split(":", 1)
            base_host = host_parts[0]
            port = ":" + host_parts[1] if len(host_parts) == 2 else ""

            parts = base_host.split(".")
            if parts[0] == "www" and len(parts) > 1:
                base_domain = ".".join(parts[1:])
            elif len(parts) <= 2:
                base_domain = base_host
            else:
                base_domain = ".".join(parts[1:])

            new_host = f"{company.slug_subdomain}.{base_domain}{port}"
            return HttpResponseRedirect(f"//{new_host}{request.get_full_path()}")
        return self.get_response(request)

