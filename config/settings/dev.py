import os

from .base import *

DEBUG = True

ENV_FILE = BASE_DIR / f"envs/local.env"
# 필요시 export DJANGO_ENV=prod
# .toml 파일에 config.settings.prod 변경 후 mypy 실행

environ.Env.read_env(str(ENV_FILE))
# environ.Env.read_env()  # .envs 파일을 읽어옴

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("DJANGO_SECRET_KEY environment variable is not set.")

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

INSTALLED_APPS += [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "apps.users.apps.UsersConfig"
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "oz_main_dev",  # 로컬 개발용 DB 이름
        "USER": "oz_main_dev",  # PostgreSQL 사용자명
        "PASSWORD": "1234",  # 비밀번호
        "HOST": "localhost",
        "PORT": "5432",
    }
}
