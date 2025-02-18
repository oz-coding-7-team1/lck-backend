from typing import Any

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiRequest, extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from ..players.models import Player
from ..teams.models import Team
from .models import PlayerImage, TeamImage, UserImage
from .serializers import PlayerImageSerializer, TeamImageSerializer, UserImageSerializer
from .utils import delete_file_from_s3, upload_image_to_s3

""" 유저 프로필 조회 """


class UserImageView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="유저의 프로필 이미지 조회",
        responses={200: UserImageSerializer(many=True)},
    )
    def get(self, request: Any, user_id: int) -> Response:
        images = UserImage.objects.filter(user_id=user_id)
        serializer = UserImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


""" 유저 프로필 이미지 업로드 및 수정, 삭제 """


class UserImageDetailView(APIView):
    parser_classes = (FormParser, MultiPartParser)

    @extend_schema(
        summary="유저 프로필 이미지 업로드",
        description="유저가 자신의 프로필 이미지를 업로드합니다. 기존 이미지가 있으면 삭제 후 새로 저장됩니다.",
        request=OpenApiRequest(
            {
                "multipart/form-data": {
                    "image": {"type": "string", "format": "binary"},
                    "category": {"type": "string", "enum": ["profile", "background", "gallery", "community"]},
                }
            }
        ),
        responses={201: UserImageSerializer, 400: {"description": "업로드 실패"}},
    )
    def post(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        file = request.FILES.get("image")

        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 기존 이미지 삭제 (1개 제한)
        existing_image = UserImage.objects.filter(user=request.user).first()

        if existing_image:
            delete_file_from_s3(existing_image.image_url)
            existing_image.delete()

        # 새 이미지 업로드
        s3_url = upload_image_to_s3(file, "profile", "users", request.user.id)

        if not s3_url:
            return Response({"error": "Upload failed"}, status=status.HTTP_400_BAD_REQUEST)

        image = UserImage.objects.create(user=request.user, image_url=s3_url)
        serializer = UserImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    """ 유저 프로필 이미지 삭제 (본인만 가능)"""

    @extend_schema(
        summary="유저 프로필 이미지 삭제",
        description="유저가 자신의 프로필 이미지를 삭제합니다.",
        responses={200: {"message": "Image deleted successfully"}, 400: {"description": "삭제 실패"}},
    )
    def delete(self, request: Any, *args: Any, **kwargs: Any) -> Response:
        image = get_object_or_404(UserImage, user=request.user)

        if delete_file_from_s3(image.image_url):
            image.delete()
            return Response({"message": "Image deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Delete failed"}, status=status.HTTP_400_BAD_REQUEST)


""" 선수 프로필 / 배경 이미지 조회 """


class PlayerProfileImageView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="선수 프로필 / 배경 이미지 조회 (가장 최근 이미지 1장)",
        responses={200: PlayerImageSerializer, 404: {"description": "이미지 없음"}},
    )
    def get(self, request: Any, player_id: int) -> Response:
        category = request.query_params.get("category")
        if category not in ["profile", "background"]:
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        image = PlayerImage.objects.filter(player_id=player_id, category=category).order_by("-uploaded_at").first()
        if not image:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = PlayerImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_200_OK)


""" 선수 프로필 / 배경 이미지 업로드 및 수정, 삭제 """


