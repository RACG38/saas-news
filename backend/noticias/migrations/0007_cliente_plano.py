# Generated by Django 5.1 on 2024-08-12 05:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0006_plano_valor'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='plano',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
