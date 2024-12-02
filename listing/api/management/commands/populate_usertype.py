from django.core.management.base import BaseCommand
from api.models import UserType

class Command(BaseCommand):
    help = 'Populează tabela UserType cu tipurile de utilizatori și setările corespunzătoare'

    def handle(self, *args, **kwargs):
        # Definirea valorilor pentru fiecare tip de utilizator
        user_types_data = [
            {
                'type_name': 'bronze',
                'max_ads': 3,
                'background_color': '#FFFFFF',  # Culoare de fundal deschisă
                'price_per_day': 0.00,  # Preț 0 pentru bronze
            },
            {
                'type_name': 'silver',
                'max_ads': 20,
                'background_color': '#C0C0C0',  # Culoare mai închisă pentru silver
                'price_per_day': 0.17,  # Calculăm un preț de 5 $ pe lună (aproximativ 0.17 $ pe zi)
            },
            {
                'type_name': 'gold',
                'max_ads': 50,
                'background_color': '#FFD700',  # Culoare aurie pentru gold
                'price_per_day': 0.33,  # Preț de aproximativ 10 $ pe lună (0.33 $ pe zi)
            },
            {
                'type_name': 'vip',
                'max_ads': 100,
                'background_color': '#FF6347',  # Culoare roșie pentru VIP
                'price_per_day': 0.50,  # Preț de aproximativ 15 $ pe lună (0.50 $ pe zi)
            },
        ]

        # Crearea fiecărui tip de utilizator și salvarea în baza de date
        for user_type_data in user_types_data:
            user_type, created = UserType.objects.get_or_create(
                type_name=user_type_data['type_name'],
                defaults={
                    'max_ads': user_type_data['max_ads'],
                    'background_color': user_type_data['background_color'],
                    'price_per_day': user_type_data['price_per_day']
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Tipul de utilizator '{user_type.type_name}' a fost creat cu succes."))
            else:
                self.stdout.write(self.style.WARNING(f"Tipul de utilizator '{user_type.type_name}' există deja."))
