from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

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
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 팀 커뮤니티 조회
    def get(self, request: Request, team_id: int) -> Response:
        # URL에서 team_id로 해당 팀에 대한 게시글을 조회
        posts = TeamPost.objects.filter(team_id=team_id)
        serializer = TeamPostSerializer(posts, many=True)
        return Response(serializer.data)

    # 팀 커뮤니티 생성
    def post(self, request: Request, team_id: int) -> Response:
        # URL에서 team_id로 해당 팀 인스턴스를 가져옴
        team = get_object_or_404(Team, id=team_id)
        serializer = TeamPostSerializer(data=request.data)
        if serializer.is_valid():
            # 게시글 생성 시 현재 사용자와 팀 정보를 함께 저장
            serializer.save(user=request.user, team=team)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamPostDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 팀 커뮤니티 상세 조회
    def get(self, request: Request, team_id: int, post_id: int) -> Response:
        post = get_object_or_404(TeamPost, id=post_id, team_id=team_id)
        serializer = TeamPostSerializer(post)
        return Response(serializer.data)

    # 팀 커뮤니티 수정
    def put(self, request: Request, team_id: int, post_id: int) -> Response:
        post = get_object_or_404(TeamPost, id=post_id, team_id=team_id)
        serializer = TeamPostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 팀 커뮤니티 삭제
    def delete(self, request: Request, team_id: int, post_id: int) -> Response:
        post = get_object_or_404(TeamPost, id=post_id, team_id=team_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class PlayerPostListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 선수 커뮤니티 조회
    def get(self, request: Request, player_id: int) -> Response:
        posts = PlayerPost.objects.filter(player_id=player_id)
        serializer = PlayerPostSerializer(posts, many=True)
        return Response(serializer.data)

    # 선수 커뮤니티 생성
    def post(self, request: Request, player_id: int) -> Response:
        player = get_object_or_404(Player, id=player_id)
        serializer = PlayerPostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, player=player)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerPostDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 선수 커뮤니티 상세 조회
    def get(self, request: Request, player_id: int, post_id: int) -> Response:
        post = get_object_or_404(PlayerPost, id=post_id, player_id=player_id)
        serializer = PlayerPostSerializer(post)
        return Response(serializer.data)

    # 선수 커뮤니티 수정
    def put(self, request: Request, player_id: int, post_id: int) -> Response:
        post = get_object_or_404(PlayerPost, id=post_id, player_id=player_id)
        serializer = PlayerPostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 선수 커뮤니티 삭제
    def delete(self, request: Request, player_id: int, post_id: int) -> Response:
        post = get_object_or_404(PlayerPost, id=post_id, player_id=player_id)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class TeamCommentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 팀 커뮤니티 댓글 작성
    def post(self, request: Request, team_id: int, post_id: int) -> Response:
        # URL에 포함된 team_id와 post_id로 해당 팀 게시글을 가져와 댓글을 생성
        post = get_object_or_404(TeamPost, id=post_id, team_id=team_id)
        serializer = TeamCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamCommentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 팀 커뮤니티 댓글 상세 조회
    def get(self, request: Request, comment_id: int) -> Response:
        comment = get_object_or_404(TeamComment, id=comment_id)
        serializer = TeamCommentSerializer(comment)
        return Response(serializer.data)

    # 팀 커뮤니티 댓글 수정
    def put(self, request: Request, comment_id: int) -> Response:
        comment = get_object_or_404(TeamComment, id=comment_id)
        serializer = TeamCommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 팀 커뮤니티 댓글 삭제
    def delete(self, request: Request, comment_id: int) -> Response:
        comment = get_object_or_404(TeamComment, id=comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------


class PlayerCommentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 선수 커뮤니티 댓글 작성
    def post(self, request: Request, player_id: int, post_id: int) -> Response:
        # URL에 포함된 player_id와 post_id로 해당 선수 게시글을 가져와 댓글을 생성
        post = get_object_or_404(PlayerPost, id=post_id, player_id=player_id)
        serializer = PlayerCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerCommentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    # 선수 커뮤니티 댓글 상세 조회
    def get(self, request: Request, comment_id: int) -> Response:
        comment = get_object_or_404(PlayerComment, id=comment_id)
        serializer = PlayerCommentSerializer(comment)
        return Response(serializer.data)

    # 선수 커뮤니티 댓글 수정
    def put(self, request: Request, comment_id: int) -> Response:
        comment = get_object_or_404(PlayerComment, id=comment_id)
        serializer = PlayerCommentSerializer(comment, data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # 선수 커뮤니티 댓글 삭제
    def delete(self, request: Request, comment_id: int) -> Response:
        comment = get_object_or_404(PlayerComment, id=comment_id)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
