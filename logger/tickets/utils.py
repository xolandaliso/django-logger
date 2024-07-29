# utils.py

from django.core.mail import EmailMessage
from django.conf import settings

def send_email_notification(recipient_email, subject, message):
    email_from = settings.DEFAULT_FROM_EMAIL
    from_name = settings.EMAIL_FROM_NAME  # Generic name to use in the email
    # Create an email message
    email = EmailMessage(
        subject,
        message,
        f'{from_name} <{email_from}>',  # set the "From" name and email address
        [recipient_email]
    )
    email.send()