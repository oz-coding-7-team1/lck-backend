from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.players.models import Player
from apps.teams.models import Team

from .models import PlayerSubscription, TeamSubscription
from .serializers import PlayerSubscriptionSerializer, TeamSubscriptionSerializer


class PlayerSubscriptionView(APIView):
    # authentication_classes = (JWTAuthentication,)  # JWT 토큰 검증
    # permission_classes = (IsAuthenticated,)  # 인증된 사용자만 접근 가능

    @transaction.atomic  # 동시성 문제를 해결하기 위해 트랜잭션
    def post(self, request: Any, player_id: int) -> Response:
        user = request.user
        player = get_object_or_404(Player, id=player_id)

        # 객체가 존재하면 객체를 반환하고 created는 False가 된다
        # 객체가 존재하지 않으면 인자로 들어간 값대로 생성된다.
        subscription, created = PlayerSubscription.objects.get_or_create(
            user=user, player=player, defaults={"deleted_at": None}
        )

        # 소프트 딜리트가 된 객체를 다시 복구하는 코드
        if not created and subscription.deleted_at:
            subscription.restore()
            subscription.save()

        serializer = PlayerSubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def delete(self, request: Any, player_id: int) -> Response:
        user = request.user
        subscription = get_object_or_404(PlayerSubscription, user=user, player_id=player_id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # permission_classes = [AllowAny]  # get은 인증되지 않은 사용자도 접근 가능
    def get(self, request: Any, player_id: int) -> Response:
        count = PlayerSubscription.objects.filter(player_id=player_id, deleted_at__isnull=True).count()
        return Response({"count": count})


class TeamSubscriptionView(APIView):
    # authentication_classes = (JWTAuthentication,)  # JWT 토큰 검증
    # permission_classes = (IsAuthenticated,)  # 인증된 사용자만 접근 가능

    @transaction.atomic
    def post(self, request: Any, team_id: int) -> Response:
        user = request.user
        team = get_object_or_404(Team, id=team_id)

        subscription, created = TeamSubscription.objects.get_or_create(
            user=user, team=team, defaults={"deleted_at": None}
        )
        if not created and subscription.deleted_at:
            subscription.restore()
            subscription.save()

        serializer = TeamSubscriptionSerializer(subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def delete(self, request: Any, team_id: int) -> Response:
        user = request.user
        subscription = get_object_or_404(TeamSubscription, user=user, team_id=team_id)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # permission_classes = [AllowAny]  # 인증되지 않은 사용자도 접근 가능
    def get(self, request: Any, team_id: int) -> Response:
        count = TeamSubscription.objects.filter(team_id=team_id, deleted_at__isnull=True).count()
        return Response({"count": count})
