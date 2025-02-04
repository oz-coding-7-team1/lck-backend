from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from apps.common.models import BaseModel


# 사용자 정보를 저장하는 모델
class User(BaseModel, AbstractBaseUser):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=130)
    nickname = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # 로그인 시 username이 아니라 email로 로그인하게 됨(식별자가 email)
    USERNAME_FIELD = "email"


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
