from .base import *

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "oz_main_dev",
        "USER": "oz_main_dev",
        "PASSWORD": 1234,
        "HOST": os.getenv("127.0.0.1", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}
