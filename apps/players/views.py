from typing import Any, Union

from django.db.models import Count
from django.db.models.query import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Player, PlayerImage, PlayerSchedule
from .serializers import (
    PlayerImageSerializer,
    PlayerProfileSerializer,
    PlayerScheduleSerializer,
    PlayerSerializer,
)


# 선수(Player) 관련 API ViewSet
class PlayerViewSet(viewsets.ReadOnlyModelViewSet[Player]):
    queryset = Player.objects.all()  # 모든 선수 데이터를 가져옴
    serializer_class = PlayerSerializer  # 데이터를 직렬화할 때 사용할 시리얼라이저 클래스 지정
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]  # 필터링, 정렬, 검색 기능을 위한 백엔드 설정
    filterset_fields = ["position", "team__name"]  # 포지션 및 팀명으로 필터링 가능 (쿼리 파라미터로 필터링)
    search_fields = ["nickname", "gamename"]  # 선수명 또는 게임 닉네임을 검색할 수 있음
    ordering_fields = ["nickname"]  # 닉네임을 기준으로 정렬 가능

    # 상위 10명의 선수를 조회하는 커스텀 액션
    @action(detail=False, methods=["get"])
    def top10(self, request: Any) -> Response:
        """
        각 선수의 구독자 수를 기준으로 상위 10명의 선수를 조회하는 메서드.
        :param request: 요청 객체
        :return: 상위 10명의 선수 데이터를 포함한 응답
        """
        top_players = Player.objects.annotate(subscriber_count=Count("tags")).order_by("-subscriber_count")[:10]
        serializer = self.get_serializer(top_players, many=True)  # 조회된 선수 데이터를 직렬화
        return Response(serializer.data)  # 직렬화된 데이터를 응답으로 반환

    # 특정 포지션의 상위 5명을 조회하는 커스텀 액션
    @action(detail=False, methods=["get"])
    def position_top5(self, request: Any) -> Response:
        """
        특정 포지션의 선수들 중 구독자 수 기준 상위 5명의 선수를 조회하는 메서드.
        :param request: 요청 객체
        :return: 해당 포지션 상위 5명의 선수 데이터를 포함한 응답
        """
        position = request.query_params.get("position")  # 쿼리 파라미터에서 포지션 정보를 가져옴
        if not position:  # 포지션 파라미터가 없는 경우 오류 응답 반환
            return Response({"error": "Position parameter is required."}, status=400)

        # 해당 포지션의 선수들 중 구독자 수 기준 상위 5명을 조회
        top_players = (
            Player.objects.filter(position=position)
            .annotate(subscriber_count=Count("tags"))
            .order_by("-subscriber_count")[:5]
        )
        serializer = self.get_serializer(top_players, many=True)  # 조회된 선수 데이터를 직렬화
        return Response(serializer.data)  # 직렬화된 데이터를 응답으로 반환


# 선수 프로필 정보를 제공하는 ViewSet
class PlayerProfileViewSet(viewsets.ReadOnlyModelViewSet[Player]):
    queryset = Player.objects.all()  # 모든 선수 데이터를 가져옴
    serializer_class = PlayerProfileSerializer  # 프로필 정보를 직렬화할 때 사용할 시리얼라이저 클래스 지정


# 선수 이미지 정보를 제공하는 ViewSet
class PlayerImageViewSet(viewsets.ReadOnlyModelViewSet[PlayerImage]):
    serializer_class = PlayerImageSerializer  # 이미지를 직렬화할 때 사용할 시리얼라이저 클래스 지정

    def get_queryset(self) -> QuerySet[PlayerImage]:
        """
        특정 선수의 이미지를 필터링하여 반환하는 메서드.
        :return: 특정 선수의 이미지 쿼리셋
        """
        player_id: Union[int, str] = self.kwargs.get("pk", "")  # URL 파라미터에서 선수 ID를 가져옴
        return PlayerImage.objects.filter(player_id=player_id)  # 해당 선수의 이미지를 필터링하여 반환


# 선수 스케줄 정보를 제공하는 ViewSet (소프트 딜리트된 데이터 제외)
class PlayerScheduleViewSet(viewsets.ReadOnlyModelViewSet[PlayerSchedule]):
    serializer_class = PlayerScheduleSerializer  # 스케줄 정보를 직렬화할 때 사용할 시리얼라이저 클래스 지정

    def get_queryset(self) -> QuerySet[PlayerSchedule]:
        """
        특정 선수의 스케줄을 필터링하여 반환하는 메서드 (소프트 딜리트되지 않은 데이터만).
        :return: 특정 선수의 스케줄 쿼리셋
        """
        player_id: Union[int, str] = self.kwargs.get("pk", "")  # URL 파라미터에서 선수 ID를 가져옴
        return PlayerSchedule.objects.filter(
            player_id=player_id, deleted_at__isnull=True
        )  # 소프트 딜리트되지 않은 스케줄을 필터링하여 반환
