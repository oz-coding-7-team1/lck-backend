from typing import Any, Dict, List, Optional

from rest_framework import serializers

from .models import Player, PlayerImage, PlayerSchedule


# Player 모델의 데이터를 직렬화하는 Serializer
class PlayerSerializer(serializers.ModelSerializer[Player]):
    class Meta:
        model = Player
        fields = "__all__"  # 모델의 모든 필드를 포함


# 선수 프로필 정보를 반환하는 Serializer
class PlayerProfileSerializer(serializers.ModelSerializer[Player]):
    images = serializers.SerializerMethodField()  # 선수 이미지 목록을 추가로 포함
    team_id = serializers.SerializerMethodField()  # 소속 팀의 ID를 추가

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
            "images",  # 이미지 목록
        ]

    def get_images(self, obj: Player) -> List[Dict[str, Any]]:
        """
        해당 선수의 이미지를 반환하는 메서드.
        :param obj: Player 객체
        :return: 이미지 정보를 담은 딕셔너리 리스트
        """
        images = PlayerImage.objects.filter(player=obj)  # 해당 선수의 이미지를 필터링
        return list(PlayerImageSerializer(images, many=True).data)  # 직렬화 후 반환

    def get_team_id(self, obj: Player) -> Optional[int]:
        """
        선수의 소속 팀 ID를 반환하는 메서드.
        :param obj: Player 객체
        :return: 팀 ID (소속 팀이 있는 경우) 또는 None (소속 팀이 없는 경우)
        """
        return obj.team.id if obj.team else None  # 선수의 소속 팀이 있는 경우 팀 ID 반환, 없는 경우 None 반환


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
