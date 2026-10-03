import asyncio
import logging

import httpx
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .config import settings

logger = logging.getLogger(__name__)

# ─── Telegram ─────────────────────────────────────────────────────────────────

async def send_telegram(chat_id: str, message: str) -> None:
    """Send a message via Telegram Bot API."""
    if not settings.telegram_bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(url, json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML",
            })
    except Exception as exc:  # noqa: BLE001
        logger.error("Telegram notification failed: %s", exc)


# ─── Email ────────────────────────────────────────────────────────────────────

async def send_email(to_email: str, subject: str, html_body: str) -> None:
    """Send an HTML email via SMTP (TLS)."""
    if not settings.smtp_user or not settings.smtp_pass or not to_email:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.smtp_user
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_pass,
            start_tls=True,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Email notification failed: %s", exc)


# ─── Dispatcher ───────────────────────────────────────────────────────────────

async def notify(monitor, event: str) -> None:
    """
    Send DOWN or RECOVERY notifications for *monitor*.

    event: "down" | "recovery"
    """
    if event == "down":
        tg_msg = (
            f"🔴 <b>{monitor.name}</b> is <b>DOWN</b>!\n"
            f"🔗 {monitor.url}\n"
            f"⚠️ Consecutive failures: {monitor.consecutive_failures}"
        )
        email_subject = f"🔴 [{monitor.name}] is DOWN"
        email_body = f"""
        <h2>🔴 {monitor.name} is DOWN</h2>
        <p><b>URL:</b> <a href="{monitor.url}">{monitor.url}</a></p>
        <p><b>Consecutive failures:</b> {monitor.consecutive_failures}</p>
        <hr>
        <small>Upfield Health Checker</small>
        """
    elif event == "recovery":
        tg_msg = (
            f"✅ <b>{monitor.name}</b> is back <b>UP</b>!\n"
            f"🔗 {monitor.url}"
        )
        email_subject = f"✅ [{monitor.name}] recovered"
        email_body = f"""
        <h2>✅ {monitor.name} is back UP</h2>
        <p><b>URL:</b> <a href="{monitor.url}">{monitor.url}</a></p>
        <hr>
        <small>Upfield Health Checker</small>
        """
    else:
        return

    tasks = []
    if monitor.telegram_chat_id:
        tasks.append(send_telegram(monitor.telegram_chat_id, tg_msg))
    if monitor.notify_email:
        tasks.append(send_email(monitor.notify_email, email_subject, email_body))

    if tasks:
        await asyncio.gather(*tasks)
