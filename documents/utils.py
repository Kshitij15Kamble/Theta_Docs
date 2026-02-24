import os
from pdf2image import convert_from_path
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
    if not doc_id:
        return []

    output_dir = os.path.join(settings.MEDIA_ROOT, "converted", f"doc_{doc_id}")
    os.makedirs(output_dir, exist_ok=True)

    # If already converted, reuse images
    existing = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.endswith(".png")
    ])

    if existing:
        return existing

    # Convert PDF to images
    pages = convert_from_path(file_path, dpi=120)

    image_paths = []
    for i, page in enumerate(pages, start=1):
        img_path = os.path.join(output_dir, f"page_{i}.png")
        page.save(img_path, "PNG")
        image_paths.append(img_path)

    return image_paths

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



