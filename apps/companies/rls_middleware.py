from django.db import connections

class PostgresRLSMiddleware:
    """Set current company for Postgres row-level security."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        company = getattr(request, "company", None)
        conn = connections['default']
        if conn.vendor == 'postgresql':
            cid = str(company.id) if company else ''
            with conn.cursor() as cursor:
                cursor.execute("SET LOCAL secuvast.current_company = %s", [cid])
        return self.get_response(request)
