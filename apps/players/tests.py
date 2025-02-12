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
    """테스트 클래스에 속성을 미리 선언하여 Mypy 오류 해결"""

    admin_user: ClassVar[User]
    normal_users: ClassVar[list[User]]
    team: ClassVar[Team]
    players: ClassVar[list[Player]]
    schedules: ClassVar[list[PlayerSchedule]]

    @classmethod
    def setUpTestData(cls) -> None:
        """클래스 수준에서 테스트 데이터를 한 번만 생성하여 쿼리 수를 줄임"""

        # 1️⃣ 관리자 유저 1명 생성
        cls.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="adminpass",
            is_staff=True,
            nickname="admin",
        )

        # 2️⃣ 일반 유저 20명 `bulk_create()`로 생성
        cls.normal_users = [
            User(
                email=f"normal{i}@example.com",
                password="normalpass",
                nickname=f"normal{i}",
            )
            for i in range(20)
        ]
        User.objects.bulk_create(cls.normal_users)

        # 3️⃣ 팀 생성
        cls.team = Team.objects.create(name="Test Team")

        # 4️⃣ 선수 15명 `bulk_create()`로 생성
        positions = ["top", "jungle", "mid", "AD Carry", "support"]
        players = [
            Player(
                team=cls.team if i % 2 == 0 else None,
                realname=f"RealName{i}",
                nickname=f"Nick{i}",
                gamename=f"GameName{i}",
                position=positions[i % len(positions)],
                date_of_birth=date(1990, 1, 1),
                debut_date=date(2010, 1, 1),
                social={"insta": f"http://instagram.com/player{i}"},
                agency="AgencyX",
            )
            for i in range(15)
        ]
        Player.objects.bulk_create(players)  # ✅ bulk_create() 실행 후 ID 문제 해결 위해 다시 가져옴
        cls.players = list(Player.objects.all())  # 📌 모든 플레이어 다시 가져오기

        # 5️⃣ 첫 번째 선수의 스케줄 `bulk_create()` 사용
        schedules = [
            PlayerSchedule(
                player=cls.players[0],
                category="경기",
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(hours=2),
                place="Stadium",
                title="Match 1",
                detail="Detail info",
            )
        ]
        cls.schedules = PlayerSchedule.objects.bulk_create(schedules)

    # JWT 인증 설정 (쿼리 최소화 유지)
    def authenticate(self, user: User) -> None:
        token = str(RefreshToken.for_user(user).access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # ✅ 전체 선수 목록 조회 API 테스트
    def test_get_player_list(self) -> None:
        url = reverse("player-list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 15)

    # ✅ 특정 선수 상세 정보 조회 API 테스트
    def test_get_player_detail(self) -> None:
        player = self.__class__.players[0]
        url = reverse("player-detail", kwargs={"pk": player.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], player.id)
        self.assertEqual(response.data["nickname"], player.nickname)

    # ✅ 관리자가 선수를 삭제하는 API 테스트
    def test_delete_player(self) -> None:
        player = self.__class__.players[0]
        url = reverse("player-detail", kwargs={"pk": player.id})
        self.authenticate(self.__class__.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Player.objects.filter(pk=player.id).exists())

    # ✅ 특정 선수의 스케줄 목록 조회 API 테스트
    def test_get_player_schedule_list(self) -> None:
        player = self.__class__.players[0]
        url = reverse("player-schedule-list", kwargs={"player_id": player.id})

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    # ✅ 선수 생성 후 상세 조회 (커버리지 복구)
    def test_create_player_and_get_detail(self) -> None:
        url = reverse("player-list")
        self.authenticate(self.admin_user)

        data = {
            "team_id": self.team.id,
            "realname": "Created Player",
            "nickname": "CreatedNick",
            "gamename": "CreatedGameName",
            "position": "mid",
            "date_of_birth": "1996-06-06",
            "debut_date": "2016-06-06",
            "social": {"insta": "http://instagram.com/newplayer"},
            "agency": "AgencyZ",
        }

        # ✅ 선수 생성
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # ✅ 생성된 선수의 ID로 상세 조회 API 호출
        player_id = Player.objects.get(nickname="CreatedNick").id
        detail_url = reverse("player-detail", kwargs={"pk": player_id})
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
