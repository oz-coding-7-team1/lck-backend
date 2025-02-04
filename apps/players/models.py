from django.db import models
from enum import Enum
from users.models import User
from teams.models import Team

class Position(Enum):
    TOP = "top"
    JGL = "jungle"
    MID = "mid"
    BOT = "bottom"
    SPT = "support"


class Player(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE) # 소속 된 팀
    realname = models.CharField(max_length=30) # 본명
    nickname = models.CharField(max_length=30, unique=True) # 선수명 (중복불가)
    gamename = models.CharField(max_length=50) # 게임 닉네임
    position = models.CharField(
        max_length=10,
        choices=[(position.value, position.name) for position in Position],
        null=False, # DB에서 NULL을 허용하지 않음
        blank=False, # 폼에서 빈 값 입력을 허용하지 않음
        default=None # 기본값을 None 으로 설정하여 선택 강제
    )
    date_of_birth = models.DateField() # 생년월일
    debut_date = models.DateField() # 데뷔일
    social = models.JSONField(default=dict, null=True, blank=True) # 소셜 URL (insta, facebook, youtube, X)
    agency = models.ForeignKey(User, on_delete=models.CASCADE) # 소속사
    is_active = models.BooleanField(default=True) # 선수 활성화 여부 (soft delete를 위해 활성화 여부 저장)