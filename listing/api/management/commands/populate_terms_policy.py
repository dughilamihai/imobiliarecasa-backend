from django.core.management.base import BaseCommand
from django.utils.timezone import now
from api.models import TermsPolicySection

# Structura termenilor și condițiilor
TERMS_POLICY_SECTIONS = [
    {
        "section_number": "1.",
        "title": "Aspecte Generale",
        "content": (
            "<p>Acești Termeni și Condiții reglementează relația dintre Site, și persoanele care utilizează Platforma Imobiliare.casa („Utilizatorii”).</p>"
            "<p>Platforma include site-urile www.imobiliare.casa si aplicațiile mobile disponibile în Google Play și App Store („Aplicația Imobiliare.casa”) și serviciile oferite prin acestea („Serviciile”).</p>"
            "<p>Accesarea și utilizarea Platformei se realizează conform prezentului set de Termeni și Condiții, care include și Politica de Confidențialitate.&nbsp;</p>"
            "<p>Pentru clienții persoane juridice, se aplică și termeni suplimentari în funcție de categoria de utilizator (agenții imobiliare, dezvoltatori, etc.).</p>"
            "<p>Limitarea responsabilității:</p>"
            "<ul><li>Societatea oferă doar infrastructura tehnică pentru publicarea anunțurilor, fără a influența conținutul acestora.</li>"
            "<li>Nu intermediem relațiile dintre vânzători și cumpărători și nu participăm la încheierea contractelor rezultate din utilizarea Platformei.</li></ul>"
            "<p><strong>Acceptarea Termenilor și Condițiilor:</strong></p>"
            "<p>Pentru a utiliza Serviciile, Utilizatorii trebuie să își exprime acordul explicit printr-o acțiune specifică (ex. bifarea casetei „Am citit și sunt de acord cu Termenii și Condițiile”)."
            " Prin utilizarea Platformei, Utilizatorii confirmă că acceptă acești Termeni și Condiții, inclusiv orice actualizare a acestora.</p>"
            "<p><strong>Dacă NU sunteți de acord</strong> cu aceste prevederi, vă rugăm să întrerupeți utilizarea Platformei și a Serviciilor noastre.</p>"
        ),
        "last_updated": "2025-02-16T09:51:32.321086+02:00"
    }
]

class Command(BaseCommand):
    help = "Populează termenii și condițiile în baza de date"

    def handle(self, *args, **kwargs):
        for section in TERMS_POLICY_SECTIONS:
            policy, created = TermsPolicySection.objects.update_or_create(
                section_number=section["section_number"],
                defaults={
                    "title": section["title"],
                    "content": section["content"],
                    "last_updated": section["last_updated"],
                }
            )
            status = "Creat" if created else "Actualizat"
            self.stdout.write(self.style.SUCCESS(f"{status} secțiunea: {policy.section_number} - {policy.title}"))
