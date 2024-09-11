from .libs import *
from django.conf import settings

logger = logging.getLogger('my_custom_logger')
logger.setLevel(logging.DEBUG)

# Configuração do cliente Twilio
client_twilio = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

google_news_api_key = settings.GOOGLE_NEWS_API_KEY
max_daily_news = settings.MAX_NEWS_DAILY
start_fetch_news = settings.START_FETCH_NEWS
end_fetch_news = settings.END_FETCH_NEWS

@shared_task
def delete_unassociated_stocks():
    # Consulta para encontrar ações sem clientes associados
    acoes_sem_cliente = AcaoSelecionada.objects.annotate(num_clientes=Count('clientes')).filter(num_clientes=0)
    
    # Deletar as ações que não estão associadas a nenhum cliente
    acoes_sem_cliente.delete()

@shared_task
def delete_unassociated_tokens():

    # Consulta para encontrar ações sem clientes
    tokens_sem_cliente = Token.objects.filter(cliente__isnull=True)
    # Deletar as ações que não estão associadas a nenhum cliente
    tokens_sem_cliente.delete()

@shared_task
def delete_previous_day_news():
    # Obtém a data de ontem
    yesterday = datetime.today().date() - timedelta(days=1)
    # Filtra as notícias que têm data de publicação do dia anterior e as exclui
    Noticia.objects.filter(data_publicacao__date=yesterday).delete()

@shared_task
def fetch_news_for_stocks():

    current_hour = datetime.now().hour  # Verifica a hora atual

    if start_fetch_news <= current_hour < end_fetch_news:
        acoes = AcaoSelecionada.objects.all()
        today_date = datetime.today().date()

        for acao in acoes:
            query = f'{acao.simbolo} OR {acao.nome}'

            url = (
                f'https://newsapi.org/v2/everything?q={query}'
                f'&from={today_date}&sortBy=publishedAt'
                f'&apiKey={google_news_api_key}&language=pt'
            )
            
            response = requests.get(url)
            news_data = response.json()

            if news_data.get('status') == 'ok':
                # Verificar quantas notícias já existem para essa ação hoje
                existing_news_count = Noticia.objects.filter(
                    acao_selecionada=acao,
                    data_publicacao__date=today_date
                ).count()

                for article in news_data.get('articles', []):
                    # Verificar se o limite de notícias já foi atingido
                    if existing_news_count >= max_daily_news:
                        break  # Parar de adicionar notícias para esta ação

                    title = article.get('title', '')
                    if not title:
                        print(f"Título não encontrado para o artigo: {article}")
                        continue  # Pula para o próximo artigo

                    # Verificar se o título contém o símbolo ou o nome da ação (case-insensitive)
                    title_lower = title.lower()
                    simbolo_lower = acao.simbolo.lower()
                    nome_lower = acao.nome.lower()

                    if simbolo_lower in title_lower or nome_lower in title_lower:
                        published_at = article.get('publishedAt')
                        if not published_at:
                            print(f"Data de publicação não encontrada para o artigo: {article}")
                            continue  # Pula para o próximo artigo

                        # Converter a data de publicação para o formato DateTimeField do Django
                        data_publicacao = parse_datetime(published_at)
                        
                        # Verificar se a data de publicação é hoje
                        if data_publicacao.date() == today_date:
                            # Criar a nova notícia no banco de dados
                            Noticia.objects.create(
                                acao_selecionada=acao,
                                fonte=article.get('source', {}).get('name', 'Fonte desconhecida'),
                                conteudo=title,
                                url=article.get('url', ''),
                                data_publicacao=data_publicacao
                            )

                            # Incrementar o contador de notícias existentes
                            existing_news_count += 1
            else:
                error_message = news_data.get('message', 'Erro desconhecido ao buscar notícias.')
                print(f"Erro ao buscar notícias para {acao.simbolo}: {error_message}")

