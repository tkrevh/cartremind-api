from django.core.management.base import BaseCommand
from djbraintree.models import BTPlan

class Command(BaseCommand):

    def handle(self, *args, **options):
        BTPlan.objects.sync_with_bt()