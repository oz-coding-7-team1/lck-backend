from datetime import timedelta

from django.core.management import call_command
from django.urls import reverse
from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.players.models import Player
from apps.subscriptions.models import PlayerSubscription, TeamSubscription
from apps.teams.models import Team
from apps.users.models import User


class PlayerSubscriptionTests(APITestCase):
    def setUp(self) -> None:
        # APIClient는 장고의 기본 Client보다 restAPI에 최적화 돼있음(응답 기본값이 JSON)
        self.client = APIClient()
        self.user = User.objects.create_user(email="testuser@example.com", password="testpass")
        # JWT 토큰 생성 및 헤더 설정
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.player = Player.objects.create(
            realname="Test Realname",
            nickname="Test Nickname",
            gamename="Test Gamename",
            position="mid",
            date_of_birth="1990-01-01",
            debut_date="2010-01-01",
            agency="Test Agency",
        )
        self.client.login(email="testuser@example.com", password="testpass")

    def test_subscribe_to_player(self) -> None:
        url = reverse("player_subscription", args=[self.player.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PlayerSubscription.objects.filter(user=self.user, player=self.player).exists())

    def test_unsubscribe_from_player(self) -> None:
        PlayerSubscription.objects.create(user=self.user, player=self.player)
        url = reverse("player_subscription", args=[self.player.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            PlayerSubscription.objects.filter(user=self.user, player=self.player, deleted_at__isnull=True).exists()
        )

    def test_get_player_subscription_count(self) -> None:
        PlayerSubscription.objects.create(user=self.user, player=self.player)
        url = reverse("player_subscription", args=[self.player.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_player_resubscribe_within_24_hours(self) -> None:
        subscription = PlayerSubscription.objects.create(user=self.user, player=self.player)
        subscription.delete()
        url = reverse("player_subscription", args=[self.player.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_player_resubscribe_after_24_hours(self) -> None:
        PlayerSubscription.objects.create(deleted_at=now() - timedelta(days=1), user=self.user, player=self.player)
        url = reverse("player_subscription", args=[self.player.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            PlayerSubscription.objects.filter(user=self.user, player=self.player, deleted_at__isnull=True).exists()
        )


class TeamSubscriptionTests(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(email="testuser@example.com", password="testpass")
        # JWT 토큰 생성 및 헤더 설정
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        self.team = Team.objects.create(name="Test Team")
        self.client.login(email="testuser@example.com", password="testpass")

    def test_subscribe_to_team(self) -> None:
        url = reverse("team_subscription", args=[self.team.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TeamSubscription.objects.filter(user=self.user, team=self.team).exists())

    def test_unsubscribe_from_team(self) -> None:
        TeamSubscription.objects.create(user=self.user, team=self.team)
        url = reverse("team_subscription", args=[self.team.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            TeamSubscription.objects.filter(user=self.user, team=self.team, deleted_at__isnull=True).exists()
        )

    def test_get_team_subscription_count(self) -> None:
        TeamSubscription.objects.create(user=self.user, team=self.team)
        url = reverse("team_subscription", args=[self.team.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_team_resubscribe_within_24_hours(self) -> None:
        subscription = TeamSubscription.objects.create(user=self.user, team=self.team)
        subscription.delete()
        url = reverse("team_subscription", args=[self.team.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_team_resubscribe_after_24_hours(self) -> None:
        TeamSubscription.objects.create(deleted_at=now() - timedelta(days=1), user=self.user, team=self.team)
        url = reverse("team_subscription", args=[self.team.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            TeamSubscription.objects.filter(user=self.user, team=self.team, deleted_at__isnull=True).exists()
        )


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
