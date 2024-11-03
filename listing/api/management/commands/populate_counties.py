from django.core.management.base import BaseCommand
from django.utils.text import slugify
from api.models import County

# Lista de județe din România
judete = [
    "Alba", "Arad", "Argeș", "Bacău", "Bihor", "Bistrița-Năsăud", "Botoșani", "Brașov", "Brăila", "Buzău", 
    "Caraș-Severin", "Călărași", "Cluj", "Constanța", "Covasna", "Dâmbovița", "Dolj", "Galați", "Giurgiu", 
    "Gorj", "Harghita", "Hunedoara", "Ialomița", "Iași", "Ilfov", "Maramureș", "Mehedinți", "Mureș", 
    "Neamț", "Olt", "Prahova", "Satu Mare", "Sălaj", "Sibiu", "Suceava", "Teleorman", "Timiș", "Tulcea", 
    "Vaslui", "Vâlcea", "Vrancea", "București"
]

class Command(BaseCommand):
    help = "Populează tabela County cu județele din România și completează câmpurile SEO"

    def handle(self, *args, **options):
        for judet in judete:
            slug = slugify(judet)
            meta_title = f"Imobiliare {judet} - Anunțuri Gratuite"
            meta_description = f"Anunțuri imobiliare în {judet}: apartamente, case, terenuri și spații comerciale de vânzare și închiriere. Găsește oferte imobiliare actualizate din {judet}."
            description = (
                f"Explorează ofertele imobiliare din {judet}. Descoperă apartamente, case, terenuri și spații comerciale "
                f"de vânzare și închiriere în {judet}. Verifică cele mai recente anunțuri imobiliare și alege "
                f"proprietatea perfectă pentru tine!"
            )
            
            # Creare sau actualizare intrare pentru județ
            County.objects.update_or_create(
                name=judet,
                defaults={
                    'slug': slug,
                    'meta_title': meta_title,
                    'meta_description': meta_description,
                    'description': description,
                }
            )
        
        self.stdout.write(self.style.SUCCESS("Județele din România au fost adăugate cu succes în baza de date."))
