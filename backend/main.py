from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.models.predictor import PredictionEngine, PredictionError
from backend.schemas.prediction import PredictionRequest, PredictionResponse
from backend.services.data_service import DataError, list_teams, validate_sport

app = FastAPI()
engine = PredictionEngine()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "status": "AI Sports System Running",
        "mode": "deterministic_prediction_engine",
    }

@app.get("/teams")
def teams(sport: str = "football"):
    try:
        sport = validate_sport(sport)
        return {"sport": sport, "teams": list_teams(sport)}
    except DataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/predict", response_model=PredictionResponse)
def predict(payload: PredictionRequest):
    home_team = payload.resolved_home_team()
    away_team = payload.resolved_away_team()
    if not home_team or not away_team:
        raise HTTPException(
            status_code=422,
            detail="home_team and away_team are required.",
        )

    try:
        return engine.predict(
            sport=payload.sport,
            home_team=home_team,
            away_team=away_team,
            odds=payload.odds,
        )
    except PredictionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/predict", response_model=PredictionResponse)
def predict_from_query(
    home: str,
    away: str,
    odds: float,
    sport: str = "football",
):
    try:
        return engine.predict(
            sport=sport,
            home_team=home,
            away_team=away,
            odds=odds,
        )
    except PredictionError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
