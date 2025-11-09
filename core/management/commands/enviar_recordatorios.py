# core/management/commands/enviar_recordatorios.py

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from core.models import Prestamo, Usuario

class Command(BaseCommand):
    """
    Comando de gestión para enviar recordatorios de préstamos que vencen mañana.
    """
    help = 'Envía recordatorios por correo para préstamos que vencen mañana.'

    def handle(self, *args, **options):
        # 1. Definir la fecha de "mañana"
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # 2. Buscar préstamos que vencen mañana Y no han sido devueltos
        prestamos_a_vencer = Prestamo.objects.filter(
            fecha_devolucion_prevista__date=tomorrow,
            fecha_devolucion_real__isnull=True
        ).select_related('usuario', 'libro') # .select_related optimiza la consulta

        if not prestamos_a_vencer.exists():
            self.stdout.write(self.style.SUCCESS('No hay préstamos que vencen mañana.'))
            return

        self.stdout.write(f'Enviando {prestamos_a_vencer.count()} recordatorio(s)...')
        
        # 3. Recorrer y enviar correo a cada uno
        count_exitosos = 0
        for prestamo in prestamos_a_vencer:
            usuario = prestamo.usuario
            libro = prestamo.libro
            
            try:
                send_mail(
                    subject='Recordatorio de Vencimiento - Biblioteca Digital',
                    message=(
                        f'Hola {usuario.first_name or usuario.username},\n\n'
                        f'Este es un recordatorio amigable de que tu préstamo del libro: "{libro.titulo}" vence mañana, {tomorrow.strftime("%Y-%m-%d")}.\n\n'
                        'Por favor, recuerda devolverlo a tiempo para evitar sanciones.\n\n'
                        '¡Gracias por usar la Biblioteca Digital!'
                    ),
                    from_email='noreply@biblioteca.com',
                    recipient_list=[usuario.email],
                    fail_silently=False,
                )
                self.stdout.write(self.style.SUCCESS(f'Correo enviado a {usuario.email} por el libro "{libro.titulo}"'))
                count_exitosos += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error enviando correo a {usuario.email}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'\nProceso completado. {count_exitosos} correos enviados.'))