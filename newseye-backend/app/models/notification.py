from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    news_id     = Column(Integer, ForeignKey("news.id"), nullable=True)
    title       = Column(String(200))
    message     = Column(Text)
    crime_type  = Column(String(50))
    is_read     = Column(Boolean, default=False)
    sent_at     = Column(DateTime, default=datetime.utcnow)
    read_at     = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="notifications")
    news = relationship("News", back_populates="notifications")

class NotificationSubscription(Base):
    __tablename__ = "notification_subscriptions"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    crime_type  = Column(String(50))
    is_enabled  = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
