# Generated by Django 5.1 on 2024-09-26 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0037_remove_noticia_data_geracao_remove_noticia_resumo'),
    ]

    operations = [
        migrations.AddField(
            model_name='noticia',
            name='data_envio',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
