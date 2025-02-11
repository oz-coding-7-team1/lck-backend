from django.contrib import admin

from .models import PlayerImage, TeamImage


@admin.register(PlayerImage)
class PlayerImageAdmin(admin.ModelAdmin):  # type: ignore
    pass


@admin.register(TeamImage)
class TeamImageAdmin(admin.ModelAdmin):  # type: ignore
    pass
