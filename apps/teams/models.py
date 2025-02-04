from django.db import models

from apps.common.models import BaseModel
from apps.users.models import User


# 팀 정보를 저장하는 모델
class Team(BaseModel):
    # 팀 이름(최대 30글자, 중복불가)
    name = models.CharField(max_length=30, unique=True, help_text="팀 이름")
    # 소셜 미디어 URL 정보를 JSON 형식으로 저장 (insta, facebook, youtube, twitter)
    social = models.JSONField(
        default=dict, blank=True, null=True, help_text="소셜 미디어 URL (insta, facebook, youtube, twitter)"
    )

    def __str__(self) -> str:
        return self.name


# 팀 일정을 저장하는 모델
class TeamSchedule(BaseModel):
    # 해당 일정이 속한 팀 (Team 모델과의 외래키 관계)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="schedules", help_text="팀 식별자")
    # 일정 카테고리 (경기, 연습 등)
    category = models.CharField(max_length=10, help_text="일정 카테고리")
    # 이벤트 시작 시간 (종료 시간보다 이전이어야 함)
    start_date = models.DateTimeField(help_text="이벤트 시작 (end_date보다 작거나 같아야 함)")
    # 이벤트 종료 시간 (시작 시간보다 이후이어야 함)
    end_date = models.DateTimeField(help_text="이벤트 종료 (start_date보다 크거나 같아야 함)")
    # 일정 장소
    place = models.CharField(max_length=30, help_text="장소")
    # 일정 제목
    title = models.CharField(max_length=50, help_text="제목")
    # 일정에 대한 상세 내용
    detail = models.CharField(max_length=255, blank=True, null=True, help_text="내용")

    def __str__(self) -> str:
        return f"{self.team.name} - {self.title}"


# 팀 구독 정보를 저장하는 모델
class TeamSub(BaseModel):
    # 구독한 유저 식별자(한명의 유저는 하나의 팀만 구독이 가능함)
    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text="구독한 유저 식별자")
    # 구독한 팀 식별자(하나의 팀은 여러명의 구독자를 가질 수 있음)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, help_text="구독한 팀 식별자")

    class Meta:
        # 동일한 user와 team의 조합은 중복되지 않도록 함
        unique_together = ("user_id", "team_id")

    def __str__(self) -> str:
        return f"User {self.user} - {self.team.name}"


# 팀 이미지 정보를 저장하는 모멜
class TeamImage(BaseModel):
    # 팀에 해당하는 이미지
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    # 이미지 카테고리(프로필, 배경, 갤러리)
    type = models.CharField(max_length=15, help_text="이미지 카테고리(프로필, 배경, 갤러리)")
    # 이미지 파일 경로
    url = models.CharField(max_length=255, help_text="이미지 URL (uuid 기반 경로)")

    def __str__(self) -> str:
        return f"{self.team.name} - {self.type}"


# 팀 관련 태그 정보를 저장하는 모델
class TeamTags(BaseModel):
    # 태그명
    name = models.CharField(max_length=50, unique=True, help_text="관련 검색어")


# 팀과 태그 간의 N:M 관계를 저장하는 모델 (팀에게 태그 등록)
class TeamTagged(BaseModel):
    # 태그가 등록된 팀 (Team 모델과의 외래키 관계)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="tagged_tags", help_text="팀 식별자")
    # 등록된 태그 (TeamTags 모델과의 외래키 관계)
    tag = models.ForeignKey(TeamTags, on_delete=models.CASCADE, related_name="team_tags", help_text="태그 식별자")
