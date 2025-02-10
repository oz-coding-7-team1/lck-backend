from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.players.models import Player
from apps.teams.models import Team
from .models import PlayerImage, TeamImage  # 이미지 모델 import


class PlayerImageListView(APIView):
    """특정 선수의 모든 이미지를 가져오는 API"""

    def get(self, request, player_id):
        player = get_object_or_404(Player, id=player_id)
        images = PlayerImage.objects.filter(player=player, deleted_at__isnull=True)

        image_list = [{"type": img.type, "url": img.url} for img in images]

        return Response(
            {"player": player.realname, "images": image_list},
            status=status.HTTP_200_OK,
        )


class TeamImageListView(APIView):
    """특정 팀의 모든 이미지를 가져오는 API"""

    def get(self, request, team_id):
        team = get_object_or_404(Team, id=team_id)
        images = TeamImage.objects.filter(team=team, deleted_at__isnull=True)

        image_list = [{"type": img.type, "url": img.url} for img in images]

        return Response(
            {"team": team.name, "images": image_list},
            status=status.HTTP_200_OK,
        )
