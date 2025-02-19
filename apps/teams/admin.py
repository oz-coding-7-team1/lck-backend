from django.contrib import admin

from apps.common.admin import BaseModelAdmin

from .models import Team, TeamSchedule


@admin.register(Team)
class TeamAdmin(BaseModelAdmin):
    pass


@admin.register(TeamSchedule)
class TeamScheduleAdmin(BaseModelAdmin):
    pass
