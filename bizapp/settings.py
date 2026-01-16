
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: load secrets from environment in production
SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-please-change")
DEBUG = os.environ.get("DEBUG", "True").lower() in ("1", "true", "yes")
ALLOWED_HOSTS = (
    os.environ.get("ALLOWED_HOSTS", "").split(",")
    if os.environ.get("ALLOWED_HOSTS")
    else []
)

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "core",  # your app
]

ROOT_URLCONF = "bizapp.urls"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",  # REQUIRED for admin
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # REQUIRED for admin
    "django.contrib.messages.middleware.MessageMiddleware",  # REQUIRED for admin
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # points to your templates folder
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# Database: use MySQL directly
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "bizzapp",          # your MySQL database name
        "USER": "root",             # replace with your MySQL username
        "PASSWORD": "Rounak@8789",# replace with your MySQL password
        "HOST": "localhost",        # or your DB server IP
        "PORT": "3306",             # default MySQL port
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

#& .venv\Scripts\activate
# python manage.py runserver
#.\.venv\Scripts\python.exe manage.py runserver
'''git add .
git commit -m "Describe your change"
git push'''