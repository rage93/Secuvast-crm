from django.apps import AppConfig

class CompaniesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.companies'

    def ready(self):
        from . import signals  # noqa
        from . import celery_ctx  # noqa
