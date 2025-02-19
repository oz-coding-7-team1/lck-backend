from django.contrib import admin
from django.utils.html import format_html

from apps.common.admin import BaseModelAdmin

from .models import Player


@admin.register(Player)
class PlayerAdmin(BaseModelAdmin):
    list_display = ("id","get_nickname_with_realname", "position", "get_team", "get_tags")
    list_filter = ("team",)
    search_fields = ("id", "nickname", "realname", "team__name", "tags__name")
    list_display_links = ("id", "get_nickname_with_realname", "get_team")
    
    def get_nickname_with_realname(self, obj):
        return f"{obj.nickname} ({obj.realname})"
    
    def get_team(self, obj):
        if obj.team is None:
            return "-"
        return format_html(
            '<a href="{}">{}</a>',
            f'/admin/teams/team/{obj.team.id}/change/',
            obj.team
        )
    
    def get_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())
    
    get_tags.short_description = "Tags"