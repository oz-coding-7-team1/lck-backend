from django.urls import path

from .views import PlayerSubscriptionView, TeamSubscriptionView

urlpatterns = [
    path("player/<int:player_id>/", PlayerSubscriptionView.as_view(), name="player_subscription"),
    path("team/<int:team_id>/", TeamSubscriptionView.as_view(), name="team_subscription"),
]
