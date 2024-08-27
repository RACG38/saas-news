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
    
    
class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    whatsapp = models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    plano = models.ForeignKey(Plano, on_delete=models.SET_NULL, null=True, blank=True)
    data_ultimo_pagamento = models.DateField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)  
    token = models.ForeignKey(Token, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.nome}"

    
class AcaoSelecionada(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='acoes_selecionadas')
    simbolo = models.CharField(max_length=10)  
    nome = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return f"{self.cliente.email} - {self.simbolo}"
    
    class Meta:
        verbose_name = 'Ticker selecionado'
        verbose_name_plural = 'Tickers selecionados'
    
    
# class DadosPagamento(models.Model):
#     cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, related_name='dados_pagamento')
#     numero_cartao = models.CharField(max_length=4)  # Armazena apenas os últimos 4 dígitos
#     data_vencimento = models.CharField(max_length=5)  # Formato MM/YY
#     cep = models.CharField(max_length=10)
#     data_renovacao_pagamento = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return f'Dados de Pagamento de {self.cliente.nome}'

#     class Meta:
#         verbose_name = 'Dados de Pagamento'
#         verbose_name_plural = 'Dados de Pagamento'

class Noticia(models.Model):
    acao_selecionada = models.ForeignKey(AcaoSelecionada, on_delete=models.CASCADE, related_name='noticias')
    fonte = models.CharField(max_length=255)
    conteudo = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True) 
    data_publicacao = models.DateTimeField(null=True, blank=True) 

    def __str__(self):
        return f"Notícia sobre {self.acao_selecionada.simbolo}"
    
