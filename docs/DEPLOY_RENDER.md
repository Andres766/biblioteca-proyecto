# Despliegue en Render: Autenticación y Persistencia

Esta guía cubre los pasos necesarios para asegurar que los flujos de **inicio de sesión** y **registro** funcionen correctamente en producción (Render) y que los datos se almacenen de forma persistente.

## Errores comunes y diagnóstico

- Error típico tras un deploy: `ProgrammingError: relation "core_usuario" does not exist`.
  - Causa: faltan migraciones aplicadas en la base de datos de producción.

- Diagnóstico rápido:
  - Visita `GET /health/db/`.
    - Devuelve `{ "status": "ok", "engine": "..." }` si la BD responde y las tablas existen.
    - Devuelve `status=500` si hay problemas (migraciones faltantes, credenciales inválidas, etc.).

## Base de datos en producción

- Recomendado: usar `DATABASE_URL` hacia PostgreSQL (Neon, Supabase, ElephantSQL, Railway).
- Alternativa: SQLite en Render (sin disco persistente en plan gratuito, los datos se pierden al reiniciar/deploy).

### Variables de entorno sugeridas

- `SECRET_KEY`: clave secreta propia y segura.
- `RENDER_EXTERNAL_HOSTNAME`: Render la define; usada para `ALLOWED_HOSTS`.
- `DATABASE_URL`: si usas PostgreSQL externo.
- `DEBUG=False`: recomendado en producción.

## Migraciones en producción

Ejecuta las migraciones antes de probar login/registro:

```bash
python manage.py migrate
```

Para automatizar, configura el Start Command en Render:

```bash
python manage.py migrate && gunicorn biblioteca.wsgi:application --bind 0.0.0.0:$PORT
```

## Crear Superusuario

Interactivo:

```bash
python manage.py createsuperuser
```

No interactivo (variables de entorno):

```bash
export DJANGO_SUPERUSER_USERNAME=admin
export DJANGO_SUPERUSER_EMAIL=admin@example.com
export DJANGO_SUPERUSER_PASSWORD=<tu_password>
python manage.py createsuperuser --noinput
```

## Verificación de autenticación

1. Accede a `/admin/` y entra con el superusuario.
2. Registra un lector en `/registrar/` y verifica que se crea en Admin.
3. Inicia sesión en `/login/` usando usuario o email; tras login redirige a `libro_list` (lectores) o `dashboard_bibliotecario`.
4. Si falla:
   - Revisa `/health/db/`.
   - Revisa logs de Render.
   - Confirma `DATABASE_URL` y que `python manage.py migrate` fue ejecutado.