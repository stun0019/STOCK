
import csv
import io
import json
from functools import lru_cache
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
VALID_SPORTS = {"football", "basketball"}


class DataError(ValueError):
    """Raised when local sports data is missing or invalid."""


def normalize_key(value):
    return " ".join(value.strip().lower().split())


def validate_sport(sport):
    normalized = normalize_key(sport)
    if normalized not in VALID_SPORTS:
        raise DataError(
            "Unsupported sport. Expected one of: "
            + ", ".join(sorted(VALID_SPORTS))
        )
    return normalized


@lru_cache(maxsize=1)
def load_teams():
    path = DATA_DIR / "teams.json"
    with path.open("r", encoding="utf-8") as handle:
        teams = json.load(handle)

    if not isinstance(teams, list):
        raise DataError("teams.json must contain a list of teams.")

    indexed = {sport: {} for sport in VALID_SPORTS}
    for team in teams:
        sport = validate_sport(str(team.get("sport", "")))
        name = str(team.get("name", "")).strip()
        if not name:
            raise DataError("Every team must have a name.")
        indexed[sport][normalize_key(name)] = dict(team)

    return indexed


@lru_cache(maxsize=None)
def load_history(sport):
    sport = validate_sport(sport)
    path = DATA_DIR / "history.csv"
    rows = []

    with path.open("r", encoding="utf-8", newline="") as handle:
        non_empty_lines = [line for line in handle if line.strip()]
        reader = csv.DictReader(io.StringIO("".join(non_empty_lines)))
        required = {
            "date",
            "sport",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
        }
        if not required.issubset(set(reader.fieldnames or [])):
            raise DataError("history.csv is missing required columns.")

        for row in reader:
            if validate_sport(row["sport"]) != sport:
                continue
            rows.append(
                {
                    "date": row["date"],
                    "sport": sport,
                    "home_team": row["home_team"].strip(),
                    "away_team": row["away_team"].strip(),
                    "home_score": int(row["home_score"]),
                    "away_score": int(row["away_score"]),
                }
            )

    rows.sort(key=lambda item: item["date"])
    return rows


def get_team(sport, team_name):
    sport = validate_sport(sport)
    team_key = normalize_key(team_name)
    teams = load_teams()[sport]

    if team_key not in teams:
        raise DataError(
            f"Unknown {sport} team '{team_name}'. Available teams: "
            + ", ".join(sorted(team["name"] for team in teams.values()))
        )

    return teams[team_key]


def list_teams(sport):
    sport = validate_sport(sport)
    return sorted(team["name"] for team in load_teams()[sport].values())
