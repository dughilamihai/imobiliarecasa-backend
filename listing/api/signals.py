from django.db.models.signals import pre_save
from django.dispatch import receiver
from api.models import User
import os

@receiver(pre_save, sender=User)
def delete_old_file_on_update(sender, instance, **kwargs):

    # Verifică dacă utilizatorul există deja
    if instance.pk:
        try:
            old_instance = sender.objects.get(pk=instance.pk)

            # Verifică și șterge fișierul vechi pentru profile_picture
            if old_instance.profile_picture and old_instance.profile_picture != instance.profile_picture:
                if os.path.isfile(old_instance.profile_picture.path):
                    os.remove(old_instance.profile_picture.path)

                # Setează hash-ul la None direct pe instanța 'instance'
                instance.profile_picture_hash = None

            # Verifică și șterge fișierul vechi pentru company_logo
            if old_instance.company_logo and old_instance.company_logo != instance.company_logo:
                if os.path.isfile(old_instance.company_logo.path):
                    os.remove(old_instance.company_logo.path)

                # Setează hash-ul pentru company_logo la None direct pe instanța 'instance'
                instance.company_logo_hash = None

        except sender.DoesNotExist:
            pass


  
