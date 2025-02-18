from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django_softdelete.models import SoftDeleteModel

from apps.common.models import BaseModel
from apps.players.models import Player
from apps.teams.models import Team


class TeamPost(BaseModel, SoftDeleteModel):  # type: ignore
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="community_posts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        db_table = "team_post"

    def __str__(self) -> str:
        return f"{self.title}"


class TeamComment(BaseModel, SoftDeleteModel):  # type: ignore
    post = models.ForeignKey(TeamPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")

    class Meta:
        db_table = "team_comment"

    def __str__(self) -> str:
        return f"Comment by {self.user} on {self.post}"


class PlayerPost(BaseModel, SoftDeleteModel):  # type: ignore
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="community_posts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        db_table = "player_post"

    def __str__(self) -> str:
        return f"{self.title}"


class PlayerComment(BaseModel, SoftDeleteModel):  # type: ignore
    post = models.ForeignKey(PlayerPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies")

    class Meta:
        db_table = "player_comment"

    def __str__(self) -> str:
        return f"Comment by {self.user} on {self.post}"


class Like(BaseModel, SoftDeleteModel):  # type: ignore
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # 어느 게시글이나 댓글에 좋아요를 남길지 범용적으로 처리 (GenericForeignKey를 쓸 수도 있음)
    content_type = models.ForeignKey("contenttypes.ContentType", on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        db_table = "like"
