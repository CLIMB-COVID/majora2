from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User, Permission, Group
from tatl import models
import sys
import json


class Command(BaseCommand):
    help = "Import users with their groups and permissions from JSON export"

    def add_arguments(self, parser):
        parser.add_argument("input", help="Input JSON file path")

    def handle(self, *args, **options):
        try:
            su = User.objects.get(is_superuser=True)
        except User.DoesNotExist:
            print("[FAIL] No superuser found.")
            sys.exit(1)

        try:
            with open(options["input"], "r") as f:
                import_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print("[FAIL] Could not read input file: %s" % e)
            sys.exit(1)

        altered_users = []

        for user_data in import_data:
            try:
                user = User.objects.get(username=user_data["username"])
            except User.DoesNotExist:
                sys.stderr.write(
                    "[WARN] User %s not found, skipping\n" % user_data["username"]
                )
                continue

            # User groups
            user_groups = []
            for group_name in user_data.get("groups", []):
                try:
                    group = Group.objects.get(name=group_name)
                    user_groups.append(group)
                except Group.DoesNotExist:
                    sys.stderr.write("[WARN] Group %s not found\n" % group_name)

            # Direct permissions
            user_permissions = []
            for perm_codename in user_data.get("permissions", []):
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    user_permissions.append(permission)
                except Permission.DoesNotExist:
                    sys.stderr.write("[WARN] Permission %s not found\n" % perm_codename)

            # Assign the groups and permissions to the user
            user.groups.set(user_groups)
            user.user_permissions.set(user_permissions)

            if user_groups or user_permissions:
                altered_users.append(user.username)
                sys.stderr.write(
                    "[NOTE] Updated user %s: %d groups, %d permissions\n"
                    % (user.username, len(user_groups), len(user_permissions))
                )

        if altered_users:
            treq = models.TatlPermFlex(
                user=su,
                substitute_user=None,
                used_permission="tatl.management.commands.import_user_permissions",
                timestamp=timezone.now(),
                content_object=su,
                extra_context=json.dumps({"altered_users": len(altered_users)}),
            )
            treq.save()

        sys.stderr.write(
            "[DONE] Assigned groups and permissions to %d users\n" % len(altered_users)
        )
