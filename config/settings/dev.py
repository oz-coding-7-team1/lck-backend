from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS += [
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "lck",  # 로컬 개발용 DB 이름
        "USER": "lck",  # PostgreSQL 사용자명
        "PASSWORD": "1234",  # 비밀번호
        "HOST": "localhost",
        "PORT": "5432",
    }
}