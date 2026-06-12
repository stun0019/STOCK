from fastapi.testclient import TestClient

from backend.main import app
from backend.models.predictor import PredictionEngine


def test_prediction_is_deterministic():
    engine = PredictionEngine()

    first = engine.predict("football", "Arsenal", "Liverpool", 2.2)
    second = engine.predict("football", "Arsenal", "Liverpool", 2.2)

    assert first == second


def test_ev_formula_controls_recommendation():
    engine = PredictionEngine()

    prediction = engine.predict("basketball", "Boston Celtics", "Denver Nuggets", 1.82)
    probability = prediction["home_win_probability"]
    expected_ev = round((probability * 1.82) - 1, 4)

    assert prediction["ev"] == expected_ev
    assert prediction["recommendation"] == ("BET" if expected_ev > 0 else "NO BET")


def test_post_predict_contract():
    client = TestClient(app)

    response = client.post(
        "/predict",
        json={
            "sport": "football",
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "odds": 2.05,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert set(
        [
            "match",
            "home_win_probability",
            "draw_probability",
            "away_win_probability",
            "predicted_score",
            "ev",
            "risk",
            "confidence",
            "recommendation",
        ]
    ).issubset(body.keys())
    assert round(
        body["home_win_probability"]
        + body["draw_probability"]
        + body["away_win_probability"],
        4,
    ) == 1.0
    assert body["trace"]["agents"]["decision_engine"]["ev_formula"] == (
        "(probability * odds) - 1"
    )
