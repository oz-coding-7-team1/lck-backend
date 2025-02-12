from django.contrib import admin

from apps.common.admin import BaseModelAdmin

from .models import Player


@admin.register(Player)
class PlayerAdmin(BaseModelAdmin):
    pass
