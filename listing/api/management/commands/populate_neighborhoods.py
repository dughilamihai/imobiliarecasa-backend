from django.core.management.base import BaseCommand
from django.utils.text import slugify
from api.models import County, City, Neighborhood

# Dicționar cu orașele și cartierele lor relevante
cartiere_orase = {
    "Alba Iulia": [
        "Cetate",
        "Micești",
        "Ștefan Cel Mare",
        "Oarda de Jos",
        "Războieni",
        "Mărăști",
        "Dâmbu Morii"
    ],
    "Aiud": [
        "Centrul Vechi",
        "Măgura",
        "Băgău",
        "Sâncrai",
        "Valea Aiudului"
    ],
    "Blaj": [
        "Centrul Istoric",
        "Călugăreni",
        "Pădurea Gălău",
        "Păcuri",
        "Sâncrai",
        "Lunca",
        "Gura Văii"
    ],
    "Cugir": [
        "Băcșa",
        "Măgura",
        "Ocoliș",
        "Săliștea",
        "Valea Cugirului"
    ],
    "Ocna Mureș": [
        "Sâncel",
        "Bălăușeri",
        "Mureșeni",
        "Sălciva",
        "Valea Ocnei"
    ],
    "Arad": [
        "Centru",
        "Bujac",
        "Micălaca",
        "Aurel Vlaicu",
        "Gai",
        "Sânnicolau Mic",
        "Bătăi",
        "Grădiște"
    ],
    "Ineu": [
        "Centrul Orașului",
        "Măgura",
        "Târnova",
        "Căpâlnaș",
        "Bătrâni"
    ],
    "Lipova": [
        "Băi",
        "Făgăraș",
        "Călărași"
    ],
    "Curtici": [
        "Bătrâni",
        "Pădureni"
    ],
    "Pâncota": [
        "Dâmbău",
        "Vârf"
    ],
    "Pitești": [
        "Centrul Civic",
        "Găvana",
        "Trivale",
        "Prundu",
        "Craiovei",
        "Negru Vodă",
        "Cărămidari"
    ],
    "Mioveni": [
        "Colibași",
        "Bascov",
        "Bărăști",
        "Rătești"
    ],
    "Curtea de Argeș": [
        "Centrul Orașului",
        "Gura Văii",
        "Șerban Vodă",
        "Negru Vodă",
        "Căpâlna"
    ],
    "Câmpulung": [
        "Toma Caragiu",
        "Mărăcineni",
        "Rudăria",
        "Păpușa"
    ],
    "Ștefănești": [
        "Băiculești",
        "Siliștea",
        "Hârtiești"
    ],
    "Bacău": [
        "Centrul Istoric",
        "Bacău Nord",
        "Mărăști",
        "Sărăcău",
        "Canton",
        "Răcăciuni"
    ],
    "Onești": [
        "Centrul Orașului",
        "Ștefan cel Mare",
        "Urziceni",
        "Bălcescu",
        "Dimitrie Cantemir"
    ],
    "Moinești": [
        "Dărmănești",
        "Sănduleni",
        "Ursărie"
    ],
    "Comănești": [
        "Sălătruc",
        "Pârâul Boului"
    ],
    "Buhuși": [
        "Urziceni",
        "Pădureni"
    ],
    "Oradea": [
        "Centrul Istoric",
        "I.C. Brătianu",
        "Crisana",
        "Nufărul",
        "Aleea Ștrandului",
        "Sânmartin",
        "Velența"
    ],
    "Salonta": [
        "Centrul Orașului",
        "Urziceni",
        "Pădurea Neagră"
    ],
    "Marghita": [
        "Centrul Orașului",
        "Măgura",
        "Călugări",
        "Fântâna Albă"
    ],
    "Beiuș": [
        "Centrul Orașului",
        "Huedin",
        "Pădurea Neagră"
    ],
    "Valea lui Mihai": [
        "Sălard",
        "Călinești"
    ],
    "Bistrița": [
        "Centrul Istoric",
        "Unirea",
        "Bistrita-Bârgăului",
        "Viișoara",
        "Dumbrava"
    ],
    "Năsăud": [
        "Centrul Orașului",
        "Pârteș",
        "Băile Figa"
    ],
    "Beclean": [
        "Centrul Orașului",
        "Fântânele",
        "Dărmănești"
    ],
    "Sângeorz-Băi": [
        "Centrul Orașului",
        "Năsăud",
    ],
    "Botoșani": [
        "Centrul Istoric",
        "Mihai Eminescu",
        "Botoșani Nord",
        "Plevna",
        "Săvenii",
        "Darabani"
    ],
    "Dorohoi": [
        "Centrul Orașului",
        "Iazuri",
        "Darabani"
    ],
    "Săveni": [
        "Centrul Orașului",
        "Bălășești",
    ],
    "Darabani": [
        "Centrul Orașului",
        "Sărățeni",
        "Dănilă"
    ],
    "Flămânzi": [
        "Centrul Orașului",
    ],
    "Brașov": [
        "Centrul Istoric",
        "Timișul de Sus",
        "Răcădău",
        "Noua",
        "Săcele",
        "Poiana Brașov"
    ],
    "Făgăraș": [
        "Centrul Orașului",
        "Tichilești",
        "Părău",
        "Sâmbăta de Sus"
    ],
    "Codlea": [
        "Centrul Orașului",
        "Pădurea Codlea",
        "Codlea de Sus"
    ],
    "Râșnov": [
        "Centrul Orașului",
        "Gura Văii",
        "Poiana Râșnov"
    ],
    "Săcele": [
        "Centrul Orașului",
        "Măgura",
        "Bărcut",
        "Târsa"
    ],
    "Brăila": [
        "Centrul Istoric",
        "Brăila Nouă",
        "Cărămidaru",
        "Viziru",
        "Între Bălți"
    ],
    "Ianca": [
        "Centrul Orașului",
        "Rădăuți",
        "Călărași"
    ],
    "Făurei": [
        "Centrul Orașului",
        "Cărbunești",
        "Bălăcița"
    ],
    "Însurăței": [
        "Centrul Orașului",
        "Vădeni",
    ],
    "Buzău": [
        "Centrul Orașului",
        "Micro 14",
        "Dorobanți",
        "Băile Buzăului"
    ],
    "Râmnicu Sărat": [
        "Centrul Orașului",
        "Gura Timișului",
    ],
    "Nehoiu": [
        "Centrul Orașului",
        "Făgăraș",
        "Bălășești"
    ],
    "Pătârlagele": [
        "Centrul Orașului",
    ],
    "Reșița": [
        "Centrul Orașului",
        "Dealul Golului",
        "Lunca Bârzavei",
        "Reșița Nord",
        "Mihai Viteazul"
    ],
    "Caransebeș": [
        "Centrul Orașului",
        "Bocșa",
        "Sânnicolau Mare",
        "Măru"
    ],
    "Bocșa": [
        "Centrul Orașului",
        "Bocșa Română",
        "Bocșa Montană"
    ],
    "Oțelu Roșu": [
        "Centrul Orașului",
    ],
    "Moldova Nouă": [
        "Centrul Orașului",
        "Gârnic"
    ],
    "Călărași": [
        "Centrul Orașului",
        "Bulevardul 1 Mai",
        "Gălășeni",
        "Poșta Veche"
    ],
    "Oltenița": [
        "Centrul Orașului",
        "Neajlov"
    ],
    "Budești": [
        "Centrul Orașului",
    ],
    "Fundulea": [
        "Centrul Orașului",
    ],
    "Cluj-Napoca": [
        "Centrul Istoric",
        "Mărăști",
        "Grigorescu",
        "Zorilor",
        "Gheorgheni"
    ],
    "Turda": [
        "Centrul Orașului",
        "Oprișani",
        "Turda Nouă"
    ],
    "Dej": [
        "Centrul Orașului",
        "Băița"
    ],
    "Câmpia Turzii": [
        "Centrul Orașului",
        "Sâncrai"
    ],
    "Gherla": [
        "Centrul Orașului",
        "Băița"
    ],
    "Constanța": [
        "Centrul Istoric",
        "Mamaia",
        "Tomis Nord",
        "Bdul. Ferdinand",
        "Delfinariu"
    ],
    "Mangalia": [
        "Centrul Orașului",
        "Mangalia Sud",
        "Mangalia Nord",
        "Saturn"
    ],
    "Medgidia": [
        "Centrul Orașului",
        "Mărăști",
        "Mihai Viteazul",
        "Gării"
    ],
    "Năvodari": [
        "Centrul Orașului",
        "Mamaia Sat"
    ],
    "Cernavodă": [
        "Centrul Orașului",
        "Cernavodă Nord"
    ],
    "Sfântu Gheorghe": [
        "Centrul Orașului",
    ],
    "Târgu Secuiesc": [
        "Centrul Orașului",
        "Sânzieni"
    ],
    "Covasna": [
        "Centrul Orașului",
    ],
    "Baraolt": [
        "Centrul Orașului",
    ],
    "Târgoviște": [
        "Centrul Orașului",
        "Răzvan",
        "Vivo",
        "Rocada"
    ],
    "Moreni": [
        "Centrul Orașului",
    ],
    "Pucioasa": [
        "Centrul Orașului",
    ],
    "Găești": [
        "Centrul Orașului",
    ],
    "Titu": [
        "Centrul Orașului",
    ],
    "Craiova": [
        "Calea București",        
        "Centrul Istoric",
        "Bănie",
        "Bucovăț",
        "Craiovița Nouă",
        "Rovine",
        "Răzoare"
    ],
    "Băilești": [
        "Centrul Orașului",
    ],
    "Calafat": [
        "Centrul Orașului",
    ],
    "Filiași": [
        "Centrul Orașului",
    ],
    "Segarcea": [
        "Centrul Orașului",
    ],
    "Galați": [
        "Centrul Orașului",
        "Micro 19",
        "Dunărea",
        "I.C. Frimu",
        "Țiglina"
    ],
    "Tecuci": [
        "Centrul Orașului",
    ],
    "Târgu Bujor": [
        "Centrul Orașului",
    ],
    "Berești": [
        "Centrul Orașului",
    ],
    "Giurgiu": [
        "Centrul Orașului",
    ],
    "Bolintin-Vale": [
        "Centrul Orașului",
    ],
    "Mihăilești": [
        "Centrul Orașului",
    ],
    "Târgu Jiu": [
        "Centrul Orașului",
        "Bârsești",
        "Preajba",
        "Iezureni",
        "Romanești"
    ],
    "Motru": [
        "Centrul Orașului",
    ],
    "Rovinari": [
        "Centrul Orașului",
    ],
    "Târgu Cărbunești": [
        "Centrul Orașului",
    ],
    "Tismana": [
        "Centrul Orașului",
    ],
    "Miercurea Ciuc": [
        "Centrul Orașului",
        "Băile Tușnad",
        "Gălăuțaș"
    ],
    "Odorheiu Secuiesc": [
        "Centrul Orașului",
    ],
    "Gheorgheni": [
        "Centrul Orașului",
    ],
    "Toplița": [
        "Centrul Orașului",
    ],
    "Deva": [
        "Centrul Orașului",
    ],
    "Hunedoara": [
        "Centrul Orașului",
    ],
    "Petroșani": [
        "Centrul Orașului",
    ],
    "Orăștie": [
        "Centrul Orașului",
    ],
    "Vulcan": [
        "Centrul Orașului", 
    ],
    "Slobozia": [
        "Centrul Orașului",
        "Tineretului",
        "Plevna",
        "Brazi",
        "Calea București",
        "Făgăraș",
        "Decebal"
    ],
    "Fetești": [
        "Centrul Orașului",
    ],
    "Urziceni": [
        "Centrul Orașului",
    ],
    "Țăndărei": [
        "Centrul Orașului",
    ],
    "Amara": [
        "Centrul Orașului",
    ],
    "Iași": [
        "Centrul Orașului",
        "Tătărași",
        "Copou",
        "Păcurari",
        "Canta",
        "Dacia",
        "Mircea cel Bătrân"
    ],
    "Pașcani": [
        "Centrul Orașului",
    ],
    "Hârlău": [
        "Centrul Orașului",
    ],
    "Târgu Frumos": [
        "Centrul Orașului",
    ],
    "Buftea": [
        "Centrul Orașului",
    ],
    "Voluntari": [
        "Centrul Orașului",
    ],
    "Otopeni": [
        "Centrul Orașului",
    ],
    "Bragadiru": [
        "Centrul Orașului",
    ],
    "Pantelimon": [
        "Centrul Orașului",
    ],
    "Baia Mare": [
        "Centrul Istoric",
        "Aleea Făget",
        "Valea Roșie",
        "Vivo Mall",
        "Bulevardul Unirii"
    ],
    "Sighetu Marmației": [
        "Centrul Orașului",
        "Mihai Eminescu",
        "Gărdani",
        "Maramureș",
        "George Coșbuc"
    ],
    "Borșa": [
        "Centrul Orașului",
        "Borșa Veche",
        "Lăpușna",
        "Vişeu de Jos"
    ],
    "Vișeu de Sus": [
        "Centrul Orașului",
        "Băița",
        "Săcel",
        "Valea Vișeului"
    ],
    "Drobeta-Turnu Severin": [
        "Centrul Orașului",
        "Băile Herculane",
        "Craiova",
        "Gura Văii"
    ],
    "Orșova": [
        "Centrul Orașului",
        "Tablă",
        "Gura Șușitei"
    ],
    "Strehaia": [
        "Centrul Orașului",
        "Sălcuța"
    ],
    "Vânju Mare": [
        "Centrul Orașului",
        "Pădurea Verde"
    ],
    "Târgu Mureș": [
        "Centrul Orașului",
        "Mureșeni",
        "Sângeorgiu de Mureș",
        "Târgu Mureș Nord"
    ],
    "Reghin": [
        "Centrul Orașului",
        "Măcelarilor",
        "Bălcescu"
    ],
    "Sighișoara": [
        "Centrul Istoric",
        "Piața Cetății",
        "Gura Nandrii",
        "Ulița Mare"
    ],
    "Târnăveni": [
        "Centrul Orașului",
        "Sărățeni"
    ],
    "Luduș": [
        "Centrul Orașului",
        "Cărbunești"
    ],
    "Piatra Neamț": [
        "Centrul Orașului",
        "Dărmănești",
        "Cochilă",
        "Păstrăveni"
    ],
    "Roman": [
        "Centrul Orașului",
        "Ion Ionescu de la Brad",
        "Valea Seacă"
    ],
    "Târgu Neamț": [
        "Centrul Orașului",
        "Bălțătești"
    ],
    "Bicaz": [
        "Centrul Orașului",
        "Izvorul Alb"
    ],
    "Slatina": [
        "Centrul Orașului",
        "Slatina Nord",
        "Slatina Sud",
        "Băile Olănești",
        "Zăvoi"
    ],
    "Caracal": [
        "Centrul Orașului",
        "Vatra",
        "Cozia",
        "Grădina de Est",
        "Sălcuța"
    ],
    "Balș": [
        "Centrul Orașului",
        "Strehaia",
        "Bălcescu"
    ],
    "Corabia": [
        "Centrul Orașului",
        "Corabia Nord",
        "Corabia Sud"
    ],
    "Drăgănești-Olt": [
        "Centrul Orașului",
        "Măgura"
    ],
    "Ploiești": [
        "Centrul Orașului",
        "Cărămidari",
        "Bănești",
        "Plopeni",
        "Cernavodă"
    ],
    "Câmpina": [
        "Centrul Orașului",
        "Câmpina Nord",
        "Câmpina Sud",
        "Ștrand"
    ],
    "Băicoi": [
        "Centrul Orașului",
        "Pietroșani"
    ],
    "Mizil": [
        "Centrul Orașului",
        "Urziceni"
    ],
    "Vălenii de Munte": [
        "Centrul Orașului",
        "Valea Doftanei"
    ],
    "Satu Mare": [
        "Centrul Orașului",
        "Micro 16",
        "Băile Băița",
        "Gării"
    ],
    "Carei": [
        "Centrul Orașului",
        "Centrul Istoric"
    ],
    "Negrești-Oaș": [
        "Centrul Orașului",
        "Băile Negrești"
    ],
    "Ardud": [
        "Centrul Orașului",
    ],
    "Zalău": [
        "Centrul Orașului",
        "Măgura",
        "Stadion",
        "Mihai Viteazu"
    ],
    "Șimleu Silvaniei": [
        "Centrul Orașului",
        "Lupoaica"
    ],
    "Jibou": [
        "Centrul Orașului",
        "Timiș"
    ],
    "Cehu Silvaniei": [
        "Centrul Orașului",
        "Tăuții Măgherăuș"
    ],
    "Sibiu": [
        "Centrul Istoric",
        "Ştrand",
        "Turnul Sfatului",
        "Păltiniș"
    ],
    "Mediaș": [
        "Centrul Orașului",
        "Gura Câlnicului"
    ],
    "Agnita": [
        "Centrul Orașului",
        "Șoarș"
    ],
    "Cisnădie": [
        "Centrul Orașului",
        "Băile Felix"
    ],
    "Copșa Mică": [
        "Centrul Orașului",
        "Centrul Istoric"
    ],
    "Suceava": [
        "Centrul Orașului",
        "Ițcani",
        "Bucovina",
        "Suceava Nouă"
    ],
    "Fălticeni": [
        "Centrul Orașului",
        "Pădureni"
    ],
    "Rădăuți": [
        "Centrul Orașului",
        "Fântâna Mare"
    ],
    "Câmpulung Moldovenesc": [
        "Centrul Orașului",
        "Băița"
    ],
    "Vatra Dornei": [
        "Centrul Orașului",
    ],
   "Alexandria": [
        "Centrul Orașului",
        "Alexandria Nord",
        "Alexandria Sud",
        "Gării"
    ],
    "Turnu Măgurele": [
        "Centrul Orașului",
        "Șoseaua Națională"
    ],
    "Roșiori de Vede": [
        "Centrul Orașului",
        "Calea București"
    ],
    "Zimnicea": [
        "Centrul Orașului",
        "Calea Brăilei"
    ],
    "Videle": [
        "Centrul Orașului",
        "Pădureni"
    ],
    "Timișoara": [
        "Centrul Orașului",
        "Iosefin",
        "Fabric",
        "Dacia",
        "Ghiroda"
    ],
    "Lugoj": [
        "Centrul Orașului",
        "Băile Figa"
    ],
    "Sânnicolau Mare": [
        "Centrul Orașului",
    ],
    "Jimbolia": [
        "Centrul Orașului",
        "Mihai Viteazul"
    ],
    "Buziaș": [
        "Centrul Orașului",
        "Pădurea Verde"
    ],
    "Tulcea": [
        "Centrul Orașului",
        "Nord"
    ],
    "Măcin": [
        "Centrul Orașului",
        "Calea Națională"
    ],
    "Babadag": [
        "Centrul Orașului",
        "Calea Mare"
    ],
    "Isaccea": [
        "Centrul Orașului",
        "Gura Gârluței"
    ],
    "Vaslui": [
        "Centrul Orașului",
        "Bulevardul 1 Decembrie"
    ],
    "Bârlad": [
        "Centrul Orașului",
        "Șoseaua Națională"
    ],
    "Huși": [
        "Centrul Orașului",
        "Calea Moldovei"
    ],
    "Murgeni": [
        "Centrul Orașului",
        "Bulevardul Principal"
    ],
    "Râmnicu Vâlcea": [
        "Centrul Orașului",
        "Știrbei Vodă",
        "Calea lui Traian",
        "Bălcescu",
        "Zăvoi"
    ],
    "Drăgășani": [
        "Centrul Orașului",
        "Gura Văii"
    ],
    "Băile Olănești": [
        "Centrul Orașului",
        "Olănești",
    ],
    "Călimănești": [
        "Centrul Orașului",
        "Căciulata"
    ],
    "Focșani": [
        "Centrul Orașului",
        "Mihai Eminescu",
        "Tineretului",
        "Bulevardul Unirii"
    ],
    "Adjud": [
        "Centrul Orașului",
        "Bulevardul 1 Decembrie"
    ],
    "Mărășești": [
        "Centrul Orașului",
        "Bulevardul 1 Decembrie"
    ],
    "Panciu": [
        "Centrul Orașului",
        "Calea Națională"
    ],
    "Odobești": [
        "Centrul Orașului",
        "Bulevardul Principal"
    ],
    "Sector 1": [
        "Aviatorilor",
        "Domenii",
        "Centrul Vechi",
        "Floreasca"
    ],
    "Sector 2": [
        "Ștefan cel Mare",
        "Popești-Leordeni",
        "Berceni",
        "Colentina"
    ],
    "Sector 3": [
        "Titan",
        "Dristor",
        "Balta Albă",
        "3 August"
    ],
    "Sector 4": [
        "Tineretului",
        "Mărăști",
        "Giurgiului",
        "Vitan"
    ],
    "Sector 5": [
        "Rahova",
        "Ferentari",
        "Cotroceni",
        "Ciorogârla"
    ],
    "Sector 6": [
        "Berceni",
        "Giulești",
        "Crângași",
        "Băneasa"
    ]                                                
}


