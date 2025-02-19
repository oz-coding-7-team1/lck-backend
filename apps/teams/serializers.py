from typing import Any, Dict

from rest_framework import serializers

from apps.players.models import Player  # Player 모델 import
from apps.subscriptions.models import TeamSubscription

from .models import Team, TeamSchedule


# 소속된 선수 정보를 위한 시리얼라이저
class PlayerForTeamSerializer(serializers.ModelSerializer[Player]):
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Player
        # 선수의 주요 정보만 제공
        fields = ["id", "nickname", "position", "gamename", "social", "profile_image_url"]

    def get_profile_image_url(self, obj: Player) -> str | None:
        image = obj.player_images.filter(category="profile").first()
        if image:
            return image.image_url
        return None


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
    profile_image_url = serializers.SerializerMethodField()
    background_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "social",
            "players",
            "is_subscribed",
            "profile_image_url",
            "background_image_url",
        ]

    def get_is_subscribed(self, obj: Team) -> bool:
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return TeamSubscription.objects.filter(team=obj, user=request.user, deleted_at__isnull=True).exists()
        return False

    def get_profile_image_url(self, obj: Team) -> str | None:
        image = obj.team_images.filter(category="profile").first()
        if image:
            return image.image_url
        return None

    def get_background_image_url(self, obj: Team) -> str | None:
        image = obj.team_images.filter(category="background").first()
        if image:
            return image.image_url
        return None


# 팀 전제 조회용 시리얼라이저
class TeamSerializer(serializers.ModelSerializer[Team]):
    social = TeamSocialSerializer()
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "name", "social", "profile_image_url"]

    def get_profile_image_url(self, obj: Team) -> str | None:
        image = obj.team_images.filter(category="profile").first()
        if image:
            return image.image_url
        return None


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
    profile_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = ["id", "name", "profile_image_url"]

    def get_profile_image_url(self, obj: Team) -> str | None:
        image = obj.team_images.filter(category="profile").first()
        if image:
            return image.image_url
        return None


# 팀 스케줄 정보를 위한 시리얼라이저
class TeamScheduleSerializer(serializers.ModelSerializer[TeamSchedule]):
    class Meta:
        model = TeamSchedule
        fields = "__all__"
