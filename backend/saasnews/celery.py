from __future__ import absolute_import, unicode_literals
import os
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
        'schedule': crontab(minute='*'),
    },
    'monitor-news-every-hour': {
        'task': 'noticias.tasks.monitor_news_for_pro_clients',
        'schedule': crontab(minute=0, hour='*/1'),  # Executa a cada hora
    },
    'delete-previous-day-news-every-day': {
        'task': 'noticias.tasks.delete_previous_day_news',
        'schedule': crontab(hour=0, minute=1),  # Executa à meia-noite e um
    },
    'check-dividends-daily': {
        'task': 'noticias.tasks.check_and_save_dividend_news',
        'schedule': crontab(hour=10, minute=0),  
    },
    'delete-unassociated-stocks-every-day': {
        'task': 'noticias.tasks.delete_unassociated_stocks',  # Corrigi o caminho da task
        'schedule': crontab(minute=0, hour=0),  # Executa todos os dias à meia-noite
    },
}
