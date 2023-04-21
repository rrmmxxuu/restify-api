"""
Django settings for restify project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
import os.path
import io
import dj_database_url
import environ
import google.auth

from urllib.parse import urlparse
from pathlib import Path
from google.oauth2 import service_account
from google.cloud import storage
from google.cloud import secretmanager

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# def get_secret(project_id, secret_name):
#     client = secretmanager.SecretManagerServiceClient()
#     secret_version_name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
#     response = client.access_secret_version(request={"name": secret_version_name})
#     return response.payload.data.decode("utf-8")

# def parse_secret(secret_value):
#     lines = secret_value.strip().split("\n")
#     env_vars = {}
#     for line in lines:
#         if line:
#             key, value = line.split("=", 1)
#             env_vars[key] = value
#     return env_vars

# PROJECT_ID = "restify-382711"
# SECRET_NAME = "django_settings"
# secret_value = get_secret(PROJECT_ID, SECRET_NAME)
# env_vars = parse_secret(secret_value)
# secret_value = get_secret(project_id, secret_id, version_id)
# print("Secret value:", secret_value)  # Add this line
# env_vars = parse_secret(secret_value)
# print("Parsed environment variables:", env_vars)  # Add this line

env = environ.Env(DEBUG=(bool, True))
env_file = os.path.join(BASE_DIR, ".env")

try:
    _, os.environ["GOOGLE_CLOUD_PROJECT"] = google.auth.default()
except google.auth.exceptions.DefaultCredentialsError:
    pass

if os.path.isfile(env_file):
    # Use a local secret file, if provided

    env.read_env(env_file)
# [START_EXCLUDE]
elif os.getenv("TRAMPOLINE_CI", None):
    # Create local settings if running with CI, for unit testing

    placeholder = (
        f"SECRET_KEY=a\n"
        "GS_BUCKET_NAME=None\n"
        f"DATABASE_URL=sqlite://{os.path.join(BASE_DIR, 'db.sqlite3')}"
    )
    env.read_env(io.StringIO(placeholder))
# [END_EXCLUDE]
elif os.environ.get("GOOGLE_CLOUD_PROJECT", None):
    # Pull secrets from Secret Manager
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")

    client = secretmanager.SecretManagerServiceClient()
    settings_name = os.environ.get("SETTINGS_NAME", "django_settings")
    name = f"projects/{project_id}/secrets/{settings_name}/versions/latest"
    payload = client.access_secret_version(name=name).payload.data.decode("UTF-8")

    print("Contents of the environment variables from Secret Manager:")
    print(payload)

    env.read_env(io.StringIO(payload))

else:
    raise Exception("No local .env or GOOGLE_CLOUD_PROJECT detected. No secrets found.")

SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-zd-ii!&3!ubnt*iiu+##=g4_k#=c-1f4^9%0%+2!j05o2x_@-)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']

# Custom settings
AUTH_USER_MODEL = 'accounts.User'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
client = storage.Client()
GS_PROJECT_ID = client.project
GS_BUCKET_NAME = env("GS_BUCKET_NAME")
GS_FILE_OVERWRITE = True
GS_QUERYSTRING_AUTH = False

REST_FRAMEWORK = {
    "NON_FIELD_ERRORS_KEY": "error",
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

from datetime import timedelta
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      },
    "DEFAULT_MODEL_RENDERING": "example"
   }
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ===== Package apps ===== #
    'drf_yasg',
    'multiselectfield',
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'storages',
    # ===== My own apps ===== #
    'apps.accounts',
    'apps.properties',
    'apps.reservations',
    'apps.comments',
    'apps.notifications'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'restify.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'restify.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASE_URL = env("DATABASE_URL")
DATABASES = {'default': dj_database_url.parse(DATABASE_URL)}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True

DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

# Use 'X-Forwarded-Proto' header for determining the scheme (http or https)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Set 'secure' flag on session cookies
SESSION_COOKIE_SECURE = True

# Set 'secure' flag on CSRF cookies
CSRF_COOKIE_SECURE = True
