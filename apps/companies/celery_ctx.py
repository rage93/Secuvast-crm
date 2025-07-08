from celery import signals

from .models import Company
from .threadlocals import set_current_company


@signals.task_prerun.connect
def attach_company(signal=None, headers=None, **kwargs):
    cid = headers.get("company_id") if headers else None
    if cid:
        try:
            set_current_company(Company.objects.get(id=cid))
        except Company.DoesNotExist:
            pass
