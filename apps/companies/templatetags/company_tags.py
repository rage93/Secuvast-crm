from django import template
from apps.companies.models import Company

register = template.Library()

@register.simple_tag
def active_companies():
    return Company.objects.filter(life_cycle=Company.LifeCycle.ACTIVE).order_by("name")
