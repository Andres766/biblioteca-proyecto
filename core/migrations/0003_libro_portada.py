from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_reserva'),
    ]

    operations = [
        migrations.AddField(
            model_name='libro',
            name='portada',
            field=models.ImageField(upload_to='portadas/', blank=True, null=True),
        ),
    ]