from django.db import models
from django_softdelete.models import SoftDeleteModel

from apps.common.models import BaseModel
from apps.players.models import Player
from apps.teams.models import Team


# 선수 이미지 관리 모델
class PlayerImage(BaseModel, SoftDeleteModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_images")
    type = models.CharField(
        max_length=15,
        choices=[("profile", "프로필 이미지"), ("background", "배경 이미지"), ("gallery", "갤러리 이미지")],
    )  # 이미지 분류 항목
    url = models.CharField(max_length=255)  # 이미지 URL

    def __str__(self) -> str:
        return f"{self.player.name} - {self.type}"

    class Meta:
        db_table = "player_image"


# 팀 이미지 정보를 저장하는 모멜
class TeamImage(BaseModel, SoftDeleteModel):
    # 팀에 해당하는 이미지
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_images")
    # 이미지 카테고리(프로필, 배경, 갤러리)
    type = models.CharField(max_length=15, help_text="이미지 카테고리(프로필, 배경, 갤러리)")
    # 이미지 파일 경로
    url = models.CharField(max_length=255, help_text="이미지 URL (uuid 기반 경로)")

    def __str__(self) -> str:
        return f"{self.team.name} - {self.type}"

    class Meta:
        db_table = "team_image"
