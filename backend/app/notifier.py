import asyncio
import logging
from datetime import datetime, timezone

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

async def send_email(to_email: str, subject: str, text_body: str, html_body: str, smtp_host: str, smtp_port: int, smtp_user: str, smtp_pass: str) -> None:
    """Send an email with both plain-text and HTML parts via SMTP."""
    if not smtp_user or not smtp_pass or not to_email:
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Upfield Notifications <{smtp_user}>"
    msg["Reply-To"] = smtp_user
    msg["To"] = to_email

    # Adding both plain text and HTML reduces the chance of being marked as SPAM
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
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
        raise exc


# ─── Dispatcher ───────────────────────────────────────────────────────────────

async def notify(monitor, event: str) -> None:
    """
    Send DOWN or RECOVERY notifications for *monitor*.
    """
    time_now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    if event == "down":
        tg_msg = (
            f"⚠️ <b>[ALERT] Monitor Down</b>\n"
            f"<b>Name:</b> {monitor.name}\n"
            f"<b>URL:</b> {monitor.url}\n"
            f"<b>Failures:</b> {monitor.consecutive_failures}"
        )
        
        email_subject = f"[Upfield Alert] Action Required: {monitor.name} is DOWN"
        
        text_body = f"""Upfield Monitoring Alert

Monitor Status: DOWN
Monitor Name: {monitor.name}
URL: {monitor.url}
Consecutive Failures: {monitor.consecutive_failures}
Time: {time_now}

Please check your systems immediately.
"""
        html_body = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
        <div style="background-color: #ef4444; color: #ffffff; padding: 15px 20px; font-weight: bold; font-size: 18px;">
            Action Required: Monitor Down
        </div>
        <div style="padding: 20px;">
            <p>The following monitor has failed health checks and is currently unreachable.</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px;">
                <tr><td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold; width: 35%; color: #64748b;">Monitor Name</td>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{monitor.name}</td></tr>
                <tr><td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Target URL</td>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;"><a href="{monitor.url}" style="color: #3b82f6; text-decoration: none;">{monitor.url}</a></td></tr>
                <tr><td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Failures</td>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{monitor.consecutive_failures} consecutive checks</td></tr>
                <tr><td style="padding: 10px; font-weight: bold; color: #64748b;">Timestamp</td>
                    <td style="padding: 10px;">{time_now}</td></tr>
            </table>
        </div>
        <div style="background-color: #f8fafc; padding: 15px 20px; font-size: 12px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0;">
            This is an automated message from Upfield Monitoring System.
        </div>
    </div>
</body>
</html>"""

    elif event == "recovery":
        tg_msg = (
            f"✅ <b>[RESOLVED] Monitor Up</b>\n"
            f"<b>Name:</b> {monitor.name}\n"
            f"<b>URL:</b> {monitor.url}"
        )
        
        email_subject = f"[Upfield Resolved] Monitor Restored: {monitor.name} is UP"
        
        text_body = f"""Upfield Monitoring Alert

Monitor Status: RESOLVED (UP)
Monitor Name: {monitor.name}
URL: {monitor.url}
Time: {time_now}

The monitor is now responding successfully.
"""
        html_body = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
    <div style="border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;">
        <div style="background-color: #10b981; color: #ffffff; padding: 15px 20px; font-weight: bold; font-size: 18px;">
            Status Resolved: Monitor Up
        </div>
        <div style="padding: 20px;">
            <p>The following monitor is now responding successfully to health checks.</p>
            <table style="width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 14px;">
                <tr><td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold; width: 35%; color: #64748b;">Monitor Name</td>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">{monitor.name}</td></tr>
                <tr><td style="padding: 10px; border-bottom: 1px solid #e2e8f0; font-weight: bold; color: #64748b;">Target URL</td>
                    <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;"><a href="{monitor.url}" style="color: #3b82f6; text-decoration: none;">{monitor.url}</a></td></tr>
                <tr><td style="padding: 10px; font-weight: bold; color: #64748b;">Timestamp</td>
                    <td style="padding: 10px;">{time_now}</td></tr>
            </table>
        </div>
        <div style="background-color: #f8fafc; padding: 15px 20px; font-size: 12px; color: #64748b; text-align: center; border-top: 1px solid #e2e8f0;">
            This is an automated message from Upfield Monitoring System.
        </div>
    </div>
</body>
</html>"""
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
            to_email=target_email, 
            subject=email_subject, 
            text_body=text_body,
            html_body=html_body, 
            smtp_host=app_settings.smtp_host, 
            smtp_port=app_settings.smtp_port, 
            smtp_user=app_settings.smtp_user, 
            smtp_pass=app_settings.smtp_pass
        ))

    if tasks:
        await asyncio.gather(*tasks)
