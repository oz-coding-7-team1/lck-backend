import boto3
from django.conf import settings  # -> DJANGO_SETTINGS_MODULE 설정에 따라 가져옴


def get_s3_client():  # type: ignore
    return boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
