import os

from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")  # 허용할 host

ENV_FILE = BASE_DIR / f"envs/prod.env"

env.read_env(str(ENV_FILE))
# environ.Env.read_env()  # .envs 파일을 읽어옴

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("DJANGO_SECRET_KEY environment variable is not set.")

INSTALLED_APPS += [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
}
