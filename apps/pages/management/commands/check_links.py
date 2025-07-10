from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client
import re

from apps.companies import audit_middleware

audit_middleware.conn = None

class Command(BaseCommand):
    help = "Crawl internal links and report broken ones"

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            help='Username to login before checking links'
        )
        parser.add_argument(
            '--start-url',
            default='/',
            help='Initial path to crawl'
        )
        parser.add_argument(
            '--depth',
            type=int,
            default=1,
            help='How deep to follow links'
        )

    def handle(self, *args, **options):
        client = Client()
        username = options.get('username')
        if username:
            User = get_user_model()
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stderr.write(self.style.ERROR(f'User {username} not found'))
                return
            client.force_login(user)

        start_url = options['start_url']
        max_depth = options['depth']

        visited = set()
        queue = [(start_url, 0)]

        while queue:
            path, depth = queue.pop(0)
            if path in visited or depth > max_depth:
                continue
            visited.add(path)
            resp = client.get(path)
            status = resp.status_code
            message = f"{status} -> {path}"
            if status >= 400:
                self.stderr.write(message)
            else:
                self.stdout.write(message)
                if depth < max_depth:
                    html = resp.content.decode('utf-8', errors='ignore')
                    for link in re.findall(r'href=[\'\"](/[^\'\"#]+)', html):
                        if link not in visited:
                            queue.append((link, depth + 1))


