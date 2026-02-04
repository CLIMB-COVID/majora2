from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from tatl import models
import sys
import json


class Command(BaseCommand):
    help = (
        "Remove directly assigned permissions from all users, excluding specified users"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "permissions", nargs="+", help="Permission codenames to remove"
        )
        parser.add_argument(
            "--exclude", nargs="*", default=[], help="Usernames to exclude"
        )

    def handle(self, *args, **options):
        try:
            su = User.objects.get(is_superuser=True)
        except User.DoesNotExist:
            print("[FAIL] No superuser found.")
            sys.exit(1)

        permissions_to_remove = []

        for p in options["permissions"]:
            try:
                permission = Permission.objects.get(codename=p)
                permissions_to_remove.append(permission)
            except Permission.DoesNotExist:
                sys.stderr.write("[WARN] No permission with name %s\n" % p)

        if not permissions_to_remove:
            print("[FAIL] No valid permissions specified.")
            sys.exit(1)

        exclude_users = set(options["exclude"])
        removed_users = []

        for user in User.objects.all():
            if user.username in exclude_users:
                sys.stderr.write("[SKIP] User %s excluded\n" % user.username)
                continue

            user_perms_removed = []
            for perm in permissions_to_remove:
                if perm in user.user_permissions.all():
                    user.user_permissions.remove(perm)
                    user_perms_removed.append(perm.codename)

            if user_perms_removed:
                removed_users.append(user.username)
                sys.stderr.write(
                    "[NOTE] Removed permissions %s from user %s\n"
                    % (user_perms_removed, user.username)
                )

        if removed_users:
            treq = models.TatlPermFlex(
                user=su,
                substitute_user=None,
                used_permission="tatl.management.commands.remove_user_permissions",
                timestamp=timezone.now(),
                content_object=su,
                extra_context=json.dumps(
                    {
                        "permissions": [p.codename for p in permissions_to_remove],
                        "affected_users": len(removed_users),
                    }
                ),
            )
            treq.save()

        sys.stderr.write(
            "[DONE] Removed permissions from %d users\n" % len(removed_users)
        )
