from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

import sys
import json


class Command(BaseCommand):
    help = "Export users with their groups and directly assigned permissions as JSON"

    def add_arguments(self, parser):
        parser.add_argument("--output", "-o", help="Output file path (default: stdout)")

    def handle(self, *args, **options):
        export_data = []

        for user in User.objects.all():
            user_data = {
                "username": user.username,
                "groups": [g.name for g in user.groups.all()],
                "permissions": [perm.codename for perm in user.user_permissions.all()],
            }
            export_data.append(user_data)

        output = json.dumps(export_data, indent=2)

        if options.get("output"):
            with open(options["output"], "w") as f:
                f.write(output)
            sys.stderr.write(
                "[NOTE] Exported %d users to %s\n"
                % (len(export_data), options["output"])
            )
        else:
            print(output)
