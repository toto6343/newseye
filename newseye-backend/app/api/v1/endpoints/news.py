from fastapi import APIRouter, HTTPException, status, Depends, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db, SessionLocal
from app.models.news import News, NewsFeedback
from app.schemas.news import NewsResponse, NewsListResponse, NewsBase
from app.middleware.auth import get_current_active_user
from typing import List
from app.services.llm_service import llm_service
from app.services.ioc_service import ioc_service
from app.services.rag_service import rag_service
from app.services.graph_service import graph_service
from app.api.v1.endpoints.websockets import manager
from app.models.user import User, RiskProfile
from app.models.notification import Notification
import asyncio
import re
import difflib
from datetime import datetime, timedelta
from pydantic import BaseModel

class FeedbackCreate(BaseModel):
    is_accurate: bool
    corrected_risk: int = None
    user_comment: str = None

router = APIRouter(prefix="/news", tags=["news"])
def extract_cves(text: str) -> list:
    """Extract CVE IDs from text."""
    if not text:
        return []
    return list(set(re.findall(r'CVE-\d{4}-\d{4,}', text)))

async def process_news_article(news_id: int):
    # This runs in background
    db = SessionLocal()
    try:
        news = db.query(News).filter(News.id == news_id).first()
        if not news:
            return
        
        # 1. Analyze with LLM First (Phase 1)
        # Move LLM analysis up so we can get a base risk score before OSINT calls
        analysis_result = await llm_service.analyze_article(news.content)
        news.summary = analysis_result.get("summary")
        news.actionable_insights = analysis_result.get("actionable_insights")
        news.mitre_attack = analysis_result.get("mitre_attack")
        news.is_analyzed = True

        # Initial risk estimation based on LLM/Keywords
        base_risk = news.risk_level or 5
        
        # 2. IoC & CVE Extraction + Selective OSINT (API Saving Mode)
        iocs = ioc_service.extract_iocs(news.content)
        cve_ids = extract_cves(news.content)
        news.cve_ids = cve_ids

        # Only call expensive OSINT APIs if risk is high enough OR contains CVEs
        if base_risk >= settings.OSINT_MIN_RISK_THRESHOLD or cve_ids:
            print(f"High risk ({base_risk}) or CVE detected. Performing OSINT enrichment...")
            intel_results = ioc_service.check_threat_intel(iocs)
            news.ioc_data = intel_results
            
            # Update risk level if malicious IoCs found
            if intel_results.get("malicious_count", 0) > 0:
                news.risk_level = max(base_risk, 8) # Upgrade to high risk
        else:
            print(f"Risk ({base_risk}) too low for OSINT. Skipping to save API quota.")
            news.ioc_data = {"note": "OSINT skipped (API Saving Mode)", "details": []}
        
        # 1.5 Threat Correlation (Campaign Grouping)
        
        # 3. Add to RAG system (Vector DB)
        await rag_service.add_news(
            news_id=news.id,
            title=news.title,
            content=news.content,
            metadata={
                "source": news.source,
                "url": news.url,
                "published_at": str(news.published_at) if news.published_at else "",
                "crime_type": news.crime_type or "unknown"
            }
        )

        # 3.5 Add to Knowledge Graph (Neo4j)
        try:
            graph_service.add_news_to_graph(
                news_id=news.id,
                title=news.title,
                crime_type=news.crime_type,
                entities=news.entities or {},
                source=news.source
            )
        except Exception as ge:
            print(f"Graph update failed: {ge}")
        
        db.commit()
        db.refresh(news)

        # 4. Notification & WebSocket Broadcast (Phase 2 & 4)
        is_high_risk = (news.risk_level or 0) >= 7
        matched_users_assets = {} # {user_id: [asset1, asset2]}
        
        profiles = db.query(RiskProfile).filter(RiskProfile.notification_enabled == True).all()
        content_to_check = f"{news.title} {news.content} {' '.join(news.keywords or [])} {' '.join(news.entities or [])}".lower()
        
        for profile in profiles:
            user_matched_assets = []
            
            # Check assets match (Improved logic for Phase 4)
            if profile.assets:
                for asset in profile.assets:
                    if asset.strip() and re.search(rf'\b{re.escape(asset.lower())}\b', content_to_check):
                        user_matched_assets.append(asset)
            
            # Check crime type match
            type_match = news.crime_type in (profile.interested_crime_types or [])
            
            if user_matched_assets or type_match:
                matched_users_assets[profile.user_id] = user_matched_assets
                
                # Create Notification record
                msg = f"A new high-risk threat has been detected: {news.title}"
                if user_matched_assets:
                    msg = f"🚨 CRITICAL: Your asset(s) [{', '.join(user_matched_assets)}] are potentially affected by a new threat: {news.title}"
                
                notification = Notification(
                    user_id=profile.user_id,
                    news_id=news.id,
                    title=f"NewsEye Alert: {news.title}",
                    message=msg,
                    crime_type=news.crime_type
                )
                db.add(notification)
        
        db.commit()

        # Broadcast via WebSocket (Phase 4: Include matched assets info)
        # Note: In a multi-user system, we'd send targeted WS messages. 
        # For this MVP, we broadcast the general alert but include 'is_asset_targeted' hint.
        await manager.broadcast({
            "type": "NEW_THREAT_ALERT",
            "news_id": news.id,
            "title": news.title,
            "risk_level": news.risk_level,
            "crime_type": news.crime_type,
            "has_cves": len(news.cve_ids) > 0 if news.cve_ids else False,
            "targeted_assets_found": list(set([a for assets in matched_users_assets.values() for a in assets]))
        })

    except Exception as e:
        print(f"Error processing news article: {e}")
    finally:
        db.close()

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_news(
    news_data: NewsBase,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Check exact URL match
    existing_url = db.query(News).filter(News.url == news_data.url).first()
    if existing_url:
        return {"message": "News already exists (Exact URL)", "id": existing_url.id}
    
    # Deduplication check: Similarity on title within the last 48 hours
    two_days_ago = datetime.utcnow() - timedelta(days=2)
    recent_news = db.query(News).filter(News.crawled_at >= two_days_ago).all()
    
    for rn in recent_news:
        similarity = difflib.SequenceMatcher(None, rn.title.lower(), news_data.title.lower()).ratio()
        if similarity > 0.85: # If title is 85% similar, consider it duplicate
            return {"message": f"News skipped (Similar title found: {rn.title})", "id": rn.id}

    # Save to db
    db_news = News(**news_data.dict())
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    
    # Trigger background processing
    background_tasks.add_task(process_news_article, db_news.id)
    
    return {"message": "News accepted for processing", "id": db_news.id}

@router.get("/latest", response_model=NewsListResponse)
async def get_latest_news(
    count: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
    # current_user=Depends(get_current_active_user),
):
    news_list = db.query(News).filter(News.is_analyzed == True) \
                              .order_by(desc(News.crawled_at)).limit(count).all()
    return {"data": news_list}

@router.get("", response_model=NewsListResponse)
async def get_news(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    crime_type: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    query = db.query(News).filter(News.is_analyzed == True)
    if crime_type:
        query = query.filter(News.crime_type == crime_type)
    if search:
        query = query.filter(
            (News.title.ilike(f"%{search}%")) | (News.content.ilike(f"%{search}%"))
        )
    total = query.count()
    items = query.order_by(desc(News.crawled_at)).offset((page - 1) * limit).limit(limit).all()

    return {
        "data": items,
        "pagination": {
            "page": page, "limit": limit, "total": total,
            "pages": (total + limit - 1) // limit,
            "has_more": (page * limit) < total,
        },
    }

@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_detail(
    news_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
):
    news = db.query(News).filter(News.id == news_id).first()
    if not news:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="News not found")
    return news
