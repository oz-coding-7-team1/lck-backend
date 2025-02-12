from __future__ import annotations

from datetime import date, timedelta
from typing import ClassVar

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.players.models import Player, PlayerSchedule
from apps.subscriptions.models import PlayerSubscription
from apps.teams.models import Team
from apps.users.models import User


class PlayerAPITestCase(APITestCase):
    """선수 및 스케줄 관련 API 테스트 (권한, CRUD, 구독 기반 조회 포함)"""

    admin_user: ClassVar[User]
    normal_user: ClassVar[User]
    team: ClassVar[Team]
    players: ClassVar[list[Player]]
    schedule: ClassVar[PlayerSchedule]

    @classmethod
    def setUpTestData(cls) -> None:
        """한 번만 실행되는 테스트 데이터를 생성하여 테스트 속도 최적화"""

        # 1️⃣ 관리자 계정 생성
        cls.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="adminpass",
            is_staff=True,
            nickname="admin",
        )

        # 2️⃣ 일반 유저 계정 생성
        cls.normal_user = User.objects.create_user(
            email="normal@example.com",
            password="normalpass",
            nickname="normaluser",
        )

        # 3️⃣ 팀 생성
        cls.team = Team.objects.create(name="Test Team")

        # 4️⃣ 선수 5명 생성 (각각 다른 포지션)
        positions = ["top", "jungle", "mid", "bottom", "support"]
        cls.players = [
            Player.objects.create(
                team=cls.team,
                realname=f"RealName{i}",
                nickname=f"Nick{i}",
                gamename=f"GameName{i}",
                position=positions[i % len(positions)],
                date_of_birth=date(1990, 1, 1),
                debut_date=date(2010, 1, 1),
                social={"insta": f"http://instagram.com/player{i}"},
                agency="AgencyX",
            )
            for i in range(5)
        ]

        # 5️⃣ 첫 번째 선수의 스케줄 생성
        cls.schedule = PlayerSchedule.objects.create(
            player=cls.players[0],
            category="경기",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=2),
            place="Stadium",
            title="Match 1",
            detail="Detail info",
        )

    def authenticate(self, user: User) -> None:
        """JWT 인증 헤더 설정"""
        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # --- 선수 관련 API 테스트 ---
    def test_get_player_list(self) -> None:
        url = reverse("player-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.players))

    def test_get_player_detail(self) -> None:
        player = self.players[0]
        url = reverse("player-detail", kwargs={"pk": player.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], player.id)

    def test_create_player_by_admin(self) -> None:
        url = reverse("player-list")
        data = {
            "team_id": self.team.id,
            "realname": "New RealName",
            "nickname": "NewNick",
            "gamename": "NewGameName",
            "position": "top",
            "date_of_birth": "1995-05-05",
            "debut_date": "2015-05-05",
            "social": {"insta": "http://instagram.com/newplayer"},
            "agency": "AgencyY",
        }
        self.authenticate(self.admin_user)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_player_by_admin(self) -> None:
        player = self.players[0]
        url = reverse("player-detail", kwargs={"pk": player.id})
        self.authenticate(self.admin_user)
        data = {
            "team_id": self.team.id,
            "realname": "Updated RealName",
            "nickname": player.nickname,
            "gamename": "UpdatedGameName",
            "position": player.position,
            "date_of_birth": "1991-01-01",
            "debut_date": "2011-01-01",
            "social": {"insta": "http://instagram.com/updated"},
            "agency": "UpdatedAgency",
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_player_by_admin(self) -> None:
        player = self.players[0]
        url = reverse("player-detail", kwargs={"pk": player.id})
        self.authenticate(self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        from apps.players.models import Player

        with self.assertRaises(Player.DoesNotExist):
            Player.objects.get(pk=player.id)

    # --- 스케줄 관련 API 테스트 ---
    def test_get_player_schedule_list(self) -> None:
        url = reverse("player-schedule-list", kwargs={"player_id": self.players[0].id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_player_schedule_by_admin(self) -> None:
        player = self.players[1]
        url = reverse("player-schedule-list", kwargs={"player_id": player.id})
        data = {
            "category": "생일",
            "start_date": timezone.now().isoformat(),
            "end_date": (timezone.now() + timedelta(hours=1)).isoformat(),
            "place": "Arena",
            "title": "Birthday Event",
            "detail": "Celebrate birthday",
        }
        self.authenticate(self.admin_user)
        response = self.client.post(url, data, format="json")
        if response.status_code != status.HTTP_201_CREATED:
            print("Serializer errors:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_update_player_schedule_by_admin(self) -> None:
        schedule = self.schedule
        url = reverse(
            "player-schedule-detail",
            kwargs={"player_id": schedule.player.id, "schedule_id": schedule.id},
        )
        self.authenticate(self.admin_user)
        data = {
            "title": "Updated Match",
            "detail": "Updated details",
            "category": schedule.category,
            "start_date": schedule.start_date.isoformat(),
            "end_date": schedule.end_date.isoformat(),
            "place": schedule.place,
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_player_schedule_by_admin(self) -> None:
        schedule = self.schedule
        url = reverse(
            "player-schedule-detail",
            kwargs={"player_id": schedule.player.id, "schedule_id": schedule.id},
        )
        self.authenticate(self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        from apps.players.models import PlayerSchedule

        with self.assertRaises(PlayerSchedule.DoesNotExist):
            PlayerSchedule.objects.get(pk=schedule.id)

    # --- 일반 유저 권한 실패 테스트 ---
    def test_create_player_by_normal_user_fail(self) -> None:
        url = reverse("player-list")
        data = {
            "team_id": self.team.id,
            "realname": "New RealName2",
            "nickname": "NewNick2",
            "gamename": "NewGameName2",
            "position": "mid",
            "date_of_birth": "1996-06-06",
            "debut_date": "2016-06-06",
            "social": {"insta": "http://instagram.com/newplayer2"},
            "agency": "AgencyZ",
        }
        self.authenticate(self.normal_user)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_player_by_normal_user_fail(self) -> None:
        url = reverse("player-detail", kwargs={"pk": self.players[0].id})
        self.authenticate(self.normal_user)
        response = self.client.put(url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_player_by_normal_user_fail(self) -> None:
        url = reverse("player-detail", kwargs={"pk": self.players[0].id})
        self.authenticate(self.normal_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_player_schedule_by_normal_user_fail(self) -> None:
        player = self.players[1]
        url = reverse("player-schedule-list", kwargs={"player_id": player.id})
        data = {
            "category": "생일",
            "start_date": timezone.now().isoformat(),
            "end_date": (timezone.now() + timedelta(hours=1)).isoformat(),
            "place": "Arena",
            "title": "Birthday Event",
            "detail": "Celebrate birthday",
        }
        self.authenticate(self.normal_user)
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_player_schedule_by_normal_user_fail(self) -> None:
        schedule = self.schedule
        url = reverse(
            "player-schedule-detail",
            kwargs={"player_id": schedule.player.id, "schedule_id": schedule.id},
        )
        self.authenticate(self.normal_user)
        response = self.client.patch(url, {"title": "Fail Update"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_player_schedule_by_normal_user_fail(self) -> None:
        schedule = self.schedule
        url = reverse(
            "player-schedule-detail",
            kwargs={"player_id": schedule.player.id, "schedule_id": schedule.id},
        )
        self.authenticate(self.normal_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- 구독 기반 조회 테스트 ---
    def test_top_players_by_subscriptions(self) -> None:
        from apps.subscriptions.models import PlayerSubscription

        # 각 선수에 대해 구독 수 부여:
        # players[0]: 5, players[1]: 3, players[2]: 1 구독 부여
        for i in range(5):
            user = User.objects.create_user(
                email=f"sub_top_{i}_{i}@example.com",
                password="pass",
                nickname=f"sub_top_{i}",
            )
            PlayerSubscription.objects.create(user=user, player=self.players[0])
        for i in range(3):
            user = User.objects.create_user(
                email=f"sub_top_{i+5}_{i}@example.com",
                password="pass",
                nickname=f"sub_top_{i+5}",
            )
            PlayerSubscription.objects.create(user=user, player=self.players[1])
        user = User.objects.create_user(
            email="sub_top_8_unique@example.com",
            password="pass",
            nickname="sub_top_8",
        )
        PlayerSubscription.objects.create(user=user, player=self.players[2])

        url = reverse("top-players")
        # API가 인증을 필요로 하는 경우, 인증을 추가할 수도 있습니다.
        self.authenticate(self.normal_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        top_player = response.data[0]
        self.assertEqual(top_player["id"], self.players[0].id)

    def test_position_top_players_by_subscriptions(self) -> None:
        from apps.subscriptions.models import PlayerSubscription

        # 각 포지션별 구독 수를 부여합니다.
        subs_counts = {"top": 4, "jungle": 3, "mid": 2, "bottom": 1, "support": 0}
        for player in self.players:
            count = subs_counts.get(player.position, 0)
            for i in range(count):
                user = User.objects.create_user(
                    email=f"pos_{player.position}_{i}_{player.id}@example.com",
                    password="pass",
                    nickname=f"pos_{player.position}_{i}",
                )
                PlayerSubscription.objects.create(user=user, player=player)
        url = reverse("position-top")
        self.authenticate(self.normal_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data  # 예: {"top": [...], "jungle": [...], ...}
        for position, players in data.items():
            for player in players:
                self.assertEqual(player["position"], position)
