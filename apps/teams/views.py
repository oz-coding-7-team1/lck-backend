from typing import Any, List

from django.db.models import Count
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Team, TeamSchedule
from .serializers import (
    TeamCreateSerializer,
    TeamDetailSerializer,
    TeamScheduleSerializer,
    TeamSerializer,
    TeamTopSerializer,
)


class TeamList(APIView):
    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method in ["POST"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    @extend_schema(
        summary="전체 팀 조회",
        description="데이터베이스에 존재하는 모든 팀 정보를 조회합니다.",
        responses={200: TeamSerializer(many=True)},
    )
    # 팀 전체 조회
    def get(self, request: Any) -> Response:
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="팀 등록",
        description="새로운 팀을 등록합니다.",
        request=TeamCreateSerializer,
        responses={
            201: OpenApiExample(
                "팀 등록 성공",
                value={"detail": "팀 등록 완료"},
            ),
            400: OpenApiExample(
                "팀 등록 실패",
                value={"field": ["에러 메시지 예시"]},
            ),
        },
    )
    # 팀 등록
    def post(self, request: Any) -> Response:
        serializer = TeamCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "팀 등록 완료"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class TeamDetail(APIView):
    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    @extend_schema(
        summary="팀 상세 정보 조회",
        description="팀의 상세 정보를 조회합니다.",
        responses={
            200: TeamDetailSerializer,
            404: OpenApiExample(
                "팀 조회 실패",
                value={"detail": "해당 팀을 찾을 수 없습니다."},
            ),
        },
    )
    # 팀 상세 페이지 조회
    def get(self, request: Any, pk: int) -> Response:
        try:
            team = Team.objects.prefetch_related("player_set").get(pk=pk)
        except Team.DoesNotExist:
            raise NotFound(detail="해당 팀을 찾을 수 없습니다.")

        serializer = TeamDetailSerializer(team, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="팀 상세 정보 수정",
        description="팀의 상세 정보를 수정합니다.",
        request=TeamDetailSerializer,
        responses={
            200: OpenApiExample(
                "팀 수정 성공",
                value={"detail": "팀 프로필 수정 완료"},
            ),
            400: OpenApiExample(
                "팀 수정 실패",
                value={"field": ["에러 메시지 예시"]},
            ),
            404: OpenApiExample(
                "팀 조회 실패",
                value={"detail": "해당 팀을 찾을 수 없습니다."},
            ),
        },
    )
    # 팀 상세 페이지 수정
    def put(self, request: Any, pk: int) -> Response:
        try:
            team = Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            raise NotFound(detail="해당 팀을 찾을 수 없습니다.")

        serializer = TeamDetailSerializer(team, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "팀 프로필 수정 완료"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="팀 삭제",
        description="팀 정보를 삭제합니다.",
        responses={
            204: OpenApiExample(
                "팀 삭제 성공",
                value={"detail": "팀 삭제 완료 (204 No Content)"},
            ),
            404: OpenApiExample(
                "팀 삭제 실패",
                value={"detail": "해당 팀을 찾을 수 없습니다."},
            ),
        },
    )
    # 팀 상세 페이지 삭제
    def delete(self, request: Any, pk: int) -> Response:
        try:
            team = Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            raise NotFound(detail="해당 팀을 찾을 수 없습니다.")

        team.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


