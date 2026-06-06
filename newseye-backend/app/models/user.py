from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id             = Column(Integer, primary_key=True, index=True)
    email          = Column(String(255), unique=True, index=True, nullable=False)
    username       = Column(String(100))
    password_hash  = Column(String(255), nullable=False)
    age_group      = Column(String(20))
    occupation     = Column(String(100))
    is_active      = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    created_at     = Column(DateTime, default=datetime.utcnow)
    updated_at     = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login     = Column(DateTime, nullable=True)

    risk_profile  = relationship("RiskProfile", back_populates="user", uselist=False)
    notifications = relationship("Notification", back_populates="user")


class RiskProfile(Base):
    __tablename__ = "risk_profiles"

    id                     = Column(Integer, primary_key=True, index=True)
    user_id                = Column(Integer, ForeignKey("users.id"), unique=True)
    online_activity_level  = Column(String(20), default="medium")
    base_risk_score        = Column(Float, default=5.0)
    interested_crime_types = Column(JSON, default=["phishing", "ransomware"])
    assets                 = Column(JSON, default=[])
    notification_enabled   = Column(Boolean, default=True)
    last_updated           = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="risk_profile")
