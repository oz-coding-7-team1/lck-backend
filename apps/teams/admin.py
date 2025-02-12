from django.contrib import admin

from apps.common.admin import BaseModelAdmin

from .models import Team


@admin.register(Team)
class TeamAdmin(BaseModelAdmin):
    pass
