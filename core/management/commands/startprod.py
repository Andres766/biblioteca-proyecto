from django.core.management.base import BaseCommand
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = "Aplica migraciones y crea el superusuario en producción si hay variables disponibles."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("[startprod] Ejecutando migraciones..."))
        call_command('migrate', interactive=False)

        # Crear superusuario si están definidas las variables de entorno
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if username and email and password:
            self.stdout.write(self.style.WARNING("[startprod] Creando superusuario si no existe..."))
            try:
                # createsuperuser --noinput usa las variables anteriores
                call_command('createsuperuser', interactive=False)
                self.stdout.write(self.style.SUCCESS("[startprod] Superusuario verificado/creado."))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"[startprod] Aviso al crear superusuario: {e}"))

        self.stdout.write(self.style.SUCCESS("[startprod] Inicialización de producción completada."))