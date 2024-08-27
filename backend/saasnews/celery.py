from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# celery -A saasnews worker -l info
# celery -A saasnews beat -l info

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saasnews.settings')

app = Celery('saasnews')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.timezone = 'America/Sao_Paulo'
app.conf.enable_utc = False

app.autodiscover_tasks(['noticias'])

app.conf.beat_schedule = {
    'fetch-daily-news': {
        'task': 'noticias.tasks.fetch_news_for_stocks',  
        'schedule': crontab(hour=23, minute=25),
    },
    'send-news-email': {
        'task': 'noticias.tasks.send_daily_news_email',  
        'schedule': crontab(hour=23, minute=26),
    },
    'monitor-news-every-minute': {
        'task': 'noticias.tasks.monitor_news_for_pro_clients',
        'schedule': crontab(minute='*/1'),  # A cada minuto
    },
    # 'cobrar-mensalidade-diaria': {
    #     'task': 'noticias.tasks.monthly_payment',
    #     'schedule': crontab(hour=0, minute=35),  # Rodar todos os dias
    # },
}
