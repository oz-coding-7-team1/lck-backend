from django.contrib import admin

from apps.cloud_images.models import PlayerImage, TeamImage, UserImage
from apps.common.admin import BaseModelAdmin


@admin.register(UserImage)
class UserImageAdmin(BaseModelAdmin):
    pass


@admin.register(PlayerImage)
class PlayerImageAdmin(BaseModelAdmin):
    pass


@admin.register(TeamImage)
class TeamImageAdmin(BaseModelAdmin):
    pass
