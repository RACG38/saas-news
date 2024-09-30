# Bibliotecas Padrão
import os
import logging
import datetime
import gc
from datetime import datetime, timedelta

# Bibliotecas de Terceiros
import torch
import feedparser
import pandas as pd
from bs4 import BeautifulSoup
from transformers import pipeline
from twilio.rest import Client
from webdriver_manager.chrome import ChromeDriverManager
from celery import Celery, chain, shared_task
from celery.schedules import crontab
from celery.exceptions import SoftTimeLimitExceeded
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from rest_framework_simplejwt.tokens import RefreshToken

# Imports Internos (do Projeto)
from django.conf import settings
from django.db.models import Count
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.utils import timezone
from .models import Token, AcaoSelecionada, Noticia, Cliente


logger = logging.getLogger('my_custom_logger')
logger.setLevel(logging.DEBUG)

# Configuração do cliente Twilio
client_twilio = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

google_news_api_key = settings.GOOGLE_NEWS_API_KEY
max_daily_news = settings.MAX_NEWS_DAILY
max_twilio_characters = settings.MAX_CHARACTERS


@shared_task
def delete_unassociated_stocks():
    # Consulta para encontrar ações sem clientes associados
    acoes_sem_cliente = AcaoSelecionada.objects.annotate(num_clientes=Count('clientes')).filter(num_clientes=0)
    
    # Deletar as ações que não estão associadas a nenhum cliente
    acoes_sem_cliente.delete()

    gc.collect()

@shared_task
def delete_unassociated_tokens(*args, **kwargs):

    # Consulta para encontrar ações sem clientes
    tokens_sem_cliente = Token.objects.filter(cliente__isnull=True)
    # Deletar as ações que não estão associadas a nenhum cliente
    tokens_sem_cliente.delete()

    gc.collect()

@shared_task
def delete_previous_day_news(*args, **kwargs):
    # Obtém a data de ontem
    yesterday = datetime.today().date() - timedelta(days=10)
    # Filtra as notícias que têm data de publicação do dia anterior e as exclui
    Noticia.objects.filter(data_publicacao__date=yesterday).delete()

    gc.collect()

@shared_task(rate_limit='10/m')
def fetch_news_for_stocks():  

    acoes = AcaoSelecionada.objects.all()    

    # RSS feed do InfoMoney
    rss_url = "https://www.infomoney.com.br/feed/"

    # Parsear o feed RSS
    feed = feedparser.parse(rss_url)   

    for acao in acoes:

        simbolo_lower = acao.simbolo.lower()
        nome_lower = acao.nome.lower() + " "

        # Iterar sobre as entradas do feed RSS e salvar no banco de dados se a notícia for relevante
        for entry in feed.entries:

            title = entry.title.lower()
            summary = entry.summary.lower() if 'summary' in entry else ""
            link = entry.link
            published_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z").date() if 'published' in entry else ""
                                    
            if published_date == datetime.today().date():                

                # Verificar se o título ou resumo contém o símbolo ou o nome da ação (case-insensitive)
                if simbolo_lower in title or nome_lower in title or simbolo_lower in summary or nome_lower in summary:
                    # Verificar se o texto já existe no banco de dados
                    if not Noticia.objects.filter(acao_selecionada=acao, conteudo=summary).exists():
                        Noticia.objects.create(
                            acao_selecionada=acao,
                            fonte="InfoMoney",
                            conteudo=summary,
                            url=link,
                            data_publicacao=published_date
                        )
                    else:
                        logger.debug(f"Notícia já existente para {acao.simbolo}")

# @shared_task(rate_limit='10/m')
# def fetch_news_for_stocks():   

#     acoes = AcaoSelecionada.objects.all()
#     three_days_ago = datetime.now() - timedelta(days=1)

#     # Formata a data de três dias atrás para o formato ISO 8601 (necessário para a URL)
#     from_time = three_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)

#     for acao in acoes:
#         # Gera a URL com a data de três dias atrás
#         url = (f'https://newsapi.org/v2/everything?q={acao.simbolo}'
#                 f'&from={from_time.isoformat()}'
#                 f'&sortBy=publishedAt'
#                 f'&apiKey={google_news_api_key}'
#                 f'&language=pt'
#                 f'&pageSize={settings.MAX_NEWS_DAILY}'
#                 )

