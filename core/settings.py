import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ===============================
# SECURITY
# ===============================
SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = [
    "theta-docs.onrender.com",
    "localhost",
    "127.0.0.1"
]

# ===============================
# APPLICATIONS
# ===============================
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'documents.apps.DocumentsConfig',
]

# ===============================
# MIDDLEWARE
# ===============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

# ===============================
# TEMPLATES
# ===============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# ===============================
# DATABASE (LOCAL + RENDER SAFE)
# ===============================
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL is not set. Please configure your .env file.")

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600
    )
}

# Enable SSL only for production (Render)
if "localhost" not in DATABASE_URL:
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
    }

# ===============================
# PASSWORD VALIDATION
# ===============================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 8},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# ===============================
# INTERNATIONALIZATION
# ===============================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

# ===============================
# STATIC FILES
# ===============================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / "documents" / "static",
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ===============================
# MEDIA FILES
# ===============================
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ===============================
# DEFAULT PK
# ===============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ===============================
# AUTH REDIRECTS
# ===============================
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = '/admin/documents/companydocument/'
LOGOUT_REDIRECT_URL = '/'

# ===============================
# JAZZMIN UI
# ===============================
JAZZMIN_SETTINGS = {
    "changeform_format": "single",
    "custom_css": "admin_custom.css",
    "site_title": "Theta Docs Admin",
    "site_header": "Theta Document Management",
    "site_brand": "Theta Docs",
    "welcome_sign": "Welcome to Theta Docs",
    "site_logo": "images/AdminLTELogo.png",
    "login_logo": "images/AdminLTELogo.png",
    "site_logo_classes": "img-circle elevation-3",
    "theme": "darkly",
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth.User": "fas fa-user",
        "auth.Group": "fas fa-users",
        "documents.CompanyDocument": "fas fa-file-pdf",
    },
    "footer": "Theta Docs © 2026 | Secure Document System",
}

# ===============================
# EMAIL CONFIG
# ===============================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# ===============================
# SITE URL
# ===============================
SITE_URL = os.environ.get("SITE_URL", "http://127.0.0.1:8000")

# ===============================
# SECURITY SETTINGS
# ===============================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"

X_FRAME_OPTIONS = "SAMEORIGIN"

# ===============================
# FILE SECURITY
# ===============================
SECURE_CONVERTED_ROOT = BASE_DIR / "secure_docs" / "converted"