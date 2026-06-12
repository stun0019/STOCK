from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    sport: str = Field(default="football")
    home_team: Optional[str] = Field(default=None)
    away_team: Optional[str] = Field(default=None)
    home: Optional[str] = Field(default=None)
    away: Optional[str] = Field(default=None)
    odds: float

    def resolved_home_team(self):
        return self.home_team or self.home

    def resolved_away_team(self):
        return self.away_team or self.away


class PredictionResponse(BaseModel):
    match: str
    home_win_probability: float
    draw_probability: float
    away_win_probability: float
    predicted_score: str
    ev: float
    risk: str
    confidence: str
    recommendation: str
    trace: Dict[str, Any]
