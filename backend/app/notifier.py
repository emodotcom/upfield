import asyncio
import logging

import httpx
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from .database import SessionLocal
from .models import AppSettings

logger = logging.getLogger(__name__)

def get_settings():
    with SessionLocal() as db:
        return db.query(AppSettings).first()

# ─── Telegram ─────────────────────────────────────────────────────────────────

async def send_telegram(chat_id: str, message: str, bot_token: str) -> None:
    """Send a message via Telegram Bot API."""
    if not bot_token or not chat_id:
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
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

async def send_email(to_email: str, subject: str, html_body: str, smtp_host: str, smtp_port: int, smtp_user: str, smtp_pass: str) -> None:
    """Send an HTML email via SMTP (TLS)."""
    if not smtp_user or not smtp_pass or not to_email:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Upfield (No Reply) <{smtp_user}>"
    msg["Reply-To"] = "noreply@upfield.local"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        # Port 465 requires implicit TLS (use_tls=True)
        # Port 587 requires explicit TLS (start_tls=True)
        use_tls = (smtp_port == 465)
        start_tls = (smtp_port != 465)

        await aiosmtplib.send(
            msg,
            hostname=smtp_host or "smtp.gmail.com",
            port=smtp_port or 587,
            username=smtp_user,
            password=smtp_pass,
            use_tls=use_tls,
            start_tls=start_tls,
        )
    except Exception as exc:  # noqa: BLE001
        logger.error("Email notification failed: %s", exc)
        raise exc # Hata yutulmasın, arayüze dönsün


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

    app_settings = get_settings()
    if not app_settings:
        return

    tasks = []
    
    # Send Telegram
    target_telegram_chat = monitor.telegram_chat_id or app_settings.telegram_chat_id
    if target_telegram_chat and app_settings.telegram_bot_token:
        tasks.append(send_telegram(target_telegram_chat, tg_msg, app_settings.telegram_bot_token))
        
    # Send Email
    target_email = monitor.notify_email or app_settings.alert_email
    if target_email and app_settings.smtp_user and app_settings.smtp_pass:
        tasks.append(send_email(
            target_email, 
            email_subject, 
            email_body, 
            app_settings.smtp_host, 
            app_settings.smtp_port, 
            app_settings.smtp_user, 
            app_settings.smtp_pass
        ))

    if tasks:
        await asyncio.gather(*tasks)
