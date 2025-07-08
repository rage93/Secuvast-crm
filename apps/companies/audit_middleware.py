import json
from django.utils import timezone
from django_redis import get_redis_connection

try:
    conn = get_redis_connection("default")
except Exception:  # pragma: no cover - fallback for tests
    conn = None

class AuditLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = timezone.now()
        response = self.get_response(request)
        duration = int((timezone.now() - start).total_seconds() * 1000)
        company = getattr(request, 'company', None)
        user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
        data = {
            'company_id': company.id if company else None,
            'user_id': user.id if user else None,
            'path': request.path,
            'ip': request.META.get('REMOTE_ADDR'),
            'method': request.method,
            'status': response.status_code,
            'ms': duration,
        }
        if conn:
            length = conn.rpush("audit_log_buffer", json.dumps(data))
            if length == 1:
                conn.set(
                    "audit_log_buffer_first_ts",
                    int(timezone.now().timestamp()),
                )
        return response
