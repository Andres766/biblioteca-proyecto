# core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URLs de Autenticación
    path('registrar/', views.RegistrarUsuarioView.as_view(), name='registrar'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    # Salud de BD
    path('health/db/', views.db_health, name='db_health'),
    
    # URLs de Dashboards
    path('dashboard/bibliotecario/', views.DashboardView.as_view(), name='dashboard_bibliotecario'),
    path('dashboard/lector/', views.dashboard_lector, name='dashboard_lector'),
    
    # URLs del CRUD DE LIBROS (Catálogo ahora en /libros/)
    path('libros/', views.LibroListView.as_view(), name='libro_list'),
    path('libros/<int:pk>/', views.LibroDetailView.as_view(), name='libro_detail'),
    path('libros/nuevo/', views.LibroCreateView.as_view(), name='libro_create'),
    path('libros/<int:pk>/editar/', views.LibroUpdateView.as_view(), name='libro_update'),
    path('libros/<int:pk>/eliminar/', views.LibroDeleteView.as_view(), name='libro_delete'),
    
    # --- URLs DE PRÉSTAMOS ---
    path('prestamos/crear/<int:libro_pk>/', views.CrearPrestamoView.as_view(), name='prestamo_crear'),
    path('prestamos/mis-prestamos/', views.MisPrestamosListView.as_view(), name='mis_prestamos'),
    path('prestamos/gestion/', views.GestionPrestamosListView.as_view(), name='gestion_prestamos'),
    path('prestamos/devolver/<int:prestamo_pk>/', views.DevolverLibroView.as_view(), name='prestamo_devolver'),
    path('prestamos/marcar-retrasado/<int:prestamo_pk>/', views.MarcarPrestamoRetrasadoView.as_view(), name='prestamo_marcar_retrasado'),
    
    # --- URLs DE REPORTES ---
    path('reportes/libros-excel/', views.exportar_libros_excel, name='reporte_libros_excel'),
    path('reportes/prestamos-pdf/', views.exportar_prestamos_pdf, name='reporte_prestamos_pdf'),
    path('reportes/libros-csv/', views.exportar_libros_csv, name='reporte_libros_csv'),
    path('reportes/prestamos-csv/', views.exportar_prestamos_csv, name='reporte_prestamos_csv'),

    # --- URLs DE RESERVAS ---
    path('reservas/crear/<int:libro_pk>/', views.CrearReservaView.as_view(), name='reserva_crear'),
    path('reservas/mis/', views.MisReservasListView.as_view(), name='mis_reservas'),

    # --- URLs CRUD de Autor/Categoría ---
    path('autores/', views.AutorListView.as_view(), name='autor_list'),
    path('autores/nuevo/', views.AutorCreateView.as_view(), name='autor_create'),
    path('autores/<int:pk>/editar/', views.AutorUpdateView.as_view(), name='autor_update'),
    path('autores/<int:pk>/eliminar/', views.AutorDeleteView.as_view(), name='autor_delete'),

    path('categorias/', views.CategoriaListView.as_view(), name='categoria_list'),
    path('categorias/nueva/', views.CategoriaCreateView.as_view(), name='categoria_create'),
    path('categorias/<int:pk>/editar/', views.CategoriaUpdateView.as_view(), name='categoria_update'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaDeleteView.as_view(), name='categoria_delete'),

    # URL de inicio (AHORA ES LA NUEVA HOME)
    path('', views.HomeView.as_view(), name='home'),
]