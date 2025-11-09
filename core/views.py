# core/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.views.generic import (
    CreateView, ListView, DetailView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, LibroForm, CustomAuthenticationForm
from .models import Usuario, Libro, Autor, Categoria, Prestamo, Reserva
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.views import View
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
import json

# --- IMPORTACIONES PARA REPORTES ---
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# --- IMPORTACIÓN PARA CORREO ---
from django.core.mail import send_mail


# --- MIXIN DE SEGURIDAD (Para Clases) ---

class BibliotecarioRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.rol == Usuario.ROL_BIBLIOTECARIO
    def handle_no_permission(self):
        return redirect('dashboard_lector')

# --- DECORADOR (Para Funciones) ---
bibliotecario_required = user_passes_test(lambda u: u.is_authenticated and u.rol == Usuario.ROL_BIBLIOTECARIO, login_url='dashboard_lector')


# --- VISTA DE INICIO (NUEVA) ---
class HomeView(TemplateView):
    template_name = 'home.html'


# --- Vistas de Autenticación ---

class RegistrarUsuarioView(CreateView):
    model = Usuario
    form_class = CustomUserCreationForm
    template_name = 'registration/registrar.html' 
    success_url = reverse_lazy('login') 

class CustomLoginView(LoginView):
    template_name = 'registration/login.html' 
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, 'Inicio de sesión correcto. ¡Bienvenido!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Credenciales inválidas. Revisa tu usuario y contraseña.')
        return super().form_invalid(form)

    def get_success_url(self):
        usuario = self.request.user
        if usuario.rol == Usuario.ROL_BIBLIOTECARIO:
            return reverse_lazy('dashboard_bibliotecario') 
        else:
            # --- LÍNEA MODIFICADA ---
            return reverse_lazy('libro_list') # Antes 'dashboard_lector'

def custom_logout_view(request):
    logout(request)
    return redirect('login') 

# --- Vistas de Dashboards ---

class DashboardView(BibliotecarioRequiredMixin, TemplateView):
    template_name = 'dashboards/dashboard_bibliotecario.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_libros'] = Libro.objects.count()
        context['total_lectores'] = Usuario.objects.filter(rol=Usuario.ROL_LECTOR).count()
        context['total_prestamos_activos'] = Prestamo.objects.filter(fecha_devolucion_real__isnull=True).count()
        prestamos_por_mes = Prestamo.objects.annotate(
            mes=TruncMonth('fecha_prestamo')
        ).values('mes').annotate(total=Count('id')).order_by('mes')
        labels_meses = [p['mes'].strftime('%b %Y') for p in prestamos_por_mes]
        data_meses = [p['total'] for p in prestamos_por_mes]
        context['chart_meses_labels'] = json.dumps(labels_meses)
        context['chart_meses_data'] = json.dumps(data_meses)
        top_libros = Libro.objects.annotate(
            num_prestamos=Count('prestamos')
        ).filter(num_prestamos__gt=0).order_by('-num_prestamos')[:5]
        labels_libros = [libro.titulo for libro in top_libros]
        data_libros = [libro.num_prestamos for libro in top_libros]
        context['chart_libros_labels'] = json.dumps(labels_libros)
        context['chart_libros_data'] = json.dumps(data_libros)
        return context

def dashboard_lector(request):
    return render(request, 'dashboards/dashboard_lector.html')

# --- VISTAS DEL CRUD DE LIBROS ---
class LibroListView(ListView):
    model = Libro
    template_name = 'core/libro_list.html' 
    context_object_name = 'libros' 
    def get_queryset(self):
        qs = Libro.objects.all().select_related('autor', 'categoria')
        q = self.request.GET.get('q')
        estado = self.request.GET.get('estado')
        categoria_id = self.request.GET.get('categoria')
        autor_id = self.request.GET.get('autor')
        if q:
            qs = qs.filter(
                Q(titulo__icontains=q) |
                Q(isbn__icontains=q) |
                Q(autor__nombre__icontains=q)
            )
        if estado:
            qs = qs.filter(estado=estado)
        if categoria_id:
            qs = qs.filter(categoria_id=categoria_id)
        if autor_id:
            qs = qs.filter(autor_id=autor_id)
        return qs.order_by('titulo')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.all().order_by('nombre')
        context['autores'] = Autor.objects.all().order_by('nombre')
        context['selected'] = {
            'q': self.request.GET.get('q', ''),
            'estado': self.request.GET.get('estado', ''),
            'categoria': self.request.GET.get('categoria', ''),
            'autor': self.request.GET.get('autor', ''),
        }
        return context
