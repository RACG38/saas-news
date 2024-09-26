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
    yesterday = datetime.today().date() - timedelta(days=1)
    # Filtra as notícias que têm data de publicação do dia anterior e as exclui
    Noticia.objects.filter(data_publicacao__date=yesterday).delete()

    gc.collect()

@shared_task(rate_limit='10/m')
def fetch_news_for_stocks():

    # Definir o fuso horário de Brasília (UTC-3)
    brasilia_tz = pytz.timezone('America/Sao_Paulo')

    # Hora atual no fuso horário de Brasília
    current_time_brasilia = timezone.now().astimezone(brasilia_tz)
    current_hour_brasilia = current_time_brasilia.hour  # Verifica a hora atual no fuso horário de Brasília

    if start_fetch_news <= current_hour_brasilia < end_fetch_news:

        acoes = AcaoSelecionada.objects.all()
        three_days_ago = datetime.now() - timedelta(days=5)

        # Formata a data de três dias atrás para o formato ISO 8601 (necessário para a URL)
        from_time = three_days_ago.replace(hour=0, minute=0, second=0, microsecond=0)

        for acao in acoes:
            # Gera a URL com a data de três dias atrás
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

                # Para cada artigo, salvar o conteúdo completo ou descrição no banco de dados
                for article in news_data.get('articles', []):
                    description = article.get('description', '')
                    content = article.get('content', '')  # Tentar pegar o conteúdo completo da notícia

                    if not description and not content:
                        continue

                    # Verificar se o conteúdo contém o símbolo ou o nome da ação (case-insensitive)
                    description_lower = description.lower()
                    simbolo_lower = acao.simbolo.lower()
                    nome_lower = acao.nome.lower()

                    if simbolo_lower in description_lower or nome_lower in description_lower:
                        full_text = content if content else description

                        # Verificar se o texto já existe no banco de dados
                        if not Noticia.objects.filter(acao_selecionada=acao, conteudo=full_text).exists():
                            # Salvar o conteúdo completo da notícia
                            Noticia.objects.create(
                                acao_selecionada=acao,
                                conteudo=full_text
                            )
                        else:
                            logger.debug(f"Notícia já existente para {acao.simbolo}")

            else:
                logger.debug(f"Erro ao buscar notícias para {acao.simbolo}: {news_data.get('message', 'Erro desconhecido ao buscar notícias.')}")


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

        if cliente.plano.nome_plano != "Pro":
            if datetime.now().hour < end_fetch_news: 
                continue

        limite_noticias = cliente.plano.qtdade_noticias if cliente.plano else max_daily_news
        acoes = cliente.tickers.all()

        if not acoes:
            continue

        # Variável para indicar se há pelo menos uma notícia válida
        has_valid_news = False

        # Carregar todas as notícias das ações do cliente
        acoes_com_noticias = []
        for acao in acoes:
            noticias = Noticia.objects.filter(acao_selecionada=acao).order_by('-id')[:limite_noticias]
            
            # Verifica se há notícias com conteúdo válido
            noticias_validas = [noticia for noticia in noticias if noticia.conteudo and noticia.conteudo.strip()]

            if noticias_validas:
                # Gerar um resumo dos principais assuntos das notícias
                resumo = "\n".join([summarizer.summarize(noticia.conteudo, ratio=0.2) for noticia in noticias_validas])

                # Separar o conteúdo das notícias em uma lista de tópicos
                topicos = [noticia.conteudo.split('\n') for noticia in noticias_validas]
                
                # Links das notícias
                links_noticias = "\n".join([noticia.url for noticia in noticias_validas if noticia.url])

                acoes_com_noticias.append({
                    'nome': acao.nome,
                    'simbolo': acao.simbolo,
                    'resumo': resumo,
                    'topicos': topicos,  # Passar os tópicos pré-processados
                    'url': links_noticias
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
            send_mail(
                subject,
                '',  
                'renan.acg7@gmail.com',
                [cliente.email],
                fail_silently=False,
                html_message=full_email_content
            )
        else:
            logger.debug(f"Sem notícias válidas para enviar para o cliente {cliente.nome}")


@shared_task(rate_limit='5/m') 
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

            # Inicializar uma variável para armazenar todas as notícias
            mensagem_completa = f"📰 *Resumo de notícias sobre as ações do cliente {cliente.nome}:*\n\n"

            for noticia in novas_noticias:

                # Verificar se a notícia tem conteúdo antes de prosseguir
                if noticia.conteudo and noticia.conteudo.strip():  # Garantir que não esteja vazio

                    # Inicializar o pipeline de sumarização usando a GPU (se disponível)
                    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", device=0 if torch.cuda.is_available() else -1)

                    try:
                        resumo = summarizer(noticia.conteudo, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
                    except Exception as e:
                        resumo = noticia.conteudo  # Caso haja um erro ou o conteúdo seja pequeno, usar o conteúdo original

                    # Verificar se a data de publicação não é None
                    if noticia.data_publicacao:
                        data_publicacao_formatada = noticia.data_publicacao.strftime('%d/%m/%Y %H:%M')
                    else:
                        data_publicacao_formatada = "Data não disponível"

                    # Montar a nova parte da mensagem
                    nova_mensagem = (
                        f"*🔹 Ação:* {noticia.acao_selecionada.nome} ({noticia.acao_selecionada.simbolo})\n"
                        f"*🔹 Fonte:* {noticia.fonte}\n"
                        f"*🔹 Data de publicação:* {data_publicacao_formatada}\n"
                        f"*🔹 Resumo:* {resumo}\n"
                        f"*🔹 Leia mais no link abaixo:*\n{noticia.url if noticia.url else 'Nenhum link disponível'}\n\n"
                    )

                    # Verificar se a nova mensagem cabe no limite de caracteres
                    if len(mensagem_completa) + len(nova_mensagem) <= max_twilio_characters:
                        mensagem_completa += nova_mensagem
                    else:
                        logger.debug(f"A notícia sobre {noticia.acao_selecionada.nome} foi omitida devido ao limite de caracteres.")

            # Enviar todas as notícias em uma única mensagem
            if mensagem_completa.strip():  # Verificar se há conteúdo para enviar
                try:
                    message = client_twilio.messages.create(
                        body=mensagem_completa,
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
                    
    torch.cuda.empty_cache()
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

