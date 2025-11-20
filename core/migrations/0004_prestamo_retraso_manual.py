from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_libro_portada'),
    ]

    operations = [
        migrations.AddField(
            model_name='prestamo',
            name='retraso_manual',
            field=models.BooleanField(default=False),
        ),
    ]