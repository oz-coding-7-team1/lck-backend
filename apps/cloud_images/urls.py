from django.urls import path

from .views import (
    PlayerGalleryListView,
    PlayerImageDeleteView,
    PlayerImageUploadView,
    TeamGalleryListView,
    TeamImageDeleteView,
    TeamImageUploadView,
    UserImageDeleteView,
    UserImageUploadView,
)

urlpatterns = [
    path("user/upload/", UserImageUploadView.as_view(), name="user_upload"),
    path("user/delete/", UserImageDeleteView.as_view(), name="user_delete"),
    path("player/upload/", PlayerImageUploadView.as_view(), name="player_upload"),
    path("player/delete/", PlayerGalleryListView.as_view(), name="player_delete"),
    path("player/<int:player_id>/gallery/", PlayerGalleryListView.as_view(), name="player_gallery"),
    path("team/upload/", TeamImageUploadView.as_view(), name="team_upload"),
    path("team/delete/", TeamImageDeleteView.as_view(), name="team_delete"),
    path("team/<int:team_id>/gallery/", TeamGalleryListView.as_view(), name="team_gallery"),
]
