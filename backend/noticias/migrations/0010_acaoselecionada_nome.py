# Generated by Django 5.1 on 2024-08-14 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0009_acaoselecionada'),
    ]

    operations = [
        migrations.AddField(
            model_name='acaoselecionada',
            name='nome',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
