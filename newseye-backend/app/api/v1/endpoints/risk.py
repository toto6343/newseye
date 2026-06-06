from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.services.risk_calculator import RiskCalculator
from app.schemas.risk import RiskScoreResponse, ThreatSummaryResponse, RecommendationResponse
from datetime import datetime
from typing import List

router = APIRouter(prefix="/risk", tags=["risk"])

@router.get("/my-risk-level", response_model=RiskScoreResponse)
async def get_my_risk_level(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    calculator = RiskCalculator(db)
    return calculator.calculate_user_risk_score(current_user.id)

@router.get("/threat-summary", response_model=ThreatSummaryResponse)
async def get_threat_summary(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Dummy summary for MVP
    return {
        "summary": "최근 피싱 및 랜섬웨어 공격이 증가하고 있습니다. 주의가 필요합니다.",
        "top_threats": ["phishing", "ransomware"],
        "last_updated": datetime.utcnow()
    }

@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    # Dummy recommendations for MVP
    return [
        {
            "title": "2단계 인증 활성화",
            "description": "중요 계정에 대해 2단계 인증을 활성화하여 보안을 강화하세요.",
            "action_url": "https://example.com/2fa"
        },
        {
            "title": "의심스러운 메일 주의",
            "description": "알 수 없는 발신자의 링크나 첨부파일을 클릭하지 마세요.",
            "action_url": None
        }
    ]
