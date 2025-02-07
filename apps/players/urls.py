from django.urls import path

from .views import (
    PlayerDetail,
    PlayerImageList,
    PlayerList,
    PlayerScheduleList,
    position_top,
    top_players,
)

urlpatterns = [
    # 전체 Player 조회
    path("players/", PlayerList.as_view(), name="player-list"),
    # Player 프로필 조회
    path("players/<int:pk>/", PlayerDetail.as_view(), name="player-detail"),
    # 구독 수가 많은 상위 10명의 선수 정보 조회
    path("players/top/", top_players, name="top-players"),
    # 특정 포지션의 구독 수가 많은 상위 5명의 선수 정보 조회
    path("players/position_top/", position_top, name="position-top"),
    # 특정 선수의 이미지조회
    path("players/<int:pk>/images/", PlayerImageList.as_view(), name="player-image-list"),
    # 특정 선수의 스케줄 조회
    path("player/<int:pk>/schedule/", PlayerScheduleList.as_view(), name="player-schedule"),
]
