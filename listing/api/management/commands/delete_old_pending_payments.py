from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta
from api.models import Payment

class Command(BaseCommand):
    help = "Șterge plățile cu status 'pending' mai vechi de 24 de ore."

    def handle(self, *args, **kwargs):
        one_day_ago = now() - timedelta(days=1)
        Payment.objects.filter(status='pending', created_at__lt=one_day_ago).delete()