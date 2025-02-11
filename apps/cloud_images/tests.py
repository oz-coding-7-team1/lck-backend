from typing import Any

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.cloud_images.models import PlayerImage, TeamImage
from apps.players.models import Player
from apps.teams.models import Team


class PlayerImageListViewTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.player: Player = Player.objects.create(
            realname="Test Realname",
            nickname="Test Nickname",
            gamename="Test Gamename",
            position="mid",
            date_of_birth="1990-01-01",
            debut_date="2010-01-01",
            agency="Test Agency",
        )
        self.image1: PlayerImage = PlayerImage.objects.create(
            player=self.player, type="profile", url="https://s3.amazonaws.com/bucket/faker_profile.jpg"
        )
        self.image2: PlayerImage = PlayerImage.objects.create(
            player=self.player, type="gallery", url="https://s3.amazonaws.com/bucket/faker_gallery.jpg"
        )
        self.url: str = reverse("player_image_list", kwargs={"player_id": self.player.id})

    def test_get_player_images(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("images", response.data)
        self.assertEqual(len(response.data["images"]), 2)

        images: list[dict[str, Any]] = response.data["images"]  # JSON 응답을 dict로 캐스팅
        self.assertEqual(images[0]["type"], "profile")
        self.assertEqual(images[1]["type"], "gallery")


class TeamImageListViewTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.team: Team = Team.objects.create(name="T1")
        self.image1: TeamImage = TeamImage.objects.create(
            team=self.team, type="profile", url="https://s3.amazonaws.com/bucket/t1_profile.jpg"
        )
        self.image2: TeamImage = TeamImage.objects.create(
            team=self.team, type="background", url="https://s3.amazonaws.com/bucket/t1_background.jpg"
        )
        self.url: str = reverse("team_image_list", kwargs={"team_id": self.team.id})

    def test_get_team_images(self) -> None:
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("images", response.data)
        self.assertEqual(len(response.data["images"]), 2)

        images: list[dict[str, Any]] = response.data["images"]
        self.assertEqual(images[0]["type"], "profile")
        self.assertEqual(images[1]["type"], "background")
