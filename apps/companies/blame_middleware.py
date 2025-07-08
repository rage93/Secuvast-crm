import uuid
from sentry_sdk import set_tag

class BlameMiddleware:
    """Attach request and company info to Sentry scope."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = str(uuid.uuid4())
        company = getattr(request, "company", None)
        set_tag("request_id", request_id)
        if company:
            set_tag("company_id", company.id)
        response = self.get_response(request)
        return response
