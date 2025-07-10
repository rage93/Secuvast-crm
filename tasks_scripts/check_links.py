#!/usr/bin/env python
"""Run the check_links management command via Celery."""
import os
import django
import argparse
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--username')
    parser.add_argument('--start-url', default='/')
    parser.add_argument('--depth', type=int, default=1)
    args = parser.parse_args(argv)

    call_command(
        'check_links',
        username=args.username,
        start_url=args.start_url,
        depth=args.depth,
    )


if __name__ == '__main__':
    main()