#         with requests.get(url) as response:
#             news_data = response.json()

#         if news_data.get('status') == 'ok':

#             # Para cada artigo, salvar o conteúdo completo ou descrição no banco de dados
#             for article in news_data.get('articles', []):

#                 source = article.get('source', '')
#                 source_name = source.get('name', '')
#                 description = article.get('description', '')
#                 content = article.get('content', '')  # Tentar pegar o conteúdo completo da notícia
#                 url = article.get('url', '')
#                 published_data = article.get('publishedAt', '')

#                 if not description and not content:
#                     continue

#                 # Verificar se o conteúdo contém o símbolo ou o nome da ação (case-insensitive)
#                 description_lower = description.lower()
#                 simbolo_lower = acao.simbolo.lower()
#                 nome_lower = acao.nome.lower()

#                 if simbolo_lower in description_lower or nome_lower in description_lower:
#                     full_text = content if content else description

#                     # Verificar se o texto já existe no banco de dados
#                     if not Noticia.objects.filter(acao_selecionada=acao, conteudo=full_text).exists():
#                         # Salvar o conteúdo completo da notícia
#                         Noticia.objects.create(
#                             acao_selecionada=acao,
#                             fonte=source_name,
#                             conteudo=full_text,
#                             url=url,
#                             data_publicacao=published_data

#                         )
#                     else:
#                         logger.debug(f"Notícia já existente para {acao.simbolo}")

#         else:
#             logger.debug(f"Erro ao buscar notícias para {acao.simbolo}: {news_data.get('message', 'Erro desconhecido ao buscar notícias.')}")

@shared_task(rate_limit='5/m')
def send_daily_news_email(*args, **kwargs):

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # Caminho para os arquivos HTML e CSS
    css_path = os.path.join(base_dir, 'templates/styles/news_email.css')

    # Carregar o CSS
    try:
        with open(css_path, 'r') as css_file:
            css_content = css_file.read()
    except FileNotFoundError:
        logger.error(f"Arquivo CSS não encontrado em: {css_path}")
        css_content = ""

    clientes = Cliente.objects.all()

    for cliente in clientes:

        limite_noticias = cliente.plano.qtdade_noticias if cliente.plano else max_daily_news
        acoes = cliente.tickers.all()

        if not acoes:
            continue

        # Variável para indicar se há pelo menos uma notícia válida
        has_valid_news = False

        # Carregar todas as notícias das ações do cliente
        acoes_com_noticias = []

        summarizer_pipeline = pipeline("summarization", model="facebook/bart-large-cnn", revision="main", device=-1)

        torch.cuda.empty_cache()   

        # Lista de IDs de todas as notícias que foram enviadas por email
        todas_noticias_enviadas_ids = []

        for acao in acoes:

            topicos = []  # Lista que conterá os tópicos de todas as notícias
            links_noticias = []

            # Obter todas as notícias relacionadas à ação que ainda não foram enviadas
            noticias = Noticia.objects.filter(
                acao_selecionada=acao,
                data_envio_email__isnull=True  # Apenas notícias que ainda não foram enviadas
            ).order_by('-id')[:limite_noticias]
            
            # Verifica se há notícias com conteúdo válido
            noticias_validas = [noticia for noticia in noticias if noticia.conteudo and noticia.conteudo.strip() and noticia.url]

            if noticias_validas:               

                for noticia in noticias_validas:
                    
                    try:
                        with torch.no_grad():
                            # Gerar o resumo apenas se o conteúdo for suficiente
                            resumo = summarizer_pipeline(noticia.conteudo, 
                                                        max_length=200, 
                                                        min_length=30, 
                                                        do_sample=False, 
                                                        clean_up_tokenization_spaces=True)[0]['summary_text']
                    
                    except ValueError:
                        # Caso o texto seja muito curto ou falhe a sumarização, usar um fallback
                        resumo = noticia.conteudo[:300]  # Usa os primeiros 300 caracteres como fallback                    

                    # Quebrar o resumo em tópicos usando a quebra de linha
                    topicos_noticia = resumo.split('\n')  # Dividir o resumo em vários tópicos com base nas quebras de linha

                    # Adicionar os tópicos da notícia atual à lista geral de tópicos
                    topicos.extend(topicos_noticia)

                    # Adicionar o link da notícia
                    if noticia.url:  # Verificar se o link existe
                        links_noticias.append(noticia.url)

                    # Adicionar o ID da notícia à lista de IDs para atualização posterior
                    todas_noticias_enviadas_ids.append(noticia.id)

                acoes_com_noticias.append({
                    'nome': acao.nome,
                    'simbolo': acao.simbolo,
                    'resumo': resumo,
                    'topicos': topicos,  # Passar os tópicos pré-processados
                    'urls': links_noticias  # Passar os links para o template
                })
                has_valid_news = True  # Marca que há pelo menos uma notícia válida

        # Se houver pelo menos uma notícia válida, enviar o e-mail
        if has_valid_news:
            # Renderizar o template HTML e passar o CSS como contexto
            full_email_content = render_to_string('noticias/news_email.html', {
                'css_content': css_content,  # Passa o CSS dinamicamente
                'acoes': acoes_com_noticias,
            })

            # Enviar o e-mail
            subject = "Notícias diárias das suas ações"
            email_enviado = send_mail(
                subject,
                '',  
                'renan.acg7@gmail.com',
                [cliente.email],
                fail_silently=False,
                html_message=full_email_content
            )

            # Se o e-mail foi enviado com sucesso, atualizar o campo data_envio_email
            if email_enviado:
                # Atualizar o campo data_envio_email das notícias que foram enviadas
                Noticia.objects.filter(id__in=todas_noticias_enviadas_ids).update(data_envio_email=timezone.now())
                logger.debug(f"E-mail enviado com sucesso para {cliente.email}.")
            else:
                logger.error(f"Erro ao enviar e-mail para {cliente.email}. Nenhuma notícia foi atualizada.")

