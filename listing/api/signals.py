from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver
from api.models import User, ImageHash, Listing
import os
from PIL import Image

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
        
@receiver(pre_delete, sender=Listing)
def delete_files_on_listing_delete(sender, instance, **kwargs):
    # Iterăm prin fiecare câmp foto de la photo1 la photo9
    for i in range(1, 10):
        # Verificăm câmpul foto
        photo_field = getattr(instance, f"photo{i}", None)
        
        if photo_field:
            
            # Căutăm toate instanțele ImageHash care au listing_uuid corespunzător
            image_hashes = ImageHash.objects.filter(listing_uuid=instance.id)  # Găsim toate instanțele

            # Ștergem toate instanțele găsite
            if image_hashes.exists():
                image_hashes.delete()  # Șterge toate instanțele asociate cu listing_uuid
                break  # Oprire buclă după ce am șters toate instanțele    

@receiver(post_save, sender=Listing)
def generate_or_update_thumbnail(sender, instance, created, **kwargs):
    if instance.photo1:  # Asigură-te că există o imagine în photo1
        # Calea completă a imaginii principale
        photo1_path = instance.photo1.path

        # Directorul pentru thumbnail-uri
        media_root = os.path.dirname(photo1_path).rsplit('listings', 1)[0]  # Obține directorul 'media'
        thumbnail_dir = os.path.join(media_root, 'thumbs')
        os.makedirs(thumbnail_dir, exist_ok=True)

        # Numele pentru thumbnail
        thumbnail_name = f"thumb_{os.path.basename(photo1_path)}"
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_name)

        # Generăm thumbnail-ul dacă nu există deja sau dacă s-a schimbat imaginea
        if not os.path.exists(thumbnail_path) or instance.thumbnail.name != os.path.join('thumbs', thumbnail_name):
            with Image.open(photo1_path) as img:
                img.thumbnail((300, 240))  # Dimensiunile pentru thumbnail
                img.save(thumbnail_path, "WEBP", quality=80)

        # Actualizăm câmpul thumbnail cu calea relativă
        relative_thumbnail_path = os.path.join('thumbs', thumbnail_name)  # Director relativ
        if instance.thumbnail.name != relative_thumbnail_path:
            instance.thumbnail.name = relative_thumbnail_path
            instance.save(update_fields=['thumbnail'])

