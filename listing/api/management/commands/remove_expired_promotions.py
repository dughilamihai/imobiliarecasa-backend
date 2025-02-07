from django.core.management.base import BaseCommand
from django.utils.timezone import now
from api.models import Listing

class Command(BaseCommand):
    help = "Dezactivează promovările expirate"

    def handle(self, *args, **kwargs):
        today = now().date()
        expired_listings = Listing.objects.filter(is_promoted=True, valability_promote_date__lt=today)
        count = expired_listings.update(is_promoted=False)  # Dezactivează promovarea
        self.stdout.write(self.style.SUCCESS(f'{count} anunțuri au fost actualizate ca nefiind promovate.'))
