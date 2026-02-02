from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Permission

from majora2 import models
from tatl import models as tmodels
from django.utils import timezone
import datetime

class Command(BaseCommand):
    help = "Load a list of accessions to sync"
    def add_arguments(self, parser):
        parser.add_argument('filename')

    def handle(self, *args, **options):
        su = User.objects.get(is_superuser=True)
        fh = open(options["filename"])
        for line in fh:
            service, cog, primary, secondary, datestamp = line.strip().split('\t')

            tar = None
            try:
                tar = models.TemporaryAccessionRecord.objects.get(service=service, primary_accession=primary)
            except:
                pass

            if tar:
                datestamp = datetime.datetime.strptime(datestamp, "%Y-%m-%d").date()
                tar.public_timestamp = datestamp
                tar.is_public = True # just in case

                if not tar.secondary_accession:
                    # for some reason these seem to be missing
                    tar.secondary_accession = secondary
                tar.save()

        treq = tmodels.TatlPermFlex(
            user = su,
            substitute_user = None,
            used_permission = "majora2.management.commands.cog_load_accessions",
            timestamp = timezone.now(),
        )
        treq.save()