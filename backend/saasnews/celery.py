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

# Autodiscover tasks em todos os apps instalados
app.autodiscover_tasks(['noticias'])

# Definir o beat_schedule
app.conf.beat_schedule = {
    'fetch-and-send-daily-news': {
        'task': 'noticias.tasks.fetch_and_send_news_chain',  # Referência à task encadeada
        'schedule': crontab(hour=settings.FETCH_AND_SEND_DAILY_NEWS_INTERVAL_HOUR, minute=settings.FETCH_AND_SEND_DAILY_NEWS_INTERVAL_MINUTE),
    },
    'monitor-news-pro': {
        'task': 'noticias.tasks.monitor_news_for_pro_clients',
        'schedule': crontab(minute=f'*/{settings.PRO_MONITOR_NEWS_INTERVAL_MINUTES}'),
    },
    'delete-previous-day-news': {
        'task': 'noticias.tasks.delete_previous_day_news',
        'schedule': crontab(hour=settings.DELETE_PREVIOUS_DAY_NEWS_INTERVAL_HOUR, minute=settings.DELETE_PREVIOUS_DAY_NEWS_INTERVAL_MINUTE),  
    },
    'check-dividends-daily': {
        'task': 'noticias.tasks.check_and_save_dividend_news',
        'schedule': crontab(hour=settings.CHECK_DIVIDENDS_DAILY_INTERVAL_HOUR, minute=settings.CHECK_DIVIDENDS_DAILY_INTERVAL_MINUTE),  
    },
    'delete-unassociated-stocks-every-day': {
        'task': 'noticias.tasks.delete_unassociated_stocks',  
        'schedule': crontab(hour=settings.DELETE_STOCKS_INTERVAL_HOUR, minute=settings.DELETE_STOCKS_INTERVAL_MINUTE),  
    },
    'delete-unassociated-tokens-every-day': {
        'task': 'noticias.tasks.delete_unassociated_tokens',  
        'schedule': crontab(hour=settings.DELETE_TOKENS_INTERVAL_HOUR, minute=settings.DELETE_TOKENS_INTERVAL_MINUTE),  
    },
}
