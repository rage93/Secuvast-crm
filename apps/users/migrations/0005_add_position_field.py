from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_add_suspended_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='position',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
