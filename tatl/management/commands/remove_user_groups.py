from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User, Group
from tatl import models
import sys
import json


class Command(BaseCommand):
    help = "Remove all users from a group, excluding specified users"

    def add_arguments(self, parser):
        parser.add_argument("group", help="Name of the group")
        parser.add_argument(
            "--exclude", nargs="*", default=[], help="Usernames to exclude"
        )

    def handle(self, *args, **options):
        try:
            su = User.objects.get(is_superuser=True)
        except User.DoesNotExist:
            print("[FAIL] No superuser found.")
            sys.exit(1)

        try:
            group = Group.objects.get(name=options["group"])
        except Group.DoesNotExist:
            print("[FAIL] No group with that name.")
            sys.exit(1)

        exclude_users = set(options["exclude"])
        removed_users = []

        for user in User.objects.filter(groups=group):
            if user.username in exclude_users:
                sys.stderr.write("[SKIP] User %s excluded\n" % user.username)
                continue

            user.groups.remove(group)
            removed_users.append(user.username)
            sys.stderr.write(
                "[NOTE] User %s removed from group %s\n" % (user.username, group.name)
            )

        if removed_users:
            treq = models.TatlPermFlex(
                user=su,
                substitute_user=None,
                used_permission="tatl.management.commands.remove_user_groups",
                timestamp=timezone.now(),
                content_object=group,
                extra_context=json.dumps(
                    {
                        "group": group.name,
                        "removed_users": len(removed_users),
                    }
                ),
            )
            treq.save()

        sys.stderr.write(
            "[DONE] Removed %d users from group %s\n" % (len(removed_users), group.name)
        )
