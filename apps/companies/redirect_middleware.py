from django.http import HttpResponseRedirect

class EnsureSubdomainMiddleware:
    """Redirect authenticated users to their company subdomain."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        company = getattr(getattr(user, "profile", None), "company", None)
        if user and user.is_authenticated and company and not getattr(request, "company", None):
            host = request.get_host()
            host_parts = host.split(":", 1)
            base_host = host_parts[0]
            port = ":" + host_parts[1] if len(host_parts) == 2 else ""
            base_domain = ".".join(base_host.split(".")[1:]) or base_host
            new_host = f"{company.slug_subdomain}.{base_domain}{port}"
            return HttpResponseRedirect(f"//{new_host}{request.get_full_path()}")
        return self.get_response(request)

