import random
import uuid
from typing import Any

from django.core.management.base import BaseCommand

from apps.cloud_images.models import PlayerImage, TeamImage, UserImage
from apps.players.models import Player
from apps.teams.models import Team
from apps.users.models import User

IMAGE_CATEGORIES = ["profile", "background", "gallery", "community"]


class Command(BaseCommand):
    help = "Generate dummy images for players, teams, and users."

    def handle(self, *args: Any, **options: Any) -> None:
        self.stdout.write("Generating dummy images...")

        # Dummy Image URL 생성 함수
        def generate_dummy_url(category: str, image_type: str) -> str:
            return f"https://dummyimage.com/600x400/{random.randint(100, 999)}/fff.png&text={category}+{image_type}+{uuid.uuid4()}"

        # 모든 선수에 대해 dummy 이미지 생성 (각 선수당 1~3개)
        players = Player.objects.all()
        for player in players:
            num_images = random.randint(1, 3)
            for _ in range(num_images):
                category = random.choice(IMAGE_CATEGORIES)
                uploaded_by = random.choice(User.objects.all()) if category in ["gallery", "community"] else None

                PlayerImage.objects.create(
                    player=player,
                    category=category,
                    image_url=generate_dummy_url("Player", category),
                    uploaded_by=uploaded_by,
                )

        # 모든 팀에 대해 dummy 이미지 생성 (각 팀당 1~3개)
        teams = Team.objects.all()
        for team in teams:
            num_images = random.randint(1, 3)
            for _ in range(num_images):
                category = random.choice(IMAGE_CATEGORIES)
                uploaded_by = random.choice(User.objects.all()) if category in ["gallery", "community"] else None

                TeamImage.objects.create(
                    team=team,
                    category=category,
                    image_url=generate_dummy_url("Team", category),
                    uploaded_by=uploaded_by,
                )

        # user profile 이미지 생성 (각 유저당 1개)
        users = User.objects.all()
        for user in users:
            if not UserImage.objects.filter(user=user).exists():  # 중복 방지
                UserImage.objects.create(
                    user=user,
                    image_url=generate_dummy_url("User", "profile"),
                )

        self.stdout.write(self.style.SUCCESS("Dummy images generated successfully."))
