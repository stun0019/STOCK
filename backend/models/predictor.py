from backend.models.elo import EloRatingSystem
from backend.services.data_service import (
    DataError,
    get_team,
    load_history,
    load_teams,
    normalize_key,
    validate_sport,
)
from backend.services.odds_service import (
    OddsError,
    calculate_ev,
    implied_probability,
    validate_decimal_odds,
)


class PredictionError(ValueError):
    """Raised when a prediction cannot be generated."""


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


class PredictionEngine:
    """Deterministic multi-agent prediction engine.

    The agents mirror AGENTS.md: factual data, tactical/statistical views,
    neutral sentiment, risk management, and a final decision engine.
    """

    AGENT_WEIGHTS = {
        "data_analyst": 0.25,
        "tactical_analyst": 0.20,
        "statistical_model": 0.55,
    }

    def predict(self, sport, home_team, away_team, odds):
        try:
            sport = validate_sport(sport)
            odds = validate_decimal_odds(odds)
            home = get_team(sport, home_team)
            away = get_team(sport, away_team)
        except (DataError, OddsError) as exc:
            raise PredictionError(str(exc)) from exc

        if normalize_key(home["name"]) == normalize_key(away["name"]):
            raise PredictionError("Home team and away team must be different.")

        teams = load_teams()[sport]
        history = load_history(sport)
        elo_snapshot = EloRatingSystem(sport).build_snapshot(teams, history)

        home_key = normalize_key(home["name"])
        away_key = normalize_key(away["name"])
        home_rating = elo_snapshot.ratings[home_key]
        away_rating = elo_snapshot.ratings[away_key]
        home_advantage = float(home.get("home_advantage", 0))

        statistical = self._statistical_model(
            home_rating,
            away_rating,
            home_advantage,
            sport,
        )
        data = self._data_analyst(sport, home["name"], away["name"], history)
        tactical = self._tactical_analyst(sport, home, away)
        sentiment = self._sentiment_analyst()

        home_win_no_draw = clamp(
            (data["home_win_no_draw"] * self.AGENT_WEIGHTS["data_analyst"])
            + (
                tactical["home_win_no_draw"]
                * self.AGENT_WEIGHTS["tactical_analyst"]
            )
            + (
                statistical["home_win_no_draw"]
                * self.AGENT_WEIGHTS["statistical_model"]
            )
            + sentiment["probability_adjustment"],
            0.05,
            0.95,
        )

        probabilities = self._probability_distribution(
            sport,
            home_win_no_draw,
            home_rating,
            away_rating,
            home_advantage,
        )

        home_win_probability = round(probabilities["home_win"], 4)
        draw_probability = round(probabilities["draw"], 4)
        away_win_probability = round(probabilities["away_win"], 4)

        ev = calculate_ev(home_win_probability, odds)
        risk = self._risk_manager(
            home_win_probability,
            odds,
            elo_snapshot.games_played[home_key],
            elo_snapshot.games_played[away_key],
            home_rating,
            away_rating,
        )
        confidence = self._confidence_level(
            home_win_probability,
            odds,
            risk["label"],
        )
        recommendation = "BET" if ev > 0 else "NO BET"
        predicted_score = self._estimate_score(
            sport,
            home,
            away,
            home_rating,
            away_rating,
        )

        return {
            "match": f"{home['name']} vs {away['name']}",
            "home_win_probability": home_win_probability,
            "draw_probability": draw_probability,
            "away_win_probability": away_win_probability,
            "predicted_score": predicted_score,
            "ev": round(ev, 4),
            "risk": risk["label"],
            "confidence": confidence,
            "recommendation": recommendation,
            "trace": {
                "sport": sport,
                "odds": odds,
                "implied_probability": round(implied_probability(odds), 4),
                "elo": {
                    "home_rating": round(home_rating, 2),
                    "away_rating": round(away_rating, 2),
                    "home_advantage": home_advantage,
                    "home_games": elo_snapshot.games_played[home_key],
                    "away_games": elo_snapshot.games_played[away_key],
                },
                "agents": {
                    "data_analyst": data,
                    "tactical_analyst": tactical,
                    "statistical_model": statistical,
                    "sentiment_analyst": sentiment,
                    "risk_manager": risk,
                    "decision_engine": {
                        "agent_weights": self.AGENT_WEIGHTS,
                        "home_win_no_draw": round(home_win_no_draw, 4),
                        "ev_formula": "(probability * odds) - 1",
                    },
                },
            },
        }

    def _statistical_model(self, home_rating, away_rating, home_advantage, sport):
        probability = EloRatingSystem(sport).expected_score(
            home_rating,
            away_rating,
            home_advantage,
        )
        return {
            "home_win_no_draw": round(probability, 4),
            "model": "elo_logistic",
            "rating_delta": round((home_rating + home_advantage) - away_rating, 2),
        }

    def _data_analyst(self, sport, home_team, away_team, history):
        home_form = self._recent_form(sport, home_team, history)
        away_form = self._recent_form(sport, away_team, history)
        form_delta = home_form["score"] - away_form["score"]

        probability = clamp(0.5 + (form_delta * 0.18), 0.35, 0.65)
        return {
            "home_win_no_draw": round(probability, 4),
            "home_recent_form": home_form,
            "away_recent_form": away_form,
        }

    def _recent_form(self, sport, team_name, history, limit=5):
        team_key = normalize_key(team_name)
        matches = []

        for match in reversed(history):
            is_home = normalize_key(match["home_team"]) == team_key
            is_away = normalize_key(match["away_team"]) == team_key
            if not is_home and not is_away:
                continue

            team_score = match["home_score"] if is_home else match["away_score"]
            opponent_score = match["away_score"] if is_home else match["home_score"]
            if team_score > opponent_score:
                points = 1.0
            elif team_score == opponent_score:
                points = 0.5 if sport == "football" else 0.0
            else:
                points = 0.0

            matches.append(
                {
                    "date": match["date"],
                    "points": points,
                    "score_for": team_score,
                    "score_against": opponent_score,
                }
            )

            if len(matches) == limit:
                break

        if not matches:
            return {
                "games": 0,
                "score": 0.5,
                "average_scored": 0,
                "average_allowed": 0,
            }

        games = len(matches)
        return {
            "games": games,
            "score": round(sum(item["points"] for item in matches) / games, 4),
            "average_scored": round(
                sum(item["score_for"] for item in matches) / games,
                2,
            ),
            "average_allowed": round(
                sum(item["score_against"] for item in matches) / games,
                2,
            ),
        }

    def _tactical_analyst(self, sport, home, away):
        if sport == "football":
            home_matchup = float(home["attack"]) / float(away["defense"])
            away_matchup = float(away["attack"]) / float(home["defense"])
        else:
            league_defense = 114.0
            home_matchup = (
                float(home["offense"])
                * (league_defense / float(away["defense"]))
                * (float(home["pace"]) / 100)
            )
            away_matchup = (
                float(away["offense"])
                * (league_defense / float(home["defense"]))
                * (float(away["pace"]) / 100)
            )

        matchup_delta = (home_matchup - away_matchup) / max(
            abs(home_matchup) + abs(away_matchup),
            1,
        )
        probability = clamp(0.5 + matchup_delta, 0.35, 0.65)
        return {
            "home_win_no_draw": round(probability, 4),
            "home_matchup_score": round(home_matchup, 4),
            "away_matchup_score": round(away_matchup, 4),
        }

    def _sentiment_analyst(self):
        return {
            "probability_adjustment": 0.0,
            "sentiment_score": 0,
            "source": "neutral_no_live_news_feed",
        }

    def _probability_distribution(
        self,
        sport,
        home_win_no_draw,
        home_rating,
        away_rating,
        home_advantage,
    ):
        if sport == "football":
            rating_delta = abs((home_rating + home_advantage) - away_rating)
            draw_probability = clamp(0.29 - min(rating_delta, 350) / 350 * 0.11, 0.18, 0.29)
            non_draw = 1 - draw_probability
            home_win = home_win_no_draw * non_draw
            away_win = non_draw - home_win
            return {
                "home_win": home_win,
                "draw": draw_probability,
                "away_win": away_win,
            }

        return {
            "home_win": home_win_no_draw,
            "draw": 0.0,
            "away_win": 1 - home_win_no_draw,
        }

    def _risk_manager(
        self,
        home_win_probability,
        odds,
        home_games,
        away_games,
        home_rating,
        away_rating,
    ):
        market_probability = implied_probability(odds)
        edge = home_win_probability - market_probability
        sample_size = min(home_games, away_games)
        data_penalty = max(0, 1 - sample_size / 6) * 25
        coin_flip_penalty = (1 - min(abs(home_win_probability - 0.5) * 2, 1)) * 35
        negative_edge_penalty = 25 if edge <= 0 else 0
        rating_gap_penalty = max(0, 1 - abs(home_rating - away_rating) / 300) * 15

        score = clamp(
            data_penalty
            + coin_flip_penalty
            + negative_edge_penalty
            + rating_gap_penalty,
            0,
            100,
        )

        if score < 35:
            label = "LOW"
        elif score < 65:
            label = "MEDIUM"
        else:
            label = "HIGH"

        return {
            "score": round(score, 2),
            "label": label,
            "market_probability": round(market_probability, 4),
            "edge": round(edge, 4),
            "sample_size": sample_size,
        }

    def _confidence_level(self, home_win_probability, odds, risk_label):
        edge = home_win_probability - implied_probability(odds)
        if edge >= 0.08 and home_win_probability >= 0.58 and risk_label != "HIGH":
            return "A"
        if edge >= 0.03 or home_win_probability >= 0.55:
            return "B"
        return "C"

    def _estimate_score(self, sport, home, away, home_rating, away_rating):
        rating_adjustment = clamp((home_rating - away_rating) / 800, -0.2, 0.2)

        if sport == "football":
            home_xg = (
                1.35
                * (float(home["attack"]) / float(away["defense"]))
                * (1 + rating_adjustment)
                + 0.12
            )
            away_xg = (
                1.1
                * (float(away["attack"]) / float(home["defense"]))
                * (1 - rating_adjustment)
            )
            return f"{round(clamp(home_xg, 0, 5))}-{round(clamp(away_xg, 0, 5))}"

        league_defense = 114.0
        combined_pace = (float(home["pace"]) + float(away["pace"])) / 2
        home_points = (
            combined_pace
            * (float(home["offense"]) / 100)
            * (league_defense / float(away["defense"]))
            + 2.5
            + (rating_adjustment * 8)
        )
        away_points = (
            combined_pace
            * (float(away["offense"]) / 100)
            * (league_defense / float(home["defense"]))
            - (rating_adjustment * 8)
        )
        return f"{round(clamp(home_points, 70, 150))}-{round(clamp(away_points, 70, 150))}"
