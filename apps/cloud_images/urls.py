from django.urls import path

from .views import (
    CloudImageDeleteView,
    CloudImageListView,
    CloudImageRetrieveView,
    CloudImageUploadView,
)

urlpatterns = [
    path("upload/", CloudImageUploadView.as_view(), name="upload"),
    path("list/<str:category>/<str:image_type>/", CloudImageListView.as_view(), name="list"),
    path("detail/<uuid:image_id>/", CloudImageRetrieveView.as_view(), name="Retrieve"),
    path("delete/<uuid:image_id>", CloudImageDeleteView.as_view(), name="delete"),
]