@shared_task
def send_daily_news_email(*args, **kwargs):

    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(base_dir, 'templates/styles/news_email.css')

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

        if not acoes.exists():
            continue

        news_content = "<div class='container'>"

        for acao in acoes:
            
            noticias = Noticia.objects.filter(acao_selecionada=acao).order_by('-id')[:limite_noticias]

            if noticias:

                news_content += f"<h2>{acao.simbolo} - {acao.nome}</h2><div class='news-cards'>"
                
                for noticia in noticias:
                    data_formatada = noticia.data_publicacao.strftime('%d/%m/%Y %H:%M') if noticia.data_publicacao else 'Data desconhecida'
                    news_content += f"""
                    <div class="news-card">
                        <strong>Fonte:</strong> {noticia.fonte}<br>
                        <strong>Data de Publicação:</strong> {data_formatada}<br>
                        <p>{noticia.conteudo}</p>
                        <a href="{noticia.url}" target="_blank">Leia mais</a>
                    </div>
                    """
                
                news_content += "</div>"  # Fechando a div news-cards

        news_content += "</div>"  # Fechando a div container

        if news_content:
            subject = f"Notícias diárias das suas ações"
            full_email_content = f"""
            <html lang="pt-BR">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>{css_content}</style>  <!-- CSS embutido diretamente no HTML -->
                <title>Notícias Diárias</title>
            </head>
            <body>
                {news_content}
            </body>
            </html>
            """
            send_mail(
                subject,
                '',  # Texto plano vazio
                'renan.acg7@gmail.com',
                [cliente.email],
                fail_silently=False,
                html_message=full_email_content
            )    

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
                    
                    noticia = Noticia(
                        acao_selecionada=acao_selecionada,
                        fonte="",
                        conteudo=conteudo,
                        url="",
                        data_publicacao=datetime.now()
                    )
                    
                    noticia.save()                

    finally:
        # Fechando o navegador
        driver.quit()

@shared_task
def monitor_news_for_pro_clients():
    
    # Definir o fuso horário de Brasília (UTC-3)
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    
    # Hora atual no fuso horário de Brasília
    current_time_brasilia = timezone.now().astimezone(brasilia_tz)
    current_hour_brasilia = current_time_brasilia.hour  # Verifica a hora atual no fuso horário de Brasília    

    if start_fetch_news <= current_hour_brasilia < end_fetch_news:       

        pro_clients = Cliente.objects.filter(plano__nome_plano="Pro")  # Buscar clientes com plano "Pro"

        for cliente in pro_clients:

            # Buscar as ações selecionadas diretamente a partir do campo ManyToMany `tickers` do cliente
            acoes = cliente.tickers.all()                

            for acao in acoes:

                # Buscar notícias desde a última verificação (último minuto)
                # from_time = current_time_brasilia - timedelta(minutes=1)
                # url = f'https://newsapi.org/v2/everything?q={acao.simbolo}&from={from_time.isoformat()}&sortBy=publishedAt&apiKey={google_news_api_key}&language=pt'
               
                # Calcula a data de ontem
                yesterday = datetime.now() - timedelta(days=1)

                # Formata a data de ontem para o formato ISO 8601 (necessário para a URL)
                from_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)

                # Gera a URL com a data de ontem
                url = f'https://newsapi.org/v2/everything?q={acao.simbolo}&from={from_time.isoformat()}&sortBy=publishedAt&apiKey={google_news_api_key}&language=pt'
                            
                
                response = requests.get(url)
                news_data = response.json()

                if news_data.get('status') == 'ok':

                    for article in news_data.get('articles', []):
                        # Converter a data de publicação da notícia para um formato datetime no fuso horário UTC
                        published_at = parse_datetime(article['publishedAt']).astimezone(pytz.UTC)
                        
                        # Verificar se a notícia foi publicada hoje no horário de Brasília
                        if published_at.astimezone(brasilia_tz).date() == current_time_brasilia.date():

                            # Verificar se a notícia já foi armazenada para evitar duplicatas
                            if not Noticia.objects.filter(acao_selecionada=acao, url=article['url']).exists():
                                noticia = Noticia.objects.create(
                                    acao_selecionada=acao,
                                    fonte=article['source']['name'],
                                    conteudo=article.get('description') or article.get('title', ''),
                                    url=article['url'],
                                    data_publicacao=published_at  # Salva a data de publicação
                                )

                                if noticia:
                                    # Enviar a notícia por e-mail, já que o plano do cliente é "Pro"
                                    send_immediate_news_email(cliente.id, noticia.id)

