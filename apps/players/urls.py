from django.urls import path

from .views import (
    PlayerDetail,
    PlayerList,
    PlayerScheduleDetail,
    PlayerScheduleList,
    PositionTop,
    TopPlayers,
)

urlpatterns = [
    # 전체 선수 조회, 등록
    path("", PlayerList.as_view(), name="player-list"),
    # 특정 선수 프로필 조회, 수정, 비활성화, 삭제
    path("<int:pk>/", PlayerDetail.as_view(), name="player-detail"),
    # 구독 수가 많은 상위 10명의 선수 정보 조회
    path("top/", TopPlayers.as_view(), name="top-players"),
    # 특정 포지션의 구독 수가 많은 상위 5명의 선수 정보 조회
    path("position_top/", PositionTop.as_view(), name="position-top"),
    # 특정 선수의 스케줄 목록 조회 및 생성
    path("<int:player_id>/schedule/", PlayerScheduleList.as_view(), name="player-schedule-list"),
    # 특정 선수 스케줄 상세 조회, 수정, 삭제
    path(
        "<int:player_id>/schedule/<int:schedule_id>/",
        PlayerScheduleDetail.as_view(),
        name="player-schedule-detail",
    ),
]
