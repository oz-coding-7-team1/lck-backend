import uuid

from django.db import models

from apps.users.models import User


class CloudImage(models.Model):
    CATEGORY_CHOICES = [
        ("users", "Users"),
        ("players", "Players"),
        ("teams", "Teams"),
    ]

    IMAGE_TYPE_CHOICES = [
        ("profile", "Profile Image"),
        ("background", "Background Image"),
        ("gallery", "Gallery Image"),
        ("community", "Community Image"),  # users/community
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)  # users, players, teams
    image_type = models.CharField(max_length=15, choices=IMAGE_TYPE_CHOICES)  # profile, background, gallery, community
    image_url = models.URLField()  # S3 URL 저장
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category}/{self.image_type} - {self.image_url}"

    class Meta:
        db_table = "cloud_images"
