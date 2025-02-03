from django.core.exceptions import ValidationError
from django.db import models


# 팀 정보를 저장하는 모델
class Team(models.Model):
    # 팀 이름(최대 30글자, 중복불가)
    name = models.CharField(max_length=30, unique=True, help_text="팀 이름")
    # 소셜 미디어 URL 정보를 JSON 형식으로 저장 (insta, facebook, youtube, twitter)
    social = models.JSONField(
        default=dict, blank=True, null=True, help_text="소셜 미디어 URL (insta, facebook, youtube, twitter)"
    )
    # 팀에 대한 설명
    detail = models.TextField(blank=True, null=True, help_text="팀 설명")
    # 팀 활성화 상태 여부(True면 활성화 상태 False면 비활성화)
    is_active = models.BooleanField(default=True, help_text="팀 활성화 상태 여부")


# 팀 일정을 저장하는 모델
class TeamSchedule(models.Model):
    # 해당 일정이 속한 팀 (Team 모델과의 외래키 관계)
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="schedules", help_text="팀 식별자")
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
    # 일정 활성화 상태 여부(True면 활성화 상태 False면 비활성화)
    is_active = models.BooleanField(default=True, help_text="일정 활성화 여부")
