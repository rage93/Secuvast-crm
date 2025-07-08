from .threadlocals import set_current_user, set_current_ip

class CurrentUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if user and user.is_authenticated:
            set_current_user(user)
        else:
            set_current_user(None)
        set_current_ip(request.META.get('REMOTE_ADDR'))
        return self.get_response(request)
