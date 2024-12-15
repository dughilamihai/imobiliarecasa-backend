from django.core.management.base import BaseCommand
from api.models import Category

class Command(BaseCommand):
    help = "Populează câmpul group pentru toate categoriile și subcategoriile."

    def handle(self, *args, **kwargs):
        # Obține categoriile principale (fără părinte)
        root_categories = Category.objects.filter(parent__isnull=True)

        for root_category in root_categories:
            group = root_category.group
            if group is None:
                self.stdout.write(f"Categoria '{root_category.name}' nu are un grup asignat.")
                continue

            # Actualizează subcategoriile cu grupul categoriei principale
            self.update_subcategories_group(root_category, group)
            self.stdout.write(f"Grupul {group} a fost asignat subcategoriilor pentru '{root_category.name}'.")

    def update_subcategories_group(self, category, group):
        # Actualizează subcategoria și toate subcategoriile ei
        subcategories = Category.objects.filter(parent=category)
        for subcategory in subcategories:
            subcategory.group = group
            subcategory.save()
            self.update_subcategories_group(subcategory, group)  # Recursiv pentru nivele mai adânci
