from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class NotificationBase(BaseModel):
    title: str
    message: str
    crime_type: str
    news_id: Optional[int] = None

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    sent_at: datetime
    read_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SubscriptionResponse(BaseModel):
    id: int
    crime_type: str
    is_enabled: bool

    class Config:
        from_attributes = True
