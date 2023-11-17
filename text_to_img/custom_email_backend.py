import os

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from djoser.email import PasswordResetEmail
from djoser.utils import encode_uid

from text_to_img import settings
from user.models import EmailMessage


class CustomPasswordResetEmail(PasswordResetEmail):

    def send(self, to, *args, **kwargs):
        context = self.get_context_data()

        message = EmailMessage.objects.filter(event='reset_password').first()
        subject = message.subject
        reset_url = context['url']
        if message:
            message_text = message.message
        else:
            message_text = ''
        if '&lt;link&gt;' in message_text:
            message_text = message.replace('&lt;link&gt;', f'http://app.djangoboiler.xyz/{reset_url}')
        else:
            message_text += f'it is your unique link:\thttp://app.djangoboiler.xyz/{reset_url}\n'

        send_mail(
            subject=subject,
            message=f'',
            from_email=os.environ.get('DEFAULT_FROM_EMAIL'),
            recipient_list=[*to],
            fail_silently=False,
            html_message=message_text,
        )

    def get_context_data(self):
        message = EmailMessage.objects.filter(event='affiliate_accept').first()
        subject = message.subject
        context = super().get_context_data()

        user = context.get("user")
        context["uid"] = encode_uid(user.pk)
        context["token"] = default_token_generator.make_token(user)
        context["url"] = getattr(settings, 'DJOSER', {}).get('PASSWORD_RESET_CONFIRM_URL', '').format(
            uid=context["uid"], token=context["token"]
        )

        context["subject"] = subject

        return context