@shared_task(rate_limit='5/m') 
def send_whatsapp_news(*args, **kwargs):  

    # Selecionar clientes com plano Pro
    pro_clients = Cliente.objects.filter(plano__nome_plano="Pro")

    # Iterar sobre os clientes Pro
    for cliente in pro_clients:

        # Verificar se há novas notícias para este cliente (notícias que ainda não foram enviadas)
        novas_noticias = Noticia.objects.filter(
            acao_selecionada__in=cliente.tickers.all(),
            data_envio_whatsapp__isnull=True  # Somente notícias que ainda não foram enviadas
        )

        # Se houver novas notícias, enviar via WhatsApp
        if novas_noticias.exists():

            for acao in cliente.tickers.all():

                # Selecionar notícias relacionadas à ação atual que ainda não foram enviadas
                noticias_acao = novas_noticias.filter(acao_selecionada=acao)

                # Se houver notícias para a ação atual, enviar uma mensagem separada
                if noticias_acao.exists():

                    for noticia in noticias_acao:

                        # Verificar se a notícia tem conteúdo antes de prosseguir
                        if noticia.conteudo and noticia.conteudo.strip():  # Garantir que não esteja vazio

                            # Inicializar o pipeline de sumarização usando a GPU (se disponível)
                            summarizer_pipeline = pipeline("summarization", model="facebook/bart-large-cnn", revision="main", device=-1)

                            torch.cuda.empty_cache()   

                            try:
                                resumo = summarizer_pipeline(noticia.conteudo, 
                                                             max_length=100, 
                                                             min_length=30, 
                                                             do_sample=False,
                                                             clean_up_tokenization_spaces=True)[0]['summary_text']
                            except Exception as e:
                                resumo = noticia.conteudo  # Caso haja um erro ou o conteúdo seja pequeno, usar o conteúdo original

                            # Verificar se a data de publicação não é None
                            data_publicacao_formatada = noticia.data_publicacao.strftime('%d/%m/%Y %H:%M') if noticia.data_publicacao else "Data não disponível"

                            # Montar a mensagem separada para a ação atual
                            mensagem = (
                                f"*📈  Ação:* {noticia.acao_selecionada.nome} ({noticia.acao_selecionada.simbolo})\n\n"
                                f"*🌐 Fonte:* {noticia.fonte}\n"
                                f"*📅 Data de publicação:* {data_publicacao_formatada}\n\n"
                                f"*📰 Resumo:* {resumo}\n\n"
                                f"*🔹 Leia mais no link abaixo:*\n{noticia.url if noticia.url else 'Nenhum link disponível'}\n\n"
                                f"---------------------------------------------------------------------\n\n\n\n"
                            )

                            # Enviar a mensagem para o cliente via WhatsApp
                            try:
                                message = client_twilio.messages.create(
                                    body=mensagem,
                                    from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,
                                    to='whatsapp:' + f'+55{cliente.whatsapp}'
                                )                                                 

                                # Se a mensagem foi enviada com sucesso, atualizar o campo data_envio_whatsapp
                                if message.status in ['queued', 'sending', 'sent', 'delivered']:
                                    logger.debug(f"Mensagem enviada com sucesso para {cliente.nome} sobre {acao.nome}: {message.sid}")

                                    # "Carimbar" a data de envio apenas se enviada com sucesso
                                    noticia.data_envio_whatsapp = timezone.now()
                                    noticia.save()  # Atualizar o campo data_envio_whatsapp

                                elif message.status in ['undelivered', 'failed']:
                                    logger.debug(f"Falha ao enviar mensagem para {cliente.nome} sobre {acao.nome}: {message.status}")

                            except Exception as e:
                                logger.debug(f"Erro ao enviar mensagem para {cliente.nome} sobre {acao.nome}: {str(e)}")

