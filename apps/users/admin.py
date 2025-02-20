from typing import Any, Type

from django.contrib import admin
from django.contrib.auth.hashers import make_password
from django.forms import ModelForm
from django.http import HttpRequest

from apps.common.admin import BaseModelAdmin

from .models import Terms, User


# Register your models here.
@admin.register(User)
class UserAdmin(BaseModelAdmin):
    # 표시할 컬럼
    list_display = ("email", "nickname", "is_staff", "is_active", "is_superuser")
    # 검색 기능 설정
    search_fields = ("email", "nickname")
    # 필터링 조건
    list_filter = ("is_active", "is_staff", "is_superuser")

    def get_form(self, request: Any, obj: User = None, **kwargs: Any):
        form = super().get_form(request, obj, **kwargs)

        if not request.user.is_superuser:
            form.base_fields["is_superuser"].disabled = True
            form.base_fields["is_staff"].disabled = True
        return form

    # 유저 생성 시 비밀번호 해쉬화
    def save_model(self, request: HttpRequest, obj: User, form: ModelForm, change: bool) -> None:
        if obj.password:
            obj.password = make_password(obj.password)

        super().save_model(request, obj, form, change)


@admin.register(Terms)
class TermsAdmin(BaseModelAdmin):
    pass