class LibroDetailView(DetailView):
    model = Libro
    template_name = 'core/libro_detail.html'
    context_object_name = 'libro'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        usuario_bloqueado = False
        if usuario.is_authenticated and usuario.rol == Usuario.ROL_LECTOR:
            usuario_bloqueado = Prestamo.objects.filter(
                usuario=usuario,
                fecha_devolucion_real__isnull=True,
                fecha_devolucion_prevista__lt=timezone.now()
            ).exists()
        context['usuario_bloqueado'] = usuario_bloqueado
        context['puede_reservar'] = self.object.estado != Libro.ESTADO_DISPONIBLE
        return context
class LibroCreateView(BibliotecarioRequiredMixin, CreateView):
    model = Libro
    form_class = LibroForm 
    template_name = 'core/libro_form.html'
    success_url = reverse_lazy('libro_list') 
class LibroUpdateView(BibliotecarioRequiredMixin, UpdateView):
    model = Libro
    form_class = LibroForm
    template_name = 'core/libro_form.html'
    success_url = reverse_lazy('libro_list')
class LibroDeleteView(BibliotecarioRequiredMixin, DeleteView):
    model = Libro
    template_name = 'core/libro_confirm_delete.html'
    success_url = reverse_lazy('libro_list')

# --- VISTAS CRUD DE AUTOR Y CATEGORÍA (UI pública para bibliotecario) ---
class AutorListView(BibliotecarioRequiredMixin, ListView):
    model = Autor
    template_name = 'core/autor_list.html'
    context_object_name = 'autores'
    def get_queryset(self):
        qs = Autor.objects.all().order_by('nombre')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

class AutorCreateView(BibliotecarioRequiredMixin, CreateView):
    model = Autor
    fields = ['nombre']
    template_name = 'core/autor_form.html'
    success_url = reverse_lazy('autor_list')

class AutorUpdateView(BibliotecarioRequiredMixin, UpdateView):
    model = Autor
    fields = ['nombre']
    template_name = 'core/autor_form.html'
    success_url = reverse_lazy('autor_list')

class AutorDeleteView(BibliotecarioRequiredMixin, DeleteView):
    model = Autor
    template_name = 'core/autor_confirm_delete.html'
    success_url = reverse_lazy('autor_list')

class CategoriaListView(BibliotecarioRequiredMixin, ListView):
    model = Categoria
    template_name = 'core/categoria_list.html'
    context_object_name = 'categorias'
    def get_queryset(self):
        qs = Categoria.objects.all().order_by('nombre')
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(nombre__icontains=q)
        return qs

class CategoriaCreateView(BibliotecarioRequiredMixin, CreateView):
    model = Categoria
    fields = ['nombre']
    template_name = 'core/categoria_form.html'
    success_url = reverse_lazy('categoria_list')

class CategoriaUpdateView(BibliotecarioRequiredMixin, UpdateView):
    model = Categoria
    fields = ['nombre']
    template_name = 'core/categoria_form.html'
    success_url = reverse_lazy('categoria_list')

class CategoriaDeleteView(BibliotecarioRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'core/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria_list')

