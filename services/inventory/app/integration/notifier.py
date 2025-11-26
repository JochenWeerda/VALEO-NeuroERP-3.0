"""Ops-Notifier: sendet Eskalationen an Teams/Webhook (optional)."""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


async def notify_ops(summary: str, details: dict[str, Any] | None = None) -> None:
    """Sende eine kurze Notifikation an den konfigurierten Kanal (Teams/Webhook)."""
    if not settings.TEAMS_WEBHOOK_URL:
        logger.info("Ops-Notify: %s | %s", summary, details or {})
        return
    payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {"type": "TextBlock", "text": "VALEO Inventory - Auto-Remediation", "weight": "bolder"},
                        {"type": "TextBlock", "text": summary, "wrap": True},
                        {
                            "type": "FactSet",
                            "facts": [{"title": k, "value": str(v)} for k, v in (details or {}).items()],
                        },
                    ],
                },
            }
        ],
    }
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(settings.TEAMS_WEBHOOK_URL, json=payload)
            resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Ops-Notify fehlgeschlagen: %s", exc)


async def send_email_escalation(subject: str, body: str, to_email: str | None = None) -> None:
    """Sende Eskalations-E-Mail (Fallback wenn Teams nicht verfügbar)."""
    if not to_email and not settings.ESCALATION_EMAIL:
        logger.warning("Keine E-Mail-Adresse für Eskalation konfiguriert")
        return
    
    email_to = to_email or settings.ESCALATION_EMAIL
    
    try:
        msg = MIMEMultipart()
        msg['From'] = 'noreply@valeo-neuroerp.com'
        msg['To'] = email_to
        msg['Subject'] = f"[VALEO CRITICAL] {subject}"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # SMTP-Server konfigurieren (einfache Implementierung)
        with smtplib.SMTP('smtp.valeo.com', 587) as server:
            server.starttls()
            # Hier würden SMTP-Credentials verwendet werden
            server.send_message(msg)
            
        logger.info("Eskalations-E-Mail gesendet an %s", email_to)
        
    except Exception as e:
        logger.error("E-Mail-Eskalation fehlgeschlagen: %s", e)


async def auto_remediate_epcis_failure(
    event_id: str, error: str, retry_count: int = 0, max_retries: int = 3
) -> bool:
    """Automatische Remediation für EPCIS-Event-Fehler mit Eskalation bei anhaltenden Problemen."""
    
    remediation_actions = {
        "nats_connection_error": "NATS-Verbindung neu aufbauen",
        "database_timeout": "DB-Connection Pool refreshen",
        "validation_error": "Event-Validierung überspringen (nur im Notfall)",
    }
    
    action = remediation_actions.get(error, "Unbekannter Fehler - manuelle Prüfung erforderlich")
    
    if retry_count < max_retries:
        # Automatischer Retry
        logger.warning("Auto-Remediation: Retry %d/%d für Event %s: %s", 
                      retry_count + 1, max_retries, event_id, action)
        await asyncio.sleep(2 ** retry_count)  # Exponential backoff
        return True
    
    # Eskalation nach max_retries
    escalation_msg = (
        f"EPCIS-Event {event_id} konnte nach {max_retries} Retries nicht verarbeitet werden. "
        f"Fehler: {error}. Letzte Remediation-Aktion: {action}"
    )
    
    # Teams-Webhook Eskalation
    await notify_ops(
        summary=f"EPCIS-Event Eskalation: {error}",
        details={
            "event_id": event_id,
            "error": error,
            "retry_count": retry_count,
            "remediation_action": action,
            "status": "eskalation_erforderlich"
        }
    )
    
    # E-Mail Fallback Eskalation
    email_body = f"""
EPCIS Event Processing Failure - Auto-Remediation fehlgeschlagen

Event ID: {event_id}
Error: {error}
Retry Attempts: {retry_count}
Remediation Action: {action}

Details:
- Service: Inventory
- Component: EPCIS Event Pipeline
- Time: {asyncio.get_event_loop().time()}

Required Action: Manuelle Intervention erforderlich
"""
    
    await send_email_escalation(
        subject=f"EPCIS Event Failure - {event_id}",
        body=email_body
    )
    
    return False

