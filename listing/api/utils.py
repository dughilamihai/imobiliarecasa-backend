# for sending messages
from django.core.mail import send_mail
from django.template.loader import get_template

# for hashing
import hashlib

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

MONTHS_RO = {
    "January": "ianuarie",
    "February": "februarie",
    "March": "martie",
    "April": "aprilie",
    "May": "mai",
    "June": "iunie",
    "July": "iulie",
    "August": "august",
    "September": "septembrie",
    "October": "octombrie",
    "November": "noiembrie",
    "December": "decembrie",
}

# Definim opțiunile pentru etaj
FLOOR_CHOICES = [
    (0, 'Demisol'),
    (1, 'Parter'),
    (2, 'Etaj 1'),
    (3, 'Etaj 2'),
    (4, 'Etaj 3'),
    (5, 'Etaj 4'),
    (6, 'Etaj 5'),
    (7, 'Etaj 6'),
    (8, 'Etaj 7'),
    (9, 'Etaj 8'),
    (10, 'Etaj 9'),
    (11, 'Etaj 10'),
    (12, 'Etaj 11'),
    (13, 'Etaj 12'),
    (14, 'Etaj 13'),
    (15, 'Etaj 14'),
    (16, 'Etaj 15'),
    (17, 'Etaj 16'),
    (18, 'Etaj 17'),
    (19, 'Etaj 18'),
    (20, 'Etaj 19'),
    (21, 'Etaj 20'),
    (22, 'Mansarda'),
    (23, 'Ultimele 2 etaje'),
]
