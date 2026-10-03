from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Monitor(Base):
    """A URL that should be periodically checked for availability."""

    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    interval_minutes = Column(Integer, default=5, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Live status (updated after every check)
    last_checked_at = Column(DateTime(timezone=True), nullable=True)
    current_status = Column(String, default="unknown")  # "up" | "down" | "unknown"
    consecutive_failures = Column(Integer, default=0)

    # Alert state — prevents duplicate notifications
    alert_sent = Column(Boolean, default=False)

    # Notification targets (both optional)
    notify_email = Column(String, nullable=True)
    telegram_chat_id = Column(String, nullable=True)

    checks = relationship("Check", back_populates="monitor", cascade="all, delete-orphan")


class Check(Base):
    """A single health-check result for a Monitor."""

    __tablename__ = "checks"

    id = Column(Integer, primary_key=True, index=True)
    monitor_id = Column(Integer, ForeignKey("monitors.id"), nullable=False)
    checked_at = Column(DateTime(timezone=True), server_default=func.now())

    status_code = Column(Integer, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    is_up = Column(Boolean, nullable=False)
    error_message = Column(String, nullable=True)

    monitor = relationship("Monitor", back_populates="checks")
