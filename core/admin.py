# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Autor, Categoria, Libro, Prestamo, Reserva

# Configuraciones personalizadas para el Admin

class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'rol', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Adicional', {'fields': ('rol',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información Adicional', {'fields': ('rol',)}),
    )

class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('libro', 'usuario', 'fecha_prestamo', 'fecha_devolucion_prevista', 'fecha_devolucion_real')
    list_filter = ('usuario', 'libro')

class LibroAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'estado', 'isbn')
    list_filter = ('estado', 'categoria', 'autor')
    search_fields = ('titulo', 'isbn', 'autor__nombre')

# Registramos los modelos
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(Autor)
admin.site.register(Categoria)
admin.site.register(Libro, LibroAdmin)
admin.site.register(Prestamo, PrestamoAdmin)
admin.site.register(Reserva)