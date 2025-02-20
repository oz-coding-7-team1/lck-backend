from rest_framework import serializers

from .models import PlayerSubscription, TeamSubscription


class PlayerSubscriptionSerializer(serializers.ModelSerializer[PlayerSubscription]):
    class Meta:
        model = PlayerSubscription
        fields = "__all__"  # 모든 필드를 포함


class TeamSubscriptionSerializer(serializers.ModelSerializer[TeamSubscription]):
    class Meta:
        model = TeamSubscription
        fields = "__all__"  # 모든 필드를 포함
