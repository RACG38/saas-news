# Generated by Django 5.0.7 on 2024-09-01 03:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0029_alter_token_token_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cliente',
            name='token',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='noticias.token'),
        ),
    ]