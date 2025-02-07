from typing import Any, Optional

from django.db.models import Count
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Player, PlayerImage, PlayerSchedule
from .serializers import (
    PlayerImageSerializer,
    PlayerPositionSerializer,
    PlayerProfileSerializer,
    PlayerScheduleSerializer,
    PlayerSerializer,
    PlayerTopSerializer,
)


# 전체 Player 조회 모델의 목록을 처리하는 API 뷰
class PlayerList(APIView):
    # 검색 기능을 사용하도록 설정
    # SearchFilter를 사용하면 URL 쿼리 파라미터를 통해 검색할 수 있다.
    filter_backends = [SearchFilter]
    # 검색할 수 있는 필드를 지정
    search_fields = ["nickname", "realname", "position", "team_id"]

    def get(self, request: Any, format: Optional[str] = None) -> Response:
        # 모든 Player 객체를 데이터베이스에서 조회
        players = Player.objects.all()
        # 조회한 Player 객체들을 PlayerSerializer를 사용하여 직렬화
        # many=True는 여러 개의 객체를 직렬화할 때 사용
        serializer = PlayerSerializer(players, many=True)
        # 직렬화된 데이터를 Response 객체로 반환
        return Response(serializer.data)


# Player 프로필 모델의 개별 객체를 처리하는 API 뷰
class PlayerDetail(APIView):
    def get_object(self, pk: int) -> Player:
        # 주어진 pk에 해당하는 Player 객체를 반환, 없으면 404 에러 발생
        try:
            # Player 모델에서 기본 키가 pk와 일치하는 객체를 조회
            return Player.objects.get(pk=pk)
        # 해당 객체가 존재하지 않으면 Player.DoesNotExist 예외가 발생
        except Player.DoesNotExist:
            raise Http404

    def get(self, request: Any, pk: int, format: Optional[str] = None) -> Response:
        # 메서드를 호출하여 pk에 해당하는 Player 객체를 조회
        player = self.get_object(pk)
        # 조회된 Player 객체를 PlayerProfileSerializer를 사용하여 직렬화
        serializer = PlayerProfileSerializer(player)
        # 직렬화된 데이터를 Response 객체에 담아 클라이언트에게 반환
        return Response(serializer.data)


# 구독 수가 많은 상위 10명의 선수 정보를 반환하는 API 뷰
@api_view(["GET"])
def top_players(request: Any) -> Response:
    try:
        # 각 Player 객체에 대해 연결된 subscriptions의 개수를 어노테이션하여
        # subscriber_count 필드에 저장한 후, 이를 기준으로 내림차순 정렬하고 상위 10개를 조회
        top_players = Player.objects.annotate(subscriber_count=Count("subscriptions")).order_by("-subscriber_count")[
            :10
        ]
        # 조회된 top_players 객체들을 PlayerTopSerializer를 사용하여 직렬화
        # many=True는 여러 개의 객체를 직렬화할 때 사용
        serializer = PlayerTopSerializer(top_players, many=True)
        # 직렬화된 데이터를 Response 객체로 반환
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # 에러가 발생하면 에러 메시지와 함께 500 에러를 반환
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 포지션의 구독 수가 많은 상위 5명의 선수 정보를 반환하는 API 뷰
@api_view(["GET"])
def position_top(request: Any) -> Response:
    # 쿼리 파라미터로 포지션을 가져옴
    position = request.query_params.get("position")
    if not position:
        return Response({"error": "Position parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        # 해당 포지션의 Player 객체에 대해 연결된 subscriptions의 개수를 어노테이션하여
        # subscriber_count 필드에 저장한 후, 이를 기준으로 내림차순 정렬하고 상위 5개를 조회
        top_players = (
            # 데이터베이스에서 position 값이 쿼리 파라미터로 전달된 값과 일치하는 Player 객체들만 선택
            Player.objects.filter(position=position)
            # subscriber_count 필드에 저장한 후, 이를 기준으로 내림차순 정렬하고 상위 5개를 조회
            .annotate(subscriber_count=Count("subscriptions"))
            .order_by("-subscriber_count")[:5]
        )
        # 조회된 top_players 객체들을 PlayerPositionSerializer를 사용하여 직렬화
        serializer = PlayerPositionSerializer(top_players, many=True)
        # 직렬화된 데이터를 Response 객체로 반환
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        # 에러가 발생하면 에러 메시지와 함께 500 에러를 반환
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 선수의 이미지를 처리하는 API 뷰
class PlayerImageList(APIView):
    def get(self, request: Any, pk: int, format: Optional[str] = None) -> Response:
        # Player ID가 없으면 에러 메시지 반환
        if pk is None:
            return Response({"error": "Player ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # 주어진 pk에 해당하는 Player의 이미지 객체들을 데이터베이스에서 조회
            images = PlayerImage.objects.filter(player_id=pk)
            # 조회된 images 객체들을 PlayerImageSerializer를 사용하여 직렬화
            serializer = PlayerImageSerializer(images, many=True)
            # 직렬화된 데이터를 Response 객체로 반환
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # 에러가 발생하면 에러 메시지와 함께 500 에러를 반환
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 특정 선수의 스케줄을 처리하는 API 뷰
class PlayerScheduleList(APIView):
    def get(self, request: Any, pk: int, format: Optional[str] = None) -> Response:
        # Player ID가 없으면 에러 메시지 반환
        if pk is None:
            return Response({"error": "Player ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # 주어진 pk에 해당하는 Player의 스케줄 객체들을 데이터베이스에서 조회
            schedules = PlayerSchedule.objects.filter(player_id=pk)
            # 조회된 schedules 객체들을 PlayerScheduleSerializer를 사용하여 직렬화
            serializer = PlayerScheduleSerializer(schedules, many=True)
            # 직렬화된 데이터를 Response 객체로 반환
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            # 에러가 발생하면 에러 메시지와 함께 500 에러를 반환
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
