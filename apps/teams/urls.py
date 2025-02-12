from django.urls import path

from .views import (
    TeamDetail,
    TeamList,
    TeamRank,
    TeamScheduleDetail,
    TeamScheduleList,
)

urlpatterns = [
    # 전체 팀 조회, 등록
    path("", TeamList.as_view(), name="team-list"),
    # 구독 수가 많은 상위 5팀 조회
    path("rank/", TeamRank.as_view(), name="team-rank"),
    # 특정 팀 상세 페이지 조회, 수정, 삭제
    path("<int:pk>/", TeamDetail.as_view(), name="team-detail"),
    # 특정 팀의 스케줄 조회 및 생성
    path("<int:team_id>/schedule/", TeamScheduleList.as_view(), name="team-schedule-list"),
    # 특정 팀 스케줄 상세 조회, 수정, 삭제
    path("<int:team_id>/schedule/<int:schedule_id>/", TeamScheduleDetail.as_view(), name="team-schedule-detail"),
]
