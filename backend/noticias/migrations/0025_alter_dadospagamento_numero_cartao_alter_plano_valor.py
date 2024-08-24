# Generated by Django 5.1 on 2024-08-21 00:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0024_rename_data_renovacao_plano_dadospagamento_data_renovacao_pagamento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dadospagamento',
            name='numero_cartao',
            field=models.CharField(max_length=4),
        ),
        migrations.AlterField(
            model_name='plano',
            name='valor',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]