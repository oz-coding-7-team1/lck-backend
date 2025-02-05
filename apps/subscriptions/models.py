from django.db import models
from django_softdelete.models import SoftDeleteModel

from apps.common.models import BaseModel
from apps.players.models import Player
from apps.teams.models import Team
from apps.users.models import User


# 선수 구독 관리 모델
class PlayerSubscription(BaseModel, SoftDeleteModel):
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE, related_name="subscriptions", help_text="구독한 선수 식별자"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="구독한 유저 식별자")

    class Meta:
        db_table = "player_subscription"


# 팀 구독 정보를 저장하는 모델
class TeamSubscription(BaseModel, SoftDeleteModel):
    # 구독한 유저 식별자(한명의 유저는 하나의 팀만 구독이 가능함)
    user = models.OneToOneField(User, on_delete=models.CASCADE, help_text="구독한 유저 식별자")
    # 구독한 팀 식별자(하나의 팀은 여러명의 구독자를 가질 수 있음)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="subscriptions", help_text="구독한 팀 식별자")

    class Meta:
        # 동일한 user와 team의 조합은 중복되지 않도록 함
        unique_together = ("user_id", "team_id")
        db_table = "team_subscription"

    def __str__(self) -> str:
        return f"User {self.user} - {self.team.name}"
