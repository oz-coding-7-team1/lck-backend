from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta

from apps.subscriptions.models import PlayerSubscription, TeamSubscription


class Command(BaseCommand):
    help = """Soft delete된 데이터 중 3일이 지난 데이터를 영구 삭제합니다.
    		명령어: python manage.py hard_delete_old_subscriptions
			매일 자정 진행: 0 0 * * * /path/to/venv/bin/python /path/to/project/manage.py hard_delete_old_subscriptions
			"""

    def handle(self, *args, **kwargs):
        threshold = now() - timedelta(days=3)

        # 3일 이상 지난 soft delete된 row 삭제
        deleted_players = PlayerSubscription.objects.filter(deleted_at__lte=threshold).delete()
        deleted_teams = TeamSubscription.objects.filter(deleted_at__lte=threshold).delete()

        self.stdout.write(self.style.SUCCESS(f"선수 구독 {deleted_players[0]}개 삭제 완료"))
        self.stdout.write(self.style.SUCCESS(f"팀 구독 {deleted_teams[0]}개 삭제 완료"))