# --- VISTAS DE PRÉSTAMOS ---
class CrearPrestamoView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        libro_pk = self.kwargs.get('libro_pk')
        libro = Libro.objects.get(pk=libro_pk)
        # Bloqueo por sanción: si el usuario tiene retrasos activos, no puede pedir
        tiene_retraso = Prestamo.objects.filter(
            usuario=request.user,
            fecha_devolucion_real__isnull=True,
            fecha_devolucion_prevista__lt=timezone.now()
        ).exists()
        if tiene_retraso:
            messages.error(request, 'No puedes pedir préstamos: tienes sanción activa por retraso.')
            return redirect('libro_detail', pk=libro_pk)
        if libro.estado == Libro.ESTADO_DISPONIBLE:
            fecha_devolucion = timezone.now() + timedelta(days=14) 
            prestamo = Prestamo.objects.create(
                libro=libro,
                usuario=request.user,
                fecha_devolucion_prevista=fecha_devolucion
            )
            libro.estado = Libro.ESTADO_PRESTADO
            libro.save()
            try:
                send_mail(
                    subject='Confirmación de Préstamo - Biblioteca Digital',
                    message=(
                        f'Hola {request.user.first_name or request.user.username},\n\n'
                        f'Te confirmamos que has pedido prestado el libro: "{libro.titulo}".\n'
                        f'La fecha de devolución es: {prestamo.fecha_devolucion_prevista.strftime("%Y-%m-%d")}.\n\n'
                        '¡Gracias por usar la Biblioteca Digital!'
                    ),
                    from_email='noreply@biblioteca.com',
                    recipient_list=[request.user.email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.warning(request, f"Préstamo registrado, pero hubo un error enviando el correo: {e}")
            messages.success(request, f'¡Has pedido prestado "{libro.titulo}" con éxito!')
            return redirect('mis_prestamos')
        else:
            messages.error(request, 'Este libro no está disponible actualmente.')
            return redirect('libro_detail', pk=libro_pk)

class CrearReservaView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        libro_pk = self.kwargs.get('libro_pk')
        libro = Libro.objects.get(pk=libro_pk)
        if libro.estado != Libro.ESTADO_DISPONIBLE:
            # Evitar duplicadas activas del mismo usuario
            ya_reservado = Reserva.objects.filter(libro=libro, usuario=request.user, atendida=False, fecha_expiracion__gt=timezone.now()).exists()
            if ya_reservado:
                messages.info(request, 'Ya tienes una reserva activa de este libro.')
                return redirect('libro_detail', pk=libro_pk)
            Reserva.objects.create(libro=libro, usuario=request.user)
            messages.success(request, 'Reserva creada. Te avisaremos cuando el libro esté disponible.')
            return redirect('mis_reservas')
        else:
            messages.info(request, 'El libro está disponible, puedes pedirlo en préstamo directamente.')
            return redirect('libro_detail', pk=libro_pk)
class MisPrestamosListView(LoginRequiredMixin, ListView):
    model = Prestamo
    template_name = 'core/mis_prestamos.html'
    context_object_name = 'prestamos'
    def get_queryset(self):
        return Prestamo.objects.filter(usuario=self.request.user).order_by('-fecha_prestamo')
class GestionPrestamosListView(BibliotecarioRequiredMixin, ListView):
    model = Prestamo
    template_name = 'core/gestion_prestamos.html'
    context_object_name = 'prestamos'
    def get_queryset(self):
        return Prestamo.objects.all().order_by('fecha_devolucion_real', '-fecha_prestamo')
class DevolverLibroView(BibliotecarioRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        prestamo_pk = self.kwargs.get('prestamo_pk')
        prestamo = Prestamo.objects.get(pk=prestamo_pk)
        prestamo.fecha_devolucion_real = timezone.now()
        prestamo.save()
        prestamo.libro.estado = Libro.ESTADO_DISPONIBLE
        prestamo.libro.save()
        # Notificar la primera reserva activa si existe
        reserva = Reserva.objects.filter(
            libro=prestamo.libro,
            atendida=False,
            fecha_expiracion__gt=timezone.now()
        ).order_by('fecha_reserva').first()
        if reserva:
            try:
                send_mail(
                    subject='Tu reserva está disponible',
                    message=(
                        f'Hola {reserva.usuario.first_name or reserva.usuario.username},\n\n'
                        f'El libro "{prestamo.libro.titulo}" ya está disponible para préstamo. '
                        f'Tienes hasta {reserva.fecha_expiracion.strftime("%Y-%m-%d %H:%M")} para recogerlo.'
                    ),
                    from_email='noreply@biblioteca.com',
                    recipient_list=[reserva.usuario.email],
                    fail_silently=True,
                )
            except Exception:
                pass
            reserva.atendida = True
            reserva.save()
        messages.success(request, f'El libro "{prestamo.libro.titulo}" ha sido devuelto.')
        return redirect('gestion_prestamos')

# --- VISTAS DE REPORTES ---
@bibliotecario_required
def exportar_libros_excel(request):
    # Importación perezosa de pandas para evitar que falle el arranque si no está instalado
    try:
        import pandas as pd
    except ImportError:
        # Si pandas no está disponible, devolvemos el reporte en CSV como alternativa
        return exportar_libros_csv(request)
    libros = Libro.objects.all()
    data = {
        'Título': [libro.titulo for libro in libros],
        'Autor': [str(libro.autor) for libro in libros],
        'Categoría': [str(libro.categoria) for libro in libros],
        'ISBN': [libro.isbn for libro in libros],
        'Estado': [libro.get_estado_display() for libro in libros],
    }
    df = pd.DataFrame(data)
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="reporte_libros.xlsx"'
    df.to_excel(response, index=False)
    return response

@bibliotecario_required
def exportar_prestamos_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_prestamos_activos.pdf"'
    prestamos = Prestamo.objects.filter(fecha_devolucion_real__isnull=True).order_by('fecha_devolucion_prevista')
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    data = [['Libro', 'Usuario (Lector)', 'Fecha Préstamo', 'Devolución Prevista', 'Estado']]
    for prestamo in prestamos:
        estado = "Retrasado" if prestamo.esta_retrasado else "En curso"
        data.append([
            prestamo.libro.titulo,
            prestamo.usuario.username,
            prestamo.fecha_prestamo.strftime('%Y-%m-%d'),
            prestamo.fecha_devolucion_prevista.strftime('%Y-%m-%d'),
            estado
        ])
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ])
    table = Table(data)
    table.setStyle(table_style)
    elements.append(table)
    doc.build(elements)
    return response

# --- VISTAS DE REPORTES CSV ---
@bibliotecario_required
def exportar_libros_csv(request):
    libros = Libro.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_libros.csv"'
    # Generar CSV manualmente para evitar dependencias
    header = 'Titulo,Autor,Categoria,ISBN,Estado\n'
    response.write(header)
    for libro in libros:
        fila = f'{libro.titulo},{libro.autor},{libro.categoria},{libro.isbn},{libro.get_estado_display()}\n'
        response.write(fila)
    return response

@bibliotecario_required
def exportar_prestamos_csv(request):
    prestamos = Prestamo.objects.all().order_by('-fecha_prestamo')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_prestamos.csv"'
    header = 'Libro,Usuario,FechaPrestamo,DevolucionPrevista,DevolucionReal,Retrasado\n'
    response.write(header)
    for p in prestamos:
        retrasado = 'SI' if p.esta_retrasado else 'NO'
        fecha_real = p.fecha_devolucion_real.strftime('%Y-%m-%d') if p.fecha_devolucion_real else ''
        fila = f'{p.libro.titulo},{p.usuario.username},{p.fecha_prestamo.strftime('%Y-%m-%d')},{p.fecha_devolucion_prevista.strftime('%Y-%m-%d')},{fecha_real},{retrasado}\n'
        response.write(fila)
    return response

# --- VISTAS DE RESERVAS ---
class MisReservasListView(LoginRequiredMixin, ListView):
    model = Reserva
    template_name = 'core/mis_reservas.html'
    context_object_name = 'reservas'
    def get_queryset(self):
        return Reserva.objects.filter(usuario=self.request.user).order_by('-fecha_reserva')