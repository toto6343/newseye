from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User, RiskProfile
from app.schemas.user import UserResponse, UserUpdate, RiskProfileUpdate, RiskProfileResponse
from app.services.user_service import UserService
from app.middleware.auth import get_current_active_user
import json

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/me/risk-profile/sbom")
async def upload_sbom(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Parses a package.json (SBoM) to automatically extract dependencies and add them to user's assets.
    """
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="Only JSON SBoM files (like package.json) are supported.")
        
    try:
        content = await file.read()
        data = json.loads(content)
        
        # Extract dependencies
        dependencies = data.get("dependencies", {})
        dev_dependencies = data.get("devDependencies", {})
        
        extracted_assets = list(set(list(dependencies.keys()) + list(dev_dependencies.keys())))
        
        if not extracted_assets:
            return {"message": "No dependencies found to add as assets.", "added": 0}
            
        profile = db.query(RiskProfile).filter(RiskProfile.user_id == current_user.id).first()
        if not profile:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Risk profile not found")
            
        current_assets = set(profile.assets or [])
        new_assets = list(current_assets.union(set(extracted_assets)))
        
        profile.assets = new_assets
        db.commit()
        
        return {
            "message": "SBoM processed successfully.",
            "added_assets": len(extracted_assets),
            "total_assets": len(new_assets)
        }
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing SBoM: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    updated = user_service.update_user(current_user.id, user_update)
    if not updated:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated

@router.get("/me/risk-profile", response_model=RiskProfileResponse)
async def get_risk_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    profile = db.query(RiskProfile).filter(RiskProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Risk profile not found")
    return profile

@router.put("/me/risk-profile", response_model=RiskProfileResponse)
async def update_risk_profile(
    profile_update: RiskProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    user_service = UserService(db)
    updated = user_service.update_risk_profile(current_user.id, profile_update)
    if not updated:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Risk profile not found")
    return updated
