# Generated by Django 4.2.9 on 2025-07-09 18:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0018_add_verified_field"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="stripe_subscription_id",
            field=models.CharField(
                blank=True,
                help_text="Latest Stripe subscription",
                max_length=255,
                null=True,
            ),
        ),
    ]
