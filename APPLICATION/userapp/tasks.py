from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import get_user_model
from django.conf import settings

from Helpdesk.celery import app
from .models import Request, Message


User = get_user_model()


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


@app.task
def bot_executor():
    bot = User.objects.get(username='admin')
    request_for_executing = Request.objects.filter(Status='new')
    for request in request_for_executing:
        Message.objects.create(
            IDRequest=request,
            Text='Мы уже работаем над этим!',
            IDAuthor=bot,
            IDRecipient=request.IDAuthor,
        )
        request.Status = 'in_work'
        request.IDExecutor = bot
        request.save()
        email.delay(
            request.id,
            settings.EMAIL_HOST_USER,
            request.IDAuthor.email,
        )
