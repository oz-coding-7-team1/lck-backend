from datetime import timedelta

from django.core.management import call_command
from django.utils.timezone import now
from rest_framework.test import APITestCase

from apps.players.models import Player
from apps.subscriptions.models import PlayerSubscription, TeamSubscription
from apps.teams.models import Team
from apps.users.models import User


# Create your tests here.
class DeleteOldSubscriptionsTest(APITestCase):
    def setUp(self) -> None:
        # 현재 시간 기준으로 4일 전의 날짜를 계산합니다.
        self.user1 = User.objects.create(email="testuser@example.com", password="testpass", nickname="test1")
        self.user2 = User.objects.create(email="testuser2@example.com", password="testpass2", nickname="test2")
        self.player1 = Player.objects.create(
            realname="Test Realname",
            nickname="Test Nickname",
            gamename="Test Gamename",
            position="mid",
            date_of_birth="1990-01-01",
            debut_date="2010-01-01",
            agency="Test Agency",
        )
        self.player2 = Player.objects.create(
            realname="Test Realname2",
            nickname="Test Nickname2",
            gamename="Test Gamename2",
            position="top",
            date_of_birth="1990-01-01",
            debut_date="2010-01-01",
            agency="Test Agency",
        )
        self.team1 = Team.objects.create(name="Test Team1")
        self.team2 = Team.objects.create(name="Test Team2")

        # 4일 전의 삭제된 PlayerSubscription과 TeamSubscription을 생성합니다.
        PlayerSubscription.objects.create(deleted_at=now() - timedelta(days=4), user=self.user1, player=self.player1)
        TeamSubscription.objects.create(deleted_at=now() - timedelta(days=4), user=self.user1, team=self.team1)

        # 2일 전의 삭제된 PlayerSubscription과 TeamSubscription을 생성합니다.
        PlayerSubscription.objects.create(deleted_at=now() - timedelta(days=2), user=self.user2, player=self.player2)
        TeamSubscription.objects.create(deleted_at=now() - timedelta(days=2), user=self.user2, team=self.team2)

    def test_delete_old_subscriptions(self) -> None:
        # 명령어를 호출합니다.
        call_command("hard_delete_old_subscriptions")

        # 4일 전에 생성된 삭제된 구독은 삭제되어야 합니다.
        self.assertEqual(
            PlayerSubscription.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=3)).count(), 0
        )
        self.assertEqual(TeamSubscription.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=3)).count(), 0)

        # 2일 전에 생성된 삭제된 구독은 남아 있어야 합니다.
        self.assertEqual(PlayerSubscription.deleted_objects.filter(deleted_at__gt=now() - timedelta(days=3)).count(), 1)
        self.assertEqual(TeamSubscription.deleted_objects.filter(deleted_at__gt=now() - timedelta(days=3)).count(), 1)
