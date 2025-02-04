from django.db import models


# 팀 정보를 저장하는 모델
class Team(models.Model):
    # 팀 이름(최대 30글자, 중복불가)
    name = models.CharField(max_length=30, unique=True, help_text="팀 이름")
    # 소셜 미디어 URL 정보를 JSON 형식으로 저장 (insta, facebook, youtube, twitter)
    social = models.JSONField(
        default=dict, blank=True, null=True, help_text="소셜 미디어 URL (insta, facebook, youtube, twitter)"
    )
    # 팀이 활성화 상태 여부(True면 활성화 상태 False면 비활성화)
    is_active = models.BooleanField(default=True, help_text="팀 활성화 상태 여부")

    def __str__(self) -> str:
        return self.name


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
    # 일정 활성화 상태 여부 (True면 활성화, False면 비활성화)
    is_active = models.BooleanField(default=True, help_text="일정 활성화 여부")

    def __str__(self) -> str:
        return f"{self.team_id.name} - {self.title}"


# 팀 구독 정보를 저장하는 모델
class TeamSub(models.Model):
    # 구독한 유저 식별자(한명의 유저는 하나의 팀만 구독이 가능함)
    user_id = models.OneToOneField("User", on_delete=models.CASCADE, help_text="구독한 유저 식별자")
    # 구독한 팀 식별자(하나의 팀은 여러명의 구독자를 가질 수 있음)
    team_id = models.ForeignKey("Team", on_delete=models.CASCADE, help_text="구독한 팀 식별자")
    # 구독 활성화 상태 여부 (True면 활성화, False면 비활성화)
    is_active = models.BooleanField(default=True, help_text="구독 활성화 상태 여부")

    class Meta:
        # 동일한 user_id와 team의 조합은 중복되지 않도록 함
        unique_together = ("user_id", "team_id")

    def __str__(self) -> str:
        return f"User {self.user_id} - {self.team_id.name}"


# 팀 이미지 정보를 저장하는 모멜
class TeamImage(models.Model):
    # 팀에 해당하는 이미지
    team_id = models.ForeignKey(Team, on_delete=models.CASCADE)
    # 이미지 카테고리(프로필, 배경, 갤러리)
    type = models.CharField(max_length=15, help_text="이미지 카테고리(프로필, 배경, 갤러리)")
    # 이미지 파일 경로
    url = models.CharField(max_length=255, help_text="이미지 URL (uuid 기반 경로)")

    def __str__(self) -> str:
        return f"{self.team_id.name} - {self.type}"
