from typing import Any

from django.contrib import admin

class BaseModelAdmin(admin.ModelAdmin):
    def has_add_permission(self, request: Any) -> bool:
        return request.user.is_staff

    def has_change_permission(self, request: Any, obj: object = None) -> bool:
        return request.user.is_staff

    def has_delete_permission(self, request: Any, obj: object = None) -> bool:
        return request.user.is_staff

    def has_module_permission(self, request: Any) -> bool:
        return request.user.is_staff
