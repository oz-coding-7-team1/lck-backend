from datetime import timedelta
from typing import Any

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
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
        now = timezone.now()

        active_subscription = PlayerSubscription.objects.filter(user=user, player=player).first()
        if active_subscription:
            return Response(
                {"message": "You are already subscribed to this player."},
                status=status.HTTP_200_OK,
            )

        # Soft-delete된 구독이 있는지 확인 (all_objects 사용)
        deleted_subscription = PlayerSubscription.deleted_objects.filter(user=user, player=player).first()

        if deleted_subscription:
            if deleted_subscription.deleted_at and now - deleted_subscription.deleted_at < timedelta(hours=24):
                return Response(
                    {"error": "You cannot resubscribe within 24 hours of unsubscribing."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            deleted_subscription.restore()
            deleted_subscription.save()
            serializer = PlayerSubscriptionSerializer(deleted_subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            subscription = PlayerSubscription.objects.create(user=user, player=player)
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

    @transaction.atomic  # 동시성 문제를 해결하기 위해 트랜잭션
    def post(self, request: Any, team_id: int) -> Response:
        user = request.user
        team = get_object_or_404(Team, id=team_id)
        now = timezone.now()

        active_subscription = TeamSubscription.objects.filter(user=user, team=team).first()
        if active_subscription:
            return Response(
                {"message": "You are already subscribed to this team."},
                status=status.HTTP_200_OK,
            )

        # Soft-delete된 구독이 있는지 확인 (all_objects 사용)
        deleted_subscription = TeamSubscription.deleted_objects.filter(user=user, team=team).first()

        if deleted_subscription:
            if deleted_subscription.deleted_at and now - deleted_subscription.deleted_at < timedelta(hours=24):
                return Response(
                    {"error": "You cannot resubscribe within 24 hours of unsubscribing."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            deleted_subscription.restore()
            deleted_subscription.save()
            serializer = TeamSubscriptionSerializer(deleted_subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            subscription = TeamSubscription.objects.create(user=user, team=team)
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
