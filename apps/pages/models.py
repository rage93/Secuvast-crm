from django.db import models

from apps.companies.models import CompanyScopedModel


class Product(CompanyScopedModel):
    """Example product scoped to a tenant company."""

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    info = models.CharField(max_length=100, default="")
    price = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.name