@shared_task
def send_whatsapp_news():

    logger.debug("TORCH CUDA IS AVAILABLE", torch.cuda.is_available())  # Verifica se a GPU está disponível
    logger.debug("TORCH DEVICE", torch.cuda.current_device())
    
    # Definir o horário da última verificação (últimos 10 minutos)
    intervalo_tempo = timezone.now() - timedelta(minutes=settings.WHATSAPP_NEWS_FETCH_INTERVAL+60)

    # Selecionar clientes com plano Pro
    pro_clients = Cliente.objects.filter(plano__nome_plano="Pro")  # Buscar clientes com plano "Pro"

    # Iterar sobre os clientes Pro
    for cliente in pro_clients:

        # Verificar se há novas notícias para este cliente
        novas_noticias = Noticia.objects.filter(
            acao_selecionada__in=cliente.tickers.all(),  # Verifica notícias das ações selecionadas pelo cliente
            data_publicacao__gte=intervalo_tempo  # Notícias publicadas nos últimos 10 minutos
        )

        # Se houver novas notícias, enviar via WhatsApp
        if novas_noticias:

            for noticia in novas_noticias:

                # Inicializar o pipeline de sumarização
                summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0)
                
                try:
                    resumo = summarizer(noticia.conteudo, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
                except Exception as e:
                    resumo = noticia.conteudo  # Caso haja um erro ou o conteúdo seja pequeno, usar o conteúdo original

                # Dividir o conteúdo em tópicos organizados
                mensagem = (
                    f"📰 *Nova notícia sobre a ação {noticia.acao_selecionada.nome} ({noticia.acao_selecionada.simbolo}):*\n\n"
                    f"*🔹 Fonte:* {noticia.fonte}\n\n"
                    f"*🔹 Data de publicação:* {noticia.data_publicacao.strftime('%d/%m/%Y %H:%M')}\n\n"
                    f"*🔹 Resumo da notícia:*\n"
                    f"{resumo}\n\n"
                    f"*🔹 Leia mais no link abaixo:*\n{noticia.url if noticia.url else 'Nenhum link disponível'}"
                )
                
                try:
                    # Enviar a notícia pelo WhatsApp
                    message = client_twilio.messages.create(
                        body=mensagem,
                        from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,                                                         
                        to='whatsapp:' + f'+55{cliente.whatsapp}'
                    )
                    
                    # Verificar o status da mensagem
                    if message.status in ['queued', 'sending', 'sent']:
                        logger.debug(f"Mensagem enviada com sucesso para {cliente.nome}: {message.sid}")
                    elif message.status == 'delivered':
                        logger.debug(f"Mensagem entregue com sucesso para {cliente.nome}.")
                    elif message.status in ['undelivered', 'failed']:
                        logger.debug(f"Falha ao enviar mensagem para {cliente.nome}: {message.status}")

                except Exception as e:
                    logger.debug(f"Erro ao enviar mensagem para {cliente.nome}: {str(e)}")   

def send_immediate_news_email(cliente_id, noticia_id):
    try:
        cliente = Cliente.objects.get(id=cliente_id)
        noticia = Noticia.objects.get(id=noticia_id)
    except Cliente.DoesNotExist:
        logger.error(f"Cliente com id {cliente_id} não encontrado.")
        return
    except Noticia.DoesNotExist:
        logger.error(f"Noticia com id {noticia_id} não encontrada.")
        return

    subject = f"Nova notícia sobre {noticia.acao_selecionada.simbolo}"

    # Lendo o conteúdo do arquivo CSS
    base_dir = os.path.dirname(os.path.abspath(__file__))
    css_path = os.path.join(base_dir, 'templates/styles/news_email.css')

    try:
        with open(css_path, 'r') as css_file:
            css_content = css_file.read()
    except FileNotFoundError:
        logger.error(f"Arquivo CSS não encontrado em: {css_path}")
        css_content = ""

    news_content = f"""
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>{css_content}</style>  <!-- CSS embutido diretamente no HTML -->
        <title>Notícia de Última Hora</title>
    </head>
    <body>
        <div class="container">
            <h1>Notícia de Última Hora!</h1>
            <p><strong>Fonte:</strong> {noticia.fonte}</p>
            <p><strong>Data de Publicação:</strong> {noticia.data_publicacao.strftime('%d/%m/%Y %H:%M') if noticia.data_publicacao else 'Data desconhecida'}</p>
            <p>{noticia.conteudo}</p>
            <p><a href="{noticia.url}" target="_blank">Leia mais</a></p>
            <hr>
            <footer>
                <p>Este email foi enviado porque você é assinante do plano Pro.</p>
            </footer>
        </div>
    </body>
    </html>
    """

    send_mail(
        subject,
        '',  # Texto plano vazio
        'renan.acg7@gmail.com',
        [cliente.email],
        fail_silently=False,
        html_message=news_content  
    )

@shared_task
def fetch_and_send_news_chain():
    
    chain(
        fetch_news_for_stocks.s(),
        send_daily_news_email.s(),
    ).apply_async()

