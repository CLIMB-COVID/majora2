from django.core.management.base import BaseCommand, CommandError

from majora2 import models
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from django.contrib.auth.forms import PasswordResetForm
from django.conf import settings

import sys

class Command(BaseCommand):
    help = "Force a password reset for a user"
    def add_arguments(self, parser):
        parser.add_argument('username')

    def handle(self, *args, **options):
        u = None
        try:
            u = User.objects.get(username=options["username"])
        except Exception as e:
            print("User does not exist.")
            sys.exit(1)

        form = PasswordResetForm({'email': u.email})
        if form.is_valid():
            request = HttpRequest()
            request.META['SERVER_PORT'] = '443'
            request.META['SERVER_NAME'] = settings.ALLOWED_HOSTS[-1]
            form.save(request=request, use_https=True)
            print("[GOOD] %s reset sent to %s successfully" % (u.username, u.email))