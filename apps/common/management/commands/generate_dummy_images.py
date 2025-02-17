import random
import uuid
from typing import Any

from django.core.management.base import BaseCommand

from apps.cloud_images.models import CloudImage
from apps.players.models import Player
from apps.teams.models import Team
from apps.users.models import User


class Command(BaseCommand):
    help = "Generate dummy images for players and teams."

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Generating dummy images...")

        # Dummy Image URL 생성 함수
        def generate_dummy_url(category: str, image_type: str) -> str:
            return f"https://dummyimage.com/600x400/{random.randint(100, 999)}/fff.png&text={category}+{image_type}+{uuid.uuid4()}"

        # 모든 선수에 대해 dummy 이미지 생성 (각 선수당 1~3개)
        players = Player.objects.all()
        for player in players:
            num_images = random.randint(1, 3)
            for i in range(num_images):
                img_type = random.choice(["profile", "background", "gallery", "community"])
                CloudImage.objects.create(
                    category="players",
                    image_type=img_type,
                    image_url=generate_dummy_url("Player", img_type),
                    uploaded_by=random.choice(User.objects.all()),
                )

        # 모든 팀에 대해 dummy 이미지 생성 (각 팀당 1~3개)
        teams = Team.objects.all()
        for team in teams:
            num_images = random.randint(1, 3)
            for i in range(num_images):
                img_type = random.choice(["profile", "background", "gallery", "community"])
                CloudImage.objects.create(
                    category="teams",
                    image_type=img_type,
                    image_url=generate_dummy_url("Team", img_type),
                    uploaded_by=random.choice(User.objects.all()),
                )

        # user profile 이미지 생성 (각 유저당 1개)
        users = User.objects.all()
        for user in users:
            CloudImage.objects.create(
                category="users",
                image_type="profile",
                image_url=generate_dummy_url("User", "profile"),
                uploaded_by=user,
            )

        self.stdout.write(self.style.SUCCESS("Dummy images generated successfully."))
