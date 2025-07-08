from django.db import migrations


def enable_rls(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("ALTER TABLE companies_company ENABLE ROW LEVEL SECURITY;")
            cursor.execute("CREATE POLICY company_isolation ON companies_company USING (id::text = current_setting('secuvast.current_company'));")

def disable_rls(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("DROP POLICY IF EXISTS company_isolation ON companies_company;")
            cursor.execute("ALTER TABLE companies_company DISABLE ROW LEVEL SECURITY;")

class Migration(migrations.Migration):
    dependencies = [
        ('companies', '0015_add_row_version_and_constraints'),
    ]

    operations = [
        migrations.RunPython(enable_rls, disable_rls),
    ]
