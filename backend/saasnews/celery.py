from __future__ import absolute_import, unicode_literals
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saasnews.settings')

app = Celery('saasnews')

# Configuração do Celery a partir das configurações do Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Definir o timezone
app.conf.timezone = 'America/Sao_Paulo'
app.conf.enable_utc = False

# Definir a reconexão ao broker no startup
app.conf.broker_connection_retry_on_startup = True 
app.conf.broker_connection_max_retries = None  # Tentar indefinidamente
app.conf.broker_connection_retry_interval = 10  # Intervalo de 10 segundos entre as tentativas


# Autodiscover tasks em todos os apps instalados
app.autodiscover_tasks(['noticias'])

start_fetch_news = settings.START_FETCH_NEWS
end_fetch_news = settings.END_FETCH_NEWS

# Definir o beat_schedule
app.conf.beat_schedule = {
    
    'fetch-and-send-daily-news': {
        'task': 'noticias.tasks.fetch_and_send_news_chain',  # Referência à task encadeada
        'schedule': crontab(minute=f'*/{settings.FETCH_AND_SEND_DAILY_NEWS_INTERVAL_MINUTE}', hour=f'{start_fetch_news}-{end_fetch_news}'),
    },
    'check-dividends-daily': {
        'task': 'noticias.tasks.check_and_save_dividend_news',
        'schedule': crontab(hour=settings.CHECK_DIVIDENDS_DAILY_INTERVAL_HOUR, minute=settings.CHECK_DIVIDENDS_DAILY_INTERVAL_MINUTE),  
    },
    'daily-cleanup': {
        'task': 'noticias.tasks.daily_data_cleanup',
        'schedule': crontab(hour=settings.DELETE_PREVIOUS_DATA_HOUR, minute=settings.DELETE_PREVIOUS_DATA_MINUTE),  
    },    
}