# biblioteca/settings.py
from pathlib import Path
import os
import dj_database_url

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# (Asegúrate de que aquí esté tu propia clave secreta)
SECRET_KEY = 'django-insecure-tu-clave-aqui'

# SECURITY WARNING: don't run with debug turned on in production!
# --- CORRECCIÓN ---
# Asegúrate de que esto esté en True para desarrollo local
DEBUG = True  # se mantiene por defecto para desarrollo

# Si DEBUG es True, ALLOWED_HOSTS puede estar vacío
ALLOWED_HOSTS = []

# Permitir host externo de Render si está presente
RENDER_EXTERNAL_HOSTNAME = os.getenv('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, '.onrender.com']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # --- Mis aplicaciones ---
    'core',
    
    # --- Aplicaciones de Terceros (Añadidas) ---
    'crispy_forms',
    'crispy_bootstrap5',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise para servir estáticos en producción de forma eficiente
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'biblioteca.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'biblioteca.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Si hay DATABASE_URL (p.ej. usando Postgres gratuito externo), usarla
DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )

# En Render (sin DATABASE_URL), usar SQLite y permitir ruta configurable
# - Si defines la variable de entorno SQLITE_PATH, se usará directamente.
# - Si existe el directorio montado '/var/data' (Disk), se guardará en esa ruta.
SQLITE_PATH = os.getenv('SQLITE_PATH')
if os.getenv('RENDER') and not DATABASE_URL:
    if SQLITE_PATH:
        DATABASES['default']['NAME'] = SQLITE_PATH
    elif os.path.isdir('/var/data'):
        DATABASES['default']['NAME'] = '/var/data/db.sqlite3'


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'es'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# --- RUTA DE ESTÁTICOS AÑADIDA ---
STATICFILES_DIRS = [BASE_DIR / 'static']

# Ruta de recolección de estáticos para producción
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Activar almacenamiento comprimido/manifest sólo en producción
if not DEBUG or os.getenv('RENDER'):  # Render establece variables de entorno en prod
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CONFIGURACIONES AÑADIDAS ---

# Modelo de usuario personalizado
AUTH_USER_MODEL = 'core.Usuario'

# Redirecciones de Login/Logout
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# --- CONFIGURACIÓN DE CORREO (Fase 6) ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- Configuración Crispy Forms (Añadida) ---
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- Media (subida de archivos) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'