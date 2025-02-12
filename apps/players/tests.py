from __future__ import annotations

from datetime import date, timedelta
from typing import ClassVar

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.players.models import Player, PlayerSchedule
from apps.teams.models import Team
from apps.users.models import User


class PlayerAPITestCase(APITestCase):
    """선수 및 스케줄 관련 API 테스트"""

    admin_user: ClassVar[User]
    normal_user: ClassVar[User]
    team: ClassVar[Team]
    players: ClassVar[list[Player]]
    schedule: ClassVar[PlayerSchedule]

    @classmethod
    def setUpTestData(cls) -> None:
        """한 번만 실행되는 테스트 데이터 생성"""

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

        # 4️⃣ 선수 3명 생성
        cls.players = [
            Player.objects.create(
                team=cls.team,
                realname=f"RealName{i}",
                nickname=f"Nick{i}",
                gamename=f"GameName{i}",
                position="top",
                date_of_birth=date(1990, 1, 1),
                debut_date=date(2010, 1, 1),
                social={"insta": f"http://instagram.com/player{i}"},
                agency="AgencyX",
            )
            for i in range(3)
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
        """JWT 인증 추가"""
        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ✅ 1️⃣ 선수 목록 조회
    def test_get_player_list(self) -> None:
        url = reverse("player-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.players))

    # ✅ 2️⃣ 특정 선수 조회
    def test_get_player_detail(self) -> None:
        player = self.players[0]
        url = reverse("player-detail", kwargs={"pk": player.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], player.id)

    # ✅ 3️⃣ 선수 등록 (관리자 권한)
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

    # ✅ 4️⃣ 선수 수정 (관리자 권한)
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

    # ✅ 5️⃣ 선수 삭제 (관리자 권한)
    def test_delete_player_by_admin(self) -> None:
        player = self.players[0]
        url = reverse("player-detail", kwargs={"pk": player.id})
        self.authenticate(self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # ✅ 6️⃣ 특정 선수 스케줄 조회
    def test_get_player_schedule_list(self) -> None:
        url = reverse("player-schedule-list", kwargs={"player_id": self.players[0].id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ✅ 7️⃣ 스케줄 등록 (관리자 권한)
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

    # ✅ 8️⃣ 스케줄 수정 (관리자 권한)
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
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ✅ 9️⃣ 스케줄 삭제 (관리자 권한)
    def test_delete_player_schedule_by_admin(self) -> None:
        schedule = self.schedule
        url = reverse(
            "player-schedule-detail",
            kwargs={"player_id": schedule.player.id, "schedule_id": schedule.id},
        )
        self.authenticate(self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # ✅ 🔟 일반 유저가 관리자 기능 실행 (실패해야 함)
    def test_create_player_by_normal_user_fail(self) -> None:
        url = reverse("player-list")
        self.authenticate(self.normal_user)
        response = self.client.post(url, {}, format="json")
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
