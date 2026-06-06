from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    content: str
    source: str
    url: str
    published_at: Optional[datetime] = None
    crime_type: Optional[str] = None
    keywords: Optional[List[str]] = None
    risk_level: Optional[int] = None
    trustability_score: Optional[float] = None

class NewsResponse(NewsBase):
    id: int
    crawled_at: datetime
    is_analyzed: bool
    summary: Optional[str] = None
    actionable_insights: Optional[str] = None

    class Config:
        from_attributes = True

class NewsListResponse(BaseModel):
    data: List[NewsResponse]
    pagination: Optional[dict] = None
