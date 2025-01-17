# Generated by Django 5.1 on 2024-09-06 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('noticias', '0032_adress_cliente_endereco'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='adress',
            options={'verbose_name': 'Endereço', 'verbose_name_plural': 'Endereços'},
        ),
        migrations.AddField(
            model_name='cliente',
            name='cpf',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='adress',
            name='cep',
            field=models.CharField(max_length=255),
        ),
    ]
