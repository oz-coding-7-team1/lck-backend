from django.urls import path

from .views import (
    PlayerGalleryListView,
    PlayerImageDeleteView,
    PlayerImageUploadView,
    TeamGalleryListView,
    TeamImageDeleteView,
    TeamImageUploadView,
    UserImageDeleteView,
    UserImageUploadView, UserProfileView, PlayerImageDetailView, TeamImageDetailView,
)

urlpatterns = [
    path("user/upload/", UserImageUploadView.as_view(), name="user_upload"),
    path("user/delete/", UserImageDeleteView.as_view(), name="user_delete"),
    path("user/profile/", UserProfileView.as_view(), name="user_profile"),
    path("player/upload/", PlayerImageUploadView.as_view(), name="player_upload"),
    path("player/delete/", PlayerImageDeleteView.as_view(), name="player_delete"),
    path("player/<int:player_id>/gallery/", PlayerGalleryListView.as_view(), name="player_detail"),
    path("player/<int:player_id>/<str:category>/", PlayerImageDetailView.as_view(), name="player_category"),
    path("team/upload/", TeamImageUploadView.as_view(), name="team_upload"),
    path("team/delete/", TeamImageDeleteView.as_view(), name="team_delete"),
    path("team/<int:team_id>/gallery/", TeamGalleryListView.as_view(), name="team_gallery"),
    path("team/<int:team_id>/<str:category>/", TeamImageDetailView.as_view(), name="team_detail"),
]
