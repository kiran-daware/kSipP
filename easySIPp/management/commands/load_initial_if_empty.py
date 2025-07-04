from django.core.management.base import BaseCommand
from django.core.management import call_command
from easySIPp.models import UacAppConfig, UasAppConfig

class Command(BaseCommand):
    help = 'Load initial data from fixture only if tables are empty'

    def handle(self, *args, **options):
        uac_exists = UacAppConfig.objects.exists()
        uas_exists = UasAppConfig.objects.exists()

        if not uac_exists or not uas_exists:
            self.stdout.write("Loading initial fixture data...")
            call_command('loaddata', 'initial_data.json')
            self.stdout.write(self.style.SUCCESS("Initial data loaded successfully."))
        else:
            self.stdout.write("Initial data already present, skipping load.")
