from .threadlocals import set_current_company

class UserCompanyMiddleware:
    """Attach company based on authenticated user's profile."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            request.company = getattr(getattr(user, 'profile', None), 'company', None)
        else:
            request.company = None
        set_current_company(request.company)
        return self.get_response(request)
