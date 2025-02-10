from django.urls import path
from .views import PlayerImageListView, TeamImageListView

urlpatterns = [
	path('<player_id>/images/', PlayerImageListView.as_view(), name='player_image_list'),
	path('<team_id>/images/', TeamImageListView.as_view(), name='team_image_list'),
]
