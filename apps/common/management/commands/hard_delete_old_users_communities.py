from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from apps.communities.models import (
    Like,
    PlayerComment,
    PlayerPost,
    TeamComment,
    TeamPost,
)
from apps.users.models import User


class Command(BaseCommand):
    help = """Soft delete된 데이터 중 7일이 지난 데이터를 영구 삭제합니다.
    		명령어: python manage.py hard_delete_old_users_communities
			매일 자정 진행: 0 0 * * * /path/to/venv/bin/python /path/to/project/hard_delete_old_users_communities
			"""

    def handle(self, *args: Any, **options: Any) -> None:

        deleted_users = User.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=7))
        deleted_TeamPosts = TeamPost.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=7))
        deleted_TeamComments = TeamComment.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=7))
        deleted_PlayerPosts = PlayerPost.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=7))
        deleted_PlayerComments = PlayerComment.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=7))
        deleted_Likes = Like.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=7))

        deleted_users_count = deleted_users.count()
        deleted_TeamPosts_count = deleted_TeamPosts.count()
        deleted_TeamComments_count = deleted_TeamComments.count()
        deleted_PlayerPosts_count = deleted_PlayerPosts.count()
        deleted_PlayerComments_count = deleted_PlayerComments.count()
        deleted_Likes_count = deleted_Likes.count()

        deleted_users.hard_delete()
        deleted_TeamPosts.hard_delete()
        deleted_TeamComments.hard_delete()
        deleted_PlayerPosts.hard_delete()
        deleted_PlayerComments.hard_delete()
        deleted_Likes.hard_delete()

        self.stdout.write(self.style.SUCCESS(f"유저 {deleted_users_count}명 삭제 완료"))
        self.stdout.write(self.style.SUCCESS(f"팀 게시판 {deleted_TeamPosts_count}개 삭제완료"))
        self.stdout.write(self.style.SUCCESS(f"팀 댓글 {deleted_TeamComments_count}개 삭제완료"))
        self.stdout.write(self.style.SUCCESS(f"선수 게시판 {deleted_PlayerPosts_count}개 삭제완료"))
        self.stdout.write(self.style.SUCCESS(f"선수 댓글 {deleted_PlayerComments_count}개 삭제완료"))
        self.stdout.write(self.style.SUCCESS(f"좋아요 {deleted_Likes_count}개 삭제완료"))
