from typing import Any

from rest_framework import serializers

from .models import Terms, TermsAgreement, User, UserImage


class UserSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ("id", "email", "nickname", "is_active", "is_staff", "is_superuser")


class MypageSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ("email", "nickname")


class UserRegisterSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ("email", "nickname", "password")

    def create(self, validated_data: Any) -> User:
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user


class UserImageSerializer(serializers.ModelSerializer[UserImage]):
    class Meta:
        model = UserImage
        fields = ("id", "user", "url")


class TermsSerializer(serializers.ModelSerializer[Terms]):
    class Meta:
        model = Terms
        fields = ("id", "name", "detail", "is_active", "is_required")


class TermsAgreementSerializer(serializers.ModelSerializer[TermsAgreement]):
    class Meta:
        model = TermsAgreement
        fields = ("id", "user", "terms", "is_active")


class UserLoginSerializer(serializers.Serializer[None]):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenResponseSerializer(serializers.Serializer[None]):
    access_token = serializers.CharField()


class ChangePasswordSerializer(serializers.Serializer[User]):
    old_password = serializers.CharField(help_text="현재 비밀번호", write_only=True)
    new_password = serializers.CharField(help_text="새 비밀번호", write_only=True)
