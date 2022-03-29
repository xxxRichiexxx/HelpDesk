from django.core.mail import send_mail
from django.conf import settings

from Helpdesk.celery import app


@app.task
def send_report():
    send_mail(
        f'Отчет',
        f'Отчет',
        settings.EMAIL_HOST_USER,
        ['andrey_dzr@mail.ru'],
        fail_silently=True,
    )
