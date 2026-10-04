from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import pyotp

from ..database import get_db
from ..models import User
from ..auth import verify_password, get_password_hash, create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

class Verify2FARequest(BaseModel):
    username: str
    code: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

@router.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Geçersiz kullanıcı adı veya şifre")
    
    if user.is_totp_enabled:
        access_token = create_access_token(data={"sub": user.username, "partial": True})
        return {"access_token": access_token, "require_2fa": True}
    
    access_token = create_access_token(data={"sub": user.username, "partial": False})
    return {"access_token": access_token, "require_2fa": False}

@router.post("/verify-2fa")
def verify_2fa(request: Verify2FARequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not user.is_totp_enabled:
        raise HTTPException(status_code=400, detail="2FA aktif değil")
    
    totp = pyotp.TOTP(user.totp_secret)
    if not totp.verify(request.code):
        raise HTTPException(status_code=401, detail="Geçersiz 2FA kodu")
        
    access_token = create_access_token(data={"sub": user.username, "partial": False})
    return {"access_token": access_token}

@router.get("/setup-2fa")
def setup_2fa(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.is_totp_enabled:
        raise HTTPException(status_code=400, detail="2FA zaten aktif")
        
    if not current_user.totp_secret:
        current_user.totp_secret = pyotp.random_base32()
        db.commit()
        
    totp = pyotp.TOTP(current_user.totp_secret)
    uri = totp.provisioning_uri(name=current_user.username, issuer_name="Upfield")
    return {"secret": current_user.totp_secret, "uri": uri}

@router.post("/enable-2fa")
def enable_2fa(code: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_code = code.get("code")
    if not current_user.totp_secret:
        raise HTTPException(status_code=400, detail="Önce kurulum yapmalısınız")
        
    totp = pyotp.TOTP(current_user.totp_secret)
    if not totp.verify(user_code):
        raise HTTPException(status_code=400, detail="Geçersiz kod")
        
    current_user.is_totp_enabled = True
    db.commit()
    return {"status": "success", "message": "2FA başarıyla aktifleştirildi"}

@router.put("/change-password")
def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mevcut şifre yanlış")
    
    current_user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    return {"status": "success", "message": "Şifre başarıyla güncellendi"}
