from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient, APITestCase

from apps.players.models import Player
from apps.subscriptions.models import PlayerSubscription, TeamSubscription
from apps.teams.models import Team

User = get_user_model()


class PlayerSubscriptionTests(APITestCase):  # type: ignore
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="testuser@example.com", password="testpass")
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
        # reverse로 API 경로 불러오기
        url: str = reverse("player_subscription", args=[self.player.id])
        # post 보내서 응답 받기
        response: Response = self.client.post(url)
        # 구독 생성 status code 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 객체 존재 여부 확인
        self.assertTrue(PlayerSubscription.objects.filter(user=self.user, player=self.player).exists())

    def test_unsubscribe_from_player(self) -> None:
        # 구독 객체 가져오기
        PlayerSubscription.objects.create(user=self.user, player=self.player)
        url: str = reverse("player_subscription", args=[self.player.id])
        # delete 요청 보내기
        response: Response = self.client.delete(url)
        # status code 확인
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # soft_delete 확인
        self.assertFalse(
            PlayerSubscription.objects.filter(user=self.user, player=self.player, deleted_at__isnull=True).exists()
        )

    def test_get_player_subscription_count(self) -> None:
        # test 구독 객체 생성
        PlayerSubscription.objects.create(user=self.user, player=self.player)
        url: str = reverse("player_subscription", args=[self.player.id])
        response: Response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class TeamSubscriptionTests(APITestCase):  # type: ignore
    def setUp(self) -> None:
        self.user = User.objects.create_user(email="testuser@example.com", password="testpass")
        self.team = Team.objects.create(name="Test Team")
        self.client.login(email="testuser@example.com", password="testpass")

    def test_subscribe_to_team(self) -> None:
        url: str = reverse("team_subscription", args=[self.team.id])
        response: Response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(TeamSubscription.objects.filter(user=self.user, team=self.team).exists())

    def test_unsubscribe_from_team(self) -> None:
        TeamSubscription.objects.create(user=self.user, team=self.team)
        url: str = reverse("team_subscription", args=[self.team.id])
        response: Response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            TeamSubscription.objects.filter(user=self.user, team=self.team, deleted_at__isnull=True).exists()
        )

    def test_get_team_subscription_count(self) -> None:
        TeamSubscription.objects.create(user=self.user, team=self.team)
        url: str = reverse("team_subscription", args=[self.team.id])
        response: Response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
