from sqlalchemy.orm import Session
from app.models.user import User, RiskProfile
from app.schemas.user import UserCreate, UserUpdate, RiskProfileUpdate
from app.core.security import get_password_hash

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user_create: UserCreate) -> User:
        db_user = User(
            email=user_create.email,
            username=user_create.username,
            password_hash=get_password_hash(user_create.password),
            age_group=user_create.age_group,
            occupation=user_create.occupation,
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_risk_profile(self, user_id: int, profile_update: RiskProfileUpdate) -> RiskProfile:
        profile = self.db.query(RiskProfile).filter(RiskProfile.user_id == user_id).first()
        if not profile:
            return None
        
        update_data = profile_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(profile, field, value)
        
        self.db.commit()
        self.db.refresh(profile)
        return profile
