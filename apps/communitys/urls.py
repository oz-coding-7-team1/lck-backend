from django.urls import path

from .views import (
    PlayerCommentCreateAPIView,
    PlayerCommentDetailAPIView,
    PlayerPostDetailAPIView,
    PlayerPostListCreateAPIView,
    TeamCommentCreateAPIView,
    TeamCommentDetailAPIView,
    TeamPostDetailAPIView,
    TeamPostListCreateAPIView,
)

urlpatterns = [
    # 팀 커뮤니티 게시글 목록 조회 및 생성
    path("team/<int:team_id>/posts/", TeamPostListCreateAPIView.as_view(), name="team-post-list-create"),
    # 팀 커뮤니티 게시글 상세 조회, 수정, 삭제
    path("team/<int:team_id>/posts/<int:post_id>/", TeamPostDetailAPIView.as_view(), name="team-post-detail"),
    # 선수 커뮤니티 게시글 목록 조회 및 생성
    path("player/<int:player_id>/posts/", PlayerPostListCreateAPIView.as_view(), name="player-post-list-create"),
    # 선수 커뮤니티 게시글 상세 조회, 수정, 삭제
    path("player/<int:player_id>/posts/<int:post_id>/", PlayerPostDetailAPIView.as_view(), name="player-post-detail"),
    # 팀 커뮤니티 댓글 작성
    path(
        "team/<int:team_id>/posts/<int:post_id>/comments/",
        TeamCommentCreateAPIView.as_view(),
        name="team-comment-create",
    ),
    # 팀 커뮤니티 댓글 상세 조회, 수정, 삭제
    path("team/comments/<int:comment_id>/", TeamCommentDetailAPIView.as_view(), name="team-comment-detail"),
    # 선수 커뮤니티 댓글 작성
    path(
        "player/<int:player_id>/posts/<int:post_id>/comments/",
        PlayerCommentCreateAPIView.as_view(),
        name="player-comment-create",
    ),
    # 선수 커뮤니티 댓글 상세 조회, 수정, 삭제
    path("player/comments/<int:comment_id>/", PlayerCommentDetailAPIView.as_view(), name="player-comment-detail"),
]