class Command(BaseCommand):
    help = "Populează tabela Neighborhood cu cartierele relevante pentru fiecare oraș din România și completează câmpurile SEO."

    def handle(self, *args, **options):
        for oras_nume, cartiere in cartiere_orase.items():
            if isinstance(cartiere, dict):  # Verifică dacă este un dicționar pentru sectoare
                for sector, cartiere_sect in cartiere.items():
                    for cartier_nume in cartiere_sect:
                        self.create_or_update_neighborhood(cartier_nume, oras_nume)
            else:  # Pentru orașele care nu au sectoare
                for cartier_nume in cartiere:
                    self.create_or_update_neighborhood(cartier_nume, oras_nume)

    def create_or_update_neighborhood(self, cartier_nume, oras_nume):
        try:
            # Obține orașul din baza de date
            oras = City.objects.get(name=oras_nume)
        except City.DoesNotExist:
            self.stdout.write(self.style.WARNING(f"Orașul {oras_nume} nu există în baza de date."))
            return

        # Generare slug din numele cartierului și numele orașului
        slug = slugify(f"{cartier_nume}-{oras_nume}")
        meta_title = f"Imobiliare {cartier_nume}, {oras_nume} - Anunțuri Gratuite"
        meta_description = (
            f"Anunțuri imobiliare în {cartier_nume}, {oras_nume}: apartamente, case, terenuri și spații comerciale "
            f"de vânzare și închiriere. Găsește oferte actualizate din {cartier_nume}."
        )
        description = (
            f"Explorează anunțurile imobiliare din {cartier_nume}, {oras_nume}. Descoperă proprietăți variate "
            f"de vânzare și închiriere, de la apartamente și case la spații comerciale și terenuri în {cartier_nume}."
        )

        # Creare sau actualizare intrare pentru cartier
        Neighborhood.objects.update_or_create(
            name=cartier_nume,
            city=oras,
            defaults={
                'slug': slug,
                'meta_title': meta_title,
                'meta_description': meta_description,
                'description': description,
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Cartierul {cartier_nume} din orașul {oras_nume} a fost adăugat/actualizat cu succes."))