class PlayerProfileImageDetailView(APIView):
    parser_classes = (FormParser, MultiPartParser)

    @extend_schema(
        summary="선수 이미지 업로드",
        description="관리자만 프로필 / 배경 이미지를 업로드할 수 있습니다.",
        request=OpenApiRequest(
            {
                "multipart/form-data": {
                    "image": {"type": "string", "format": "binary"},
                    "category": {"type": "string", "enum": ["profile", "background", "gallery", "community"]},
                }
            }
        ),
        responses={201: PlayerImageSerializer, 400: {"description": "업로드 실패"}, 403: {"description": "권한 없음"}},
    )
    def post(self, request: Any, player_id: int, *args: Any, **kwargs: Any) -> Response:
        player = get_object_or_404(Player, id=player_id)

        category = request.data.get("category")
        if category not in ["profile", "background"]:
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        # 프로필 / 배경 이미지는 관리자만 업로드 가능
        if category in ["profile", "background"] and not request.user.is_staff:
            return Response({"error": "Only staff can upload images"}, status=status.HTTP_403_FORBIDDEN)

        # 파일 유무 확인
        file = request.FILES.get("image")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 기존 이미지 삭제 (1개 제한)
        if category in ["profile", "background"]:
            existing_image = PlayerImage.objects.filter(player=player, category=category).first()
            if existing_image:
                delete_file_from_s3(existing_image.image_url)
                existing_image.delete()

        # 새 이미지 업로드
        s3_url = upload_image_to_s3(file, category, "players", player.nickname)
        if not s3_url:
            return Response({"error": "Upload failed"}, status=status.HTTP_400_BAD_REQUEST)

        image = PlayerImage.objects.create(
            player=player,
            category=category,
            image_url=s3_url,
            uploaded_by=None,
        )

        serializer = PlayerImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    """ 선수 이미지 삭제 """

    @extend_schema(
        summary="선수 이미지 삭제",
        description="관리자만 프로필 / 배경 이미지를 삭제할 수 있습니다.",
        responses={
            200: {"message": "Image deleted successfully"},
            403: {"description": "권한 없음"},
            400: {"description": "삭제 실패"},
        },
    )
    def delete(self, request: Any, image_id: int) -> Response:
        image = get_object_or_404(PlayerImage, id=image_id)

        # 프로필 / 배경 이미지는 관리자만 삭제 가능
        if image.category in ["profile", "background"] and not request.user.is_staff:
            return Response({"error": "Only staff can delete images"}, status=status.HTTP_403_FORBIDDEN)

        if delete_file_from_s3(image.image_url):
            image.delete()
            return Response({"message": "Image deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Delete failed"}, status=status.HTTP_400_BAD_REQUEST)


""" 팀 프로필 / 배경 이미지 조회 """


