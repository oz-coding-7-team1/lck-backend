from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django_softdelete.models import SoftDeleteModel

from apps.common.models import BaseModel


class User(BaseModel, AbstractBaseUser, PermissionsMixin, SoftDeleteModel):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=130)
    nickname = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # 로그인 시 username이 아니라 email로 로그인하게 됨(식별자가 email)
    USERNAME_FIELD = "email"

    def has_perm(self, perm, obj=None) -> bool:
        # 사용자가 superuser인 경우 Django의 모든 권한 부여
        if self.is_superuser:
            return True
        return False

    def has_module_perms(self, app_label) -> bool:
        # 사용자가 superuser인 경우 모든 앱의 권한을 부여
        if self.is_superuser:
            return True
        return False