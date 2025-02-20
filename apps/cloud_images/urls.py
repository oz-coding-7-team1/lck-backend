from django.urls import path

from .views import (
    PlayerGalleryDetailView,
    PlayerGalleryImageView,
    PlayerProfileImageDetailView,
    PlayerProfileImageView,
    TeamGalleryDetailView,
    TeamGalleryImageView,
    TeamProfileImageDetailView,
    TeamProfileImageView,
    UserImageDetailView,
    UserImageView,
)

urlpatterns = [
    # 유저 프로필 이미지
    path("users/<int:user_id>/profile/", UserImageView.as_view(), name="get_user_profile"),
    path("users/profile/", UserImageDetailView.as_view(), name="user_profile"),
    # 선수 프로필 / 배경 이미지
    path("players/<int:player_id>/", PlayerProfileImageView.as_view(), name="get_player_profile"),
    path("players/<int:player_id>/profile/", PlayerProfileImageDetailView.as_view(), name="player_profile"),
    # 선수 갤러리
    path("players/<int:player_id>/gallery/", PlayerGalleryImageView.as_view(), name="player_gallery"),
    path(
        "players/<int:player_id>/gallery/<int:image_id>/",
        PlayerGalleryDetailView.as_view(),
        name="player_gallery_details",
    ),
    # 팀 프로필 / 배경 이미지
    path("teams/<int:team_id>/", TeamProfileImageView.as_view(), name="get_team_profile"),
    path("teams/<int:team_id>/profile/", TeamProfileImageDetailView.as_view(), name="team_profile"),
    # 팀 갤러리
    path("teams/<int:team_id>/gallery/", TeamGalleryImageView.as_view(), name="team_gallery"),
    path("teams/<int:team_id>/gallery/<int:image_id>/", TeamGalleryDetailView.as_view(), name="team_gallery_details"),
]
