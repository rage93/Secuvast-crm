from .models import Company
from .threadlocals import set_current_company


class SubdomainCompanyMiddleware:
    """Attach company object based on subdomain."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]
        try:
            request.company = Company.objects.get(
                slug_subdomain=subdomain,
                is_active=True,
            )
        except Company.DoesNotExist:
            request.company = None
        set_current_company(request.company)
        return self.get_response(request)
