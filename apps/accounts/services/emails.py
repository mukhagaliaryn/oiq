from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


def send_registration_success_email(user):
    subject = _('Welcome to the OIQ platform!')
    context = {
        'user': user,
        'platform_name': 'OIQ',
    }
    text_content = render_to_string(
        'accounts/auth/email/registration_success.txt',
        context,
    )
    html_content = render_to_string(
        'accounts/auth/email/registration_success.html',
        context,
    )
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    email.attach_alternative(html_content, 'text/html')
    email.send(fail_silently=False)
