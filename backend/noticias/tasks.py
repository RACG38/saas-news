from celery import shared_task
from .models import *
from django.core.mail import send_mail
import requests
import datetime
from django.utils import timezone
import stripe

stripe.api_key = 'sk_test_51Pn4lyFoYdflkG65qPLotl9dBgfaHOltbrQHlGXcyagLR8JpBTWpJIwSFmLgMI3rvRwBF1RmQ596z4ZvCCm1QhCg00rhjYHrvk'

@shared_task
def fetch_news_for_stocks():
    api_key = '9618d67ea9104c7c8d43dada952926ef'
    
    acoes = AcaoSelecionada.objects.all()

    for acao in acoes:
        url = f'https://newsapi.org/v2/everything?q={acao.simbolo}&from="{datetime.date.today()}"&sortBy=publishedAt&apiKey={api_key}&language=pt'
        response = requests.get(url)
        news_data = response.json()

        if news_data.get('status') == 'ok':
            for article in news_data.get('articles', []):
                # Converter a data de publicação para o formato DateTimeField do Django
                data_publicacao = article['publishedAt']

                Noticia.objects.create(
                    acao_selecionada=acao,
                    fonte=article['source']['name'],
                    conteudo=article['description'] or article['title'],
                    url=article['url'],
                    data_publicacao=data_publicacao  # Salvar a data de publicação
                )

@shared_task
def send_daily_news_email():
    clientes = Cliente.objects.all()

    for cliente in clientes:
        limite_noticias = cliente.plano.qtdade_noticias if cliente.plano else 5
        acoes = AcaoSelecionada.objects.filter(cliente=cliente)

        if not acoes.exists():
            continue

        news_content = ""

        for acao in acoes:
            noticias = Noticia.objects.filter(acao_selecionada=acao).order_by('-id')[:limite_noticias]

            if noticias.exists():
                news_content += f"<h2>{acao.simbolo} - {acao.nome}</h2><ul>"
                
                for noticia in noticias:
                    data_formatada = noticia.data_publicacao.strftime('%d/%m/%Y %H:%M') if noticia.data_publicacao else 'Data desconhecida'
                    news_content += f"""
                    <li>
                        <strong>Fonte:</strong> {noticia.fonte}<br>
                        <strong>Data de Publicação:</strong> {data_formatada}<br>
                        {noticia.conteudo}<br>
                        <a href="{noticia.url}" target="_blank">Leia mais</a>
                    </li>
                    """
                
                news_content += "</ul>"

        if news_content:
            subject = f"Notícias diárias das suas ações"
            send_mail(
                subject,
                news_content,
                'renan.acg7@gmail.com',
                [cliente.email],
                fail_silently=False,
                html_message=news_content
            )

@shared_task
def monitor_news_for_pro_clients():
    # Buscar clientes com plano "Pro"
    pro_clients = Cliente.objects.filter(plano__nome_plano="Pro")
    current_time = timezone.now()

    for cliente in pro_clients:
        acoes = AcaoSelecionada.objects.filter(cliente=cliente)

        for acao in acoes:
            # Buscar notícias desde a última verificação (último minuto)
            url = f'https://newsapi.org/v2/everything?q={acao.simbolo}&from={current_time - timezone.timedelta(minutes=1)}&sortBy=publishedAt&apiKey=YOUR_API_KEY&language=pt'
            response = requests.get(url)
            news_data = response.json()

            if news_data.get('status') == 'ok':
                for article in news_data.get('articles', []):
                    # Verificar se a notícia já foi armazenada para evitar duplicatas
                    if not Noticia.objects.filter(acao_selecionada=acao, url=article['url']).exists():
                        noticia = Noticia.objects.create(
                            acao_selecionada=acao,
                            fonte=article['source']['name'],
                            conteudo=article['description'] or article['title'],
                            url=article['url'],
                            data_publicacao=article['publishedAt']
                        )

                        # Enviar email com novo formato HTML e CSS
                        send_immediate_news_email(cliente, noticia)

def send_immediate_news_email(cliente, noticia):
    subject = f"Nova notícia sobre {noticia.acao_selecionada.simbolo}"
    news_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h1 style="color: #FF5733;">Notícia de Última Hora!</h1>
        <p><strong>Fonte:</strong> {noticia.fonte}</p>
        <p><strong>Data de Publicação:</strong> {noticia.data_publicacao.strftime('%d/%m/%Y %H:%M')}</p>
        <p>{noticia.conteudo}</p>
        <p><a href="{noticia.url}" style="color: #1a73e8; text-decoration: none;" target="_blank">Leia mais</a></p>
        <hr>
        <footer>
            <p>Este email foi enviado porque você é assinante do plano Pro.</p>
        </footer>
    </body>
    </html>
    """

    send_mail(
        subject,
        news_content,
        'renan.acg7@gmail.com',
        [cliente.email],
        fail_silently=False,
        html_message=news_content  # Enviar o email como HTML
    )

# @shared_task
# def monthly_payment():
#     hoje = timezone.now().date()

#     # Buscar clientes com planos Basic ou Pro cuja data de renovação seja hoje
#     clientes = Cliente.objects.filter(plano__nome_plano__in=['Basic', 'Pro'], dados_pagamento__data_renovacao_pagamento=hoje)

#     for cliente in clientes:
#         try:
#             # Recuperar os dados de pagamento do cliente
#             dados_pagamento = DadosPagamento.objects.get(cliente=cliente)

#             # Criar uma nova cobrança usando o Stripe
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=int(cliente.plano.valor * 100),  # valor em centavos
#                 currency='brl',
#                 customer=dados_pagamento.stripe_customer_id,  # Substitua pelo ID do cliente no Stripe
#                 payment_method=dados_pagamento.stripe_payment_method_id,  # Substitua pelo ID do método de pagamento
#                 off_session=True,
#                 confirm=True,
#             )

#             # Atualizar a data do último pagamento e agendar a próxima renovação
#             cliente.data_ultimo_pagamento = hoje
#             dados_pagamento.data_renovacao_pagamento = hoje + timezone.timedelta(days=30)
#             cliente.save()
#             dados_pagamento.save()

#             # Enviar email de confirmação de pagamento
#             send_mail(
#                 subject="Confirmação de Pagamento",
#                 message=f"Olá {cliente.nome}, seu pagamento do plano {cliente.plano.nome_plano} foi realizado com sucesso.",
#                 from_email="seu_email@example.com",
#                 recipient_list=[cliente.email],
#                 fail_silently=False,
#             )

#         except stripe.error.StripeError as e:
#             # Lidar com erro de pagamento
#             print(f"Erro ao processar pagamento para o cliente {cliente.nome}: {str(e)}")

#         except Exception as e:
#             # Lidar com qualquer outro erro
#             print(f"Erro ao processar cliente {cliente.nome}: {str(e)}")