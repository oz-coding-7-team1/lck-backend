import random
from typing import Any, Dict

from django.core.management.base import BaseCommand

from apps.players.models import Player, Position
from apps.teams.models import Team


class Command(BaseCommand):
    help = "Generate dummy data for Teams and Players (without Faker, with duplicate check)"

    def handle(self, *args: Any, **kwargs: Any) -> None:
        self.stdout.write(self.style.SUCCESS("Generating dummy data without Faker..."))

        positions: list[Position] = list(Position)

        def random_social() -> dict[str, str]:
            # 1~4개의 랜덤 소셜 미디어 정보 포함 (없을 수도 있음)
            social_platforms: dict[str, str] = {
                "insta": "https://instagram.com/example",
                "facebook": "https://facebook.com/example",
                "youtube": "https://youtube.com/example",
                "X": "https://twitter.com/example",
                "soop": "https://soop.com/example",
                "chzzk": "https://chzzk.com/example",
            }
            selected_keys = random.sample(list(social_platforms.keys()), k=random.randint(0, 6))
            return {key: social_platforms[key] for key in selected_keys} if selected_keys else {}

        # 팀 데이터 생성 (중복 방지)
        team_names: list[str] = [
            "T1",
            "Gen.G",
            "DK",
            "Hanwha Life",
            "KT Rolster",
            "DRX",
            "Nongshim RedForce",
            "Kwangdong Freecs",
            "Liiv Sandbox",
            "OK Savings Bank",
        ]
        teams: list[Team] = []

        for name in team_names:
            team, created = Team.objects.get_or_create(
                name=name,
                defaults={"social": random_social()},
            )
            teams.append(team)

        self.stdout.write(self.style.SUCCESS("Created or retrieved 10 teams"))

        # 팀당 5명의 선수 생성 (각 포지션 1명씩)
        nicknames: list[str] = [f"Player{i}" for i in range(1, 51)]
        realnames: list[str] = [f"Real Name {i}" for i in range(1, 51)]

        player_index: int = 0
        for team in teams:
            used_positions: set[Position] = set()
            for _ in range(5):
                available_positions = [pos for pos in positions if pos not in used_positions]
                position = random.choice(available_positions)
                used_positions.add(position)

                Player.objects.create(
                    team=team,
                    realname=realnames[player_index],
                    nickname=nicknames[player_index],
                    gamename=nicknames[player_index],
                    position=position.value,
                    date_of_birth="1995-01-01",
                    debut_date="2015-01-01",
                    social=random_social(),
                    agency="Esports Management",
                    is_active=True,
                    nationality="KOREA",
                )
                player_index += 1

        self.stdout.write(self.style.SUCCESS("Assigned 5 players to each team (Total: 50 players)"))

        # 나머지 30명의 선수는 팀 없이 생성 (무소속)
        for i in range(50, 80):
            position = random.choice(positions)

            Player.objects.create(
                team=None,
                realname=f"Player {i+1}",
                nickname=f"Nickname {i+1}",
                gamename=f"GameName {i+1}",
                position=position.value,
                date_of_birth="1997-02-15",
                debut_date="2016-05-10",
                social=random_social(),
                agency="Freelancer",
                is_active=True,
                nationality="KOREA",
            )

        self.stdout.write(self.style.SUCCESS("Created 30 unassigned players"))
        self.stdout.write(self.style.SUCCESS("Dummy data generation complete!"))
