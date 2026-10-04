from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AppSettings
from ..schemas import SettingsUpdate, SettingsResponse
from ..auth import get_current_user

router = APIRouter(
    prefix="/settings", 
    tags=["Settings"],
    dependencies=[Depends(get_current_user)]
)

def get_or_create_settings(db: Session) -> AppSettings:
    settings = db.query(AppSettings).first()
    if not settings:
        settings = AppSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.get("/", response_model=SettingsResponse, summary="Get global settings")
def get_settings(db: Session = Depends(get_db)):
    return get_or_create_settings(db)

@router.put("/", response_model=SettingsResponse, summary="Update global settings")
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)
    
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
        
    db.commit()
    db.refresh(settings)
    return settings
