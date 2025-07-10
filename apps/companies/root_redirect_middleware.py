from django.conf import settings
from django.http import HttpResponseRedirect

class RootDomainRedirectMiddleware:
    """Ensure requests use the base domain.

    Older bookmarks might still point to company-specific subdomains.
    This middleware redirects those URLs to the single domain setup
    so session cookies work correctly.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host()
        if ':' in host:
            hostname, port = host.split(':', 1)
            port = ':' + port
        else:
            hostname = host
            port = ''
        base = settings.SAAS_ROOT_DOMAIN
        if hostname not in {base, 'testserver'}:
            return HttpResponseRedirect(f'//{base}{port}{request.get_full_path()}')
        return self.get_response(request)

