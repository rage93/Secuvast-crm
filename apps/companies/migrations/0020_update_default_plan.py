# Generated by Django 4.2.9 on 2025-07-09 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0019_add_company_subscription_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="company",
            name="plan",
            field=models.CharField(default="basic", max_length=50),
        ),
    ]
