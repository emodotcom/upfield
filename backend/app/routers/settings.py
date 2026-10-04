from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AppSettings
from ..schemas import SettingsUpdate, SettingsResponse
from ..auth import get_current_user
from ..notifier import send_email

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

@router.post("/test-email", summary="Send a test email")
async def test_email(db: Session = Depends(get_db)):
    settings = get_or_create_settings(db)
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_pass or not settings.alert_email:
        raise HTTPException(status_code=400, detail="Missing SMTP settings. Please save settings and try again.")
    
    try:
        await send_email(
            to_email=settings.alert_email,
            subject="🚀 Upfield Notification Test",
            html_body="<h2>✅ Upfield Email Test Successful!</h2><p>Your email settings are correctly configured. When the system goes down, emails will arrive here.</p>",
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_user=settings.smtp_user,
            smtp_pass=settings.smtp_pass
        )
        return {"status": "success", "message": "Test email sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
