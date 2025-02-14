from typing import Optional, Union

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import (
    AbstractBaseUser,
    AnonymousUser,
    PermissionsMixin,
)
from django.db import models
from django.db.models.base import Model
from django_softdelete.models import SoftDeleteModel

from apps.common.models import BaseModel


class UserManager(BaseUserManager):
    def active_user(self):
        return self.filter(is_active=True)

    def active_staff(self):
        return self.filter(is_staff=True, is_active=True)

    def withdraw_user(self):
        return self.filter(is_active=False, is_staff=False)

    def withdraw_staff(self):
        return self.filter(is_staff=True, is_active=False)

    # 함수 앞 _는 이 파일에서만 사용하겠다는 의미
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("이메일 주소는 필수입니다.")
        if not password:
            raise ValueError("비밀번호는 필수입니다.")
        email = self.normalize_email(email)  # 이메일 정규화
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        # self._db는 UserManager에서 사용 중인 데이터베이스를 말함
        user.save(
            using=self._db
        )  # 다중 데이터 베이스를 사용하는 상황에서 정확히 지정해주기 위함이지만 단일에서도 관례적으로 사용
        return user

    def create_superuser(self, email: str, password: Optional[str], **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin, SoftDeleteModel):  # type: ignore
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=130)
    nickname = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # 로그인 시 username이 아니라 email로 로그인하게 됨(식별자가 email)
    USERNAME_FIELD = "email"

    objects = UserManager()

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

    class Meta:
        db_table = "user"


# 유저 이미지 정보를 저장하는 모멜
class UserImage(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="images")
    url = models.CharField(max_length=255)

    class Meta:
        db_table = "user_image"


# 사용자의 약관 동의 정보를 저장하는 모델
class TermsAgreement(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    terms = models.ForeignKey("Terms", on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "terms_agreement"


# 약관 정보를 저장하는 모델
class Terms(BaseModel):
    name = models.CharField(max_length=50)
    detail = models.TextField()
    is_active = models.BooleanField(default=True)
    is_required = models.BooleanField(default=True)

    class Meta:
        db_table = "terms"

    def __str__(self) -> str:
        return f"{self.name}"
