from typing import Any, Optional

from django.db.models import Count
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Player, PlayerSchedule
from .serializers import (
    PlayerPositionSerializer,
    PlayerProfileSerializer,
    PlayerScheduleSerializer,
    PlayerSerializer,
    PlayerTopSerializer,
)


# 전체 Player 조회
class PlayerList(APIView):
    """
    타입 어노테이션은 변수나 함수의 타입 정보를 명시하여 코드의 가독성과 안정성을 높여주며, 정적 타입 검사 도구와 IDE의 기능을 향상시킴
    """

    def get(self, request: Any, format: Optional[str] = None) -> Response:
        # 모든 Player 객체를 데이터베이스에서 조회
        players = Player.objects.all()
        # 조회한 Player 객체들을 PlayerSerializer를 사용하여 직렬화
        # many=True는 여러 개의 객체를 직렬화할 때 사용
        serializer = PlayerSerializer(players, many=True)
        # 직렬화된 데이터를 Response 객체로 반환
        return Response(serializer.data)


# Player 프로필 조회
class PlayerDetail(APIView):
    def get(self, request: Request, pk: int, format: Optional[str] = None) -> Response:
        try:
            # 주어진 pk에 해당하는 Player 객체를 조회
            player = Player.objects.get(pk=pk)
        # 해당 객체가 존재하지 않으면 Player.DoesNotExist 예외가 발생
        # DoesNotExist는 "해당 객체가 존재하지 않음"을 나타내는 Django의 기본 예외이며
        # 이를 통해 조회 실패 시 적절한 에러 처리를 할 수 있음
        except Player.DoesNotExist:
            # 객체가 존재하지 않으면 NotFound 예외를 발생시켜 404 에러 응답을 보냄
            raise NotFound(detail="해당 플레이어를 찾을 수 없습니다.")

        # 조회된 Player 객체를 PlayerProfileSerializer를 사용하여 직렬화
        serializer = PlayerProfileSerializer(player)
        # 직렬화된 데이터를 Response 객체에 담아 클라이언트에게 반환
        return Response(serializer.data, status=status.HTTP_200_OK)


# 구독 수가 많은 상위 10명의 선수 조회
class TopPlayers(APIView):
    def get(self, request: Request, format: Optional[str] = None) -> Response:
        try:
            """
            어노테이션은 QuerySet에 새로운 필드(계산된 값)를 추가하기 위한 메서드,
            subscriber_count는 각 선수의 구독자 수를 나타내는 동적으로 추가된 필드,
            Count("subscriptions")는 각 Player 객체와 연결된 subscriptions의 개수를 계산
            """
            # 각 Player 객체에 대해 연결된 subscriptions의 개수를 어노테이션하여
            # subscriber_count 필드에 저장한 후, 이를 기준으로 내림차순 정렬하고 상위 10개를 조회
            top_players = Player.objects.annotate(subscriber_count=Count("subscriptions")).order_by(
                "-subscriber_count"
            )[:10]
            # 조회된 top_players 객체들을 PlayerTopSerializer를 사용하여 직렬화
            # many=True는 여러 개의 객체를 직렬화할 때 사용
            serializer = PlayerTopSerializer(top_players, many=True)
            # 직렬화된 데이터를 Response 객체로 반환
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # 에러가 발생하면 에러 메시지와 함께 500 에러를 반환
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 포지션의 구독 수가 많은 상위 5명의 선수 조회
class PositionTop(APIView):
    def get(self, request: Request, format: Optional[str] = None) -> Response:
        # 클라이언트의 요청에서 쿼리 파라미터로 전달된 'position' 값을 가져옴
        position = request.query_params.get("position")
        if not position:
            # 만약 'position' 값이 제공되지 않았다면,
            # 클라이언트에게 400 오류와 함께 에러 메시지를 반환
            return Response({"error": "Position parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # Player 모델에서, 포지션 필드가 요청한 값과 일치하는 선수들만 필터링함
            # 필터링된 Player 객체들에 대해, 연결된 subscriptions의 개수를 계산하여
            # subscriber_count라는 이름의 동적 필드로 추가
            # 이후, subscriber_count 필드를 기준으로 내림차순 정렬한 후 상위 5명을 선택
            top_players = (
                Player.objects.filter(position=position)
                .annotate(subscriber_count=Count("subscriptions"))
                .order_by("-subscriber_count")[:5]
            )

            # 조회된 Player 객체들을 PlayerPositionSerializer를 사용하여 직렬화
            # many=True는 여러 개의 객체를 직렬화할 때 사용
            serializer = PlayerPositionSerializer(top_players, many=True)

            # 직렬화된 데이터를 HTTP 200상태 코드와 함께 Response 객체로 반환
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # 예외 발생 시, 에러 메시지와 함께 HTTP 500상태 코드를 반환
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 선수의 스케줄 조회
class PlayerScheduleList(APIView):
    def get(self, request: Request, pk: int, format: Optional[str] = None) -> Response:
        try:
            # 주어진 pk에 해당하는 Player의 스케줄들을 조회
            schedules = PlayerSchedule.objects.filter(player_id=pk)
            # 조회된 스케줄들을 PlayerScheduleSerializer를 사용해 직렬화
            # many=True는 여러 개의 객체를 직렬화할 때 사용
            serializer = PlayerScheduleSerializer(schedules, many=True)
            # 직렬화된 데이터를 HTTP 200 상태와 함께 반환
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # 예외 발생 시, 에러 메시지와 함께 HTTP 500상태 코드를 반환
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
