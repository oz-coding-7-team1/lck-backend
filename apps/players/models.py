from django.db import models
from enum import Enum
from apps.common.models import BaseModel
from apps.users.models import User
from apps.teams.models import Team


# 선수 포지션 선택지
class Position(Enum):
    TOP = "top"
    JGL = "jungle"
    MID = "mid"
    BOT = "bottom"
    SPT = "support"


# 선수 상세 정보 관리 모델
class Player(BaseModel):
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


# 선수 구독 관리 모델
class PlayerSub(BaseModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE) # 특정 선수
    user = models.ForeignKey(User, on_delete=models.CASCADE) # 특정 선수를 구독 한 유저
    is_active = models.BooleanField(default=True) # 구독 활성화 여부
