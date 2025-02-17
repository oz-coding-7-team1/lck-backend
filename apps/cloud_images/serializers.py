from rest_framework import serializers

from .models import CloudImage


class CloudImageSerializer(serializers.ModelSerializer[CloudImage]):

    class Meta:
        model = CloudImage
        fields = ["id", "category", "image_type", "image_url", "uploaded_by", "uploaded_at"]
