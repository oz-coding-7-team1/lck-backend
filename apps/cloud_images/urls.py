from django.urls import path

from .views import PlayerImageListView, TeamImageListView

urlpatterns = [
    path("player-images/<int:player_id>/", PlayerImageListView.as_view(), name="player_image_list"),
    path("team-images/<int:team_id>/", TeamImageListView.as_view(), name="team_image_list"),
]
