# core/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta

# Requisito: Roles (lector / bibliotecario)
class Usuario(AbstractUser):
    ROL_LECTOR = 'lector'
    ROL_BIBLIOTECARIO = 'bibliotecario'
    
    ROLES_CHOICES = [
        (ROL_LECTOR, 'Lector'),
        (ROL_BIBLIOTECARIO, 'Bibliotecario'),
    ]
    
    rol = models.CharField(
        max_length=20,
        choices=ROLES_CHOICES,
        default=ROL_LECTOR,
        help_text='Rol del usuario en el sistema'
    )

# Requisito: CRUD de autores y categorías
class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return self.nombre

# Requisito: CRUD de libros y estado
class Libro(models.Model):
    ESTADO_DISPONIBLE = 'disponible'
    ESTADO_PRESTADO = 'prestado'
    ESTADO_RETRASADO = 'retrasado'
    
    ESTADO_CHOICES = [
        (ESTADO_DISPONIBLE, 'Disponible'),
        (ESTADO_PRESTADO, 'Prestado'),
        (ESTADO_RETRASADO, 'Retrasado'),
    ]

    titulo = models.CharField(max_length=255)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE, related_name='libros')
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='libros')
    
    isbn = models.CharField(max_length=13, unique=True, help_text="ISBN de 13 caracteres")
    resumen = models.TextField(blank=True, null=True)
    # Nueva opción de portada subida como archivo; mantenemos portada_url para compatibilidad
    portada = models.ImageField(upload_to='portadas/', blank=True, null=True)
    portada_url = models.URLField(blank=True, null=True)
    
    estado = models.CharField(
        max_length=15,
        choices=ESTADO_CHOICES,
        default=ESTADO_DISPONIBLE
    )
    
    def __str__(self):
        return self.titulo

# Requisito: Reservas y préstamos con control de fechas
class Prestamo(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='prestamos')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='prestamos')
    
    fecha_prestamo = models.DateTimeField(default=timezone.now)
    fecha_devolucion_prevista = models.DateTimeField()
    fecha_devolucion_real = models.DateTimeField(null=True, blank=True)
    # Permite al bibliotecario marcar retraso manualmente
    retraso_manual = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Préstamo de '{self.libro.titulo}' a {self.usuario.username}"

    @property
    def esta_retrasado(self):
        if self.fecha_devolucion_real:
            return False
        # Si se marcó manualmente, considerar retrasado
        if self.retraso_manual:
            return True
        if timezone.now() > self.fecha_devolucion_prevista:
            return True
            
        return False

# Requisito: Reservas con control de fechas
def default_expiration():
    # La reserva caduca automáticamente en 3 días si no se atiende
    return timezone.now() + timedelta(days=3)

class Reserva(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name='reservas')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reservas')
    fecha_reserva = models.DateTimeField(default=timezone.now)
    fecha_expiracion = models.DateTimeField(default=default_expiration)
    atendida = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserva de '{self.libro.titulo}' por {self.usuario.username}"

    @property
    def activa(self):
        return (not self.atendida) and timezone.now() <= self.fecha_expiracion