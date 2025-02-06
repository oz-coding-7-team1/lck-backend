from enum import Enum

from django.db import models
from django_softdelete.models import SoftDeleteModel
from taggit.managers import TaggableManager

from apps.common.models import BaseModel
from apps.teams.models import Team


# 선수 포지션 선택지
class Position(Enum):
    TOP = "top"
    JGL = "jungle"
    MID = "mid"
    BOT = "bottom"
    SPT = "support"


# 선수 상세 정보 관리 모델
class Player(BaseModel, SoftDeleteModel):
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)  # 팀 삭제 시 선수가 무소속이 됨
    realname = models.CharField(max_length=30)  # 본명
    nickname = models.CharField(max_length=30, unique=True)  # 선수명 (중복불가)
    gamename = models.CharField(max_length=50)  # 게임 닉네임
    position = models.CharField(
        max_length=10,
        choices=[(position.value, position.name) for position in Position],
        null=False,  # DB에서 NULL을 허용하지 않음
        blank=False,  # 폼에서 빈 값 입력을 허용하지 않음
        default=None,  # 기본값을 None 으로 설정하여 선택 강제
    )
    date_of_birth = models.DateField()  # 생년월일
    debut_date = models.DateField()  # 데뷔일
    social = models.JSONField(default=dict, null=True, blank=True)  # 소셜 URL (insta, facebook, youtube, X)
    agency = models.CharField(max_length=50)  # 소속사
    is_active = models.BooleanField(default=True)  # 선수 활성화 여부
    tags = TaggableManager(blank=True)

    class Meta:
        db_table = "player"

    def __str__(self) -> str:
        return f"[{self.team}] {self.nickname}({self.realname})"


# 선수 스케줄 관리 모델
class PlayerSchedule(BaseModel, SoftDeleteModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    category = models.CharField(
        max_length=10, choices=[("생일", "생일"), ("경기", "경기일정"), ("개인방송", "개인방송")]
    )  # 스케줄 분류 항목
    start_date = models.DateTimeField()  # 이벤트 시작 일시
    end_date = models.DateTimeField()  # 이벤트 종료 일시
    place = models.CharField(max_length=30, null=True)  # 이벤트 장소
    title = models.CharField(max_length=50, null=False, blank=False, default=None)  # 이벤트 제목
    detail = models.CharField(max_length=255, blank=True)  # 이벤트 상세 내용

    class Meta:
        db_table = "player_schedule"


# 선수 이미지 관리 모델
class PlayerImage(BaseModel, SoftDeleteModel):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    type = models.CharField(
        max_length=15,
        choices=[("profile", "프로필 이미지"), ("background", "배경 이미지"), ("gallery", "갤러리 이미지")],
    )  # 이미지 분류 항목
    url = models.CharField(max_length=255)  # 이미지 URL

    class Meta:
        db_table = "player_image"
