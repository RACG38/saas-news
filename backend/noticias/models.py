from django.db import models

#python manage.py makemigrations
#python manage.py migrate

class Plano(models.Model):
    nome_plano = models.CharField(max_length=255)       # Coluna para o nome do plano
    valor = models.FloatField(null=True, blank=True)    # Coluna para o valor do plano 
    qtdade_ativos = models.IntegerField()               # Coluna para quantidade de ativos
    qtdade_noticias = models.IntegerField()             # Coluna para quantidade de noticias
    periodicidade = models.IntegerField()               # Coluna para periodicidade
    email = models.BooleanField()                       # Coluna booleana para email
    whatsapp = models.BooleanField()                    # Coluna booleana para whatsapp
    tempo_real = models.BooleanField()                  # Coluna booleana para noticia em tempo real

    def __str__(self):
        return self.nome_plano
    
class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    whatsapp = models.CharField(max_length=15, blank=True, null=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    plano = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True, blank=True)  # Corrigir para ForeignKey
    data_ultimo_pagamento = models.DateField(null=True, blank=True)  

    def __str__(self):
        return self.nome
    
class AcaoSelecionada(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='acoes_selecionadas')
    simbolo = models.CharField(max_length=10)  # Simbolo da ação, como "AAPL" para Apple
    nome = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.cliente.nome} - {self.simbolo}"