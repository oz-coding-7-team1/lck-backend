from typing import Any, Tuple

from django.contrib import admin, messages

from apps.common.admin import BaseModelAdmin

from .models import PlayerSubscription, TeamSubscription

from django_softdelete.models import SoftDeleteModel


admin.site.disable_action("delete_selected")

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
            return queryset.model.global_objects.filter(deleted_at__isnull=False)
        elif self.value() == "False":
            return queryset.filter(deleted_at__isnull=True)
        return queryset


@admin.action(description="선택한 항목 소프트 삭제(복구 가능)")  # 버튼 이름 변경
def soft_delete_selected(modeladmin, request, queryset):
    """관리자에서 여러 항목을 Soft Delete로 삭제"""
    count = 0
    for obj in queryset:
        if isinstance(obj, SoftDeleteModel):
            obj.delete()
            count += 1
    modeladmin.message_user(request, f"{count}개 항목이 소프트 삭제되었습니다.", messages.SUCCESS)
    

@admin.action(description="선택한 항목 완전히 삭제(복구 불가)")
def hard_delete_selected(modeladmin, request, queryset):
    count = queryset.count()
    queryset.delete()
    modeladmin.message_user(request, f"{count}개 항목이 영구 삭제되었습니다.", messages.SUCCESS)


@admin.action(description="선택한 항목 복구")
def restore_selected(modeladmin, request, queryset):
    count = 0
    for obj in queryset:
        if isinstance(obj, SoftDeleteModel):
            obj.restore()
            count += 1
    modeladmin.message_user(request, f"{count}개 항목이 복구되었습니다.", messages.SUCCESS)


@admin.register(PlayerSubscription)
class PlayerSubscriptionAdmin(BaseModelAdmin):  # type: ignore
    list_display = ("id", "user", "player", "deleted_at", "restored_at", "is_alived")
    list_filter = (SoftDeleteListFilter,)
    actions = [hard_delete_selected, soft_delete_selected, restore_selected]
    
    # 삭제된 데이터도 포함해서 보임
    def get_queryset(self, request):
        return self.model.global_objects.all()

    def is_alived(self, obj):  # type: ignore
        return obj.deleted_at is None

    is_alived.boolean = True  # type: ignore


@admin.register(TeamSubscription)
class TeamSubscriptionAdmin(BaseModelAdmin):  # type: ignore
    list_display = ("id", "user", "team", "deleted_at", "restored_at", "is_alived")
    list_filter = (SoftDeleteListFilter,)
    actions = [hard_delete_selected, soft_delete_selected, restore_selected]
    
    def get_queryset(self, request):
        return self.model.global_objects.all()

    def is_alived(self, obj):  # type: ignore
        return obj.deleted_at is None

    is_alived.boolean = True  # type: ignore
