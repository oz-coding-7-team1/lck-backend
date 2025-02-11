from rest_framework import serializers

from .models import *


class UserSerializer(serializers.ModelSerializer):  # type: ignore
    # class Meta:
    #     model = User
    #     fields = [
    #         "id",
    #         "email",
    #         "nickname",
    #         "is_active",
    #         "is_staff",
    #         "is_superuser",
    #         "last_login",
    #         "created_at",
    #         "updated_at",
    #     ]
    class Meta:
        model = User
        # API 응답에 노출할 필드와 입력받을 필드 지정
        fields = ('id', 'email', 'nickname', 'is_active', 'is_staff', 'is_superuser', 'password')
        extra_kwargs = {
            'password': {'write_only': True}  # 클라이언트로는 password가 노출되지 않도록 함
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)  # 비밀번호 해싱 처리
        user.save()
        return user


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserImage
        fields = ('id', 'user', 'url')


class TermsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terms
        fields = ('id', 'name', 'detail', 'is_active', 'is_required')


class TermsAgreementSerializer(serializers.ModelSerializer):
    class Meta:
        model = TermsAgreement
        fields = ('id', 'user', 'terms', 'is_active')