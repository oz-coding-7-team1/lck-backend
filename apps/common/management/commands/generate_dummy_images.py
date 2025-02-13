import random
from typing import Any

from django.core.management.base import BaseCommand

from apps.cloud_images.models import PlayerImage, TeamImage
from apps.players.models import Player
from apps.teams.models import Team


class Command(BaseCommand):
    help = "Generate dummy images for players and teams."

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Generating dummy images...")

        # 모든 선수에 대해 dummy 이미지 생성 (각 선수당 1~3개)
        players = Player.objects.all()
        for player in players:
            num_images = random.randint(1, 3)
            for i in range(num_images):
                img_type = random.choice(["profile", "action", "award"])
                # 예시 URL: dummyimage.com을 활용하여 임의의 이미지 URL 생성
                url = f"http://dummyimage.com/600x400/{random.randint(100,999)}/fff.png&text=Player+{player.id}+{img_type}+{i}"
                PlayerImage.objects.create(
                    player=player,
                    type=img_type,
                    url=url,
                    # deleted_at가 NULL이면 이미지가 활성 상태임
                )

        # 모든 팀에 대해 dummy 이미지 생성 (각 팀당 1~3개)
        teams = Team.objects.all()
        for team in teams:
            num_images = random.randint(1, 3)
            for i in range(num_images):
                img_type = random.choice(["logo", "banner", "group"])
                url = f"http://dummyimage.com/800x600/{random.randint(100,999)}/fff.png&text=Team+{team.id}+{img_type}+{i}"
                TeamImage.objects.create(
                    team=team,
                    type=img_type,
                    url=url,
                    # deleted_at가 NULL이면 이미지가 활성 상태임
                )

        self.stdout.write(self.style.SUCCESS("Dummy images generated successfully."))
