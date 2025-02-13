from typing import Any, Dict

from rest_framework import serializers

from apps.players.models import Player  # Player 모델 import
from apps.subscriptions.models import TeamSubscription

from .models import Team, TeamSchedule


# 소속된 선수 정보를 위한 시리얼라이저
class PlayerForTeamSerializer(serializers.ModelSerializer[Player]):
    class Meta:
        model = Player
        # 선수의 주요 정보만 제공
        fields = ["id", "nickname", "position", "gamename", "social"]


# 소셜 미디어 정보를 직렬화하는 시리얼라이저
class TeamSocialSerializer(serializers.Serializer[None]):
    insta = serializers.URLField(required=False)  # 이 필드는 필수 입력이 아님
    facebook = serializers.URLField(required=False)  # 이 필드는 필수 입력이 아님
    youtube = serializers.URLField(required=False)  # 이 필드는 필수 입력이 아님
    X = serializers.URLField(required=False)  # 이 필드는 필수 입력이 아님
    soop = serializers.URLField(required=False)
    chzzk = serializers.URLField(required=False)


# 팀 상세 정보를 위한 시리얼라이저 (선수 목록 포함)
class TeamDetailSerializer(serializers.ModelSerializer[Team]):
    social = TeamSocialSerializer()
    players = PlayerForTeamSerializer(many=True, source="player_set")  # 팀에 소속된 선수 목록 추가
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "name", "social", "players", "is_subscribed"]

    def get_is_subscribed(self, obj: Team) -> bool:
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return TeamSubscription.objects.filter(team=obj, user=request.user, deleted_at__isnull=True).exists()
        return False


# 팀 전제 조회용 시리얼라이저
class TeamSerializer(serializers.ModelSerializer[Team]):
    social = TeamSocialSerializer()

    class Meta:
        model = Team
        fields = ["id", "name", "social"]


# 팀 등록용 시리얼라이저
class TeamCreateSerializer(serializers.ModelSerializer[Team]):
    social = TeamSocialSerializer(required=False)

    class Meta:
        model = Team
        fields = ["name", "social"]

    def create(self, validated_data: Dict[str, Any]) -> Team:
        return Team.objects.create(**validated_data)


# 상위 5팀 정보를 직렬화하는 시리얼라이저
class TeamTopSerializer(serializers.ModelSerializer[Team]):
    class Meta:
        model = Team
        fields = ["id", "name"]


# 팀 스케줄 정보를 위한 시리얼라이저
class TeamScheduleSerializer(serializers.ModelSerializer[TeamSchedule]):
    class Meta:
        model = TeamSchedule
        fields = "__all__"
