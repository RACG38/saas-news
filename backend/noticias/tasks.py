from .libs import *
from django.conf import settings

torch.cuda.empty_cache()

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

    gc.collect()

@shared_task
def delete_unassociated_tokens():

    # Consulta para encontrar ações sem clientes
    tokens_sem_cliente = Token.objects.filter(cliente__isnull=True)
    # Deletar as ações que não estão associadas a nenhum cliente
    tokens_sem_cliente.delete()

    gc.collect()

@shared_task
def delete_previous_day_news():
    # Obtém a data de ontem
    yesterday = datetime.today().date() - timedelta(days=1)
    # Filtra as notícias que têm data de publicação do dia anterior e as exclui
    Noticia.objects.filter(data_publicacao__date=yesterday).delete()

    gc.collect()

@shared_task
def fetch_news_for_stocks():
    
    # Definir o fuso horário de Brasília (UTC-3)
    brasilia_tz = pytz.timezone('America/Sao_Paulo')
    
    # Hora atual no fuso horário de Brasília
    current_time_brasilia = timezone.now().astimezone(brasilia_tz)
    current_hour_brasilia = current_time_brasilia.hour  # Verifica a hora atual no fuso horário de Brasília  

    if start_fetch_news <= current_hour_brasilia < end_fetch_news:

        acoes = AcaoSelecionada.objects.all()
        today_date = datetime.today().date() 
        yesterday = datetime.now() - timedelta(days=3)

        # Formata a data de ontem para o formato ISO 8601 (necessário para a URL)
        from_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)    

        for acao in acoes:        
            # Dicionário para acumular o conteúdo das notícias por ação
            all_descriptions = []

            # Gera a URL com a data de ontem
            url = (f'https://newsapi.org/v2/everything?q={acao.simbolo}'
            f'&from={from_time.isoformat()}'
            f'&sortBy=publishedAt'
            f'&apiKey={google_news_api_key}'
            f'&language=pt'
            f'&pageSize={settings.MAX_NEWS_DAILY}'
            )

            with requests.get(url) as response:
                news_data = response.json()

            if news_data.get('status') == 'ok':                
                # Verificar quantas notícias já existem para essa ação hoje
                existing_news_count = Noticia.objects.filter(
                    acao_selecionada=acao,
                    data_publicacao__date=from_time
                ).count()                 

                for article in news_data.get('articles', []):                     
                    # Verificar se o limite de notícias já foi atingido
                    if existing_news_count >= max_daily_news: break

                    description = article.get('description', '')               

                    if not description: continue

                    # Verificar se o conteúdo contém o símbolo ou o nome da ação (case-insensitive)
                    description_lower = description.lower()
                    simbolo_lower = acao.simbolo.lower()
                    nome_lower = acao.nome.lower()

                    if simbolo_lower in description_lower or nome_lower in description_lower:
                        published_at = article.get('publishedAt')

                        if not published_at: continue

                        # Acumular as descrições das notícias para a ação
                        all_descriptions.append(description)

                        # Converter a data de publicação para o formato DateTimeField do Django
                        data_publicacao = parse_datetime(published_at)      

                        # Verificar se a notícia já foi armazenada para evitar duplicatas
                        if not Noticia.objects.filter(acao_selecionada=acao, url=article['url']).exists():                  
                            # Criar a nova notícia no banco de dados
                            Noticia.objects.create(
                                acao_selecionada=acao,
                                fonte=article.get('source', {}).get('name', 'Fonte desconhecida'),
                                conteudo=description,
                                url=article.get('url', ''),
                                data_publicacao=data_publicacao
                            )                                

                            # Incrementar o contador de notícias existentes
                            existing_news_count += 1
            
            # Gerar resumo se houver notícias
            if all_descriptions:
                full_text = ' '.join(all_descriptions)
                try:
                    resumo = summarizer.summarize(full_text, word_count=100)  # Ajustar o número de palavras conforme necessário
                except ValueError:
                    resumo = full_text[:500]  # Caso o texto seja muito curto para sumarização, usar os primeiros 500 caracteres

                # Salvar o resumo para a ação (caso deseje salvar o resumo no modelo de notícia ou em um campo específico)
                Noticia.objects.create(
                    acao_selecionada=acao,
                    resumo=resumo,
                    data_geracao=today_date
                )
                
            else:
                logger.debug(f"Nenhuma notícia relevante encontrada para {acao.simbolo}")

        else:
            error_message = news_data.get('message', 'Erro desconhecido ao buscar notícias.')
            logger.debug(f"Erro ao buscar notícias para {acao.simbolo}: {error_message}")

