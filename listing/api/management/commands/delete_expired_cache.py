import os
import time
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Deletes expired cache files'

    def handle(self, *args, **kwargs):
        cache_dir = settings.CACHES['default']['LOCATION']
        timeout = settings.CACHES['default']['TIMEOUT']  # Timpul de expirare al cache-ului, în secunde

        # Verificăm dacă directorul de cache există
        if os.path.exists(cache_dir):
            current_time = time.time()  # Obține timpul curent în secunde

            # Parcurgem fișierele din directorul de cache
            for filename in os.listdir(cache_dir):
                file_path = os.path.join(cache_dir, filename)

                # Verificăm dacă fișierul este un fișier (nu un director)
                if os.path.isfile(file_path):
                    file_mtime = os.path.getmtime(file_path)  # Obținem timpul ultimei modificări a fișierului

                    # Calculăm diferența de timp dintre timpul curent și ultima modificare a fișierului
                    if current_time - file_mtime > timeout:
                        try:
                            os.remove(file_path)  # Ștergem fișierul
                            self.stdout.write(self.style.SUCCESS(f'Successfully deleted expired cache file: {filename}'))
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'Error deleting file {filename}: {e}'))
        else:
            self.stdout.write(self.style.WARNING(f'Cache directory {cache_dir} does not exist.'))
