import uuid
from typing import Any

import boto3
from django.conf import settings  # -> DJANGO_SETTINGS_MODULE 설정에 따라 가져옴

# 허용된 확장자 목록
ALLOWED_EXTENSIONS = {"jpeg", "png", "jpg", "gif"}


def validate_file_extension(filename: str) -> Any:
    file_parts = filename.rsplit(".", 1)
    if len(file_parts) != 2:
        return None, None  # 확장자가 없는 경우

    file_name, file_extension = file_parts
    file_extension = file_extension.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        return None, None  # 허용되지 않은 확장자

    return file_name, file_extension


def upload_image_to_s3(file: Any, category: str, image_type: str, user: Any) -> Any:
    file_name, file_extension = validate_file_extension(file.name)
    if not file_name or not file_extension:
        return None  # 확장자 검증 실패

    new_filename = f"{uuid.uuid4()}.{file_extension}"  # UUID 기반의 파일명 생성
    s3_path = f"media/{category}/{image_type}/{new_filename}"

    try:
        settings.s3_client.upload_fileobj(file, settings.AWS_S3_BUCKET_NAME, s3_path, ExtraArgs={"ACL": "public-read"})
        return f"{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_path}"
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None
