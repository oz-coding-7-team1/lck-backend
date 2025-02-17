from email.mime import image
from typing import Any

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CloudImage
from .serializers import CloudImageSerializer
from .utils import upload_image_to_s3


class CloudImageUploadView(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        category = request.data.get("category")
        image_type = request.data.get("image_type")
        file = request.FILES.get("image")

        valid_categories = ["users", "players", "teams"]
        valid_image_types = ["profile", "background", "gallery", "community"]

        if category not in valid_categories or image_type not in valid_image_types or not file:
            return Response(
                {"error": "Invalid category, image type, or missing file"}, status=status.HTTP_400_BAD_REQUEST
            )

        # 권한 검증
        if category in ["players", "teams"]:
            if image_type in ["profile", "background"] and not request.user.is_staff:
                return Response(
                    {"error": "Only admins can upload profile and background images for players and teams."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if image_type == "gallery" and not request.user.is_authenticated:
                return Response(
                    {"error": "Only authenticated users can upload gallery images"}, status=status.HTTP_403_FORBIDDEN
                )

        # 유저 프로필은 한 개만 존재해야 하므로 기존 이미지 삭제 후 업로드
        if category == "users" and image_type == "profile":
            CloudImage.objects.filter(category="users", image_type="profile", uploaded_by=request.user).delete()

        s3_url = upload_image_to_s3(file, category, image_type, request.user)
        if not s3_url:
            return Response({"error": "Invalid file type or upload failed"}, status=status.HTTP_400_BAD_REQUEST)

        image = CloudImage.objects.create(
            category=category, image_type=image_type, image_url=s3_url, uploaded_by=request.user
        )
        serializer = CloudImageSerializer(image)
        return Response(
            {"message": "Image uploaded successfully", "data": serializer.data}, status=status.HTTP_201_CREATED
        )


class CloudImageListView(APIView):
    permission_classes = (AllowAny,)

    # 카테고리별 이미지 목록 조회
    def get(self, request: Any, category: str, image_type: str) -> Response:
        images = CloudImage.objects.filter(category=category, image_type=image_type)
        serializer = CloudImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CloudImageRetrieveView(APIView):
    permission_classes = (AllowAny,)

    # 개별 이미지 조회
    def get(self, request: Any, image_id: int) -> Response:
        image = get_object_or_404(CloudImage, id=image_id)
        serializer = CloudImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CloudImageDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    # 이미지 삭제
    def delete(self, request: Any, image_id: int) -> Response:
        image = get_object_or_404(CloudImage, id=image_id)

        # players, teams 의 프로필, 배경 사진은 관리자만 삭제 가능
        if image.category in ["players", "teams"]:
            if (
                image.image_type in ["profile", "background"]
                and image.image_type in ["profile", "background"]
                and not request.user.is_staff
            ):
                return Response(
                    {"error": "Only admins can delete profile and background images"}, status=status.HTTP_403_FORBIDDEN
                )

        if image.uploaded_by != request.user and not request.user.is_staff:
            return Response(
                {"error": "You do not have permission to delete this image"}, status=status.HTTP_403_FORBIDDEN
            )

        image.delete()
        return Response({"error": "Image deleted successfully"}, status=status.HTTP_200_OK)
