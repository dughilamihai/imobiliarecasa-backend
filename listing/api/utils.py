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
