from django.urls import path
from .views import TagSearchView

urlpatterns = [
	path("tag-search/", TagSearchView.as_view(), name="tag_search"),
]