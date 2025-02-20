from .base import *

DEBUG = True

REFRESH_TOKEN_COOKIE_SECURE = False

# ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")

INSTALLED_APPS += [
    "drf_spectacular",
]

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=300),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

REST_FRAMEWORK.update(
    {
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    }
)

# 로컬용
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": "oz_main_dev",
#         "USER": "oz_main_dev",
#         "PASSWORD": 1234,
#         "HOST": os.getenv("127.0.0.1", "localhost"),
#         "PORT": os.getenv("DB_PORT", "5432"),
#     }
# }
