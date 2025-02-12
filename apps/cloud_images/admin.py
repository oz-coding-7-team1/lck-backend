from django.contrib import admin

from apps.common.admin import BaseModelAdmin

from .models import PlayerImage, TeamImage


@admin.register(PlayerImage)
class PlayerImageAdmin(BaseModelAdmin):
    pass


@admin.register(TeamImage)
class TeamImageAdmin(BaseModelAdmin):
    pass
