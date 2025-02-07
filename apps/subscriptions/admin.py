from typing import Any, Tuple

from django.contrib import admin
from django_softdelete.admin import SoftDeletedModelAdmin

from .models import PlayerSubscription, TeamSubscription


class SoftDeleteListFilter(admin.SimpleListFilter):
    title = "삭제 여부"
    parameter_name = "deleted_at"

    def lookups(self, request: Any, model_admin: Any) -> Tuple[Tuple[str, str], ...]:
        return (
            ("True", "삭제됨"),
            ("False", "삭제되지 않음"),
        )

    def queryset(self, request: Any, queryset: Any) -> Any:
        if self.value() == "True":
            return queryset.filter(deleted_at__isnull=False)
        elif self.value() == "False":
            return queryset.filter(deleted_at__isnull=True)
        return queryset


@admin.register(PlayerSubscription)
class PlayerSubscriptionAdmin(SoftDeletedModelAdmin, admin.ModelAdmin):  # type: ignore
    list_display = ("user", "player", "deleted_at", "restored_at")
    list_filter = (SoftDeleteListFilter,)

    def is_deleted(self, obj):  # type: ignore
        return obj.deleted_at is not None

    is_deleted.boolean = True  # type: ignore


@admin.register(TeamSubscription)
class TeamSubscriptionAdmin(SoftDeletedModelAdmin, admin.ModelAdmin):  # type: ignore
    list_display = ("user", "team", "deleted_at", "restored_at")
    list_filter = (SoftDeleteListFilter,)

    def is_deleted(self, obj):  # type: ignore
        return obj.deleted_at is not None

    is_deleted.boolean = True  # type: ignore
