import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Clears the cache directory'

    def handle(self, *args, **kwargs):
        cache_dir = settings.CACHES['default']['LOCATION']

        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            os.makedirs(cache_dir)
        else:
            self.stdout.write(self.style.WARNING(f'Cache directory {cache_dir} does not exist.'))