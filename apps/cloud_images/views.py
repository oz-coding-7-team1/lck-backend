from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.players.models import Player
from apps.teams.models import Team

from .models import PlayerImage, TeamImage  # 이미지 모델 import


class PlayerImageListView(APIView):
    """특정 선수의 모든 이미지를 가져오는 API"""

    permission_classes = (AllowAny,)

    def get(self, request: Any, player_id: int) -> Response:
        player = get_object_or_404(Player, id=player_id)
        images = PlayerImage.objects.filter(player=player, deleted_at__isnull=True)

        image_list = [{"type": img.type, "url": img.url} for img in images]

        return Response(
            {"player": player.nickname, "images": image_list},
            status=status.HTTP_200_OK,
        )


class TeamImageListView(APIView):
    """특정 팀의 모든 이미지를 가져오는 API"""

    permission_classes = (AllowAny,)

    def get(self, request: Any, team_id: int) -> Response:
        # team = get_object_or_404(Team, id=team_id)
        try:
            team = Team.objects.get(id=team_id)
        except Team.DoesNotExist:
            # 객체가 없을 경우, NotFound 예외를 발생시켜 404 응답을 반환
            raise NotFound(detail="해당 팀 찾을 수 없습니다.")
        images = TeamImage.objects.filter(team=team, deleted_at__isnull=True)

        image_list = [{"type": img.type, "url": img.url} for img in images]

        return Response(
            {"team": team.name, "images": image_list},
            status=status.HTTP_200_OK,
        )
