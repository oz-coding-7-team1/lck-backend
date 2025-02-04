from typing import Optional, Union

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser, PermissionsMixin
from django.db import models
from django.db.models.base import Model
from django_softdelete.models import SoftDeleteModel  # type: ignore

from apps.common.models import BaseModel


class User(BaseModel, AbstractBaseUser, PermissionsMixin, SoftDeleteModel):  # type: ignore
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=130)
    nickname = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # 로그인 시 username이 아니라 email로 로그인하게 됨(식별자가 email)
    USERNAME_FIELD = "email"

    def has_perm(self, perm: str, obj: Optional[Union[Model, AnonymousUser]] = None) -> bool:
        # 사용자가 superuser인 경우 Django의 모든 권한 부여
        if self.is_superuser:
            return True
        return False


    def has_module_perms(self, app_label: str) -> bool:
        # 사용자가 superuser인 경우 모든 앱의 권한을 부여
        if self.is_superuser:
            return True
        return False


# 유저 이미지 정보를 저장하는 모멜
class UserImage(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="images")
    url = models.CharField(max_length=255)


# 사용자의 약관 동의 정보를 저장하는 모델
class TermsAgreements(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    terms = models.ForeignKey("Terms", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)


# 약관 정보를 저장하는 모델
class Terms(BaseModel):
    name = models.CharField(max_length=50)
    detail = models.TextField()
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=True)
