"""Einfacher SMTP-Versand für GDPR-Verifizierung (blocking in Thread)."""

from __future__ import annotations

import asyncio
import logging
import smtplib
from email.message import EmailMessage

from app.config.settings import settings

logger = logging.getLogger(__name__)


async def send_verification_email_async(to_email: str, verification_token: str, request_id: str) -> bool:
    if not settings.SMTP_HOST:
        logger.warning("SMTP_HOST nicht gesetzt — Verifikations-Mail wird nicht verschickt")
        return False

    base = (settings.GDPR_PUBLIC_VERIFICATION_URL or "").rstrip("/")
    link_hint = ""
    if base:
        link_hint = (
            f"\n\nBestätigung: Öffnen Sie {base}?request_id={request_id}&token={verification_token} "
            f"(falls Ihr Frontend diesen Pfad bereitstellt)."
        )

    subject = settings.GDPR_VERIFICATION_EMAIL_SUBJECT
    body = (
        f"Sie haben eine Datenanfrage gestellt.\n\n"
        f"Ihr Bestätigungstoken:\n{verification_token}\n"
        f"{link_hint}\n\n"
        f"Diese Nachricht enthält keine Anhänge. Bewahren Sie den Token sicher auf."
    )

    def _send() -> None:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_FROM or "noreply@localhost"
        msg["To"] = to_email
        msg.set_content(body)
        host = settings.SMTP_HOST
        port = int(settings.SMTP_PORT or 587)
        timeout = float(settings.SMTP_TIMEOUT_SECONDS or 30)
        with smtplib.SMTP(host, port, timeout=timeout) as smtp:
            if settings.SMTP_USE_TLS:
                smtp.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            smtp.send_message(msg)

    try:
        await asyncio.to_thread(_send)
        logger.info("gdpr_verification_email_sent", to=to_email)
        return True
    except Exception:
        logger.exception("gdpr_verification_email_failed", to=to_email)
        return False
