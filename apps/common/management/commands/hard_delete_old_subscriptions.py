from datetime import timedelta
from typing import Any

from django.core.management.base import BaseCommand
from django.utils.timezone import now

from apps.subscriptions.models import PlayerSubscription, TeamSubscription


class Command(BaseCommand):
    help = """Soft delete된 데이터 중 3일이 지난 데이터를 영구 삭제합니다.
    		명령어: python manage.py hard_delete_old_subscriptions
			매일 자정 진행: 0 0 * * * /path/to/venv/bin/python /path/to/project/manage.py hard_delete_old_subscriptions
			"""

    def handle(self, *args: Any, **options: Any) -> None:
        # 3일 이상 지난 soft delete된 row 삭제
        # 소프트 딜리트된 레코드를 포함한 모든 레코드를 가져옵니다.
        deleted_players = PlayerSubscription.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=3))
        deleted_teams = TeamSubscription.deleted_objects.filter(deleted_at__lte=now() - timedelta(days=3))

        deleted_players_count = deleted_players.count()
        deleted_teams_count = deleted_teams.count()

        deleted_players.hard_delete()
        deleted_teams.hard_delete()

        self.stdout.write(self.style.SUCCESS(f"선수 구독 {deleted_players_count}개 삭제 완료"))
        self.stdout.write(self.style.SUCCESS(f"팀 구독 {deleted_teams_count}개 삭제 완료"))
