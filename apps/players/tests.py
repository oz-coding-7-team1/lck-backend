from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from apps.players.models import Player, PlayerSchedule
from apps.subscriptions.models import PlayerSubscription
from apps.teams.models import Team

User = get_user_model()


class PlayerAPITestCase(APITestCase):
    def setUp(self) -> None:
        # 관리자 유저 1명 생성
        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="adminpass", is_staff=True, nickname="admin"  # 관리자 고유 nickname
        )
        # 일반 유저 20명 생성
        self.normal_users = []
        for i in range(20):
            user = User.objects.create_user(
                email=f"normal{i}@example.com",
                password="normalpass",
                nickname=f"normal{i}",  # 각 일반 유저는 고유한 nickname을 가짐
            )
            self.normal_users.append(user)

        # 선수 생성에 사용할 팀 객체를 생성
        self.team = Team.objects.create(name="Test Team")

        # 15명의 선수를 생성
        # 짝수 인덱스의 선수는 팀에 소속되고 홀수 인덱스의 선수는 소속되지 않음
        # positions 리스트를 순환하여 각 선수에게 포지션 값을 할당
        positions = ["top", "jungle", "mid", "bottom", "support"]
        self.players = []
        for i in range(15):
            player = Player.objects.create(
                team=self.team if i % 2 == 0 else None,  # 짝수 인덱스: 팀 소속, 홀수 인덱스: 팀 미소속
                realname=f"RealName{i}",
                nickname=f"Nick{i}",  # 각 선수의 nickname은 고유하게 생성
                gamename=f"GameName{i}",
                position=positions[i % len(positions)],  # positions 리스트의 값을 순환하며 할당
                date_of_birth=date(1990, 1, 1),
                debut_date=date(2010, 1, 1),
                social={"insta": f"http://instagram.com/player{i}"},
                agency="AgencyX",
            )
            self.players.append(player)

        # 테스트용으로 첫 번째 선수(self.players[0])의 스케줄 하나를 생성
        self.schedule = PlayerSchedule.objects.create(
            player=self.players[0],
            category="경기",  # 경기 일정으로 분류
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(hours=2),
            place="Stadium",
            title="Match 1",
            detail="Detail info",
        )

    # 전체 선수 목록을 조회하는 API
    def test_get_player_list(self) -> None:
        # 'player-list' URL 경로를 reverse 함수를 통해 생성
        url = reverse("player-list")
        response = self.client.get(url)
        # HTTP 200 OK 상태 코드를 반환하는지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 반환된 데이터의 길이가 15인지 (생성한 선수 수와 일치) 확인
        self.assertEqual(len(response.data), 15)

    # 관리자 계정으로 새로운 선수를 생성하는 API
    def test_create_player_by_admin(self) -> None:
        url = reverse("player-list")
        data = {
            "team_id": self.team.id,
            "realname": "New RealName",
            "nickname": "NewNick",  # 새로운 고유 nickname
            "gamename": "NewGameName",
            "position": "top",
            "date_of_birth": "1995-05-05",
            "debut_date": "2015-05-05",
            "social": {"insta": "http://instagram.com/newplayer"},
            "agency": "AgencyY",
        }
        # 관리자 계정으로 로그인 (이메일이 username 역할)
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.post(url, data, format="json")
        # HTTP 201 Created 상태 코드를 반환하는지 확인
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 응답 데이터에 '선수 등록 완료'라는 메시지가 포함되어 있는지 확인
        self.assertEqual(response.data.get("detail"), "선수 등록 완료")

    # 일반 사용자로 선수를 생성하려고 시도할 때
    def test_create_player_by_normal_user(self) -> None:
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
        # 일반 사용자 계정으로 로그인
        self.client.login(username="normal0@example.com", password="normalpass")
        # POST 요청 시도를 통해 선수를 생성하려고 함
        response = self.client.post(url, data, format="json")
        # 일반 사용자는 관리자 권한이 없으므로 HTTP 403 Forbidden 상태 코드를 반환
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # 특정 선수의 상세 정보를 조회하는 API
    def test_get_player_detail(self) -> None:
        # 테스트 대상 선수 선택 (players 리스트의 첫 번째 선수)
        player = self.players[0]
        # 'player-detail' URL 경로를 생성하며 URL의 pk 파라미터에 선수 id를 전달
        url = reverse("player-detail", kwargs={"pk": player.id})
        # GET 요청으로 선수의 상세 정보를 조회
        response = self.client.get(url)
        # HTTP 200 OK 상태 코드를 반환하는지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 데이터의 id와 nickname이 생성된 선수의 정보와 일치하는지 확인
        self.assertEqual(response.data["id"], player.id)
        self.assertEqual(response.data["nickname"], player.nickname)

    # 관리자가 선수의 상세 정보를 수정하는 API
    def test_update_player_detail(self) -> None:
        player = self.players[0]
        # 'player-detail' URL 경로 생성 (선수의 id를 URL에 포함)
        url = reverse("player-detail", kwargs={"pk": player.id})
        # 관리자 계정으로 로그인
        self.client.login(username="admin@example.com", password="adminpass")
        data = {
            "team_id": self.team.id,
            "realname": "Updated RealName",
            "nickname": player.nickname,  # nickname은 중복 이슈를 피하기 위해 기존 값 유지
            "gamename": "UpdatedGameName",
            "position": player.position,
            "date_of_birth": "1991-01-01",
            "debut_date": "2011-01-01",
            "social": {"insta": "http://instagram.com/updated"},
            "agency": "UpdatedAgency",
        }
        # PUT 요청을 통해 전체 객체를 업데이트
        response = self.client.put(url, data, format="json")
        # HTTP 200 OK 상태 코드를 반환하는지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답에 '선수 프로필 수정 완료' 메시지가 포함되어 있는지 확인
        self.assertEqual(response.data.get("detail"), "선수 프로필 수정 완료")

    # 관리자가 선수를 비활성화(활성 상태 변경)하는 API
    def test_deactivate_player(self) -> None:
        player = self.players[0]
        # 'player-detail' URL 경로 생성
        url = reverse("player-detail", kwargs={"pk": player.id})
        # 관리자 계정으로 로그인
        self.client.login(username="admin@example.com", password="adminpass")
        data = {"is_active": False}
        # PATCH 요청으로 선수의 일부 속성(여기서는 is_active)을 업데이트
        response = self.client.patch(url, data, format="json")
        # HTTP 204 No Content 상태 코드를 반환하는지 확인
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # DB에서 최신 선수 데이터를 불러와 is_active 값이 False로 변경되었는지 확인
        player.refresh_from_db()
        self.assertFalse(player.is_active)

    # 관리자가 선수를 삭제하는 API
    def test_delete_player(self) -> None:
        player = self.players[0]
        # 'player-detail' URL 경로 생성 (삭제할 선수의 id 포함)
        url = reverse("player-detail", kwargs={"pk": player.id})
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.delete(url)
        # HTTP 204 No Content 상태 코드를 반환하는지 확인
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 삭제된 선수를 DB에서 조회할 경우, Player.DoesNotExist 예외가 발생해야 함
        with self.assertRaises(Player.DoesNotExist):
            Player.objects.get(pk=player.id)

    # 구독 수를 기반으로 상위 선수 10명을 조회하는 API
    def test_top_players(self) -> None:
        # 상위 5명의 선수에 대해, 각각 다른 수의 구독을 생성
        # 첫 번째 선수에는 5개의 구독, 두 번째 선수에는 4개, ... 형식으로 생성
        for i, player in enumerate(self.players[:10]):
            count = 10 - i  # 각 선수에 할당할 구독 수
            for user in self.normal_users[:count]:
                PlayerSubscription.objects.create(user=user, player=player)
        url = reverse("top-players")
        response = self.client.get(url)
        # HTTP 200 OK 상태 코드를 반환하는지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 데이터의 첫 번째 항목이 가장 인기 있는 선수여야 함
        top_player = response.data[0]
        self.assertEqual(top_player["id"], self.players[0].id)

    # 구독 수를 기반으로 상위 특정 포지션의 상위 5명 선수들을 조회하는 API
    def test_position_top(self) -> None:
        url = reverse("position-top")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 데이터는 포지션 이름을 키로 하고 해당 포지션의 선수 리스트를 값으로 갖는 딕셔너리
        positions_data = response.data  # {"top": [...], "jungle": [...], ...}
        # 모든 포지션에 대해 각 선수의 position 필드가 해당 키와 일치하는지 확인
        for position, players in positions_data.items():
            for player in players:
                self.assertEqual(player["position"], position)

    # 특정 선수의 스케줄 목록을 조회하는 API
    def test_get_player_schedule_list(self) -> None:
        player = self.players[0]
        url = reverse("player-schedule-list", kwargs={"player_id": player.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 생성 시점에 추가한 스케줄이 1개 있는지 확인
        self.assertEqual(len(response.data), 1)

    # 관리자가 선수를 위한 새로운 스케줄을 생성하는 API
    def test_create_player_schedule(self) -> None:
        player = self.players[1]
        url = reverse("player-schedule-list", kwargs={"player_id": player.id})
        data = {
            "category": "생일",
            "start_date": timezone.now().isoformat(),  # ISO 포맷의 날짜 문자열
            "end_date": (timezone.now() + timedelta(hours=1)).isoformat(),
            "place": "Arena",
            "title": "Birthday Event",
            "detail": "Celebrate birthday",
        }
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # 응답 메시지가 '선수 스케줄 생성 완료'인지 확인
        self.assertEqual(response.data.get("detail"), "선수 스케줄 생성 완료")

    # 관리자가 선수의 스케줄 정보를 수정하는 API
    def test_update_player_schedule(self) -> None:
        schedule = self.schedule
        url = reverse(
            "player-schedule-detail",
            kwargs={"player_id": schedule.player.id, "schedule_id": schedule.id},
        )
        self.client.login(username="admin@example.com", password="adminpass")
        data = {
            "title": "Updated Match Title",
            "detail": "Updated details",
        }
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("detail"), "선수 스케줄 수정 완료")

    # 관리자가 선수의 스케줄을 삭제하는 API
    def test_delete_player_schedule(self) -> None:
        schedule = self.schedule
        url = reverse(
            "player-schedule-detail",
            kwargs={"player_id": schedule.player.id, "schedule_id": schedule.id},
        )
        self.client.login(username="admin@example.com", password="adminpass")
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 삭제된 스케줄을 DB에서 조회할 경우 PlayerSchedule.DoesNotExist 예외가 발생해야 함
        with self.assertRaises(PlayerSchedule.DoesNotExist):
            PlayerSchedule.objects.get(pk=schedule.id)
