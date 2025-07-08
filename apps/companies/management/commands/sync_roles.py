from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.conf import settings
from pathlib import Path
import yaml

class Command(BaseCommand):
    help = "Sync default role permissions from role_matrix.yml"

    def handle(self, *args, **options):
        fixture = Path(settings.BASE_DIR) / "fixtures" / "role_matrix.yml"
        if not fixture.exists():
            self.stderr.write("role_matrix.yml not found")
            return
        with open(fixture) as f:
            matrix = yaml.safe_load(f) or {}
        for name, perms in matrix.items():
            group, _ = Group.objects.get_or_create(name=name)
            group.permissions.clear()
            for code in perms:
                app_label, codename = code.split(".")
                try:
                    perm = Permission.objects.get(content_type__app_label=app_label, codename=codename)
                except Permission.DoesNotExist:
                    continue
                group.permissions.add(perm)
        self.stdout.write(self.style.SUCCESS("Roles synced"))
