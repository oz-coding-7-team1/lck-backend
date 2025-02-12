from django.urls import path

from .views import (
    PlayerSubscriptionCountView,
    PlayerSubscriptionDetailView,
    PlayerSubscriptionView,
    TeamSubscriptionCountView,
    TeamSubscriptionDetailView,
    TeamSubscriptionView,
)

urlpatterns = [
    path("player/<int:player_id>/", PlayerSubscriptionView.as_view(), name="player_subscription"),
    path("player/choeae/", PlayerSubscriptionDetailView.as_view(), name="player_subscription_detail"),
    path("player/<int:player_id>/count/", PlayerSubscriptionCountView.as_view(), name="player_subscription_count"),
    path("team/<int:team_id>/", TeamSubscriptionView.as_view(), name="team_subscription"),
    path("team/choeae/", TeamSubscriptionDetailView.as_view(), name="team_subscription_detail"),
    path("team/<int:team_id>/count/", TeamSubscriptionCountView.as_view(), name="team_subscription_count"),
]
