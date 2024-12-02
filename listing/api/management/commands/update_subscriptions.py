from django.core.management.base import BaseCommand
from django.utils.timezone import now
from api.models import UserSubscription, UserType

class Command(BaseCommand):
    help = 'Actualizează abonamentele expirate și setează utilizatorii la tipul bronze'

    def handle(self, *args, **kwargs):
        # Obține tipul "bronze"
        try:
            bronze_type = UserType.objects.get(type_name='bronze')
        except UserType.DoesNotExist:
            self.stderr.write("Tipul 'bronze' nu există. Adaugă-l înainte să rulezi acest script.")
            return

        # Selectează abonamentele expirate
        expired_subscriptions = UserSubscription.objects.filter(
            end_date__lt=now(),
            is_active_field=True  # Numai cele active
        )

        # Actualizează utilizatorii expirați
        updated_count = 0
        for subscription in expired_subscriptions:
            subscription.user_type = bronze_type
            subscription.end_date = None  # Abonament nelimitat
            subscription.is_active_field = False  # Dezactivează abonamentul
            subscription.save()
            updated_count += 1
            self.stdout.write(f"Actualizat utilizatorul {subscription.user.email} la tipul 'bronze'.")

        self.stdout.write(f"Au fost actualizate {updated_count} abonamente expirate.")
