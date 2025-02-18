from django.db import models

from apps.players.models import Player
from apps.teams.models import Team
from apps.users.models import User

IMAGE_CATEGORIES = [
    ("profile", "Profile Image"),
    ("background", "Background Image"),
    ("gallery", "Gallery Image"),
    ("community", "Community Image"),
]


class UserImage(models.Model):
    # User Profile Image Model
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_images")
    image_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"User {self.user.id} - {self.image_url}"

    class Meta:
        db_table = "user_images"


class PlayerImage(models.Model):
    # Player Image Model
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="player_images")
    category = models.CharField(max_length=20, choices=IMAGE_CATEGORIES)
    image_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="uploaded_player_images"
    )

    def __str__(self):
        return f"Player {self.player.id} - {self.category} - {self.image_url}"

    class Meta:
        db_table = "player_images"


class TeamImage(models.Model):
    # Team Image Model
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_images")
    category = models.CharField(max_length=20, choices=IMAGE_CATEGORIES)
    image_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.CASCADE, related_name="uploaded_team_images"
    )

    def __str__(self):
        return f"Team {self.team.id} - {self.category} - {self.image_url}"

    class Meta:
        db_table = "team_images"
