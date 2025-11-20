# core/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Usuario, Libro
from django.forms import ClearableFileInput

# Crispy Forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Fieldset, HTML, Field
from django.forms import ClearableFileInput

class CustomUserCreationForm(UserCreationForm):
    """
    Formulario de creación de usuario personalizado que incluye el campo 'rol'.
    """
    class Meta(UserCreationForm.Meta):
        model = Usuario
        fields = UserCreationForm.Meta.fields + ('email', 'rol',)

class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulario de autenticación que permite iniciar sesión con
    nombre de usuario o email en el mismo campo.
    """
    username = forms.CharField(label="Usuario o Email")

    def clean(self):
        # Validación personalizada para permitir login por email o username
        username_input = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username_input or not password:
            # Si faltan datos, delega en la validación estándar para mostrar errores de campos
            return super().clean()

        # Resolver el username real si se ingresó un email
        username_to_use = username_input
        if '@' in username_input:
            User = get_user_model()
            try:
                user_obj = User.objects.get(email=username_input)
                username_to_use = user_obj.username
            except User.DoesNotExist:
                # Si el email no existe, intentar con el input tal cual
                username_to_use = username_input

        from django.contrib.auth import authenticate
        user = authenticate(self.request, username=username_to_use, password=password)
        if user is None:
            raise forms.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
                params={'username': self.fields['username'].label},
            )

        self.confirm_login_allowed(user)
        self.user_cache = user
        return self.cleaned_data

class LibroForm(forms.ModelForm):
    """
    Formulario basado en el modelo Libro.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Placeholders y ayudas
        self.fields['titulo'].widget.attrs.update({'placeholder': 'Ej: Cien años de soledad'})
        self.fields['isbn'].widget.attrs.update({'placeholder': '978XXXXXXXXXX'})
        self.fields['resumen'].widget.attrs.update({'placeholder': 'Sinopsis breve del contenido'})
        self.fields['portada_url'].widget.attrs.update({'placeholder': 'https://.../imagen.jpg'})

        # Organizar con Crispy
        self.helper = FormHelper()
        # No renderizamos el form tag/submit desde crispy; ya están en la plantilla
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                'Datos del Libro',
                Row(
                    Column(Field('titulo'), css_class='col-md-8'),
                    Column(Field('isbn'), css_class='col-md-4'),
                ),
                Row(
                    Column(Field('autor'), css_class='col-md-6'),
                    Column(Field('categoria'), css_class='col-md-6'),
                ),
                Field('resumen'),
            ),
            Fieldset(
                'Portada',
                Row(
                    Column(Field('portada'), css_class='col-md-6'),
                    Column(Field('portada_url'), css_class='col-md-6'),
                ),
                HTML('<small class="text-muted">Sube una imagen o pega una URL. Si ambas existen, se usará la subida.</small>'),
            ),
            Fieldset(
                'Estado',
                Row(Column(Field('estado'), css_class='col-md-4')),
            ),
        )
    class Meta:
        model = Libro
        fields = ['titulo', 'autor', 'categoria', 'isbn', 'resumen', 'portada', 'portada_url', 'estado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'autor': forms.Select(attrs={'class': 'form-select'}),
            'categoria': forms.Select(attrs={'class': 'form-select'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'resumen': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'portada': ClearableFileInput(attrs={'class': 'form-control'}),
            'portada_url': forms.URLInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }