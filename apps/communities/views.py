from typing import Any, Dict, List, Type, cast

from django.contrib.contenttypes.models import ContentType
from django.db.models import Model
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from apps.players.models import Player
from apps.teams.models import Team

from .models import Like, PlayerComment, PlayerPost, TeamComment, TeamPost
from .serializers import (
    LikeSerializer,
    PlayerCommentSerializer,
    PlayerPostSerializer,
    TeamCommentSerializer,
    TeamPostSerializer,
)


class TeamPostListCreateAPIView(APIView):

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

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

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

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
            404: OpenApiExample("실패 응답 예시", value={"detail": "게시글을 찾을 수 없습니다."}),
        },
    )
    # 팀 커뮤니티 수정
    def put(self, request: Request, team_id: int, post_id: int) -> Response:
        post = TeamPost.objects.filter(id=post_id, team_id=team_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
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

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

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
            404: OpenApiExample("실패 응답 예시", value={"detail": "선수를 찾을 수 없습니다."}),
        },
    )
    # 선수 커뮤니티 생성
    def post(self, request: Request, player_id: int) -> Response:
        player = Player.objects.filter(id=player_id).first()
        if not player:
            return Response({"detail": "선수를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlayerPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, player=player)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerPostDetailAPIView(APIView):

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

    @extend_schema(
        summary="선수 커뮤니티 게시글 상세 조회",
        description="특정 선수 커뮤니티 게시글의 상세 정보를 조회합니다.",
        responses={200: PlayerPostSerializer},
    )
    # 선수 커뮤니티 상세 조회
    def get(self, request: Request, player_id: int, post_id: int) -> Response:
        post = PlayerPost.objects.filter(id=post_id, player_id=player_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PlayerPostSerializer(post)
        return Response(serializer.data)

    @extend_schema(
        summary="선수 커뮤니티 게시글 수정",
        description="특정 선수 커뮤니티 게시글을 수정합니다. (작성자만 수정 가능)",
        request=PlayerPostSerializer,
        responses={
            200: OpenApiExample("성공 응답 예시", value={"detail": "게시글 수정 완료"}),
            404: OpenApiExample("실패 응답 예시", value={"detail": "게시글을 찾을 수 없습니다."}),
        },
    )
    # 선수 커뮤니티 수정
    def put(self, request: Request, player_id: int, post_id: int) -> Response:
        post = PlayerPost.objects.filter(id=post_id, player_id=player_id).first()
        if not post:
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
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
            return Response({"detail": "게시글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        if post.user != request.user:
            return Response({"detail": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class TeamCommentCreateAPIView(APIView):

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

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

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
            return Response({"detail": "댓글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        if comment.user != request.user:
            return Response({"detail": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class PlayerCommentCreateAPIView(APIView):

    def get_permissions(self) -> List[Any]:
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

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

    def get_authenticators(self) -> List[Any]:
        if not hasattr(self, "request") or self.request is None:
            return super().get_authenticators()

        if self.request.method == "GET":
            return []
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAuthenticated()]

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
            return Response({"detail": "댓글을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        if comment.user != request.user:
            return Response({"detail": "삭제 권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class LikeAPIView(APIView):

    def get_authenticators(self) -> List[Any]:
        return [JWTAuthentication()]

    def get_permissions(self) -> List[Any]:
        return [IsAuthenticated()]

    @extend_schema(
        summary="커뮤니티 게시판 및 댓글 좋아요 추가",
        description="특정 커뮤니티 게시판이나 댓글에 대해 좋아요를 추가합니다. "
        "(한 사용자는 동일한 대상에 대해 한 번만 좋아요를 남길 수 있습니다.)",
        responses={
            201: OpenApiExample("성공 응답 예시", value={"detail": "좋아요 추가"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "유효하지 않은 모델 타입입니다."}),
            404: OpenApiExample("실패 응답 예시", value={"detail": "대상 객체를 찾을 수 없습니다."}),
        },
    )
    # 커뮤니티 게시판이나 댓글 좋아요
    def post(self, request: Request, model_type: str, object_id: int) -> Response:
        allowed_models: Dict[str, Type[Model]] = {
            "teampost": TeamPost,
            "playerpost": PlayerPost,
            "teamcomment": TeamComment,
            "playercomment": PlayerComment,
        }
        model_type = model_type.lower()
        if model_type not in allowed_models:
            return Response(
                {"detail": "유효하지 않은 모델 타입입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model: Type[Model] = allowed_models[model_type]
        # 모델의 objects 매니저에 접근 (mypy 우회를 위해 cast 사용)
        obj = cast(Any, model).objects.filter(id=object_id).first()
        if not obj:
            return Response(
                {"detail": "대상 객체를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        content_type = ContentType.objects.get_for_model(model)
        # 이미 좋아요가 존재하는지 확인
        if Like.objects.filter(
            user=cast(Any, request.user),
            content_type=content_type,
            object_id=object_id,
        ).exists():
            return Response(
                {"detail": "이미 좋아요가 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # 좋아요 생성
        like = Like.objects.create(
            user=cast(Any, request.user),
            content_type=content_type,
            object_id=object_id,
        )
        serializer = LikeSerializer(like)
        return Response(
            {"detail": "좋아요 추가", "like": serializer.data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="커뮤니티 게시판 및 댓글 좋아요 취소",
        description="특정 커뮤니티 게시판이나 댓글에 대해 좋아요를 취소합니다. (좋아요를 남긴 사용자만 삭제 가능)",
        responses={
            200: OpenApiExample("성공 응답 예시", value={"detail": "좋아요 취소"}),
            400: OpenApiExample("실패 응답 예시", value={"detail": "유효하지 않은 모델 타입입니다."}),
            404: OpenApiExample("실패 응답 예시", value={"detail": "대상 객체를 찾을 수 없습니다."}),
        },
    )
    # 커뮤니티 게시판이나 댓글 좋아요 취소
    def delete(self, request: Request, model_type: str, object_id: int) -> Response:
        allowed_models: Dict[str, Type[Model]] = {
            "teampost": TeamPost,
            "playerpost": PlayerPost,
            "teamcomment": TeamComment,
            "playercomment": PlayerComment,
        }
        model_type = model_type.lower()
        if model_type not in allowed_models:
            return Response(
                {"detail": "유효하지 않은 모델 타입입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        model: Type[Model] = allowed_models[model_type]
        obj = cast(Any, model).objects.filter(id=object_id).first()
        if not obj:
            return Response(
                {"detail": "대상 객체를 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        content_type = ContentType.objects.get_for_model(model)
        try:
            like = Like.objects.get(
                user=cast(Any, request.user),
                content_type=content_type,
                object_id=object_id,
            )
        except Like.DoesNotExist:
            return Response(
                {"detail": "좋아요가 존재하지 않습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = LikeSerializer(like)
        like.delete()
        return Response(
            {"detail": "좋아요 취소", "like": serializer.data},
            status=status.HTTP_200_OK,
        )
