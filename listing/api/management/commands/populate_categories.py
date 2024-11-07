from django.core.management.base import BaseCommand
from django.utils.text import slugify
from api.models import Category

# Structura categoriilor și subcategoriilor cu titluri, descrieri și texte SEO detaliate
CATEGORIES = [
    {
        "name": "Apartamente",
        "description": "Găsește cele mai bune apartamente de vânzare și închiriere.",
        "custom_text": "Apartamente de vânzare și închiriere în toate zonele orașului, ideale pentru familii, tineri profesioniști și studenți.",
        "subcategories": [
            {"name": "Garsoniere de vânzare", "meta_title": "Garsoniere de vânzare", "meta_description": "Garsoniere de vânzare, perfecte pentru investiții și locuit.",
             "description": "Vezi cele mai bune oferte de garsoniere de vânzare.", 
             "custom_text": "Garsoniere de vânzare în zone centrale și periferice, ideale pentru locuit sau investiții."},
            {"name": "Garsoniere de închiriat", "meta_title": "Garsoniere de închiriat", "meta_description": "Găsește garsoniere de închiriat în diverse locații.",
             "description": "Garsoniere confortabile de închiriat, în diverse locații.",
             "custom_text": "Închirieri de garsoniere pentru studenți, tineri profesioniști sau cupluri în diverse cartiere ale orașului."},
            {"name": "Apartamente cu 1 cameră de vânzare", "meta_title": "Apartamente cu 1 cameră de vânzare", "meta_description": "Descoperă apartamente cu 1 cameră de vânzare.",
             "description": "Cele mai atractive apartamente cu 1 cameră de vânzare.",
             "custom_text": "Apartamente cu 1 cameră, ideale pentru cei aflați la început de drum sau pentru investiții."},
            {"name": "Apartamente cu 1 cameră de închiriat", "meta_title": "Apartamente cu 1 cameră de închiriat", "meta_description": "Închiriază apartamente cu 1 cameră confortabile.",
             "description": "Găsește apartamente cu 1 cameră de închiriat la prețuri accesibile.",
             "custom_text": "Închirieri de apartamente cu 1 cameră, potrivite pentru studenți și tineri profesioniști."},
            {"name": "Apartamente cu 2 camere de vânzare", "meta_title": "Apartamente cu 2 camere de vânzare", "meta_description": "Apartamente cu 2 camere de vânzare, ideale pentru familii mici.",
             "description": "Vezi cele mai bune oferte de apartamente cu 2 camere de vânzare.",
             "custom_text": "Apartamente cu 2 camere de vânzare, perfecte pentru familii și cupluri."},
            {"name": "Apartamente cu 2 camere de închiriat", "meta_title": "Apartamente cu 2 camere de închiriat", "meta_description": "Închiriază apartamente cu 2 camere în orașul tău.",
             "description": "Apartamente confortabile cu 2 camere de închiriat.",
             "custom_text": "Închirieri apartamente cu 2 camere, ideale pentru familii mici sau cupluri."},
            {"name": "Apartamente cu 3 camere de vânzare", "meta_title": "Apartamente cu 3 camere de vânzare", "meta_description": "Găsește apartamente spațioase cu 3 camere de vânzare.",
             "description": "Apartamente cu 3 camere de vânzare, ideale pentru familii numeroase.",
             "custom_text": "Apartamente mari, cu 3 camere, perfecte pentru familii numeroase."},
            {"name": "Apartamente cu 3 camere de închiriat", "meta_title": "Apartamente cu 3 camere de închiriat", "meta_description": "Închiriază apartamente spațioase cu 3 camere.",
             "description": "Apartamente cu 3 camere de închiriat, confortabile și spațioase.",
             "custom_text": "Apartamente cu 3 camere de închiriat, excelente pentru familii."},
            {"name": "Apartamente cu 4+ camere de vânzare", "meta_title": "Apartamente cu 4+ camere de vânzare", "meta_description": "Apartamente mari cu 4+ camere de vânzare.",
             "description": "Apartamente spațioase cu 4+ camere de vânzare pentru familii mari.",
             "custom_text": "Apartamente de lux cu 4 sau mai multe camere, ideale pentru familii mari."},
            {"name": "Apartamente cu 4+ camere de închiriat", "meta_title": "Apartamente cu 4+ camere de închiriat", "meta_description": "Închiriază apartamente spațioase cu 4+ camere.",
             "description": "Apartamente de închiriat cu 4+ camere, perfecte pentru spații de locuit generoase.",
             "custom_text": "Închirieri apartamente mari, cu 4 sau mai multe camere, pentru spațiu și confort."}
        ]
    },
    # Repetăm structura similar pentru alte categorii, cum ar fi Case și Vile, Terenuri etc.
    {
        "name": "Case și Vile",
        "description": "Case și vile de vânzare și închiriat în zone urbane și rurale.",
        "custom_text": "Găsește casa sau vila ideală pentru tine, disponibile atât la vânzare cât și la închiriere.",
        "subcategories": [
            {"name": "Case de vânzare", "meta_title": "Case de vânzare", "meta_description": "Case de vânzare în toate locațiile.",
             "description": "Case de vânzare la prețuri variate, pentru fiecare preferință.",
             "custom_text": "Case de vânzare, ideale pentru familii sau investiții de lungă durată."},
            {"name": "Case de închiriat", "meta_title": "Case de închiriat", "meta_description": "Case de închiriat pentru fiecare buget.",
             "description": "Închirieri case confortabile, în locații excelente.",
             "custom_text": "Închiriază o casă spațioasă în orașul tău sau la periferie."}
        ]
    }
    # Continuăm pentru Terenuri, Birouri și Spații Comerciale, Alte proprietăți etc.
]

class Command(BaseCommand):
    help = "Populează tabela Category cu categoriile și subcategoriile de imobiliare, incluzând meta_title, meta_description, description și custom_text."

    def handle(self, *args, **kwargs):
        for category_data in CATEGORIES:
            # Creăm categoria părinte
            parent_category, created = Category.objects.get_or_create(
                name=category_data["name"],
                defaults={
                    "slug": slugify(category_data["name"]),
                    "meta_title": category_data["name"],
                    "meta_description": f"{category_data['name']} disponibile pentru vânzare și închiriere.",
                    "description": category_data["description"],
                    "custom_text": category_data["custom_text"]
                }
            )
            
            # Parcurgem fiecare subcategorie
            for subcategory_data in category_data["subcategories"]:
                subcategory, created = Category.objects.get_or_create(
                    name=subcategory_data["name"],
                    parent=parent_category,
                    defaults={
                        "slug": slugify(subcategory_data["name"]),
                        "meta_title": subcategory_data["meta_title"],
                        "meta_description": subcategory_data["meta_description"],
                        "description": subcategory_data["description"],
                        "custom_text": subcategory_data["custom_text"]
                    }
                )
                
                # Mesaj de confirmare
                action = "Creată" if created else "Există deja"
                self.stdout.write(self.style.SUCCESS(f"{action} subcategoria: {subcategory.name} în categoria {parent_category.name}"))
        
        self.stdout.write(self.style.SUCCESS("Popularea categoriilor și subcategoriilor a fost realizată cu succes."))
