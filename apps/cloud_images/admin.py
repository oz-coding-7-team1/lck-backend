from django.contrib import admin

from apps.cloud_images.models import CloudImage
from apps.common.admin import BaseModelAdmin


@admin.register(CloudImage)
class CloudImageAdmin(BaseModelAdmin):
    pass
