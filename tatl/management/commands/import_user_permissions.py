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

        assigned_groups = []
        assigned_permissions = []

        for user_data in import_data:
            try:
                user = User.objects.get(username=user_data["username"])
            except User.DoesNotExist:
                sys.stderr.write(
                    "[WARN] User %s not found, skipping\n" % user_data["username"]
                )
                continue

            # Assign groups
            for group_name in user_data.get("groups", []):
                try:
                    group = Group.objects.get(name=group_name)
                    if not user.groups.filter(pk=group.pk).exists():
                        user.groups.add(group)
                        assigned_groups.append(
                            {"username": user.username, "group": group_name}
                        )
                        sys.stderr.write(
                            "[NOTE] User %s added to group %s\n"
                            % (user.username, group_name)
                        )
                except Group.DoesNotExist:
                    sys.stderr.write("[WARN] Group %s not found\n" % group_name)

            # Assign direct permissions
            for perm_codename in user_data.get("permissions", []):
                try:
                    permission = Permission.objects.get(codename=perm_codename)
                    if permission not in user.user_permissions.all():
                        user.user_permissions.add(permission)
                        assigned_permissions.append(
                            {"username": user.username, "permission": perm_codename}
                        )
                        sys.stderr.write(
                            "[NOTE] Permission %s assigned to user %s\n"
                            % (perm_codename, user.username)
                        )
                except Permission.DoesNotExist:
                    sys.stderr.write("[WARN] Permission %s not found\n" % perm_codename)

            user.save()

        if assigned_groups or assigned_permissions:
            treq = models.TatlPermFlex(
                user=su,
                substitute_user=None,
                used_permission="tatl.management.commands.import_user_permissions",
                timestamp=timezone.now(),
                content_object=su,
                extra_context=json.dumps(
                    {
                        "assigned_groups": assigned_groups,
                        "assigned_permissions": assigned_permissions,
                    }
                ),
            )
            treq.save()

        sys.stderr.write(
            "[DONE] Assigned %d groups and %d permissions\n"
            % (len(assigned_groups), len(assigned_permissions))
        )
