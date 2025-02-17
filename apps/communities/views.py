from typing import Any, List

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.players.models import Player
from apps.teams.models import Team

from .models import PlayerComment, PlayerPost, TeamComment, TeamPost
from .serializers import (
    PlayerCommentSerializer,
    PlayerPostSerializer,
    TeamCommentSerializer,
    TeamPostSerializer,
)


class TeamPostListCreateAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return super().get_permissions()  # type: ignore

    @extend_schema(
        summary="팀 커뮤니티 게시글 조회",
        description="특정 팀의 커뮤니티 게시글 목록을 조회합니다.",
        responses={200: TeamPostSerializer(many=True)},
    )
    # 팀 커뮤니티 조회
    def get(self, request: Request, team_id: int) -> Response:
        posts = TeamPost.objects.filter(team_id=team_id)
        serializer = TeamPostSerializer(posts, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="팀 커뮤니티 게시글 생성",
        description="새로운 팀 커뮤니티 게시글을 생성합니다.",
        request=TeamPostSerializer,
        responses={
            201: OpenApiExample("성공 응답 예시", value={"detail": "게시글 생성 완료"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "팀을 찾을 수 없습니다."}),
        },
    )
    # 팀 커뮤니티 생성
    def post(self, request: Request, team_id: int) -> Response:
        team = Team.objects.filter(id=team_id).first()
        if not team:
            return Response({"detail": "팀을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = TeamPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, team=team)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamPostDetailAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return super().get_permissions()  # type: ignore

    @extend_schema(
        summary="팀 커뮤니티 게시글 상세 조회",
        description="특정 팀 커뮤니티 게시글의 상세 정보를 조회합니다.",
        responses={200: TeamPostSerializer},
    )
    # 팀 커뮤니티 상세 조회
    def get(self, request: Request, team_id: int, post_id: int) -> Response:
        post = TeamPost.objects.filter(id=post_id, team_id=team_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TeamPostSerializer(post)
        return Response(serializer.data)

    @extend_schema(
        summary="팀 커뮤니티 게시글 수정",
        description="특정 팀 커뮤니티 게시글을 수정합니다. (작성자만 수정 가능)",
        request=TeamPostSerializer,
        responses={
            200: OpenApiExample("성공 응답 예시", value={"detail": "게시글 수정 완료"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "게시글을 찾을 수 없습니다."}),
        },
    )
    # 팀 커뮤니티 수정
    def put(self, request: Request, team_id: int, post_id: int) -> Response:
        post = TeamPost.objects.filter(id=post_id, team_id=team_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        # 수정 권한 확인 (작성자만 수정 가능)
        if post.user != request.user:
            return Response({"detail": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TeamPostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="팀 커뮤니티 게시글 삭제",
        description="특정 팀 커뮤니티 게시글을 삭제합니다. (작성자만 삭제 가능)",
        responses={204: OpenApiExample("성공 응답 예시", value={"detail": "게시글 삭제 완료"})},
    )
    # 팀 커뮤니티 삭제
    def delete(self, request: Request, team_id: int, post_id: int) -> Response:
        post = TeamPost.objects.filter(id=post_id, team_id=team_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        # 삭제 권한 확인 (작성자만 삭제 가능)
        if post.user != request.user:
            return Response({"detail": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class PlayerPostListCreateAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return super().get_permissions()  # type: ignore

    @extend_schema(
        summary="선수 커뮤니티 게시글 조회",
        description="특정 선수의 커뮤니티 게시글 목록을 조회합니다.",
        responses={200: PlayerPostSerializer(many=True)},
    )
    # 선수 커뮤니티 조회
    def get(self, request: Request, player_id: int) -> Response:
        posts = PlayerPost.objects.filter(player_id=player_id)
        serializer = PlayerPostSerializer(posts, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="선수 커뮤니티 게시글 생성",
        description="새로운 선수 커뮤니티 게시글을 생성합니다.",
        request=PlayerPostSerializer,
        responses={
            201: OpenApiExample("성공 응답 예시", value={"detail": "게시글 생성 완료"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "선수를 찾을 수 없습니다."}),
        },
    )
    # 선수 커뮤니티 생성
    def post(self, request: Request, player_id: int) -> Response:
        player = Player.objects.filter(id=player_id).first()
        if not player:
            return Response({"detail": "선수를 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PlayerPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, player=player)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerPostDetailAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return super().get_permissions()  # type: ignore

    @extend_schema(
        summary="선수 커뮤니티 게시글 상세 조회",
        description="특정 선수 커뮤니티 게시글의 상세 정보를 조회합니다.",
        responses={200: PlayerPostSerializer},
    )
    # 선수 커뮤니티 상세 조회
    def get(self, request: Request, player_id: int, post_id: int) -> Response:
        post = PlayerPost.objects.filter(id=post_id, player_id=player_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PlayerPostSerializer(post)
        return Response(serializer.data)

    @extend_schema(
        summary="선수 커뮤니티 게시글 수정",
        description="특정 선수 커뮤니티 게시글을 수정합니다. (작성자만 수정 가능)",
        request=PlayerPostSerializer,
        responses={
            200: OpenApiExample("성공 응답 예시", value={"detail": "게시글 수정 완료"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "게시글을 찾을 수 없습니다."}),
        },
    )
    # 선수 커뮤니티 수정
    def put(self, request: Request, player_id: int, post_id: int) -> Response:
        post = PlayerPost.objects.filter(id=post_id, player_id=player_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        if post.user != request.user:
            return Response({"detail": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PlayerPostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="선수 커뮤니티 게시글 삭제",
        description="특정 선수 커뮤니티 게시글을 삭제합니다. (작성자만 삭제 가능)",
        responses={204: OpenApiExample("성공 응답 예시", value={"detail": "게시글 삭제 완료"})},
    )
    # 선수 커뮤니티 삭제
    def delete(self, request: Request, player_id: int, post_id: int) -> Response:
        post = PlayerPost.objects.filter(id=post_id, player_id=player_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        if post.user != request.user:
            return Response({"detail": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class TeamCommentCreateAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return super().get_permissions()  # type: ignore

    @extend_schema(
        summary="팀 커뮤니티 댓글 작성",
        description="특정 팀 커뮤니티 게시글에 댓글을 작성합니다. (로그인한 사용자만 작성 가능)",
        request=TeamCommentSerializer,
        responses={
            201: OpenApiExample("성공 응답 예시", value={"detail": "댓글 작성 완료"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "게시글을 찾을 수 없습니다."}),
        },
    )
    # 팀 커뮤니티 댓글 작성
    def post(self, request: Request, team_id: int, post_id: int) -> Response:
        post = TeamPost.objects.filter(id=post_id, team_id=team_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TeamCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamCommentDetailAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return super().get_permissions()  # type: ignore

    @extend_schema(
        summary="팀 커뮤니티 댓글 상세 조회",
        description="특정 팀 커뮤니티 댓글의 상세 정보를 조회합니다.",
        responses={200: TeamCommentSerializer},
    )
    # 팀 커뮤니티 댓글 상세 조회
    def get(self, request: Request, comment_id: int) -> Response:
        comment = TeamComment.objects.filter(id=comment_id).first()
        if not comment:
            return Response({"detail": "댓글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TeamCommentSerializer(comment)
        return Response(serializer.data)

    @extend_schema(
        summary="팀 커뮤니티 댓글 수정",
        description="특정 팀 커뮤니티 댓글을 수정합니다. (작성자만 수정 가능)",
        request=TeamCommentSerializer,
        responses={
            200: OpenApiExample("성공 응답 예시", value={"detail": "댓글 수정 완료"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "댓글을 찾을 수 없습니다."}),
        },
    )
    # 팀 커뮤니티 댓글 수정
    def put(self, request: Request, comment_id: int) -> Response:
        comment = TeamComment.objects.filter(id=comment_id).first()
        if not comment:
            return Response({"detail": "댓글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        if comment.user != request.user:
            return Response({"detail": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer = TeamCommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="팀 커뮤니티 댓글 삭제",
        description="특정 팀 커뮤니티 댓글을 삭제합니다. (작성자만 삭제 가능)",
        responses={204: OpenApiExample("성공 응답 예시", value={"detail": "댓글 삭제 완료"})},
    )
    # 팀 커뮤니티 댓글 삭제
    def delete(self, request: Request, comment_id: int) -> Response:
        comment = TeamComment.objects.filter(id=comment_id).first()
        if not comment:
            return Response({"detail": "댓글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        if comment.user != request.user:
            return Response({"detail": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class PlayerCommentCreateAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return super().get_permissions()  # type: ignore

    @extend_schema(
        summary="선수 커뮤니티 댓글 작성",
        description="특정 선수 커뮤니티 게시글에 댓글을 작성합니다. (로그인한 사용자만 작성 가능)",
        request=PlayerCommentSerializer,
        responses={
            201: OpenApiExample("성공 응답 예시", value={"detail": "댓글 작성 완료"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "게시글을 찾을 수 없습니다."}),
        },
    )
    # 선수 커뮤니티 댓글 작성
    def post(self, request: Request, player_id: int, post_id: int) -> Response:
        post = PlayerPost.objects.filter(id=post_id, player_id=player_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PlayerCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerCommentDetailAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = (JWTAuthentication,)

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method in ["PUT", "DELETE"]:
            return [IsAuthenticated()]
        return super().get_permissions()  # type: ignore

    @extend_schema(
        summary="선수 커뮤니티 댓글 상세 조회",
        description="특정 선수 커뮤니티 댓글의 상세 정보를 조회합니다.",
        responses={200: PlayerCommentSerializer},
    )
    # 선수 커뮤니티 댓글 상세 조회
    def get(self, request: Request, comment_id: int) -> Response:
        comment = PlayerComment.objects.filter(id=comment_id).first()
        if not comment:
            return Response({"detail": "댓글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = PlayerCommentSerializer(comment)
        return Response(serializer.data)

    @extend_schema(
        summary="선수 커뮤니티 댓글 수정",
        description="특정 선수 커뮤니티 댓글을 수정합니다. (작성자만 수정 가능)",
        request=PlayerCommentSerializer,
        responses={
            200: OpenApiExample("성공 응답 예시", value={"detail": "댓글 수정 완료"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "댓글을 찾을 수 없습니다."}),
        },
    )
    # 선수 커뮤니티 댓글 수정
    def put(self, request: Request, comment_id: int) -> Response:
        comment = PlayerComment.objects.filter(id=comment_id).first()
        if not comment:
            return Response({"detail": "댓글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        if comment.user != request.user:
            return Response({"detail": "수정 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        serializer = PlayerCommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="선수 커뮤니티 댓글 삭제",
        description="특정 선수 커뮤니티 댓글을 삭제합니다. (작성자만 삭제 가능)",
        responses={204: OpenApiExample("성공 응답 예시", value={"detail": "댓글 삭제 완료"})},
    )
    # 선수 커뮤니티 댓글 삭제
    def delete(self, request: Request, comment_id: int) -> Response:
        comment = PlayerComment.objects.filter(id=comment_id).first()
        if not comment:
            return Response({"detail": "댓글을 찾을 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        if comment.user != request.user:
            return Response({"detail": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