# 상위 5팀 조회
class TeamRank(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()

    @extend_schema(
        summary="상위 5팀 조회",
        description="구독자 수 기준 상위 5팀 정보를 조회합니다.",
        responses={
            200: TeamTopSerializer(many=True),
            500: OpenApiExample(
                "내부 서버 에러",
                value={"error": "에러 메시지"},
            ),
        },
    )
    def get(self, request: Any) -> Response:
        try:
            top_teams = Team.objects.annotate(subscriber_count=Count("team_subscriptions")).order_by(
                "-subscriber_count"
            )[:5]
            serializer = TeamTopSerializer(top_teams, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class TeamScheduleList(APIView):

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    @extend_schema(
        summary="특정 팀 스케줄 조회",
        description="특정 팀의 모든 스케줄 정보를 조회합니다.",
        responses={200: TeamScheduleSerializer(many=True)},
    )
    # 특정 팀의 스케줄 조회
    def get(self, request: Any, team_id: int) -> Response:
        schedules = TeamSchedule.objects.filter(team_id=team_id)
        serializer = TeamScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="팀 스케줄 생성",
        description="특정 팀의 스케줄을 생성합니다.",
        request=TeamScheduleSerializer,
        responses={
            201: OpenApiExample(
                "팀 스케줄 생성 성공",
                value={"detail": "팀 스케줄 생성 완료"},
            ),
            400: OpenApiExample(
                "팀 스케줄 생성 실패",
                value={"field": ["에러 메시지 예시"]},
            ),
        },
    )
    # 특정 팀의 스케줄 생성
    def post(self, request: Any, team_id: int) -> Response:
        data = request.data.copy()
        data["team"] = team_id
        serializer = TeamScheduleSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "팀 스케줄 생성 완료"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class TeamScheduleDetail(APIView):
    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), IsAdminUser()]
        return [AllowAny()]

    @extend_schema(
        summary="특정 팀 스케줄 상세 조회",
        description="특정 팀의 특정 스케줄 상세 정보를 조회합니다.",
        responses={
            200: TeamScheduleSerializer,
            404: OpenApiExample(
                "스케줄 조회 실패",
                value={"detail": "해당 팀 스케줄을 찾을 수 없습니다."},
            ),
        },
    )
    # 특정 팀 스케줄 상세 조회
    def get(self, request: Any, team_id: int, schedule_id: int) -> Response:
        try:
            schedule = TeamSchedule.objects.get(pk=schedule_id, team_id=team_id)
        except TeamSchedule.DoesNotExist:
            raise NotFound(detail="해당 팀 스케줄을 찾을 수 없습니다.")

        serializer = TeamScheduleSerializer(schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="특정 팀 스케줄 수정",
        description="특정 팀의 스케줄을 부분 수정합니다.",
        request=TeamScheduleSerializer,
        responses={
            200: OpenApiExample(
                "팀 스케줄 수정 성공",
                value={"detail": "팀 스케줄 수정 완료"},
            ),
            400: OpenApiExample(
                "팀 스케줄 수정 실패",
                value={"field": ["에러 메시지 예시"]},
            ),
            404: OpenApiExample(
                "스케줄 조회 실패",
                value={"detail": "해당 팀 스케줄을 찾을 수 없습니다."},
            ),
        },
    )
    # 특정 팀 스케줄 상세 수정
    def patch(self, request: Any, team_id: int, schedule_id: int) -> Response:
        try:
            schedule = TeamSchedule.objects.get(pk=schedule_id, team_id=team_id)
        except TeamSchedule.DoesNotExist:
            raise NotFound(detail="해당 팀 스케줄을 찾을 수 없습니다.")

        serializer = TeamScheduleSerializer(schedule, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "팀 스케줄 수정 완료"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="특정 팀 스케줄 삭제",
        description="특정 팀의 스케줄을 삭제합니다.",
        responses={
            204: OpenApiExample(
                "팀 스케줄 삭제 성공",
                value={"detail": "팀 스케줄 삭제 완료 (204 No Content)"},
            ),
            404: OpenApiExample(
                "스케줄 삭제 실패",
                value={"detail": "해당 팀 스케줄을 찾을 수 없습니다."},
            ),
        },
    )
    # 특정 팀 스케줄 상세 삭제
    def delete(self, request: Any, team_id: int, schedule_id: int) -> Response:
        try:
            schedule = TeamSchedule.objects.get(pk=schedule_id, team_id=team_id)
        except TeamSchedule.DoesNotExist:
            raise NotFound(detail="해당 팀 스케줄을 찾을 수 없습니다.")

        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
