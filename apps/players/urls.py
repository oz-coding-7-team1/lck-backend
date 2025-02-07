from django.urls import path

from .views import (
    PlayerDetail,
    PlayerList,
    PlayerScheduleList,
    PositionTop,
    TopPlayers,
)

urlpatterns = [
    # 전체 Player 조회
    path("players/", PlayerList.as_view(), name="player-list"),
    # Player 프로필 조회
    path("players/<int:pk>/", PlayerDetail.as_view(), name="player-detail"),
    # 구독 수가 많은 상위 10명의 선수 정보 조회
    path("players/top/", TopPlayers.as_view(), name="top-players"),
    # 특정 포지션의 구독 수가 많은 상위 5명의 선수 정보 조회
    path("players/position_top/", PositionTop.as_view(), name="position-top"),
    # 특정 선수의 스케줄 조회
    path("player/<int:pk>/schedule/", PlayerScheduleList.as_view(), name="player-schedule"),
]
