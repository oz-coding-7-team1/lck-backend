from rest_framework import serializers

from .models import Player, PlayerImage, PlayerSchedule


# 소셜 미디어 정보를 직렬화하는 시리얼라이저
class PlayerSocialSerializer(serializers.Serializer[None]):
    insta = serializers.URLField(required=False)  # 이 필드는 필수 입력이 아님
    facebook = serializers.URLField(required=False)  # 이 필드는 필수 입력이 아님
    youtube = serializers.URLField(required=False)  # 이 필드는 필수 입력이 아님
    X = serializers.URLField(required=False)  # 이 필드는 필수 입력이 아님


# 전체 선수 정보를 직렬화하는 시리얼라이저
class PlayerSerializer(serializers.ModelSerializer[Player]):
    social = PlayerSocialSerializer()  # 소셜 미디어 정보를 포함

    class Meta:
        model = Player
        fields = ["id", "nickname", "realname", "position", "social"]


# 상위 10명의 선수 정보를 직렬화하는 시리얼라이저
class PlayerTopSerializer(serializers.ModelSerializer[Player]):
    class Meta:
        model = Player
        fields = ["id", "nickname", "realname"]


# 특정 포지션의 상위 5명의 선수 정보를 직렬화하는 시리얼라이저
class PlayerPositionSerializer(serializers.ModelSerializer[Player]):
    class Meta:
        model = Player
        fields = ["id", "nickname", "position"]


# 선수 프로필 정보를 반환하는 Serializer
class PlayerProfileSerializer(serializers.ModelSerializer[Player]):

    class Meta:
        model = Player
        fields = [
            "id",  # 선수의 ID
            "team_id",  # 소속 팀의 ID
            "realname",  # 선수의 실제 이름
            "nickname",  # 선수의 닉네임
            "gamename",  # 게임에서 사용하는 이름
            "position",  # 포지션
            "date_of_birth",  # 생년월일
            "debut_date",  # 데뷔 날짜
            "social",  # 소셜 미디어 정보
            "agency",  # 소속 에이전시
        ]


# PlayerImage 모델의 데이터를 직렬화하는 Serializer
class PlayerImageSerializer(serializers.ModelSerializer[PlayerImage]):
    class Meta:
        model = PlayerImage
        fields = "__all__"  # 모델의 모든 필드를 포함


# PlayerSchedule 모델의 데이터를 직렬화하는 Serializer
class PlayerScheduleSerializer(serializers.ModelSerializer[PlayerSchedule]):
    class Meta:
        model = PlayerSchedule
        fields = "__all__"  # 모델의 모든 필드를 포함
