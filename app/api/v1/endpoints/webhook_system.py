"""
Outbound Webhook Registration
Analog externe Agrar-ERP-Plattform Webhook-Modul
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Valid event areas
# ---------------------------------------------------------------------------

VALID_BEREICHE = [
    "WIEGUNG_NEU",
    "WIEGUNG_GEAENDERT",
    "KONTRAKT_NEU",
    "KONTRAKT_FREIGEGEBEN",
    "SETTLEMENT_GEBUCHT",
    "RECHNUNG_NEU",
    "BESTELLUNG_FREIGEGEBEN",
    "LIEFERSCHEIN_ERSTELLT",
    "INVENTUR_ABGESCHLOSSEN",
    "KUNDE_NEU",
    "INTERESSENT_KONVERTIERT",
]

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class WebhookCreate(BaseModel):
    url: str
    bereich: str
    beschreibung: Optional[str] = None
    secret: Optional[str] = None
    is_active: bool = True

    @field_validator("url")
    @classmethod
    def url_must_be_https(cls, v: str) -> str:
        if not v.startswith("https://"):
            raise ValueError("URL muss mit https:// beginnen")
        return v

    @field_validator("bereich")
    @classmethod
    def bereich_must_be_valid(cls, v: str) -> str:
        if v not in VALID_BEREICHE:
            raise ValueError(f"Unbekannter Bereich '{v}'. Gültig: {VALID_BEREICHE}")
        return v


class WebhookOut(BaseModel):
    id: str
    nr: int
    url: str
    bereich: str
    beschreibung: Optional[str] = None
    is_active: bool
    erstellt_am: Optional[str] = None
    letzte_auslosung_am: Optional[str] = None
    fehler_count: int = 0


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=list[WebhookOut], tags=["webhooks"])
def list_webhooks(db: Session = Depends(get_db)) -> list[WebhookOut]:
    """List all registered webhooks."""
    try:
        rows = db.execute(
            text("SELECT id, nr, url, bereich, beschreibung, is_active, erstellt_am, letzte_auslosung_am, fehler_count FROM domain_shared.webhooks ORDER BY nr")
        ).mappings().all()
        return [WebhookOut(**dict(r)) for r in rows]
    except Exception:  # noqa: BLE001
        return []


@router.get("/bereiche", response_model=list[str], tags=["webhooks"])
def list_bereiche() -> list[str]:
    """List available webhook event areas."""
    return VALID_BEREICHE


@router.post("/bereiche/{bereich}", response_model=WebhookOut, status_code=201, tags=["webhooks"])
def register_webhook(bereich: str, payload: WebhookCreate, db: Session = Depends(get_db)) -> WebhookOut:
    """Register a new outbound webhook for a given event area."""
    # Validate bereich via model (will also be validated by Pydantic on the body, but bereich comes from path)
    if bereich not in VALID_BEREICHE:
        raise HTTPException(status_code=422, detail=f"Unbekannter Bereich '{bereich}'. Gültig: {VALID_BEREICHE}")
    if not payload.url.startswith("https://"):
        raise HTTPException(status_code=422, detail="URL muss mit https:// beginnen")

    new_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    try:
        # Get next nr
        row = db.execute(text("SELECT COALESCE(MAX(nr), 0) + 1 AS next_nr FROM domain_shared.webhooks")).mappings().one()
        next_nr = row["next_nr"]
        db.execute(
            text(
                "INSERT INTO domain_shared.webhooks (id, nr, url, bereich, beschreibung, is_active, erstellt_am, fehler_count) "
                "VALUES (:id, :nr, :url, :bereich, :beschreibung, :is_active, :erstellt_am, 0)"
            ),
            {
                "id": new_id,
                "nr": next_nr,
                "url": payload.url,
                "bereich": bereich,
                "beschreibung": payload.beschreibung,
                "is_active": payload.is_active,
                "erstellt_am": now,
            },
        )
        db.commit()
        return WebhookOut(
            id=new_id,
            nr=next_nr,
            url=payload.url,
            bereich=bereich,
            beschreibung=payload.beschreibung,
            is_active=payload.is_active,
            erstellt_am=now,
            fehler_count=0,
        )
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc), headers={"X-Migration-Hint": "CREATE TABLE domain_shared.webhooks (...)"}) from exc


@router.delete("/{nr}", status_code=204, tags=["webhooks"])
def unregister_webhook(nr: int, db: Session = Depends(get_db)) -> None:
    """Unregister (delete) a webhook by its sequential number."""
    try:
        result = db.execute(text("DELETE FROM domain_shared.webhooks WHERE nr = :nr"), {"nr": nr})
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Webhook nr={nr} nicht gefunden")
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Internal helper (not exposed as endpoint)
# ---------------------------------------------------------------------------

async def _trigger_webhook(bereich: str, payload: dict[str, Any], db: Session) -> None:
    """Best-effort: fire all active webhooks for the given event area."""
    try:
        rows = db.execute(
            text("SELECT id, nr, url FROM domain_shared.webhooks WHERE bereich = :b AND is_active = TRUE"),
            {"b": bereich},
        ).mappings().all()
    except Exception:  # noqa: BLE001
        logger.warning("_trigger_webhook: cannot read webhooks table")
        return

    for row in rows:
        url = row["url"]
        try:
            import httpx  # optional dependency
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(url, json=payload)
            db.execute(
                text("UPDATE domain_shared.webhooks SET letzte_auslosung_am = NOW() WHERE id = :id"),
                {"id": row["id"]},
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Webhook %s failed: %s", url, exc)
            try:
                db.execute(
                    text("UPDATE domain_shared.webhooks SET fehler_count = fehler_count + 1 WHERE id = :id"),
                    {"id": row["id"]},
                )
            except Exception:  # noqa: BLE001
                pass
    try:
        db.commit()
    except Exception:  # noqa: BLE001
        pass
