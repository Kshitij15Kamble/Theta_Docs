import os
from pdf2image import convert_from_path
import aspose.words as aw
import secrets
import string
from django.core.mail import send_mail
from django.conf import settings


def generate_secure_password(length=12):
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(chars) for _ in range(length))


def send_user_credentials_email(username, password, email):
    subject = "Your Secure Docs Account Access"
    message = f"""
Hello {username},

Your account has been created.

Login URL:
{settings.SITE_URL}/login/

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

def convert_any_to_images(file_path, doc_id=None):
    images = []

    if not doc_id:
        return images

    output_dir = os.path.join(settings.MEDIA_ROOT, "converted", f"doc_{doc_id}")
    os.makedirs(output_dir, exist_ok=True)

    existing_files = sorted(os.listdir(output_dir))
    if existing_files:
        return [os.path.join(output_dir, f) for f in existing_files]

    if file_path.lower().endswith(".pdf"):
        pages = convert_from_path(file_path, dpi=120)

        for i, page in enumerate(pages):
            img_path = os.path.join(output_dir, f"page_{i+1}.png")
            page.save(img_path, "PNG")
            images.append(img_path)

    return images


def get_or_create_images(doc):
    doc_folder = os.path.join(
        settings.SECURE_CONVERTED_ROOT,
        f"doc_{doc.id}"
    )

    if os.path.exists(doc_folder) and os.listdir(doc_folder):
        return sorted([
            os.path.join(doc_folder, f)
            for f in os.listdir(doc_folder)
        ])

    os.makedirs(doc_folder, exist_ok=True)

    images = convert_from_path(doc.file.path, dpi=150)

    paths = []
    for i, img in enumerate(images, start=1):
        path = os.path.join(doc_folder, f"page_{i}.png")
        img.save(path, "PNG")
        paths.append(path)

    return paths



