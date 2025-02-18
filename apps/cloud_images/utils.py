import uuid
from typing import Any, Optional, Tuple

from django.conf import settings  # -> DJANGO_SETTINGS_MODULE 설정에 따라 가져옴

# 허용된 확장자 목록
ALLOWED_EXTENSIONS = {"jpeg", "png", "jpg", "gif"}


def validate_file_extension(filename: str) -> Optional[Tuple[str, str]]:
    file_parts = filename.rsplit(".", 1)
    if len(file_parts) != 2:
        return None  # 확장자가 없는 경우

    file_name, file_extension = file_parts
    file_extension = file_extension.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        return None  # 허용되지 않은 확장자

    return file_name, file_extension


def upload_image_to_s3(file: Any, category: str, instance_type: str, object_id: int) -> Optional[str]:
    """
    S3 에 이미지 업로드 후 URL 반환

    Args:
        file (Any); 업로드할 파일 객체
        category (str): 이미지 카테고리
        instance_type (str): "users", "players", "teams" 중 하나
        object_id (int): 해당 객체의 ID (user_id, player_id, team_id)

    Returns:
        Optional[str]: 업로드된 파일의 S3 URL 또는 None (오류 발생 시)
    """

    # 확장자 검증
    ext = file.name.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        print(f"Invalid file extension: {ext}")
        return None

    new_filename = f"{uuid.uuid4()}.{ext}"

    # S3 저장 경로 설정
    if instance_type == "users":
        s3_path = f"media/users/{object_id}/{new_filename}"
    elif instance_type == "players":
        s3_path = f"media/players/{object_id}/{category}/{new_filename}"
    elif instance_type == "teams":
        s3_path = f"media/teams/{object_id}/{category}/{new_filename}"
    else:
        print(f"Invalid instance type: {instance_type}")
        return None

    try:
        settings.s3_client.upload_fileobj(file, settings.AWS_S3_BUCKET_NAME, s3_path, ExtraArgs={"ACL": "public-read"})
        return f"{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_path}"
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None


def delete_file_from_s3(image_url: str) -> bool:
    """
    S3 에서 이미지 삭제

    Args:
        image_url (str): 삭제할 이미지의 S3 URL

    Returns:
        bool: 삭제 성공 여부
    """

    try:
        s3_path = image_url.replace(settings.AWS_S3_CUSTOM_DOMAIN + "/", "")
        settings.s3_client.delete_object(Bucket=settings.AWS_S3_BUCKET_NAME, Key=s3_path)
        return True
    except Exception as e:
        print(f"S3 Delete Error: {e}")
        return False
