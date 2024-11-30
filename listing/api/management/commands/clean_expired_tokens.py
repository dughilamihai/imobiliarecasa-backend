from django.utils.timezone import now
from django.core.management.base import BaseCommand
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

class Command(BaseCommand):
    help = "Curăță token-urile expirate din tabelă."

    def handle(self, *args, **kwargs):
        # timezone.now() obține un datetime aware
        tokens_deleted, _ = OutstandingToken.objects.filter(expires_at__lt=now()).delete()
        self.stdout.write(f"{tokens_deleted} token-uri expirate au fost șterse.")
