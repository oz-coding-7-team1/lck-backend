from rest_framework import serializers

from .models import *


class UserSerializer(serializers.ModelSerializer):  # type: ignore
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "is_active",
            "is_staff",
            "is_superuser",
            "last_login",
            "created_at",
            "updated_at",
        ]