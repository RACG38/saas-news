# Generated by Django 5.1 on 2024-09-26 01:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0038_noticia_data_envio'),
    ]

    operations = [
        migrations.RenameField(
            model_name='noticia',
            old_name='data_envio',
            new_name='data_envio_email',
        ),
        migrations.AddField(
            model_name='noticia',
            name='data_envio_whatsapp',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
