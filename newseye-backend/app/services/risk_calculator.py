from sqlalchemy.orm import Session, joinedload
from app.models.user import User, RiskProfile
from app.models.news import News
from datetime import datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)

class RiskCalculator:
    CRIME_TYPE_WEIGHTS = {
        'phishing': 0.30, 
        'ransomware': 0.50, # High weight for ransomware
        'hacking': 0.40,  
        'fraud': 0.25, 
        'malware': 0.35,
        'zero-day': 0.60
    }

    def __init__(self, db: Session):
        self.db = db

    def calculate_user_risk_score(self, user_id: int) -> dict:
        user = self.db.query(User).options(
            joinedload(User.risk_profile)
        ).filter(User.id == user_id).first()

        if not user or not user.risk_profile:
            return {"risk_score": 5.0, "risk_level": "medium", "message": "Unable to calculate risk"}

        profile = user.risk_profile
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_news = self.db.query(News).filter(
            News.crawled_at > seven_days_ago,
            News.is_analyzed == True,
        ).all()

        news_risk    = self._calculate_news_based_risk(recent_news, profile.interested_crime_types, profile.assets)
        profile_risk = self._calculate_profile_based_risk(user, profile)

        # News risk has higher weight in the final score
        final_risk = round(min(10.0, max(1.0, news_risk * 0.7 + profile_risk * 0.3)), 1)

        return {
            "risk_score":  final_risk,
            "risk_level":  self._get_risk_level(final_risk),
            "news_risk":   round(news_risk, 1),
            "profile_risk": round(profile_risk, 1),
            "updated_at":  datetime.utcnow().isoformat(),
        }

    def _calculate_profile_based_risk(self, user: User, profile: RiskProfile) -> float:
        risk = profile.base_risk_score
        activity_adjustments = {"low": -1.0, "medium": 0.0, "high": 1.5}
        risk += activity_adjustments.get(profile.online_activity_level, 0)

        if user.occupation and any(
            kw in user.occupation.lower()
            for kw in ['it', 'developer', 'tech', 'engineer', 'admin', 'security']
        ):
            risk += 1.0 # Professionals are more targeted

        return min(10.0, max(1.0, risk))

    def _calculate_news_based_risk(self, news_list, interested_types, assets) -> float:
        if not news_list:
            return 5.0
        
        assets_lower = [a.lower() for a in (assets or [])]
        
        total = 0.0
        for n in news_list:
            # Use specific news risk level if available (1-10)
            base_score = n.risk_level if n.risk_level else (self.CRIME_TYPE_WEIGHTS.get(n.crime_type or 'other', 0.2) * 10)
            
            interest_factor = 1.5 if n.crime_type in (interested_types or []) else 1.0
            
            asset_factor = 1.0
            # Broad content check including extracted keywords/entities
            keywords_text = " ".join(n.keywords) if n.keywords else ""
            entities_text = " ".join(n.entities) if n.entities else ""
            content_to_check = f"{n.title or ''} {n.content or ''} {keywords_text} {entities_text}".lower()
            
            for asset in assets_lower:
                if not asset.strip(): continue
                # Match as whole word to avoid partial matches (e.g., 'java' matching 'javascript' incorrectly)
                if re.search(rf'\b{re.escape(asset)}\b', content_to_check):
                    asset_factor = 3.0 # High relevance
                    break
                
            total += base_score * interest_factor * asset_factor
            
        return min(10.0, max(1.0, total / len(news_list)))

    def _get_risk_level(self, score: float) -> str:
        if score < 3.5: return 'low'
        if score < 7.5: return 'medium'
        return 'high'
