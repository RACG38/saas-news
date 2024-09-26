from django.db import models

# python manage.py makemigrations 
# python manage.py migrate

class Plano(models.Model):
    nome_plano = models.CharField(max_length=255)       # Coluna para o nome do plano
    valor = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    qtdade_ativos = models.IntegerField()               # Coluna para quantidade de ativos
    qtdade_noticias = models.IntegerField()             # Coluna para quantidade de noticias
    periodicidade = models.IntegerField()               # Coluna para periodicidade
    email = models.BooleanField()                       # Coluna booleana para email
    whatsapp = models.BooleanField()                    # Coluna booleana para whatsapp
    tempo_real = models.BooleanField()                  # Coluna booleana para noticia em tempo real

    def __str__(self):
        return self.nome_plano
    
    class Meta:
        verbose_name = 'Plano disponível'
        verbose_name_plural = 'Planos disponíveis'

class Token(models.Model):

    token_id = models.CharField(max_length=6, null=True, blank=True)
    data_criacao = models.DateTimeField(null=True, blank=True) 
    data_expiracao = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"{self.token_id}"
    
class AcaoSelecionada(models.Model):    
    simbolo = models.CharField(max_length=10)  
    nome = models.CharField(max_length=255, null=True, blank=True)
    volume = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.simbolo}"
    
    class Meta:
        verbose_name = 'Ticker selecionado'
        verbose_name_plural = 'Tickers selecionados'

class Noticia(models.Model):
    acao_selecionada = models.ForeignKey(AcaoSelecionada, on_delete=models.CASCADE, related_name='noticias')
    fonte = models.CharField(max_length=255)
    conteudo = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True) 
    data_publicacao = models.DateTimeField(null=True, blank=True)     
    data_envio_email = models.DateTimeField(null=True, blank=True)  
    data_envio_whatsapp = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"Notícia sobre {self.acao_selecionada.simbolo}"

class Endereco(models.Model):

    cep = models.CharField(max_length=255)
    logradouro = models.CharField(max_length=255)
    numero = models.CharField(max_length=255)
    complemento = models.CharField(max_length=255)
    bairro = models.CharField(max_length=255)
    cidade = models.CharField(max_length=255)
    estado = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Endereço'
        verbose_name_plural = 'Endereços'

class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    cpf = models.CharField(max_length=12, null=True, blank=True)
    email = models.EmailField(unique=True)
    whatsapp = models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    plano = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True, blank=True)
    data_ultimo_pagamento = models.DateField(null=True, blank=True)
    tickers = models.ManyToManyField(AcaoSelecionada, related_name='clientes')
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)  
    token = models.ForeignKey(Token, on_delete=models.CASCADE, null=True, blank=True)
    endereco = models.ForeignKey(Endereco, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.nome}"
    




    
