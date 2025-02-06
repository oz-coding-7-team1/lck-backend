from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    PlayerImageViewSet,
    PlayerProfileViewSet,
    PlayerScheduleViewSet,
    PlayerViewSet,
)

# DefaultRouter를 사용하여 ViewSet들을 등록/ 자동으로 URL 라우팅을 처리하고, 브라우저에서 탐색할 수 있는 API 루트를 제공함
router = DefaultRouter()
router.register(r"player", PlayerViewSet, basename="player")

# URL 패턴 정의
urlpatterns = [
    # 등록된 ViewSet들을 포함하는 라우팅 설정
    path("api/v1/", include(router.urls)),
    # 탑 10명 선수 조회
    path("api/v1/player/rank/", PlayerViewSet.as_view({"get": "top10"}), name="player-top10"),
    # 라인별 탑 5명 선수 조회
    path("api/v1/player/rank/position/", PlayerViewSet.as_view({"get": "position_top5"}), name="player-position-top5"),
    # 선수 프로필 페이지
    path("api/v1/player/<int:pk>/", PlayerProfileViewSet.as_view({"get": "retrieve"}), name="player-profile"),
    # 키워드로 검색
    path("api/v1/player/search/", PlayerViewSet.as_view({"get": "list"}), name="player-search"),
    # 선수 이미지 조회
    path("api/v1/player/<int:pk>/image/", PlayerImageViewSet.as_view({"get": "list"}), name="player-images"),
    # 선수 스케줄 전체 조회
    path("api/v1/player/<int:pk>/schedule/", PlayerScheduleViewSet.as_view({"get": "list"}), name="player-schedule"),
]
