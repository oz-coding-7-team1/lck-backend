from datetime import date
from typing import Any

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.players.models import Player
from apps.subscriptions.models import PlayerSubscription

# 커스텀 User 모델을 가져
User = get_user_model()


# 테스트용 Player 객체를 생성하는 헬퍼 함수
# 반환값: 생성된 Player 인스턴스
def create_player(nickname: str, realname: str, position: str) -> Player:
    return Player.objects.create(
        realname=realname,  # 플레이어의 실제 이름
        nickname=nickname,  # 플레이어의 고유 닉네임
        gamename=f"game_{nickname}",  # 게임 내에서 사용하는 이름 (닉네임 기반)
        position=position,  # 플레이어의 포지션
        date_of_birth=date(2000, 1, 1),  # 예시 생년월일
        debut_date=date(2020, 1, 1),  # 예시 데뷔일
        agency="TestAgency",  # 테스트용 소속사 이름
        social={},  # 소셜 미디어 정보 (빈 딕셔너리)
    )


# 테스트용 PlayerSubscription 객체를 생성하는 헬퍼 함수
def create_subscription(player: Player, user: Any) -> PlayerSubscription:
    return PlayerSubscription.objects.create(player=player, user=user)


# 전체 플레이어 중 구독 수가 많은 상위 플레이어들을 반환하는 API 엔드포인트를 테스트하는 클래스
class TopPlayersAPITest(APITestCase):
    # 각 테스트가 실행되기 전에 호출되는 설정 메서드
    def setUp(self) -> None:
        # 테스트용 사용자(User)들을 생성합니다. 각 사용자는 고유의 nickname을 가짐
        self.user1 = User.objects.create_user(email="user1@example.com", password="pass", nickname="user1")
        self.user2 = User.objects.create_user(email="user2@example.com", password="pass", nickname="user2")
        self.user3 = User.objects.create_user(email="user3@example.com", password="pass", nickname="user3")
        self.user4 = User.objects.create_user(email="user4@example.com", password="pass", nickname="user4")
        self.user5 = User.objects.create_user(email="user5@example.com", password="pass", nickname="user5")
        self.user6 = User.objects.create_user(email="user6@example.com", password="pass", nickname="user6")

        # 3명의 플레이어 객체를 생성
        self.player1 = create_player("P1", "Player One", "top")
        self.player2 = create_player("P2", "Player Two", "mid")
        self.player3 = create_player("P3", "Player Three", "bot")

        # player1에 대해 2명의 사용자가 구독 (구독 수 = 2)
        create_subscription(self.player1, self.user1)
        create_subscription(self.player1, self.user2)

        # player2에 대해 3명의 사용자가 구독 (구독 수 = 3)
        create_subscription(self.player2, self.user1)
        create_subscription(self.player2, self.user2)
        create_subscription(self.player2, self.user3)

        # player3에 대해 1명의 사용자가 구독 (구독 수 = 1)
        create_subscription(self.player3, self.user1)

    # 구독 수가 많은 상위 플레이어들이 올바른 순서로 반환되는지 테스트
    # 예상 결과:
    #   - player2 (구독 수 3)
    #   - player1 (구독 수 2)
    #   - player3 (구독 수 1)
    def test_top_players_ordering(self) -> None:
        # URL 패턴 이름 "top-players"를 사용하여 API URL을 조회
        url = reverse("top-players")
        # 조회한 URL로 GET 요청
        response = self.client.get(url)
        # 응답 상태 코드가 200(성공)인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 JSON 데이터를 파싱
        data = response.json()
        # 반환된 플레이어 수가 3개인지 확인
        self.assertEqual(len(data), 3)
        # 반환된 데이터의 순서가 구독 수 내림차순인지 확인
        # 첫 번째 항목은 구독 수가 3인 player2여야함
        self.assertEqual(data[0]["nickname"], "P2")
        # 두 번째 항목은 구독 수가 2인 player1이어야함
        self.assertEqual(data[1]["nickname"], "P1")
        # 세 번째 항목은 구독 수가 1인 player3이어야함
        self.assertEqual(data[2]["nickname"], "P3")


# 특정 포지션의 플레이어 중 구독 수가 많은 순서대로 상위 5개를 반환하는 API 엔드포인트를 테스트하는 클래스
class PositionTopAPITest(APITestCase):
    # 각 테스트가 실행되기 전에 호출되는 설정 메서드
    def setUp(self) -> None:
        # 테스트용 사용자(User)들을 생성
        self.user1 = User.objects.create_user(email="user1@example.com", password="pass", nickname="user1")
        self.user2 = User.objects.create_user(email="user2@example.com", password="pass", nickname="user2")
        self.user3 = User.objects.create_user(email="user3@example.com", password="pass", nickname="user3")
        self.user4 = User.objects.create_user(email="user4@example.com", password="pass", nickname="user4")

        # 'mid' 포지션에 해당하는 플레이어 3개를 생성
        self.player_mid_1 = create_player("M1", "Mid One", "mid")
        self.player_mid_2 = create_player("M2", "Mid Two", "mid")
        self.player_mid_3 = create_player("M3", "Mid Three", "mid")

        # player_mid_1에 대해 1명의 사용자가 구독 (구독 수 = 1)
        create_subscription(self.player_mid_1, self.user1)

        # player_mid_2에 대해 3명의 사용자가 구독 (구독 수 = 3)
        create_subscription(self.player_mid_2, self.user1)
        create_subscription(self.player_mid_2, self.user2)
        create_subscription(self.player_mid_2, self.user3)

        # player_mid_3에 대해 2명의 사용자가 구독 (구독 수 = 2)
        create_subscription(self.player_mid_3, self.user1)
        create_subscription(self.player_mid_3, self.user2)

    # 포지션 파라미터가 전달되지 않았을 때 API가 400 에러를 반환하는지 테스트
    def test_position_top_without_parameter(self) -> None:
        # URL 패턴 이름 "position-top"을 사용하여 API URL을 조회
        url = reverse("position-top")
        # 쿼리 파라미터 없이 GET 요청
        response = self.client.get(url)
        # 응답 상태 코드가 400(Bad Request)인지 확인
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # 응답 오류 메시지에 "Position parameter is required"가 포함되어 있는지 확인
        self.assertIn("Position parameter is required", response.json().get("error", ""))

    # 'mid' 포지션의 플레이어 중 구독 수 내림차순 정렬 결과가 올바르게 반환되는지 테스트
    # 예상 결과:
    #   - player_mid_2 (구독 수 3)
    #   - player_mid_3 (구독 수 2)
    #   - player_mid_1 (구독 수 1)
    def test_position_top_ordering(self) -> None:
        # URL 패턴 이름 "position-top"을 사용하여 API URL을 조회
        url = reverse("position-top")
        # 'position' 쿼리 파라미터를 'mid'로 설정하여 GET 요청
        response = self.client.get(url, {"position": "mid"})
        # 응답 상태 코드가 200(성공)인지 확인
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 응답 JSON 데이터를 파싱
        data = response.json()
        # 'mid' 포지션의 플레이어 수가 3개인지 확인
        self.assertEqual(len(data), 3)
        # 반환된 데이터가 구독 수 내림차순으로 정렬되어 있는지 확인
        # 첫 번째 항목은 구독 수가 3인 player_mid_2여야함
        self.assertEqual(data[0]["nickname"], "M2")
        # 두 번째 항목은 구독 수가 2인 player_mid_3이어야함
        self.assertEqual(data[1]["nickname"], "M3")
        # 세 번째 항목은 구독 수가 1인 player_mid_1이어야함
        self.assertEqual(data[2]["nickname"], "M1")
