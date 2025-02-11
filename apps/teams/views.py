from typing import Any, List

from django.db.models import Count
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Team, TeamSchedule
from .serializers import (
    TeamCreateSerializer,
    TeamDetailSerializer,
    TeamScheduleSerializer,
    TeamSerializer,
    TeamTopSerializer,
)


class TeamList(APIView):
    def get_permissions(self) -> List[Any]:
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return []

    # 팀 전체 조회
    def get(self, request: Any) -> Response:
        teams = Team.objects.all()
        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)

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
    def get_permissions(self) -> List[Any]:
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated(), IsAdminUser()]
        return []

    # 팀 상세 페이지 조회
    def get(self, request: Any, pk: int) -> Response:
        try:
            team = Team.objects.prefetch_related("player_set").get(pk=pk)
        except Team.DoesNotExist:
            raise NotFound(detail="해당 팀을 찾을 수 없습니다.")

        serializer = TeamDetailSerializer(team)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    def get_permissions(self) -> List[Any]:
        if self.request.method == "POST":
            return [IsAuthenticated(), IsAdminUser()]
        return []

    # 특정 팀의 스케줄 조회
    def get(self, request: Any, team_id: int) -> Response:
        schedules = TeamSchedule.objects.filter(team_id=team_id)
        serializer = TeamScheduleSerializer(schedules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    def get_permissions(self) -> List[Any]:
        if self.request.method in ["PATCH", "DELETE"]:
            return [IsAuthenticated(), IsAdminUser()]
        return []

    # 특정 팀 스케줄 상세 조회
    def get(self, request: Any, team_id: int, schedule_id: int) -> Response:
        try:
            schedule = TeamSchedule.objects.get(pk=schedule_id, team_id=team_id)
        except TeamSchedule.DoesNotExist:
            raise NotFound(detail="해당 팀 스케줄을 찾을 수 없습니다.")

        serializer = TeamScheduleSerializer(schedule)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

    # 특정 팀 스케줄 상세 삭제
    def delete(self, request: Any, team_id: int, schedule_id: int) -> Response:
        try:
            schedule = TeamSchedule.objects.get(pk=schedule_id, team_id=team_id)
        except TeamSchedule.DoesNotExist:
            raise NotFound(detail="해당 팀 스케줄을 찾을 수 없습니다.")

        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
