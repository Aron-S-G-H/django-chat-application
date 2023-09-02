from django.core.mail import send_mail
from django.conf import settings
from celery import shared_task


@shared_task
def send_email(random_code: int, user_email: str):
    try:
        send_mail(
            subject='Authentication Code',
            message=f'Your authentication code {random_code}',
            from_email=settings.EMAIL_HOST_USER, recipient_list=[user_email]
        )
        return True
    except:
        return False
