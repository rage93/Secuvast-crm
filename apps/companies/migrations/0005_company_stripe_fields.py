from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0004_add_subscription_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='stripe_customer_id',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='company',
            name='ignore_subscription',
            field=models.BooleanField(default=False, help_text='Keep company active even if Stripe subscription is inactive'),
        ),
    ]
