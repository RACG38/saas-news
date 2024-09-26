from pathlib import Path
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
STRIPE_PUBLICABLE_KEY = os.getenv('STRIPE_PUBLICABLE_KEY')
GOOGLE_NEWS_API_KEY = os.getenv('GOOGLE_NEWS_API_KEY')

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = '+14155238886'

DOMAIN_NEWS = {"infomoney.com.br", "suno.com.br", "uol.com.br", "dinheirama.com.br"}

# Variáveis de tempo para execução das funções
MAX_NEWS_DAILY = 5 # Quantidade máxima de notícias diárias por ação
START_FETCH_NEWS = 0 # Inicio do pregão
END_FETCH_NEWS =  24 # Horário após o fim do pregão

MAX_CHARACTERS = 1600

FETCH_AND_SEND_DAILY_NEWS_INTERVAL_MINUTE = 2
CHECK_DIVIDENDS_DAILY_INTERVAL_HOUR = 3
CHECK_DIVIDENDS_DAILY_INTERVAL_MINUTE = 40
DELETE_PREVIOUS_DATA_HOUR = 0
DELETE_PREVIOUS_DATA_MINUTE = 0

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Exemplo: ajuste conforme seu front-end (Renan pegou no chatgpt dia 11/08)
]

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-bqhh%_%z$i^fbfo_mgvr77fb*xz*cez05(hzeq5jwqila7cc09'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'noticias',
    'rest_framework',
    'corsheaders',
    'rest_framework_simplejwt',    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'saasnews.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Adicione o caminho correto se seus templates estiverem em uma pasta global
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

WSGI_APPLICATION = 'saasnews.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Se estiver usando pathlib
        # ou
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # Se estiver usando os.path
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

# TIME_ZONE = 'UTC'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # Certifique-se de definir uma chave secreta segura
    # Outras configurações opcionais...
}

# Exemplo de configuração para Gmail
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'renan.acg7@gmail.com'
EMAIL_HOST_PASSWORD = 'alnc xkvd kfwz zgif'
DEFAULT_FROM_EMAIL = 'renan.acg7@gmail.com'

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
CELERY_ENABLE_UTC = False  # Define que o Celery deve usar o fuso horário local em vez de UTC
CELERY_USE_TZ = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',  # Mude para INFO, WARNING, etc., conforme necessário
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',  # Mostrar apenas avisos e erros para Django
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',  # Mostrar apenas erros para requests do Django
            'propagate': False,
        },
        # Logger para seu código customizado
        'my_custom_logger': {
            'handlers': ['console'],
            'level': 'DEBUG',  # Manter DEBUG para seu logger
            'propagate': False,
        },
    },
}