@shared_task
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

        if cliente.plano.nome_plano != "Pro":
            if datetime.now().hour < end_fetch_news: 
                continue

        limite_noticias = cliente.plano.qtdade_noticias if cliente.plano else max_daily_news
        acoes = cliente.tickers.all()

        if not acoes:
            continue

        # Carregar todas as notícias das ações do cliente
        acoes_com_noticias = []
        for acao in acoes:
            noticias = Noticia.objects.filter(acao_selecionada=acao).order_by('-id')[:limite_noticias]
            
            # Verifica se há notícias
            if noticias:
                acoes_com_noticias.append({
                    'nome': acao.nome,
                    'simbolo': acao.simbolo,
                    'noticias': noticias
                })
            else:
                # Adiciona uma mensagem indicando que não há notícias
                acoes_com_noticias.append({
                    'nome': acao.nome,
                    'simbolo': acao.simbolo,
                    'noticias': None  # Marca que não há notícias
                })

        if acoes_com_noticias:
            # Renderizar o template HTML e passar o CSS como contexto
            full_email_content = render_to_string('noticias/news_email.html', {
                'css_content': css_content,  # Passa o CSS dinamicamente
                'acoes': acoes_com_noticias,
            })

            # Enviar o e-mail
            subject = "Notícias diárias das suas ações"
            send_mail(
                subject,
                '',  
                'renan.acg7@gmail.com',
                [cliente.email],
                fail_silently=False,
                html_message=full_email_content
            )

@shared_task
def send_whatsapp_news(*args, **kwargs):  

    # Selecionar clientes com plano Pro
    pro_clients = Cliente.objects.filter(plano__nome_plano="Pro")

    # Iterar sobre os clientes Pro
    for cliente in pro_clients:

        # Verificar se há novas notícias para este cliente
        novas_noticias = Noticia.objects.filter(
            acao_selecionada__in=cliente.tickers.all(),            
        )

        # Se houver novas notícias, enviar via WhatsApp
        if novas_noticias:

            for noticia in novas_noticias:

                # Inicializar o pipeline de sumarização usando a GPU (se disponível)
                # summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=0 if torch.cuda.is_available() else -1)
                summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=0 if torch.cuda.is_available() else -1)

                
                try:
                    resumo = summarizer(noticia.conteudo, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
                except Exception as e:
                    resumo = noticia.conteudo  # Caso haja um erro ou o conteúdo seja pequeno, usar o conteúdo original

                mensagem = (
                    f"📰 *Nova notícia sobre a ação da empresa {noticia.acao_selecionada.nome} ({noticia.acao_selecionada.simbolo}):*\n\n"
                    f"*🔹 Fonte:* {noticia.fonte}\n\n"
                    f"*🔹 Data de publicação:* {noticia.data_publicacao.strftime('%d/%m/%Y %H:%M')}\n\n"
                    f"*🔹 Resumo da notícia:*\n"
                    f"{resumo}\n\n"
                    f"*🔹 Leia mais no link abaixo:*\n{noticia.url if noticia.url else 'Nenhum link disponível'}"
                )                

                try:

                    message = client_twilio.messages.create(
                        body=mensagem,
                        from_='whatsapp:' + settings.TWILIO_PHONE_NUMBER,                                                         
                        to='whatsapp:' + f'+55{cliente.whatsapp}'
                    )                    
                    
                    if message.status in ['queued', 'sending', 'sent']:
                        logger.debug(f"Mensagem enviada com sucesso para {cliente.nome}: {message.sid}")
                    elif message.status == 'delivered':
                        logger.debug(f"Mensagem entregue com sucesso para {cliente.nome}.")
                    elif message.status in ['undelivered', 'failed']:
                        logger.debug(f"Falha ao enviar mensagem para {cliente.nome}: {message.status}")

                except Exception as e:
                    logger.debug(f"Erro ao enviar mensagem para {cliente.nome}: {str(e)}") 

    gc.collect()

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
        send_daily_news_email.s(),
        send_whatsapp_news.s(),    

    ).apply_async()

@shared_task
def daily_data_cleanup():    
    
    chain(
        delete_unassociated_stocks.s(),
        delete_unassociated_tokens.s(),
        delete_previous_day_news.s()
    ).apply_async()

