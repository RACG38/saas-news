# Generated by Django 5.1 on 2024-08-12 21:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0007_cliente_plano'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='data_ultimo_pagamento',
            field=models.DateField(blank=True, null=True),
        ),
    ]