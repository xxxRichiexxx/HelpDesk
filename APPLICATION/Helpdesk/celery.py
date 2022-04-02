import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Helpdesk.settings')

app = Celery('Helpdesk')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-report-two-times': {
        'task': 'analytics.tasks.send_report',
        'schedule': crontab(minute=0, hour='10,17')
    },
    'bot-executor-every-single-minute': {
        'task': 'userapp.tasks.bot_executor',
        'schedule': crontab()
    },
}
