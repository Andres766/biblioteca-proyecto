# Generated manually to add Reserva model

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models
import core.models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_reserva', models.DateTimeField(default=django.utils.timezone.now)),
                ('fecha_expiracion', models.DateTimeField(default=core.models.default_expiration)),
                ('atendida', models.BooleanField(default=False)),
                ('libro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to='core.libro')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reservas', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]