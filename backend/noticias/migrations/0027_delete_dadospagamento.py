# Generated by Django 5.0.7 on 2024-08-24 01:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0026_cliente_stripe_customer_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='DadosPagamento',
        ),
    ]
