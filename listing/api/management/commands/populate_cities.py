from django.core.management.base import BaseCommand
from django.utils.text import slugify
from api.models import County, City

# Dicționar cu județele și lista de orașe relevante
oras_judete = {
    "Alba": ["Alba Iulia", "Aiud", "Blaj", "Cugir", "Ocna Mureș"],
    "Arad": ["Arad", "Ineu", "Lipova", "Curtici", "Pâncota"],
    "Argeș": ["Pitești", "Mioveni", "Curtea de Argeș", "Câmpulung", "Ștefănești"],
    "Bacău": ["Bacău", "Onești", "Moinești", "Comănești", "Buhuși"],
    "Bihor": ["Oradea", "Salonta", "Marghita", "Beiuș", "Valea lui Mihai"],
    "Bistrița-Năsăud": ["Bistrița", "Năsăud", "Beclean", "Sângeorz-Băi"],
    "Botoșani": ["Botoșani", "Dorohoi", "Săveni", "Darabani", "Flămânzi"],
    "Brașov": ["Brașov", "Făgăraș", "Codlea", "Râșnov", "Săcele"],
    "Brăila": ["Brăila", "Ianca", "Făurei", "Însurăței"],
    "Buzău": ["Buzău", "Râmnicu Sărat", "Nehoiu", "Pătârlagele"],
    "Caraș-Severin": ["Reșița", "Caransebeș", "Bocșa", "Oțelu Roșu", "Moldova Nouă"],
    "Călărași": ["Călărași", "Oltenița", "Budești", "Fundulea"],
    "Cluj": ["Cluj-Napoca", "Turda", "Dej", "Câmpia Turzii", "Gherla"],
    "Constanța": ["Constanța", "Mangalia", "Medgidia", "Năvodari", "Cernavodă"],
    "Covasna": ["Sfântu Gheorghe", "Târgu Secuiesc", "Covasna", "Baraolt"],
    "Dâmbovița": ["Târgoviște", "Moreni", "Pucioasa", "Găești", "Titu"],
    "Dolj": ["Craiova", "Băilești", "Calafat", "Filiași", "Segarcea"],
    "Galați": ["Galați", "Tecuci", "Târgu Bujor", "Berești"],
    "Giurgiu": ["Giurgiu", "Bolintin-Vale", "Mihăilești"],
    "Gorj": ["Târgu Jiu", "Motru", "Rovinari", "Târgu Cărbunești", "Tismana"],
    "Harghita": ["Miercurea Ciuc", "Odorheiu Secuiesc", "Gheorgheni", "Toplița"],
    "Hunedoara": ["Deva", "Hunedoara", "Petroșani", "Orăștie", "Vulcan"],
    "Ialomița": ["Slobozia", "Fetești", "Urziceni", "Țăndărei", "Amara"],
    "Iași": ["Iași", "Pașcani", "Hârlău", "Târgu Frumos"],
    "Ilfov": ["Buftea", "Voluntari", "Otopeni", "Bragadiru", "Pantelimon"],
    "Maramureș": ["Baia Mare", "Sighetu Marmației", "Borșa", "Vișeu de Sus"],
    "Mehedinți": ["Drobeta-Turnu Severin", "Orșova", "Strehaia", "Vânju Mare"],
    "Mureș": ["Târgu Mureș", "Reghin", "Sighișoara", "Târnăveni", "Luduș"],
    "Neamț": ["Piatra Neamț", "Roman", "Târgu Neamț", "Bicaz"],
    "Olt": ["Slatina", "Caracal", "Balș", "Corabia", "Drăgănești-Olt"],
    "Prahova": ["Ploiești", "Câmpina", "Băicoi", "Mizil", "Vălenii de Munte"],
    "Satu Mare": ["Satu Mare", "Carei", "Negrești-Oaș", "Ardud"],
    "Sălaj": ["Zalău", "Șimleu Silvaniei", "Jibou", "Cehu Silvaniei"],
    "Sibiu": ["Sibiu", "Mediaș", "Agnita", "Cisnădie", "Copșa Mică"],
    "Suceava": ["Suceava", "Fălticeni", "Rădăuți", "Câmpulung Moldovenesc", "Vatra Dornei"],
    "Teleorman": ["Alexandria", "Turnu Măgurele", "Roșiori de Vede", "Zimnicea", "Videle"],
    "Timiș": ["Timișoara", "Lugoj", "Sânnicolau Mare", "Jimbolia", "Buziaș"],
    "Tulcea": ["Tulcea", "Măcin", "Babadag", "Isaccea"],
    "Vaslui": ["Vaslui", "Bârlad", "Huși", "Murgeni"],
    "Vâlcea": ["Râmnicu Vâlcea", "Drăgășani", "Băile Olănești", "Călimănești"],
    "Vrancea": ["Focșani", "Adjud", "Mărășești", "Panciu", "Odobești"],
    "București": ["Sector 1", "Sector 2", "Sector 3", "Sector 4", "Sector 5", "Sector 6"]
}

class Command(BaseCommand):
    help = "Populează tabela City cu orașele relevante pentru fiecare județ din România și completează câmpurile SEO."

    def handle(self, *args, **options):
        for judet_nume, orase in oras_judete.items():
            try:
                # Obține județul din baza de date
                judet = County.objects.get(name=judet_nume)
            except County.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Județul {judet_nume} nu există în baza de date."))
                continue

            for oras_nume in orase:
                # Generare slug și câmpuri SEO
                slug = slugify(oras_nume)
                meta_title = f"Imobiliare {oras_nume}, {judet_nume} - Anunțuri Gratuite"
                meta_description = (
                    f"Anunțuri imobiliare în {oras_nume}, {judet_nume}: apartamente, case, terenuri și spații comerciale "
                    f"de vânzare și închiriere. Găsește oferte actualizate din {oras_nume}."
                )
                description = (
                    f"Explorează anunțurile imobiliare din {oras_nume}, {judet_nume}. Descoperă proprietăți variate "
                    f"de vânzare și închiriere, de la apartamente și case la spații comerciale și terenuri."
                )

                # Creare sau actualizare intrare pentru oraș
                City.objects.update_or_create(
                    name=oras_nume,
                    county=judet,
                    defaults={
                        'slug': slug,
                        'meta_title': meta_title,
                        'meta_description': meta_description,
                        'description': description,
                    }
                )

        self.stdout.write(self.style.SUCCESS("Orașele relevante au fost adăugate cu succes în baza de date."))
