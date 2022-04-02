from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ObjectDoesNotExist

from Helpdesk.celery import app
from .models import Request

@app.task
def email(request_id, sender, recipient):
    try:
        request = Request.objects.get(id=request_id)
    except ObjectDoesNotExist:
        print('Письмо не отправленою')
        return
    html_message = render_to_string('UserAPP/email.html', {'request': request})
    plain_message = strip_tags(html_message)
    send_mail(
        f'Изменен статус Вашей заявки №{request_id}',
        plain_message,
        sender,
        [recipient],
        fail_silently=True,
        html_message=html_message,
    )