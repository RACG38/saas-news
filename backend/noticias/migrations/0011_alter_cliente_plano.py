# Generated by Django 5.1 on 2024-08-14 02:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0010_acaoselecionada_nome'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='plano',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='noticias.plano'),
        ),
    ]
