from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from apps.players.models import Player
from apps.teams.models import Team
from models import PlayerImage, TeamImage

class PlayerImageListViewTest(APITestCase):
    def setUp(self):
        self.player = Player.objects.create(realname="Faker")
        self.image1 = PlayerImage.objects.create(player=self.player, type="profile", url="https://s3.amazonaws.com/bucket/faker_profile.jpg")
        self.image2 = PlayerImage.objects.create(player=self.player, type="gallery", url="https://s3.amazonaws.com/bucket/faker_gallery.jpg")
        self.url = reverse('player_image_list', kwargs={'player_id': self.player.id})

    def test_get_player_images(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("images", response.data)
        self.assertEqual(len(response.data["images"]), 2)
        self.assertEqual(response.data["images"][0]["type"], "profile")
        self.assertEqual(response.data["images"][1]["type"], "gallery")


class TeamImageListViewTest(APITestCase):
    def setUp(self):
        self.team = Team.objects.create(name="T1")
        self.image1 = TeamImage.objects.create(team=self.team, type="profile", url="https://s3.amazonaws.com/bucket/t1_profile.jpg")
        self.image2 = TeamImage.objects.create(team=self.team, type="background", url="https://s3.amazonaws.com/bucket/t1_background.jpg")
        self.url = reverse('team_image_list', kwargs={'team_id': self.team.id})

    def test_get_team_images(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("images", response.data)
        self.assertEqual(len(response.data["images"]), 2)
        self.assertEqual(response.data["images"][0]["type"], "profile")
        self.assertEqual(response.data["images"][1]["type"], "background")
