import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-your-key-here')

DEBUG = True

ALLOWED_HOSTS = []

# -----------------------------
# Application Definition
# -----------------------------
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Your Apps
    'admin_app',
    'core',
    'customer',
    'seller',

    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # Google Provider
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1

# -----------------------------
# Middleware
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Allauth Middleware
    'allauth.account.middleware.AccountMiddleware',
]

# -----------------------------
# URL Configuration
# -----------------------------
ROOT_URLCONF = 'pro1.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # Required by Allauth
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pro1.wsgi.application'

# -----------------------------
# Database
# -----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# -----------------------------
# Custom User Model
# -----------------------------
AUTH_USER_MODEL = 'core.User'

# -----------------------------
# Authentication Backends
# -----------------------------
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# -----------------------------
# Allauth Configuration
# -----------------------------
# Removed deprecated allauth settings
ACCOUNT_LOGIN_METHODS = {"email": True}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]

ACCOUNT_EMAIL_VERIFICATION = "none"

ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGOUT_ON_GET = True

LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# Custom Adapters
ACCOUNT_ADAPTER = 'core.adapter.MyLoginAdapter'
SOCIALACCOUNT_ADAPTER = 'core.adapter.MySocialAccountAdapter'

# Auto connect existing users
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True

# -----------------------------
# Google Provider Settings
# -----------------------------
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email'
        ],
        'AUTH_PARAMS': {
            'access_type': 'online'
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}

# -----------------------------
# Static Files
# -----------------------------
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / "static"
]

# -----------------------------
# Media Files
# -----------------------------
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# -----------------------------
# Email Configuration (OTP / Verification)
# -----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "musi974798@gmail.com"
EMAIL_HOST_PASSWORD = "pewd dlqp cyow clak"

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER