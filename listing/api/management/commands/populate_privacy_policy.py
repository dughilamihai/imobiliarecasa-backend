from django.core.management.base import BaseCommand
from django.utils.timezone import now
from api.models import PrivacyPolicySection

# Structura politicii de confidențialitate
PRIVACY_POLICY_SECTIONS = [
    {
        "section_number": "1.",
        "title": "Politica De Confidențialitate A Datelor",
        "content": (
            "Societatea colectează și prelucrează date cu caracter personal ale Utilizatorilor atunci când aceștia "
            "accesează Platforma Imobiliare.casa sau utilizează serviciile noastre. Prezenta Politică de Confidențialitate "
            "explică tipurile de date colectate, modul în care sunt utilizate, drepturile dvs. privind prelucrarea acestora "
            "și măsurile luate pentru protecția lor, în conformitate cu Regulamentul (UE) 2016/679 (\"GDPR\").<br/>"
            "Vă recomandăm să citiți această Politică înainte de a utiliza Platforma Imobiliare.casa sau serviciile noastre "
            "pentru a înțelege cum vă sunt prelucrate datele. Dacă aveți întrebări sau nelămuriri, vă rugăm să ne contactați."
        )
    },
    {
        "section_number": "2.",
        "title": "Cine este responsabil de prelucrarea datelor dvs.?",
        "content": (
            "<p>Societatea este operatorul datelor cu caracter personal, conform legislației privind protecția datelor "
            "cu caracter personal inclusiv GDPR, în ceea ce privește datele cu caracter personal ale Utilizatorilor "
            "colectate și prelucrate prin intermediul Platformei imobiliare.casa.</p>"
            "<p>Pentru activitatea de prelucrare a datelor cu caracter personal Societatea și-a desemnat un responsabil "
            "cu protecția datelor (Data Protection Officer sau DPO) care poate fi contactat folosind următoarele date "
            "de contact:</p>"
            "<p><strong>Email: dpo@imobiliare.casa</strong></p>"
        )
    }
]

class Command(BaseCommand):
    help = "Populează politica de confidențialitate în baza de date"

    def handle(self, *args, **kwargs):
        for section in PRIVACY_POLICY_SECTIONS:
            policy, created = PrivacyPolicySection.objects.update_or_create(
                section_number=section["section_number"],
                defaults={
                    "title": section["title"],
                    "content": section["content"],
                    "last_updated": now(),
                }
            )
            status = "Creat" if created else "Actualizat"
            self.stdout.write(self.style.SUCCESS(f"{status} secțiunea: {policy.section_number} - {policy.title}"))
