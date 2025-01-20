"""
Django settings for listing project.

Generated by 'django-admin startproject' using Django 5.1.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# for JWT tokens
from datetime import timedelta 

# load variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4=9y%9s%k5=n=urgxcb&uzlu=l)!&2zhn9a1k+0j_s8c)_^@qr'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'api.imobiliare.casa']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',
    'django_cleanup',  # delete the image aftere deleteing the model  
    'rest_framework_simplejwt', 
    'rest_framework_simplejwt.token_blacklist',  
    'django_bleach', # for cleaning htmlfile fields      
    'django_filters', # for filtering fields    
    'corsheaders',       
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',       
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'listing.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'listing.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DATABASE_NAME'),
        'USER': os.getenv('DATABASE_USER'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': os.getenv('DATABASE_HOST'),
        'PORT': os.getenv('DATABASE_PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES', innodb_strict_mode=1",
        },
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Bucharest'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# maximum number of confirmation emails to an user    
MAX_CONFIRMATION_EMAILS = 2

AUTH_USER_MODEL = 'api.User'

# for JWT authentication
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    # 'DEFAULT_THROTTLE_CLASSES': [
    #     'rest_framework.throttling.AnonRateThrottle',  # Pentru utilizatori anonimi
    #     'rest_framework.throttling.UserRateThrottle',  # Pentru utilizatori autentificați
    # ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '3/min',  # Permite 3 cereri pe minut pentru utilizatori anonimi
        'user': '1000/day',  # Permite 1000 de cereri pe zi pentru utilizatori autentificați
    },
    
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=120),  # Tokenul de acces va expira după 2 ore.
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),    # Tokenul de refresh va fi valid pentru o zi.
    'ROTATE_REFRESH_TOKENS': False,                # Tokenurile de refresh nu vor fi rotite.
    'BLACKLIST_AFTER_ROTATION': False,             # Tokenurile de refresh vechi nu vor fi adăugate în blacklist (nu este relevant dacă rotația este dezactivată).
    "UPDATE_LAST_LOGIN": True,                     # Se va actualiza câmpul `last_login` la fiecare utilizare a unui refresh token.
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': BASE_DIR / 'cache',  # Using BASE_DIR to set the cache directory,
        'TIMEOUT': 8 * 60 * 60,  # Timpul de expirare pentru cache (în secunde), 28800 seconds (8 hours) 
    }
}

# for bleach allowed tags
# Which HTML tags are allowed
BLEACH_ALLOWED_TAGS = ['p', 'br']

# Strip unknown tags if True, replace with HTML escaped characters if
# False
BLEACH_STRIP_TAGS = True

# custom variables
if DEBUG:
    PAGE_SIZE = 8
else:
    PAGE_SIZE = 20
    
SUGGESTION_LIMIT = 3  

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'WARNING',  # Setează nivelul la 'WARNING' pentru a evita logurile de tip 'INFO'
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',  # Setează nivelul pentru logger-ul Django la 'WARNING'
            'propagate': True,
        },
    },
}

SITE_NAME = 'Imobiliare.Casa'  
DEFAULT_FROM_EMAIL = "admin@imobiliare.casa"  # Adresa de email implicită pentru trimiterea emailurilor
FRONTEND_URL = "https://imobiliare.casa"  # URL-ul frontend-ului

# for testing
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# for email server
#EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'user@example.com'
EMAIL_HOST_PASSWORD = 'password'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",
    "https://imobiliare.casa",            
    # Add other allowed origins as needed
]