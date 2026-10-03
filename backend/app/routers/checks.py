from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Check
from ..schemas import CheckResponse, MonitorStats

router = APIRouter(prefix="/monitors", tags=["Checks & Stats"])


@router.get(
    "/{monitor_id}/checks",
    response_model=List[CheckResponse],
    summary="Get recent check history",
)
def get_checks(
    monitor_id: int,
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    db: Session = Depends(get_db),
):
    return (
        db.query(Check)
        .filter(Check.monitor_id == monitor_id)
        .order_by(Check.checked_at.desc())
        .limit(limit)
        .all()
    )


@router.get(
    "/{monitor_id}/stats",
    response_model=MonitorStats,
    summary="Get uptime stats for a time window",
)
def get_stats(
    monitor_id: int,
    days: int = Query(1, ge=1, le=90, description="Look-back window in days"),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    checks = (
        db.query(Check)
        .filter(Check.monitor_id == monitor_id, Check.checked_at >= since)
        .all()
    )

    total = len(checks)
    successful = sum(1 for c in checks if c.is_up)
    uptime_pct = (successful / total * 100) if total > 0 else 0.0

    response_times = [c.response_time_ms for c in checks if c.response_time_ms is not None]
    avg_rt = sum(response_times) / len(response_times) if response_times else None

    return MonitorStats(
        monitor_id=monitor_id,
        period_days=days,
        total_checks=total,
        successful_checks=successful,
        uptime_percentage=round(uptime_pct, 2),
        avg_response_time_ms=round(avg_rt, 2) if avg_rt is not None else None,
    )
