from django.core.management.base import BaseCommand
from django.utils.text import slugify
from api.models import Tag, Category

class Command(BaseCommand):
    help = "Populează tabela Tag cu date SEO pentru tag-uri specifice"

    # Array-ul de tag-uri cu SEO
    TAGS = [
        # tag-uri pentru apartamente
        {
            "name": "Boxă",
            "meta_title": "Apartamente și garsoniere cu boxă proprie pentru depozitare",
            "meta_description": "Descoperă apartamente și garsoniere dotate cu boxă proprie pentru depozitare. Oferte ideale pentru cei care au nevoie de spațiu suplimentar organizat și sigur.",
            "description": "Locuințe moderne, precum apartamente și garsoniere, cu boxă proprie inclusă. Perfecte pentru depozitarea obiectelor personale, oferind un plus de confort și funcționalitate.",
            "categories": [
                "Apartamente",
                "Apartamente cu 1 cameră de închiriat",
                "Apartamente cu 1 cameră de vânzare",
                "Apartamente cu 2 camere de închiriat",
                "Apartamente cu 2 camere de vânzare",
                "Apartamente cu 3 camere de închiriat",
                "Apartamente cu 3 camere de vânzare",
                "Apartamente cu 4+ camere de închiriat",
                "Apartamente cu 4+ camere de vânzare",
                "Garsoniere de închiriat",
                "Garsoniere de vânzare"
            ]
        },              
        # tag-uri pentru apartamente, case, vile, spatii comerciale, pensiuni si hoteluri
        {
            "name": "Aer condiționat",
            "meta_title": "Apartamente, case, vile, spatii comerciale, garsoniere cu aer condiționat",
            "meta_description": "Caută apartamente, garsoniere, case, vile sau spații comerciale dotate cu aer condiționat. Găsește locuințe confortabile, ideale pentru zilele toride de vară.",
            "description": "Locuințe și spații comerciale moderne, dotate cu aer condiționat, pentru un confort sporit. Alege dintr-o gamă variată de apartamente, garsoniere, case și vile cu facilități complete.",
            "categories": [
                "Apartamente",
                "Apartamente cu 1 cameră de închiriat",
                "Apartamente cu 1 cameră de vânzare",
                "Apartamente cu 2 camere de închiriat",
                "Apartamente cu 2 camere de vânzare",
                "Apartamente cu 3 camere de închiriat",
                "Apartamente cu 3 camere de vânzare",
                "Apartamente cu 4+ camere de închiriat",
                "Apartamente cu 4+ camere de vânzare",
                "Birouri de închiriat",
                "Birouri de vânzare",
                "Birouri și Spații Comerciale",
                "Case de închiriat",
                "Case de vânzare",
                "Case și Vile",
                "Garsoniere de închiriat",
                "Garsoniere de vânzare",
                "Pensiuni și hoteluri",
                "Spații comerciale de închiriat",
                "Spații comerciale de vânzare"
            ]
        },
        {
            "name": "Parcare proprie",
            "meta_title": "Apartamente, case, vile, spatii comerciale, garsoniere cu locuri de parcare proprii",
            "meta_description": "Alege o locuință, apartament, garsoniera, casa, vila, spatiu comercial cu parcare proprie și beneficiază de un spațiu sigur și accesibil. Descoperă oferte de apartamente cu parcare inclusă.",
            "description": "Apartamente, case, vile, spatii comerciale, garsoniere cu locuri de parcare proprii, accesibile și sigure, în zone centrale și rezidențiale. Oferte pentru toate tipurile de locuințe.",
            "categories": ["Apartamente", "Apartamente cu 1 cameră de închiriat", "Apartamente cu 1 cameră de vânzare", "Apartamente cu 2 camere de închiriat", "Apartamente cu 2 camere de vânzare", "Apartamente cu 3 camere de închiriat", "Apartamente cu 3 camere de vânzare", "Apartamente cu 4+ camere de închiriat", "Apartamente cu 4+ camere de vânzare", "Birouri de închiriat", "Birouri de vânzare", "Birouri și Spații Comerciale", "	Case de închiriat", "Case de vânzare", "Case și Vile", "Garsoniere de închiriat", "Garsoniere de vânzare", "Pensiuni și hoteluri", "Spații comerciale de închiriat", "Spații comerciale de vânzare"]
        },
        {
            "name": "Centrală proprie",
            "meta_title": "Apartamente, case, vile, spatii comerciale, garsoniere cu centrală proprie",
            "meta_description": "Descoperă locuințe moderne cu centrală proprie: apartamente, case, garsoniere și vile pentru un confort termic optim. Oferte diverse în toate zonele.",
            "description": "Proprietăți dotate cu centrală proprie, ideale pentru un consum eficient și un confort termic sporit. Alege dintr-o selecție variată de apartamente, case, vile și spații comerciale.",
            "categories": [
                "Apartamente",
                "Apartamente cu 1 cameră de închiriat",
                "Apartamente cu 1 cameră de vânzare",
                "Apartamente cu 2 camere de închiriat",
                "Apartamente cu 2 camere de vânzare",
                "Apartamente cu 3 camere de închiriat",
                "Apartamente cu 3 camere de vânzare",
                "Apartamente cu 4+ camere de închiriat",
                "Apartamente cu 4+ camere de vânzare",
                "Birouri de închiriat",
                "Birouri de vânzare",
                "Birouri și Spații Comerciale",
                "Case de închiriat",
                "Case de vânzare",
                "Case și Vile",
                "Garsoniere de închiriat",
                "Garsoniere de vânzare",
                "Pensiuni și hoteluri",
                "Spații comerciale de închiriat",
                "Spații comerciale de vânzare"
            ]
        },
        # tag-uri pentru apartamente, case, vile, spatii comerciale
        {
            "name": "Garaj",
            "meta_title": "Apartamente, case, vile, spatii comerciale, garsoniere cu garaj propriu",
            "meta_description": "Găsește locuințe cu garaj propriu: apartamente, case, vile și spații comerciale. Oferte variate pentru un plus de confort și siguranță pentru mașina ta.",
            "description": "Proprietăți cu garaj propriu, perfecte pentru cei care caută un spațiu sigur și practic pentru mașina lor. Descoperă apartamente, garsoniere, case și vile dotate cu garaj în zone atractive.",
            "categories": [
                "Apartamente",
                "Apartamente cu 1 cameră de închiriat",
                "Apartamente cu 1 cameră de vânzare",
                "Apartamente cu 2 camere de închiriat",
                "Apartamente cu 2 camere de vânzare",
                "Apartamente cu 3 camere de închiriat",
                "Apartamente cu 3 camere de vânzare",
                "Apartamente cu 4+ camere de închiriat",
                "Apartamente cu 4+ camere de vânzare",
                "Birouri de închiriat",
                "Birouri de vânzare",
                "Birouri și Spații Comerciale",
                "Case de închiriat",
                "Case de vânzare",
                "Case și Vile",
                "Garsoniere de închiriat",
                "Garsoniere de vânzare",
                "Spații comerciale de închiriat",
                "Spații comerciale de vânzare"
            ]
        },
        # tag-uri pentru case, vile, spatii comerciale, pensiuni si hoteluri
        {
            "name": "Beci",
            "meta_title": "Case, vile și pensiuni cu beci pentru depozitare",
            "meta_description": "Explorează oferte de case, vile și pensiuni dotate cu beci. Ideal pentru depozitare sau amenajări speciale, aceste proprietăți oferă funcționalitate suplimentară.",
            "description": "Proprietăți moderne și tradiționale, precum case, vile și pensiuni, dotate cu beci spațios. Perfect pentru depozitare, păstrarea alimentelor sau alte utilizări personalizate.",
            "categories": [
                "Case de închiriat",
                "Case de vânzare",
                "Case și Vile",
                "Pensiuni și hoteluri"
            ]
        },
        {
            "name": "Piscină",
            "meta_title": "Case, vile și pensiuni cu piscină proprie pentru relaxare",
            "meta_description": "Găsește case, vile și pensiuni dotate cu piscină proprie. Bucură-te de confort, intimitate și relaxare în locuințe exclusiviste cu piscină.",
            "description": "Proprietăți premium, precum case, vile și pensiuni, dotate cu piscină proprie. Oferă un plus de lux și confort, perfecte pentru relaxare și activități recreative.",
            "categories": [
                "Case de închiriat",
                "Case de vânzare",
                "Case și Vile",
                "Pensiuni și hoteluri"
            ]
        },
        # tag-uri pentru terenuri, depozite, hale industriale            
        {
            "name": "Drum asfaltat",
            "meta_title": "Terenuri și proprietăți cu acces la drum asfaltat",
            "meta_description": "Descoperă terenuri și proprietăți, depozite, hale industriale cu acces direct la drum asfaltat. Ideal pentru construcții, agricultură sau activități industriale, cu infrastructură modernă.",
            "description": "Proprietăți și terenuri cu acces la drum asfaltat, depozite, hale industriale perfecte pentru dezvoltare industrială, agricultură sau construcții rezidențiale. Infrastructura asigură acces rapid și facil pentru orice tip de activitate.",
            "categories": [
                "Terenuri",
                "Terenuri agricole",
                "Terenuri industriale",
                "Terenuri pentru construcții",
                "Hale industriale",
                "Depozite"
            ]
        },
        {
            "name": "Utilități disponibile",
            "meta_title": "Terenuri și proprietăți cu utilități disponibile",
            "meta_description": "Găsește terenuri și proprietăți, hale industriale dotate cu utilități disponibile: apă, gaz, curent electric și canalizare. Ideal pentru construcții, agricultură sau activități industriale.",
            "description": "Terenuri și proprietăți, hale industriale cu utilități disponibile, inclusiv apă, gaz, electricitate și canalizare. Aceste oferte sunt perfecte pentru construcții rezidențiale, industriale sau activități agricole.",
            "categories": [
                "Terenuri",
                "Terenuri agricole",
                "Terenuri industriale",
                "Terenuri pentru construcții",
                "Hale industriale",
                "Depozite"
            ]
        }                 
    ]

    def handle(self, *args, **kwargs):
        for tag_data in self.TAGS:
            # Verifică dacă tag-ul există deja
            tag, created = Tag.objects.get_or_create(name=tag_data["name"])

            if created:
                # Dacă tag-ul este creat, completează câmpurile SEO
                tag.slug = slugify(tag_data["name"])
                tag.meta_title = tag_data["meta_title"]
                tag.meta_description = tag_data["meta_description"]
                tag.description = tag_data["description"]

                # Setează statusul la 1 (Activ)
                tag.status = 1

                # Adaugă categoriile necesare
                for category_name in tag_data["categories"]:
                    try:
                        category = Category.objects.get(name=category_name)
                        tag.categories.add(category)
                    except Category.DoesNotExist:
                        print(f"Categoria '{category_name}' nu a fost găsită!")

                # Salvează tag-ul în baza de date
                tag.save()
                self.stdout.write(self.style.SUCCESS(f"Tag-ul '{tag_data['name']}' a fost creat și completat cu succes!"))
            else:
                self.stdout.write(self.style.WARNING(f"Tag-ul '{tag_data['name']}' există deja."))
