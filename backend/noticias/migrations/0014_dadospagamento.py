# Generated by Django 5.1 on 2024-08-16 01:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0013_alter_cliente_plano'),
    ]

    operations = [
        migrations.CreateModel(
            name='DadosPagamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('numero_cartao', models.CharField(max_length=16)),
                ('data_vencimento', models.CharField(max_length=5)),
                ('cvv', models.CharField(max_length=4)),
                ('cep', models.CharField(max_length=10)),
                ('cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dados_pagamento', to='noticias.cliente')),
            ],
            options={
                'verbose_name': 'Dados de Pagamento',
                'verbose_name_plural': 'Dados de Pagamento',
            },
        ),
    ]