"""
Background scheduler — runs a continuous async loop that:
  1. Every CHECK_LOOP_INTERVAL_SECONDS wakes up
  2. Fetches all active monitors from DB
  3. Runs health checks for any monitor whose next check is due
  4. Saves results and sends notifications when needed
"""

import asyncio
import logging
from datetime import datetime, timezone

from .checker import check_url
from .config import settings
from .database import SessionLocal
from .models import Check, Monitor
from .notifier import notify

logger = logging.getLogger(__name__)

# How many consecutive failures before an alert is sent
FAILURE_THRESHOLD = 3


async def run_check(monitor_id: int) -> None:
    """Perform one health check for the given monitor ID and persist the result."""
    db = SessionLocal()
    try:
        monitor = db.query(Monitor).filter(Monitor.id == monitor_id).first()
        if not monitor or not monitor.is_active:
            return

        result = await check_url(monitor.url)

        # Persist check record
        check = Check(
            monitor_id=monitor.id,
            status_code=result["status_code"],
            response_time_ms=result["response_time_ms"],
            is_up=result["is_up"],
            error_message=result["error_message"],
        )
        db.add(check)

        # Update monitor live status
        monitor.last_checked_at = datetime.now(timezone.utc)

        if result["is_up"]:
            was_alerting = monitor.consecutive_failures >= FAILURE_THRESHOLD and monitor.alert_sent
            monitor.consecutive_failures = 0
            monitor.current_status = "up"

            # Send recovery notification once
            if was_alerting:
                await notify(monitor, "recovery")
                monitor.alert_sent = False
        else:
            monitor.consecutive_failures += 1
            monitor.current_status = "down"
            logger.warning("Monitor %s (%s) FAILED — consecutive: %d", monitor.name, monitor.url, monitor.consecutive_failures)

            # Alert after N consecutive failures, but only once per incident
            if monitor.consecutive_failures >= FAILURE_THRESHOLD and not monitor.alert_sent:
                await notify(monitor, "down")
                monitor.alert_sent = True

        db.commit()
        logger.debug(
            "Checked %s → %s (%sms)",
            monitor.url,
            "UP" if result["is_up"] else "DOWN",
            result["response_time_ms"],
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Error running check for monitor %d: %s", monitor_id, exc)
        db.rollback()
    finally:
        db.close()


async def monitor_loop() -> None:
    """
    Main background loop.
    Wakes up every CHECK_LOOP_INTERVAL_SECONDS and dispatches due checks concurrently.
    """
    logger.info("Monitor loop started (interval: %ds)", settings.check_loop_interval_seconds)

    while True:
        db = SessionLocal()
        try:
            now = datetime.now(timezone.utc)
            monitors = db.query(Monitor).filter(Monitor.is_active == True).all()  # noqa: E712

            due = []
            for m in monitors:
                if m.last_checked_at is None:
                    due.append(m.id)
                else:
                    # Make last_checked_at timezone-aware if needed (SQLite stores naive datetimes)
                    last = m.last_checked_at
                    if last.tzinfo is None:
                        last = last.replace(tzinfo=timezone.utc)
                    elapsed_minutes = (now - last).total_seconds() / 60
                    if elapsed_minutes >= m.interval_minutes:
                        due.append(m.id)

            if due:
                logger.info("Dispatching %d check(s)…", len(due))
                await asyncio.gather(*[run_check(mid) for mid in due])
        except Exception as exc:  # noqa: BLE001
            logger.error("Monitor loop error: %s", exc)
        finally:
            db.close()

        await asyncio.sleep(settings.check_loop_interval_seconds)
