"""
Django settings for backend project.

Generated by 'django-admin startproject' using Django 5.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

APPEND_SLASH = False
FCM_SERVER_KEY = "BKM1av-IBAu2ORof5Du6PlCvbg9pJMLPvDhhFWcmE0TuQj7vd2Sr2S2jHBNrqOwqS0xlIJ7Qt7Dr-8GuyFy07JY"
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-4+7xmrg12uqb#68w=3yz@)nxnnb)v#hf@jj^b%(4b04wuaei^w'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

ONESIGNAL_APP_ID = '5f7fb217-caf4-4e0e-9aa6-28e73ef970f9'
ONESIGNAL_REST_API_KEY = 'os_v2_app_l573ef6k6rha5gvgfdtt56lq7fmfpcp4wi5et5evzfzvraoabjb3anlfaovw76ljosc7ywwqqslko6c4zwp4snmmnbylchb57rlcyka'
# Application definition

HMS_APP_ACCESS_KEY = "68525572145cb4e8449afcd9"  # From Developer > Access Credentials
HMS_APP_SECRET = "f_yesDyJ4nDhlgYMO9DO1r9MwxPhN4I9MDRTajcljhF3icTKgQsWgT_TvdQKe4D4_WXMmR3WTaykpokgz8O4d2lVm8p4i3Fdjto_cknEgFJSplKC3JGtI6FGhYVHpeGI2hhFLDOx4JxtQnxRsYE2OCXIhElXRBTeEEmJIQc_UT4="
HMS_API_BASE_URL = "https://api.100ms.live/v2"
HMS_TEMPLATE_ID = "68563d9374147bd574ba4cb3"



INSTALLED_APPS = [
    'daphne',
    'channels',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'chat',
    'user',
]
#Daphane
ASGI_APPLICATION = 'backend.asgi.application'
# settings.py

import os  # Make sure this is at the top of the file

STATIC_URL = '/static/'

# ✅ Add this line below STATIC_URL
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
AUTH_USER_MODEL = 'user.CustomUser'

# Channels configuration
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                "redis://default:usBS4QJd1VkzdFlc3FAB2hWKV8nAUXIQ@redis-16662.c321.us-east-1-2.ec2.redns.redis-cloud.com:16662"
            ]
        },
    },
}
#upstash

"""CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [{
                "address": "rediss://default:AT5qAAIjcDE1YzEwMTRiYTE3NTM0MjhhYTlmNmE3ZjZhZTczZGU3ZXAxMA@driving-cockatoo-15978.upstash.io:6379",
                
            }],
        },
    },
}"""



# Channels configuration for Redis
"""CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6380)],
        },
    },
}
"""
import os
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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
CORS_ALLOW_ALL_ORIGINS = True 
ROOT_URLCONF = 'backend.urls'

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

WSGI_APPLICATION = 'backend.wsgi.application'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'Neondb',
        'USER': 'Neondb_owner',
        'PASSWORD': 'npg_O8yEZRHsW4Qt',
        'HOST': 'ep-flat-river-a8x5lgti-pooler.eastus2.azure.neon.tech',
        'PORT': '5432',
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}"""

"""DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'defaultdb',  # Your database name
        'USER': 'avnadmin',  # Your username
        'PASSWORD': 'AVNS_9MLHjLDbBJdWuJZyr1w',  # Your password
        'HOST': 'mysql-1f71f1e7-umairsaeed320-5b63.d.aivencloud.com',  # Your host
        'PORT': '27629',  # Your port
        'OPTIONS': {
            'ssl_mode': 'REQUIRED',  # Required SSL mode
        }
    }
}"""





# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
