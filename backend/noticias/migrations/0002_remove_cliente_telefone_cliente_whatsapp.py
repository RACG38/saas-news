# Generated by Django 5.1 on 2024-08-11 07:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cliente',
            name='telefone',
        ),
        migrations.AddField(
            model_name='cliente',
            name='whatsapp',
            field=models.CharField(blank=True, max_length=11),
        ),
    ]