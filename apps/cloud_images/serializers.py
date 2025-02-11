from rest_framework import serializers

from .models import PlayerImage, TeamImage


# PlayerImage 모델의 데이터를 직렬화하는 시리얼라이저
class PlayerImageSerializer(serializers.ModelSerializer[PlayerImage]):
    class Meta:
        model = PlayerImage
        fields = "__all__"  # 모델의 모든 필드를 포함


class TeamImageSerializer(serializers.ModelSerializer[TeamImage]):
    class Meta:
        model = TeamImage
        fields = "__all__"
