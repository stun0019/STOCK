import math
from dataclasses import dataclass

from backend.services.data_service import normalize_key


@dataclass(frozen=True)
class EloSnapshot:
    ratings: dict
    games_played: dict
    updates: list


class EloRatingSystem:
    K_FACTORS = {
        "football": 24,
        "basketball": 20,
    }

    def __init__(self, sport):
        self.sport = sport
        self.k_factor = self.K_FACTORS.get(sport, 24)

    @staticmethod
    def expected_score(home_rating, away_rating, home_advantage=0):
        rating_delta = (home_rating + home_advantage) - away_rating
        return 1 / (1 + math.pow(10, -rating_delta / 400))

    def build_snapshot(self, teams, history):
        ratings = {}
        games_played = {}
        updates = []

        for key, team in teams.items():
            ratings[key] = float(team.get("elo_seed", 1500))
            games_played[key] = 0

        for match in history:
            home_key = normalize_key(match["home_team"])
            away_key = normalize_key(match["away_team"])
            if home_key not in ratings or away_key not in ratings:
                continue

            home_rating = ratings[home_key]
            away_rating = ratings[away_key]
            home_advantage = float(teams[home_key].get("home_advantage", 0))

            expected_home = self.expected_score(
                home_rating,
                away_rating,
                home_advantage,
            )
            actual_home = self._actual_home_result(
                match["home_score"],
                match["away_score"],
            )
            multiplier = self._margin_multiplier(
                match["home_score"],
                match["away_score"],
            )
            rating_change = self.k_factor * multiplier * (actual_home - expected_home)

            ratings[home_key] = home_rating + rating_change
            ratings[away_key] = away_rating - rating_change
            games_played[home_key] += 1
            games_played[away_key] += 1

            updates.append(
                {
                    "date": match["date"],
                    "home_team": match["home_team"],
                    "away_team": match["away_team"],
                    "expected_home": round(expected_home, 4),
                    "actual_home": actual_home,
                    "rating_change": round(rating_change, 2),
                }
            )

        return EloSnapshot(
            ratings=ratings,
            games_played=games_played,
            updates=updates,
        )

    def _actual_home_result(self, home_score, away_score):
        if home_score > away_score:
            return 1.0
        if home_score < away_score:
            return 0.0
        return 0.5

    def _margin_multiplier(self, home_score, away_score):
        margin = abs(home_score - away_score)
        if margin <= 1:
            return 1.0
        return 1 + (math.log(margin) * 0.15)
