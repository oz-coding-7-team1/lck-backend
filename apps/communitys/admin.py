from django.contrib import admin

from apps.common.admin import BaseModelAdmin

from .models import Like, PlayerComment, PlayerPost, TeamComment, TeamPost


@admin.register(TeamPost)
class TeamPostAdmin(BaseModelAdmin):
    pass


@admin.register(TeamComment)
class TeamCommentAdmin(BaseModelAdmin):
    pass


@admin.register(PlayerPost)
class PlayerPostAdmin(BaseModelAdmin):
    pass


@admin.register(PlayerComment)
class PlayerCommentAdmin(BaseModelAdmin):
    pass


@admin.register(Like)
class LikeAdmin(BaseModelAdmin):
    pass
