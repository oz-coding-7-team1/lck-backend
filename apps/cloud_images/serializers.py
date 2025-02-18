from rest_framework import serializers

from .models import PlayerImage, TeamImage, UserImage


class UserImageSerializer(serializers.ModelSerializer[UserImage]):
    class Meta:
        model = UserImage
        fields = ("id", "user", "image_url", "uploaded_at")
        read_only_fields = ("id", "uploaded_at")


class PlayerImageSerializer(serializers.ModelSerializer[PlayerImage]):
    class Meta:
        model = PlayerImage
        fields = ("id", "player", "category", "image_url", "uploaded_by", "uploaded_at")
        read_only_fields = ("id", "uploaded_by", "uploaded_at")


class TeamImageSerializer(serializers.ModelSerializer[TeamImage]):
    class Meta:
        model = TeamImage
        fields = ("id", "team", "category", "image_url", "uploaded_by", "uploaded_at")
        read_only_fields = ("id", "uploaded_by", "uploaded_at")
