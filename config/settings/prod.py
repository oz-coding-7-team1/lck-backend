from .base import *

DEBUG = False

REFRESH_TOKEN_COOKIE_SECURE = True

ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")  # 허용할 host

SIMPLE_JWT = {
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=3),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
}

# # 테스트용
# INSTALLED_APPS += [
#     "drf_spectacular",
# ]

# REST_FRAMEWORK.update(
#     {
#         "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
#     }
# )
