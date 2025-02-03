from django.db import models


# 팀 정보를 저장하는 모델
class Team(models.Model):
    # 팀 이름(최대 30글자, 중복불가)
    name = models.CharField(max_length=30, unique=True, help_text='팀 이름')
    # 소셜 미디어 URL 정보를 JSON 형식으로 저장 (insta, facebook, youtube, twitter)
    social = models.JSONField(default=dict, blank=True, null=True, help_text='소셜 미디어 URL (insta, facebook, youtube, twitter)')
    # 팀에 대한 설명
    detail = models.TextField(blank=True, null=True, help_text='팀 설명')
    # 팀이 활성화 상태 여부(True면 활성화 상태 False면 비활성화)
    is_active = models.BooleanField(default=True, help_text='팀 활성화 상태 여부')