@shared_task
def check_and_save_dividend_news():
    # Configurar o ChromeDriver
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Executa o Chrome em modo headless

    # Iniciar o ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # URL do site que você quer fazer o scraping
    url = "https://statusinvest.com.br/acoes/proventos/ibovespa"

    try:
        # Acessando a página
        driver.get(url)

        # Esperando até que o tbody esteja presente no DOM
        driver.implicitly_wait(10)

        # Encontrando todos os elementos tr com a classe "item"
        tr_elements = driver.find_elements(By.CSS_SELECTOR, 'tr.item')

        # Lista para armazenar os dados
        data = []

        # Iterar sobre cada elemento tr e extrair as informações
        for tr_element in tr_elements:
            td_elements = tr_element.find_elements(By.TAG_NAME, 'td')
            
            # Extraindo os dados de cada <td>
            codigo = td_elements[0].get_attribute('title')
            valor_provento = td_elements[1].text
            data_com = td_elements[2].text
            data_pagamento = td_elements[3].text
            tipo = td_elements[4].text
            dy = td_elements[5].text
            
            # Verificar se todas as colunas estão preenchidas
            if all([codigo, valor_provento, data_com, data_pagamento, tipo, dy]):
                data.append({
                    "Código": codigo,
                    "Valor do Provento": valor_provento,
                    "Data Com": data_com,
                    "Data de Pagamento": data_pagamento,
                    "Tipo": tipo,
                    "Dividend Yield": dy
                })

        # Criando um DataFrame do pandas com os dados
        df = pd.DataFrame(data)

        # Data de hoje
        data_hoje = datetime.today().date().strftime('%d/%m/%Y')

        for index, row in df.iterrows():
            if row['Data de Pagamento'] == data_hoje:
                acao_selecionada = AcaoSelecionada.objects.filter(simbolo=row['Código']).first()
                if acao_selecionada:
                    conteudo = f"Hoje ({data_hoje}) as ações de {row['Código']} irão pagar um {row['Tipo']} no valor de R${round(float(row['Valor do Provento']), 2):.2f} por ação"
                    
                    Noticia.objects.create(
                        acao_selecionada=acao_selecionada,
                        fonte="",
                        conteudo=conteudo,
                        url="",
                        data_publicacao=datetime.now()                        
                    )              
                                   

    finally:
        # Fechando o navegador
        driver.quit()

# Tasks síncronas
@shared_task
def fetch_and_send_news_chain():    
    
    chain(
        fetch_news_for_stocks.s(),
        send_whatsapp_news.s(),
        send_daily_news_email.s()
    ).apply_async()

@shared_task
def daily_data_cleanup():    
    
    chain(
        delete_unassociated_stocks.s(),
        delete_unassociated_tokens.s(),
        delete_previous_day_news.s()
    ).apply_async()

