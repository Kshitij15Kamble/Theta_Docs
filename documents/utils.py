import secrets
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_secure_password(length=8):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))


def send_user_credentials_email(username, password, email):
    subject = "Your Secure Docs Account Access"
    message = f"""
Hello {username},

Your account has been created.

Login URL:
{settings.SITE_URL}/

Username: {username}
Temporary Password: {password}

Please login and change your password immediately.

Regards,
Secure Docs Team
"""

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )