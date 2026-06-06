from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from datetime import datetime
from app.database import Base

class CrimeType(Base):
    __tablename__ = "crime_types"

    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), unique=True, nullable=False)
    keywords    = Column(JSON, nullable=True)
    description = Column(Text, nullable=True)

class CrawlLog(Base):
    __tablename__ = "crawl_logs"

    id            = Column(Integer, primary_key=True, index=True)
    source        = Column(String(100), nullable=False)
    status        = Column(String(20), nullable=False)
    article_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    crawled_at    = Column(DateTime, default=datetime.utcnow)
