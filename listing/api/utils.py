# for sending messages
from django.core.mail import send_mail
from django.template.loader import get_template

# for hashing
import hashlib

# for similar listings
from django.db.models import Q
from django.db.models.functions import Abs
from django.db.models import F
from .models import Listing

def send_confirmation_email(email, token_id, user_id):
    data = {
        'token_id': str(token_id),
        'user_id': str(user_id)
    }
    message = get_template('confirmation_email.txt').render(data)
    send_mail(subject = 'Va rugam sa confirmatia dresa de email',
              message = message,
              from_email = 'contact@imobiliare.casa',
              recipient_list=[email],
              fail_silently= True)
    print("Email-ul de confirmarea  fost trimis catre " + email)
    
def get_similar_listings(listing_id):
    try:
        # Preia anunțul original
        listing = Listing.objects.get(id=listing_id)
    except Listing.DoesNotExist:
        return None

    # Filtre de bază
    filters = Q(is_active_by_user=True) & Q(status=1) & Q(city=listing.city) & Q(category=listing.category)

    # Include neighborhood dacă există
    primary_filters = filters
    if listing.neighborhood:
        primary_filters &= Q(neighborhood=listing.neighborhood)

    # Caută anunțuri care respectă toate condițiile, inclusiv neighborhood
    # Nu tine cont de scorul combinat
    # similar_listings = list(
    #     Listing.objects.filter(primary_filters)
    #     .annotate(
    #         price_diff=Abs(listing.price - F('price')),
    #         surface_diff=Abs(listing.suprafata_utila - F('suprafata_utila')),
    #         year_diff=Abs(listing.year_of_construction - F('year_of_construction'))
    #     )
    #     .exclude(id=listing.id)  # Exclude anunțul original
    #     .order_by('price_diff', 'surface_diff', 'year_diff')[:4]
    # )
    
    # Caută anunțuri care respectă toate condițiile, inclusiv neighborhood
    similar_listings = list(
    Listing.objects.filter(primary_filters)
    .annotate(
        price_diff=Abs(listing.price - F('price')),
        surface_diff=Abs(listing.suprafata_utila - F('suprafata_utila')),
        year_diff=Abs(listing.year_of_construction - F('year_of_construction')),
        # Calculăm un scor combinat
        total_score=F('price_diff') + F('surface_diff') + F('year_diff')
    )
    .exclude(id=listing.id)  # Exclude anunțul original
    .order_by('total_score')[:4]  # Ordonează după scor total
)

    # Dacă nu sunt suficiente rezultate, completează fără neighborhood
    if len(similar_listings) < 4:
        # Pregătește lista ID-urilor deja incluse
        included_ids = [listing.id for listing in similar_listings]
        
        fallback_filters = filters  # Ignoră neighborhood
        fallback_listings = (
            Listing.objects.filter(fallback_filters)
            .exclude(id__in=included_ids)  # Exclude anunțurile deja incluse
            .annotate(
                price_diff=Abs(listing.price - F('price')),
                surface_diff=Abs(listing.suprafata_utila - F('suprafata_utila')),
                year_diff=Abs(listing.year_of_construction - F('year_of_construction'))
            )
            .exclude(id=listing.id)  # Exclude anunțul original
            .order_by('price_diff', 'surface_diff', 'year_diff')[:4 - len(similar_listings)]
        )

        # Completează rezultatele
        similar_listings += list(fallback_listings)

    return similar_listings

    
def generate_hash(image_file):
    """
    Generare hash pe baza conținutului fișierului.
    """
    if not image_file:
        return None  # Dacă fișierul nu există, returnează None

    # Asigură-te că fișierul este deschis corect pentru citire binară
    image_file.open('rb')  # Deschide fișierul pentru citirea binară
    try:
        hash_value = hashlib.md5(image_file.read()).hexdigest()
    finally:
        image_file.seek(0)  # Reface poziția cursorului înainte de redimensionare
    return hash_value


