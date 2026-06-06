from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import Config

engine = create_engine(Config.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

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

def init_db():
    Base.metadata.create_all(bind=engine)
