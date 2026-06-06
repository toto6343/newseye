from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.middleware.auth import get_current_active_user
from app.models.user import User
from app.models.notification import Notification, NotificationSubscription
from app.schemas.notification import NotificationResponse, SubscriptionResponse
from typing import List
from datetime import datetime

router = APIRouter(prefix="/notifications", tags=["notifications"])

@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    return db.query(Notification).filter(Notification.user_id == current_user.id) \
                                 .order_by(Notification.sent_at.desc()).all()

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Notification not found")
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    db.refresh(notification)
    return notification

@router.post("/subscribe/{crime_type}", response_model=SubscriptionResponse)
async def subscribe_to_crime_type(
    crime_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    sub = db.query(NotificationSubscription).filter(
        NotificationSubscription.user_id == current_user.id,
        NotificationSubscription.crime_type == crime_type
    ).first()
    
    if sub:
        sub.is_enabled = True
    else:
        sub = NotificationSubscription(
            user_id=current_user.id,
            crime_type=crime_type,
            is_enabled=True
        )
        db.add(sub)
    
    db.commit()
    db.refresh(sub)
    return sub

@router.delete("/unsubscribe/{crime_type}", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_from_crime_type(
    crime_type: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    sub = db.query(NotificationSubscription).filter(
        NotificationSubscription.user_id == current_user.id,
        NotificationSubscription.crime_type == crime_type
    ).first()
    
    if sub:
        sub.is_enabled = False
        db.commit()
    
    return None
