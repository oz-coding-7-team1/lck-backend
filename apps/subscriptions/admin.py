from django.contrib import admin
from .models import PlayerSubscription, TeamSubscription
from django_softdelete.admin import SoftDeletedModelAdmin

class SoftDeleteListFilter(admin.SimpleListFilter):
    title = '삭제 여부'
    parameter_name = 'is_deleted'

    def lookups(self, request, model_admin):
        return (
            ('True', '삭제됨'),
            ('False', '삭제되지 않음'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'True':
            return queryset.filter(deleted_at__isnull=False)
        elif self.value() == 'False':
            return queryset.filter(deleted_at__isnull=True)
        return queryset

@admin.register(PlayerSubscription)
class PlayerSubscriptionAdmin(SoftDeletedModelAdmin, admin.ModelAdmin):
    list_display = ('user', 'player', 'deleted_at', 'restored_at')
    list_filter = (SoftDeleteListFilter,)

    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True

@admin.register(TeamSubscription)
class TeamSubscriptionAdmin(SoftDeletedModelAdmin, admin.ModelAdmin):
    list_display = ('user', 'team', 'deleted_at', 'restored_at')
    list_filter = (SoftDeleteListFilter,)

    def is_deleted(self, obj):
        return obj.deleted_at is not None
    is_deleted.boolean = True