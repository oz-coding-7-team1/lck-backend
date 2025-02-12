from datetime import timedelta
from typing import Any, List, Optional, Sequence

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.players.models import Player
from apps.players.serializers import PlayerSerializer
from apps.teams.models import Team
from apps.teams.serializers import TeamSerializer

from .models import PlayerSubscription, TeamSubscription
from .serializers import PlayerSubscriptionSerializer, TeamSubscriptionSerializer


class PlayerSubscriptionView(APIView):
    # Sequence: 순서를 가진 데이터의 집합을 나타내는 타입(list, tuple, str)
    # 이렇게 관리해보고 싶어서 만들어봄
    def get_permissions(self) -> List[BasePermission]:
        if self.request.method in ["POST", "DELETE", "GET"]:
            # authentication은 어떤 사용자로부터 왔는지를 판별, JWT로 검증하겠다는 의미
            self.authentication_classes = (JWTAuthentication,)  # 반환 필요 없음
            # permission은 인증된 사용자가 해당 리소스에 접근할 권한이 있는지를 판단
            # 인등된 사용자만 접근 가능하게 하겠다는 의미
            self.permission_classes = (IsAuthenticated,)  # 반환 필요함
        # permission_classes의 각 클래스의 인스턴스를 생성하여 반환해야 함
        return [permission() for permission in self.permission_classes]  # type: ignore

    @extend_schema(
        summary="선수 구독 생성",
        responses={
            201: PlayerSubscriptionSerializer,  # 구독 생성 성공 시 생성된 구독 객체 반환
            200: OpenApiExample(
                "이미 구독된 경우",
                value={"message": "You are already subscribed to this player."},
            ),
            400: OpenApiExample(
                "재구독 제한 오류",
                value={"error": "You cannot resubscribe within 24 hours of unsubscribing."},
            ),
        },
    )
    @transaction.atomic  # 동시성 문제를 해결하기 위해 트랜잭션
    def post(self, request: Any, player_id: int) -> Response:
        user = request.user
        player = get_object_or_404(Player, id=player_id)
        now = timezone.now()

        # 이미 다른 선수를 구독 중인지 확인
        existing_subscription = PlayerSubscription.objects.filter(user=user, deleted_at__isnull=True).first()
        if existing_subscription:
            return Response(
                {"error": "You can only subscribe to one player at a time. Unsubscribe first."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 이미 같은 선수를 구독 중인지 확인
        active_subscription: Optional[PlayerSubscription] = PlayerSubscription.objects.filter(
            user=user, player=player, deleted_at__isnull=True
        ).first()
        if active_subscription:
            return Response(
                {"message": "You are already subscribed to this player."},
                status=status.HTTP_200_OK,
            )

        # Soft-delete된 구독이 있는지 확인 (deleted_objects 사용)
        # Optional: 값이 존재할 수도 존재하지 않을 수도 있음
        deleted_subscription: Optional[PlayerSubscription] = PlayerSubscription.deleted_objects.filter(
            user=user, player=player
        ).first()

        # 구독을 취소한 지 24시간이 지났는 지 유효성 검사
        if (
            deleted_subscription
            and deleted_subscription.deleted_at
            and now - deleted_subscription.deleted_at < timedelta(hours=24)
        ):
            return Response(
                {"error": "You cannot resubscribe within 24 hours of unsubscribing."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 새로운 구독자가 이전과 같으면 restore, 아니면 새로 생성
        if deleted_subscription and deleted_subscription.player.id == player.id:
            deleted_subscription.restore()
            deleted_subscription.save()
            serializer = PlayerSubscriptionSerializer(deleted_subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            subscription = PlayerSubscription.objects.create(user=user, player=player)
            serializer = PlayerSubscriptionSerializer(subscription)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="선수 구독 취소",
        responses={
            204: OpenApiExample(
                "구독 취소 성공",
                value={"detail": "No Content"},
            ),
            404: OpenApiExample(
                "구독 정보 없음",
                value={"detail": "Not Found"},
            ),
        },
    )
    @transaction.atomic
    def delete(self, request: Any, player_id: int) -> Response:
        user = request.user
        subscription: Optional[PlayerSubscription] = get_object_or_404(
            PlayerSubscription, user=user, player_id=player_id
        )
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class PlayerSubscriptionDetailView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(summary="최애 선수 조회")
    def get(self, request: Any) -> Response:
        # 현재 로그인한 사용자의 활성화된 구독 선수 정보 조회
        subscribed_player = PlayerSubscription.objects.filter(user=request.user, deleted_at__isnull=True).first()

        if not subscribed_player:
            return Response({"message": "No subscribed player found."}, status=status.HTTP_404_NOT_FOUND)

        # Player 객체들을 시리얼라이즈
        serializer = PlayerSerializer(subscribed_player.player)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TeamSubscriptionView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        summary="팀 구독 생성",
        responses={
            201: TeamSubscriptionSerializer,  # 구독 생성 성공 시 생성된 구독 객체 반환
            200: OpenApiExample(
                "이미 구독된 경우",
                value={"message": "You are already subscribed to this team."},
            ),
            400: OpenApiExample(
                "재구독 제한 오류",
                value={"error": "You cannot resubscribe within 24 hours of unsubscribing."},
            ),
        },
    )
    @transaction.atomic  # 동시성 문제를 해결하기 위해 트랜잭션
    def post(self, request: Any, team_id: int) -> Response:
        user = request.user
        team = get_object_or_404(Team, id=team_id)
        now = timezone.now()

        active_subscription: Optional[TeamSubscription] = TeamSubscription.objects.filter(user=user, team=team).first()
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

    @extend_schema(
        summary="팀 구독 취소",
        responses={
            204: OpenApiExample(
                "구독 취소 성공",
                value={"detail": "No Content"},
            ),
            404: OpenApiExample(
                "구독 정보 없음",
                value={"detail": "Not Found"},
            ),
        },
    )
    @transaction.atomic
    def delete(self, request: Any, team_id: int) -> Response:
        user = request.user
        subscription: Optional[TeamSubscription] = get_object_or_404(TeamSubscription, user=user, team_id=team_id)
        if subscription:
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)



class TeamSubscriptionDetailView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    @extend_schema(summary="최애 팀 조회")
    def get(self, request: Any) -> Response:
        # 현재 로그인한 사용자의 활성화된 구독 선수 정보 조회
        subscribed_team = TeamSubscription.objects.filter(user=request.user, deleted_at__isnull=True).first()

        if not subscribed_team:
            return Response({"message": "No subscribed team found."}, status=status.HTTP_404_NOT_FOUND)

        # Team 객체들을 시리얼라이즈
        serializer = TeamSerializer(subscribed_team.team)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlayerSubscriptionCountView(APIView):
    @extend_schema(summary="선수 구독 수")
    def get(self, request: Any, player_id: int) -> Response:
        count = PlayerSubscription.objects.filter(player_id=player_id, deleted_at__isnull=True).count()
        return Response({"count": count})


class TeamSubscriptionCountView(APIView):
    @extend_schema(summary="팀 구독 수")
    def get(self, request: Any, team_id: int) -> Response:
        count = TeamSubscription.objects.filter(team_id=team_id, deleted_at__isnull=True).count()
        return Response({"count": count})