class TeamProfileImageView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        summary="팀 프로필 / 배경 이미지 조회 (가장 최근 이미지 1장)",
        responses={200: TeamImageSerializer, 404: {"description": "이미지 없음"}},
    )
    def get(self, request: Any, team_id: int) -> Response:
        category = request.data.get("category")
        if category not in ["profile", "background"]:
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        image = TeamImage.objects.filter(team_id=team_id, category=category).order_by("-uploaded_at").first()
        if not image:
            return Response({"error": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = TeamImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_200_OK)


""" 팀 프로필 / 배경 이미지 업로드 및 수정, 삭제 """


class TeamProfileImageDetailView(APIView):
    parser_classes = (FormParser, MultiPartParser)

    @extend_schema(
        summary="팀 이미지 업로드",
        description="관리자만 프로필 / 배경 이미지를 업로드할 수 있습니다.",
        request=OpenApiRequest(
            {
                "multipart/form-data": {
                    "image": {"type": "string", "format": "binary"},
                    "category": {"type": "string", "enum": ["profile", "background", "gallery", "community"]},
                }
            }
        ),
        responses={201: TeamImageSerializer, 400: {"description": "업로드 실패"}, 403: {"description": "권한 없음"}},
    )
    def post(self, request: Any, team_id: int, *args: Any, **kwargs: Any) -> Response:
        team = get_object_or_404(Team, id=team_id)

        category = request.data.get("category")
        if category not in ["profile", "background"]:
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        # 프로필 / 배경 이미지는 관리자만 업로드 가능
        if category in ["profile", "background"] and not request.user.is_staff:
            return Response({"error": "Only staff can upload images"}, status=status.HTTP_403_FORBIDDEN)

        # 파일 유무 확인
        file = request.FILES.get("image")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        # 기존 이미지 삭제 (1개 제한)
        existing_image = TeamImage.objects.filter(team=team, category=category).first()
        if existing_image:
            delete_file_from_s3(existing_image.image_url)
            existing_image.delete()

        # 새 이미지 업로드
        s3_url = upload_image_to_s3(file, category, "teams", team.name)
        if not s3_url:
            return Response({"error": "Upload failed"}, status=status.HTTP_400_BAD_REQUEST)

        image = TeamImage.objects.create(
            team=team,
            category=category,
            image_url=s3_url,
            uploaded_by=None,
        )

        serializer = TeamImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    """ 팀 이미지 삭제 """

    @extend_schema(
        summary="팀 이미지 삭제",
        description="관리자만 프로필 / 배경 이미지를 삭제할 수 있습니다.",
        responses={
            200: {"message": "Image deleted successfully"},
            403: {"description": "권한 없음"},
            400: {"description": "삭제 실패"},
        },
    )
    def delete(self, request: Any, image_id: int) -> Response:
        image = get_object_or_404(TeamImage, id=image_id)

        # 프로필 / 배경 이미지는 관리자만 삭제 가능
        if image.category in ["profile", "background"] and not request.user.is_staff:
            return Response({"error": "Only staff can delete images"}, status=status.HTTP_403_FORBIDDEN)

        if delete_file_from_s3(image.image_url):
            image.delete()
            return Response({"message": "Image deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Delete failed"}, status=status.HTTP_400_BAD_REQUEST)


""" 선수 갤러리 이미지 업로드 및 수정, 삭제 """


class PlayerGalleryImageView(APIView):
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request: Any, player_id: int, *args: Any, **kwargs: Any) -> Response:
        player = get_object_or_404(Player, id=player_id)

        category = request.data.get("category")
        if category != "gallery":
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        # 유저만 사진 업로드 가능
        if not request.user.is_active:
            return Response({"error": "Only User can upload images"}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get("image")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        s3_url = upload_image_to_s3(file, category, "players", player.nickname)
        if not s3_url:
            return Response({"error": "Upload failed"}, status=status.HTTP_400_BAD_REQUEST)

        image = PlayerImage.objects.create(
            player_id=player_id,
            category=category,
            image_url=s3_url,
            uploaded_by=request.user if category in "gallery" else None,
        )
        serializer = PlayerImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    """ 선수 갤러리 이미지 삭제 """

    def delete(self, request: Any, image_id: int) -> Response:
        image = get_object_or_404(PlayerImage, id=image_id)

        # 갤러리는 업로더 본인만 삭제 가능
        if image.category == "gallery" and image.uploaded_by != request.user:
            return Response(
                {"error": "You do not have permission to delete this image"}, status=status.HTTP_403_FORBIDDEN
            )

        if delete_file_from_s3(image.image_url):
            image.delete()
            return Response({"message": "Image deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Delete failed"}, status=status.HTTP_400_BAD_REQUEST)


""" 팀 갤러리 이미지 업로드 및 수정, 삭제 """


class TeamGalleryImageView(APIView):
    parser_classes = (FormParser, MultiPartParser)

    def post(self, request: Any, team_id: int, *args: Any, **kwargs: Any) -> Response:
        team = get_object_or_404(Team, id=team_id)

        category = request.data.get("category")
        if category != "gallery":
            return Response({"error": "Invalid category"}, status=status.HTTP_400_BAD_REQUEST)

        # 유저만 사진 업로드 가능
        if not request.user.is_active:
            return Response({"error": "Only User can upload images"}, status=status.HTTP_403_FORBIDDEN)

        file = request.FILES.get("image")
        if not file:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)

        s3_url = upload_image_to_s3(file, category, "teams", team.name)
        if not s3_url:
            return Response({"error": "Upload failed"}, status=status.HTTP_400_BAD_REQUEST)

        image = TeamImage.objects.create(
            team=team,
            category=category,
            image_url=s3_url,
            uploaded_by=request.user if category in "gallery" else None,
        )
        serializer = TeamImageSerializer(image)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    """ 팀 갤러리 이미지 삭제 """

    def delete(self, request: Any, image_id: int) -> Response:
        image = get_object_or_404(TeamImage, id=image_id)

        # 갤러리는 업로더 본인만 삭제 가능
        if image.category == "gallery" and image.uploaded_by != request.user:
            return Response(
                {"error": "You do not have permission to delete this image"}, status=status.HTTP_403_FORBIDDEN
            )

        if delete_file_from_s3(image.image_url):
            image.delete()
            return Response({"message": "Image deleted successfully"}, status=status.HTTP_200_OK)

        return Response({"error": "Delete failed"}, status=status.HTTP_400_BAD_REQUEST)


""" 선수 갤러리 이미지 전체 조회 """


class PlayerGalleryListView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="특정 선수의 갤러리 이미지 목록 조회",
        responses={200: PlayerImageSerializer(many=True)},
    )
    def get(self, request: Any, player_id: int) -> Response:
        images = PlayerImage.objects.filter(player_id=player_id, category="gallery")
        serializer = PlayerImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


""" 팀 갤러리 이미지 전체 조회 """


class TeamGalleryListView(APIView):
    authentication_classes = []
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="특정 팀의 갤러리 이미지 목록 조회",
        responses={200: TeamImageSerializer(many=True)},
    )
    def get(self, request: Any, team_id: int) -> Response:
        images = TeamImage.objects.filter(team_id=team_id, category="gallery")
        serializer = TeamImageSerializer(images, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
