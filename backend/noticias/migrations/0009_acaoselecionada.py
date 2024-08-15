# Generated by Django 5.1 on 2024-08-13 16:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0008_cliente_data_ultimo_pagamento'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcaoSelecionada',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('simbolo', models.CharField(max_length=10)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='acoes_selecionadas', to='noticias.cliente')),
            ],
        ),
    ]
