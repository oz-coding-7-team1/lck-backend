import uuid
from typing import Any, Optional, Tuple

from config.settings import base

# 허용된 확장자 목록
ALLOWED_EXTENSIONS = {"jpeg", "png", "jpg", "gif"}


def validate_file_extension(filename: str) -> Optional[Tuple[str, str]]:
    file_parts = filename.rsplit(".", 1)
    if len(file_parts) != 2:
        raise ValueError("File must have an extension")  # 확장자가 없는 경우

    file_name, file_extension = file_parts
    file_extension = file_extension.lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        raise ValueError(f"Invalid file extension: {file_extension}")  # 허용되지 않은 확장자

    return file_name, file_extension


def upload_image_to_s3(file: Any, category: str, instance_type: str, object_identifier: int | str) -> Optional[str]:
    """
    S3 에 이미지 업로드 후 URL 반환

    Args:
        file (Any); 업로드할 파일 객체
        category (str): 이미지 카테고리
        instance_type (str): "users", "players", "teams" 중 하나
        object_identifier (int | str): 해당 객체의 식별자 (user_id, player_nickname, team_name)

    Returns:
        Optional[str]: 업로드된 파일의 S3 URL 또는 None (오류 발생 시)
    """

    # 확장자 검증
    validation_result = validate_file_extension(file.name)
    if validation_result is None:
        raise ValueError(f"Invalid file extension: {file.name.split('.')[-1].lower()}")

    file_name, file_extension = validation_result
    new_filename = f"{uuid.uuid4()}.{file_extension}"

    # S3 저장 경로 설정
    if instance_type == "users":
        s3_path = f"users_images/{object_identifier}/{new_filename}"
    elif instance_type == "players":
        s3_path = f"players_images/{object_identifier}/{category}/{new_filename}"
    elif instance_type == "teams":
        s3_path = f"teams_images/{object_identifier}/{category}/{new_filename}"
    else:
        raise ValueError(f"Invalid instance type: {instance_type}")

    try:
        base.s3_client.upload_fileobj(file, base.AWS_S3_BUCKET_NAME, s3_path)
        return f"{base.AWS_S3_CUSTOM_DOMAIN}/{s3_path}"
    except Exception as e:
        raise RuntimeError(f"S3 Upload Error: {e}")


def delete_file_from_s3(image_url: str) -> bool:
    """
    S3 에서 이미지 삭제

    Args:
        image_url (str): 삭제할 이미지의 S3 URL

    Returns:
        bool: 삭제 성공 여부
    """

    try:
        s3_path = image_url.replace(base.AWS_S3_CUSTOM_DOMAIN + "/", "")
        base.s3_client.delete_object(Bucket=base.AWS_S3_BUCKET_NAME, Key=s3_path)
        return True
    except Exception as e:
        raise RuntimeError(f"S3 Delete Error: {e}")
