"""
Django settings for VLE project.

Generated by 'django-admin startproject' using Django 2.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

# SECURITY WARNING: KEEP secret
SECRET_KEY = '{{SECRET_KEY}}'

from VLE.settings.base import *

# SECURITY WARNING: KEEP secret
LTI_SECRET = '{{LTI_SECRET}}'
LTI_KEY = '{{LTI_KEY}}'

BASELINK = '{{BASELINK}}'
CORS_ORIGIN_ALLOW_ALL = True

MIDDLEWARE = ['corsheaders.middleware.CorsMiddleware'] + MIDDLEWARE
ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.{{DATABASE_TYPE}}',
        'NAME': '{{DATABASE_NAME}}',
        'USER': '{{DATABASE_USER}}',
        'PASSWORD': '{{DATABASE_PASSWORD}}',
        'HOST': '{{DATABASE_HOST}}',
        'PORT': '{{DATABASE_PORT}}',
    }
}