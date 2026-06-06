from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    age_group: Optional[str] = None
    occupation: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    age_group: Optional[str] = None
    occupation: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RiskProfileBase(BaseModel):
    online_activity_level: str = "medium"
    interested_crime_types: List[str] = ["phishing", "ransomware"]
    assets: List[str] = []
    notification_enabled: bool = True

class RiskProfileUpdate(BaseModel):
    online_activity_level: Optional[str] = None
    interested_crime_types: Optional[List[str]] = None
    assets: Optional[List[str]] = None
    notification_enabled: Optional[bool] = None

class RiskProfileResponse(RiskProfileBase):
    id: int
    user_id: int
    base_risk_score: float
    last_updated: datetime

    class Config:
        from_attributes = True
