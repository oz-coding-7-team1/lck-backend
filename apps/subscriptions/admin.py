from django.contrib import admin

from .models import PlayerSubscription, TeamSubscription


# Register your models here.
@admin.register(PlayerSubscription, TeamSubscription)
class PlayerSubscriptionAdmin(admin.ModelAdmin):  # type: ignore
    pass


class TeamSubscriptionAdmin(admin.ModelAdmin):  # type: ignore
    pass
