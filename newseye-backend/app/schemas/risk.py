from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class RiskScoreResponse(BaseModel):
    risk_score: float
    risk_level: str
    news_risk: float
    profile_risk: float
    updated_at: str
    message: Optional[str] = None

class ThreatSummaryResponse(BaseModel):
    summary: str
    top_threats: List[str]
    last_updated: datetime

class RecommendationResponse(BaseModel):
    title: str
    description: str
    action_url: Optional[str] = None
