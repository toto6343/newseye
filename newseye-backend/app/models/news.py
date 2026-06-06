from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ARRAY, ForeignKey
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class News(Base):
    __tablename__ = "news"

    id               = Column(Integer, primary_key=True, index=True)
    title            = Column(String(500), nullable=False)
    content          = Column(Text, nullable=False)
    source           = Column(String(100), nullable=False)
    url              = Column(String(500), unique=True, nullable=False)
    published_at     = Column(DateTime, nullable=True)
    crawled_at       = Column(DateTime, default=datetime.utcnow)
    crime_type       = Column(String(50), nullable=True)
    keywords         = Column(JSON, nullable=True)
    entities         = Column(JSON, nullable=True)
    risk_level       = Column(Integer, nullable=True)
    trustability_score = Column(Float, nullable=True)
    is_analyzed      = Column(Boolean, default=False)
    summary          = Column(Text, nullable=True)
    actionable_insights = Column(Text, nullable=True)
    ioc_data         = Column(JSON, nullable=True)
    cve_ids          = Column(JSON, nullable=True)
    mitre_attack     = Column(JSON, nullable=True)
    campaign_id      = Column(String(100), nullable=True) # Used to group related incidents

    notifications = relationship("Notification", back_populates="news")
    feedbacks     = relationship("NewsFeedback", back_populates="news")

class NewsFeedback(Base):
    __tablename__ = "news_feedback"

    id               = Column(Integer, primary_key=True, index=True)
    news_id          = Column(Integer, ForeignKey("news.id"))
    user_id          = Column(Integer, ForeignKey("users.id"))
    is_accurate      = Column(Boolean, nullable=False) # True for thumbs up, False for thumbs down
    corrected_risk   = Column(Integer, nullable=True)
    user_comment     = Column(Text, nullable=True)
    created_at       = Column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="feedbacks")
