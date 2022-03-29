from django.core.mail import send_mail

from Helpdesk.celery import app

@app.task
def email(request_id, sender, recipient, new_status):
    send_mail(
        f'Изменен статус Вашей заявки №{request_id}',
        f'Изменен статус Вашей заявки №{request_id} - {new_status}',
        sender,
        [recipient],
        fail_silently=True,
    )