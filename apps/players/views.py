from typing import Any, List, Optional

from django.db.models import Count
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Player, PlayerSchedule, Position
from .serializers import (
    PlayerCreateSerializer,
    PlayerPositionSerializer,
    PlayerProfileSerializer,
    PlayerScheduleSerializer,
    PlayerSerializer,
    PlayerTopSerializer,
)


class PlayerList(APIView):
    def get_permissions(self) -> List[Any]:
        """
        GET 요청은 누구나 접근할 수 있지만,
        POST 요청은 인증된 관리자(Staff Permission)만 접근할 수 있도록 설정
        DRF에서 제공하는 권한 클래스의 인스턴스를 리스트 형태로 반환하는 코드 입니다.
        IsAuthenticated 클래스는 사용자가 로그인되어 있는지를 확인하고 요청하는 사용자가 인증되지 않은 상태라면 이 권한 검증에서 실패하게 되어 API 접근이 거부됩니다.
        IsAdminUser클래스는 인증된 사용자 중에서 관리자인지(예: is_staff=True 또는 is_superuser=True)를 확인하고 인증은 되어 있지만 관리자가 아닌 사용자라면 접근이 거부됩니다.
        """
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return []

    @extend_schema(
        summary="전체 선수 조회",
        description="데이터베이스에 존재하는 모든 선수 정보를 조회합니다.",
        responses={200: PlayerSerializer(many=True)},
    )
    # 전체 선수 조회
    def get(self, request: Any) -> Response:
        # 모든 Player 객체를 데이터베이스에서 조회
        players = Player.objects.all()
        # 조회한 Player 객체들을 PlayerSerializer를 사용하여 직렬화
        # many=True는 여러 개의 객체를 직렬화할 때 사용
        serializer = PlayerSerializer(players, many=True)
        # 직렬화된 데이터를 Response 객체로 반환
        return Response(serializer.data)

    @extend_schema(
        summary="선수 등록",
        description="새로운 선수를 등록합니다. position: top / jungle / mid / AD Carry / support",
        request=PlayerCreateSerializer,
        responses={
            201: OpenApiExample(
                "성공 응답 예시",
                value={"detail": "선수 등록 완료"},
            ),
            400: OpenApiExample(
                "선수 등록 실패",
                value={"field": ["에러 메시지 예시"]},
            ),
        },
    )
    # 선수 등록
    def post(self, request: Request) -> Response:
        # 클라이언트가 전송한 JSON 데이터를 기반으로 PlayerCreateSerializer를 초기화
        serializer = PlayerCreateSerializer(data=request.data)
        # 데이터 유효성 검증 수행
        if serializer.is_valid():
            # 데이터가 유효하면 새로운 Player 객체를 생성
            serializer.save()
            # 생성 성공 메시지와 함께 HTTP 201 상태 코드 반환
            return Response({"detail": "선수 등록 완료"}, status=status.HTTP_201_CREATED)
        # 데이터가 유효하지 않으면 에러 메시지와 함께 HTTP 400 상태 코드 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class PlayerDetail(APIView):

    def get_permissions(self) -> List[Any]:
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthenticated(), IsAdminUser()]
        return []

    @extend_schema(
        summary="선수 프로필 조회",
        description="선수의 상세 프로필 정보를 조회합니다.",
        responses={
            200: PlayerProfileSerializer,
            404: OpenApiExample(
                "선수 조회 실패",
                value={"detail": "해당 선수를 찾을 수 없습니다."},
            ),
        },
    )
    # 선수 프로필 조회
    def get(self, request: Request, pk: int) -> Response:
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
        serializer = PlayerProfileSerializer(player, context={"request": request})
        # 직렬화된 데이터를 Response 객체에 담아 클라이언트에게 반환
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="선수 프로필 수정",
        description="선수의 프로필 정보를 수정합니다. 전체 데이터를 재전송해야 합니다.",
        request=PlayerProfileSerializer,
        responses={
            200: OpenApiExample(
                "선수 수정 성공",
                value={"detail": "선수 프로필 수정 완료"},
            ),
            400: OpenApiExample(
                "선수 수정 실패",
                value={"field": ["에러 메시지 예시"]},
            ),
            404: OpenApiExample(
                "선수 조회 실패",
                value={"detail": "해당 선수를 찾을 수 없습니다."},
            ),
        },
    )
    # 선수 프로필 수정
    def put(self, request: Request, pk: int) -> Response:
        # 주어진 pk를 기반으로 Player 객체를 데이터베이스에서 조회
        try:
            player = Player.objects.get(pk=pk)
        except Player.DoesNotExist:
            # 객체가 없을 경우, NotFound 예외를 발생시켜 404 응답을 반환
            raise NotFound(detail="해당 플레이어를 찾을 수 없습니다.")

        # 클라이언트가 전송한 JSON 데이터를 이용해 PlayerProfileSerializer를 초기화
        # 기존의 Player 객체와 업데이트할 데이터를 함께 전달 (전체 필드 업데이트)
        serializer = PlayerProfileSerializer(player, data=request.data)

        # 전달받은 데이터의 유효성을 검사
        if serializer.is_valid():
            # 데이터가 유효하면 serializer.save()를 호출하여 Player 객체를 업데이트
            serializer.save()
            # 성공 메시지와 함께 HTTP 200 상태 코드를 반환
            return Response({"detail": "선수 프로필 수정 완료"}, status=status.HTTP_200_OK)

        # 데이터 유효성 검사에 실패한 경우, 에러 메시지와 함께 HTTP 400 상태 코드를 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="선수 비활성화",
        description="요청 본문에 is_active: false가 포함된 경우 선수를 비활성화합니다.",
        responses={
            204: OpenApiExample("비활성화 성공", value={"detail": "No Content"}),
            400: OpenApiExample(
                "잘못된 요청",
                value={"error": "요청 데이터가 올바르지 않습니다. is_active 값은 반드시 False여야 합니다."},
            ),
            404: OpenApiExample(
                "선수 조회 실패",
                value={"detail": "해당 플레이어를 찾을 수 없습니다."},
            ),
        },
    )
    # 선수 비활성화
    def patch(self, request: Request, pk: int) -> Response:
        try:
            # 주어진 pk를 기반으로 Player 객체를 데이터베이스에서 조회
            player = Player.objects.get(pk=pk)
        except Player.DoesNotExist:
            # 객체가 없으면 NotFound 예외를 발생시켜 404 응답 반환
            raise NotFound(detail="해당 플레이어를 찾을 수 없습니다.")

        # 요청 본문에 "is_active" 값이 False 인지 확인 (비활성화 요청)
        if request.data.get("is_active") is False:
            # Player 객체의 is_active 필드를 False로 변경
            player.is_active = False
            player.save()
            # HTTP 204 No Content 상태 코드를 반환
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # 요청 데이터가 올바르지 않으면 에러 메시지와 함께 HTTP 400 상태 코드 반환
            return Response(
                {"error": "요청 데이터가 올바르지 않습니다. is_active 값은 반드시 False여야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @extend_schema(
        summary="선수 삭제",
        description="해당 선수의 정보를 soft delete 방식으로 삭제합니다.",
        responses={
            204: OpenApiExample(
                "선수 삭제 성공",
                value={"detail": "선수 삭제 완료 (204 No Content)"},
            ),
            404: OpenApiExample(
                "선수 삭제 실패",
                value={"detail": "해당 선수를 찾을 수 없습니다."},
            ),
        },
    )
    # 선수 삭제
    def delete(self, request: Request, pk: int) -> Response:
        try:
            # 주어진 pk를 기반으로 Player 객체를 데이터베이스에서 조회
            player = Player.objects.get(pk=pk)
        except Player.DoesNotExist:
            # 객체가 없으면 NotFound 예외를 발생시켜 404 응답 반환
            raise NotFound(detail="해당 플레이어를 찾을 수 없습니다.")

        # soft delete 방식으로 Player 객체 삭제 (실제 삭제가 아닌 상태 변경)
        player.delete()
        # HTTP 204 No Content 상태 코드를 반환
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


# 구독 수가 많은 상위 10명의 선수 조회
class TopPlayers(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @extend_schema(
        summary="전체 선수 중 구독수 상위 10위",
        description="각 선수의 구독자 수를 계산하여 내림차순 정렬 후 상위 10명의 정보를 반환합니다.",
        responses={
            200: PlayerTopSerializer(many=True),
            500: OpenApiExample(
                "내부 서버 에러",
                value={"error": "에러 메시지"},
            ),
        },
    )
    def get(self, request: Request) -> Response:
        try:
            """
            어노테이션은 QuerySet에 새로운 필드(계산된 값)를 추가하기 위한 메서드,
            subscriber_count는 각 선수의 구독자 수를 나타내는 동적으로 추가된 필드,
            Count("player_subscriptions")는 각 Player 객체와 연결된 subscriptions의 개수를 계산
            """
            # 각 Player 객체에 대해 연결된 subscriptions의 개수를 어노테이션하여
            # subscriber_count 필드에 저장한 후, 이를 기준으로 내림차순 정렬하고 상위 10개를 조회
            top_players = Player.objects.annotate(subscriber_count=Count("player_subscriptions")).order_by(
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


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


# 특정 포지션의 구독 수가 많은 상위 5명의 선수 조회
class PositionTop(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @extend_schema(
        summary="포지션 별 선수 중 구독수 상위 5위",
        description="Position Enum에 정의된 각 포지션에 대해 구독자 수 기준 상위 5명의 선수를 반환합니다.",
        responses={
            200: PlayerPositionSerializer(many=True),
            500: OpenApiExample(
                "내부 서버 에러",
                value={"error": "에러 메시지"},
            ),
        },
    )
    def get(self, request: Any) -> Response:
        try:
            result = {}
            # Position Enum에 정의된 모든 포지션에 대해 반복
            for pos in Position:
                # 해당 포지션에 속하는 선수들을 필터링하고 구독자 수를 어노테이션한 후 내림차순 정렬하여 상위 5명을 선택
                players_qs = (
                    Player.objects.filter(position=pos.value)
                    .annotate(subscriber_count=Count("player_subscriptions"))
                    .order_by("-subscriber_count")[:5]
                )
                # 선택된 선수들을 직렬화
                serializer = PlayerPositionSerializer(players_qs, many=True)
                # 결과 딕셔너리에 포지션 값을 키로 하여 직렬화된 데이터를 저장
                result[pos.value] = serializer.data

            # 모든 포지션에 대한 결과를 포함하는 딕셔너리를 반환
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            # 예외 발생 시 에러 메시지와 함께 500 상태 코드를 반환
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class PlayerScheduleList(APIView):
    def get_permissions(self) -> List[Any]:
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return []

    @extend_schema(
        summary="선수 스케줄 전체 조회",
        description="특정 선수의 스케줄 목록을 조회합니다.",
        responses={200: PlayerScheduleSerializer(many=True)},
    )
    # 특정 선수의 스케줄 목록 조회
    def get(self, request: Request, player_id: int) -> Response:
        # 선수 ID에 해당하는 모든 스케줄 객체들을 필터링
        schedules = PlayerSchedule.objects.filter(player_id=player_id)
        # 조회한 스케줄 객체들을 PlayerScheduleSerializer를 이용하여 직렬화
        # many=True를 지정하여 여러 객체를 리스트 형태로 직렬화
        serializer = PlayerScheduleSerializer(schedules, many=True)
        # 직렬화된 데이터를 HTTP 200 상태 코드와 함께 클라이언트에 반환
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="선수 스케줄 생성",
        description="요청 본문에 스케줄 정보를 포함하여 특정 선수의 스케줄을 생성합니다. 경기 / 방송 / 팬미팅 / 기타",
        request=PlayerScheduleSerializer,
        responses={
            201: OpenApiExample(
                "생성 성공",
                value={"detail": "선수 스케줄 생성 완료"},
            ),
            400: OpenApiExample(
                "선수 스케줄 생성 실패",
                value={"field": ["에러 메시지 예시"]},
            ),
        },
    )
    # 특정 선수의 스케줄 목록 생성
    def post(self, request: Request, player_id: int) -> Response:
        # 클라이언트가 전송한 데이터를 복사
        data = request.data.copy()
        # URL에서 전달된 선수 ID를 사용하여 데이터의 'player' 필드를 설정
        data["player"] = player_id
        # PlayerScheduleSerializer를 사용하여 데이터의 유효성을 검사하고 직렬화
        serializer = PlayerScheduleSerializer(data=data)
        if serializer.is_valid():
            # 데이터가 유효하면 새 스케줄 객체를 생성
            serializer.save()
            # 생성 성공 메시지와 함께 HTTP 201 상태 코드를 반환
            return Response({"detail": "선수 스케줄 생성 완료"}, status=status.HTTP_201_CREATED)
        # 데이터 유효성 검사에 실패하면 오류 메시지와 함께 HTTP 400 상태 코드를 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class PlayerScheduleDetail(APIView):
    def get_permissions(self) -> List[Any]:
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), IsAdminUser()]
        return []

    @extend_schema(
        summary="선수 스케줄 상세 조회",
        description="특정 선수의 특정 스케줄 상세 정보를 조회합니다.",
        responses={
            200: PlayerScheduleSerializer,
            404: OpenApiExample(
                "스케줄 조회 실패",
                value={"detail": "해당 선수 스케줄을 찾을 수 없습니다."},
            ),
        },
    )
    # 특정 선수 스케줄 상세 조회
    def get(self, request: Request, player_id: int, schedule_id: int) -> Response:
        try:
            # 데이터베이스에서 선수 ID와 스케줄 ID가 모두 일치하는 스케줄 객체를 조회
            schedule = PlayerSchedule.objects.get(pk=schedule_id, player_id=player_id)
        except PlayerSchedule.DoesNotExist:
            # 만약 해당 스케줄 객체가 존재하지 않으면, 404 Not Found 예외를 발생
            raise NotFound(detail="해당 스케줄을 찾을 수 없습니다.")

            # 조회한 스케줄 객체를 직렬화하여 JSON 형태로 변환
        serializer = PlayerScheduleSerializer(schedule)

        # 직렬화된 데이터를 포함하는 응답 객체를 HTTP 200 상태 코드와 함께 반환
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="선수 스케줄 수정",
        description="요청 본문에 포함된 데이터로 특정 선수의 스케줄을 부분 수정합니다.",
        responses={
            200: OpenApiExample(
                "수정 성공",
                value={"detail": "선수 스케줄 수정 완료"},
            ),
            400: OpenApiExample(
                "선수 스케줄 수정 실패",
                value={"field": ["에러 메시지 예시"]},
            ),
            404: OpenApiExample(
                "스케줄 조회 실패",
                value={"detail": "해당 선수 스케줄을 찾을 수 없습니다."},
            ),
        },
    )
    # 특정 선수 스케줄 상세 수정
    def patch(self, request: Request, player_id: int, schedule_id: int) -> Response:
        try:
            # 데이터베이스에서 선수 ID와 스케줄 ID가 모두 일치하는 스케줄 객체를 조회
            schedule = PlayerSchedule.objects.get(pk=schedule_id, player_id=player_id)
        except PlayerSchedule.DoesNotExist:
            # 해당 스케줄 객체가 존재하지 않으면 404 Not Found 예외를 발생
            raise NotFound(detail="해당 스케줄을 찾을 수 없습니다.")
        # 전달받은 데이터로 부분 업데이트를 위한 serializer를 초기화합니다.
        serializer = PlayerScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            # 데이터가 유효하면 객체를 업데이트하고 저장
            serializer.save()
            # 업데이트 성공 메시지와 함께 HTTP 200 상태 코드를 반환
            return Response({"detail": "선수 스케줄 수정 완료"}, status=status.HTTP_200_OK)
        # 데이터 유효성 검사에 실패하면 오류 메시지와 함께 HTTP 400 상태 코드를 반환
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="선수 스케줄 삭제",
        description="특정 선수의 스케줄을 삭제합니다.",
        responses={
            204: OpenApiExample(
                "선수 스케줄 삭제 성공",
                value={"detail": "No Content"},
            ),
            404: OpenApiExample(
                "스케줄 삭제 실패",
                value={"detail": "해당 선수 스케줄을 찾을 수 없습니다."},
            ),
        },
    )
    # 특정 선수 스케줄 상세 삭제
    def delete(self, request: Request, player_id: int, schedule_id: int) -> Response:
        try:
            # 데이터베이스에서 선수 ID와 스케줄 ID가 모두 일치하는 스케줄 객체를 조회
            schedule = PlayerSchedule.objects.get(pk=schedule_id, player_id=player_id)
        except PlayerSchedule.DoesNotExist:
            # 해당 스케줄 객체가 존재하지 않으면 404 Not Found 예외를 발생
            raise NotFound(detail="해당 스케줄을 찾을 수 없습니다.")
        # 조회된 스케줄 객체를 삭제
        schedule.delete()
        # HTTP 204 상태 코드를 반환
        return Response(status=status.HTTP_204_NO_CONTENT)
