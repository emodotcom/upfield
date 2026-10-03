from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, field_validator


# ─── Monitor ──────────────────────────────────────────────────────────────────

class MonitorCreate(BaseModel):
    name: str
    url: str
    interval_minutes: int = 5
    notify_email: Optional[str] = None
    telegram_chat_id: Optional[str] = None

    @field_validator("interval_minutes")
    @classmethod
    def interval_must_be_positive(cls, v: int) -> int:
        if v < 1:
            raise ValueError("interval_minutes must be at least 1")
        return v

    @field_validator("url")
    @classmethod
    def url_must_have_scheme(cls, v: str) -> str:
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")
        return v


class MonitorUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    interval_minutes: Optional[int] = None
    is_active: Optional[bool] = None
    notify_email: Optional[str] = None
    telegram_chat_id: Optional[str] = None


class MonitorResponse(BaseModel):
    id: int
    name: str
    url: str
    interval_minutes: int
    is_active: bool
    created_at: datetime
    last_checked_at: Optional[datetime]
    current_status: str
    consecutive_failures: int
    notify_email: Optional[str]
    telegram_chat_id: Optional[str]

    model_config = {"from_attributes": True}


# ─── Check ────────────────────────────────────────────────────────────────────

class CheckResponse(BaseModel):
    id: int
    monitor_id: int
    checked_at: datetime
    status_code: Optional[int]
    response_time_ms: Optional[float]
    is_up: bool
    error_message: Optional[str]

    model_config = {"from_attributes": True}


# ─── Stats ────────────────────────────────────────────────────────────────────

class MonitorStats(BaseModel):
    monitor_id: int
    period_days: int
    total_checks: int
    successful_checks: int
    uptime_percentage: float
    avg_response_time_ms: Optional[float]


# ─── Settings ─────────────────────────────────────────────────────────────────

class SettingsUpdate(BaseModel):
    telegram_bot_token: Optional[str] = None
    telegram_chat_id: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    alert_email: Optional[str] = None

class SettingsResponse(BaseModel):
    telegram_bot_token: Optional[str]
    telegram_chat_id: Optional[str]
    smtp_host: str
    smtp_port: int
    smtp_user: Optional[str]
    smtp_pass: Optional[str]
    alert_email: Optional[str]

    model_config = {"from_attributes": True}
