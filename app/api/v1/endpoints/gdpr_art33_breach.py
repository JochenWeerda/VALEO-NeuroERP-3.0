"""
DSGVO Art. 33 — Datenpannen-Meldeprozess (Personal Data Breach Notification).

Art. 33 Abs. 1: Meldung an Aufsichtsbehörde innerhalb von 72 Stunden nach Bekanntwerden.
Art. 33 Abs. 3 Pflichtinhalt:
  a) Art der Verletzung, ggf. Kategorien und Zahl betroffener Personen und Datensätze
  b) Name und Kontaktdaten des DSB
  c) Wahrscheinliche Folgen der Verletzung
  d) Ergriffene / vorgeschlagene Maßnahmen

Status-Workflow: ENTDECKT → IN_BEARBEITUNG → GEMELDET → ABGESCHLOSSEN

Endpoints:
  GET    /gdpr/art33/breaches              — Liste aller Datenpannen
  POST   /gdpr/art33/breaches              — Neue Datenpanne erfassen
  GET    /gdpr/art33/breaches/{id}         — Einzelansicht
  PUT    /gdpr/art33/breaches/{id}         — Aktualisieren
  GET    /gdpr/art33/breaches/{id}/deadline — 72h-Fristinfo
  POST   /gdpr/art33/breaches/{id}/notify  — Als behördengemeldet markieren
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/gdpr/art33", tags=["gdpr", "compliance", "art33"])

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

BREACH_TYPES = {
    "VERTRAULICHKEIT": "Unbefugter Zugriff auf personenbezogene Daten",
    "INTEGRITAET": "Unbefugte Änderung personenbezogener Daten",
    "VERFUEGBARKEIT": "Verlust / Zerstörung personenbezogener Daten",
}

BREACH_STATUSES = {"ENTDECKT", "IN_BEARBEITUNG", "GEMELDET", "ABGESCHLOSSEN"}

DEADLINE_HOURS = 72


class BreachIn(BaseModel):
    """Eingabe-Schema für eine Datenpanne (Art. 33 Abs. 3 DSGVO)."""

    # a) Art der Verletzung
    breach_type: str = Field(
        ...,
        description="VERTRAULICHKEIT / INTEGRITAET / VERFUEGBARKEIT",
    )
    description: str = Field(..., max_length=2000, description="Beschreibung der Datenpanne")

    # Betroffene Personen und Datensätze
    data_categories: list[str] = Field(
        default_factory=list,
        description="Kategorien betroffener personenbezogener Daten",
    )
    persons_count_approx: int = Field(
        default=0,
        ge=0,
        description="Ungefähre Anzahl betroffener Personen",
    )
    records_count_approx: int = Field(
        default=0,
        ge=0,
        description="Ungefähre Anzahl betroffener Datensätze",
    )

    # b) DSB-Kontakt
    dpo_name: str = Field(default="", max_length=200, description="Name des Datenschutzbeauftragten")
    dpo_contact: str = Field(default="", max_length=500, description="Kontaktdaten DSB (E-Mail / Tel.)")

    # c) Wahrscheinliche Folgen
    likely_consequences: str = Field(
        default="",
        max_length=2000,
        description="Wahrscheinliche Folgen der Verletzung (Art. 33 Abs. 3 lit. c)",
    )

    # d) Maßnahmen
    measures_taken: str = Field(
        default="",
        max_length=2000,
        description="Ergriffene / vorgeschlagene Abhilfemaßnahmen (Art. 33 Abs. 3 lit. d)",
    )

    # Metadaten
    discovered_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Zeitpunkt der Entdeckung (Fristbeginn für 72h-Meldepflicht)",
    )
    status: str = Field(
        default="ENTDECKT",
        description="ENTDECKT / IN_BEARBEITUNG / GEMELDET / ABGESCHLOSSEN",
    )
    internal_reference: str = Field(
        default="",
        max_length=100,
        description="Internes Aktenzeichen / Ticket-Nummer",
    )


class BreachOut(BreachIn):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    notified_at: Optional[datetime] = None
    notified_by: Optional[str] = None
    authority_reference: Optional[str] = None


class DeadlineInfo(BaseModel):
    breach_id: str
    discovered_at: datetime
    deadline_at: datetime
    hours_remaining: float
    hours_elapsed: float
    is_overdue: bool
    is_notified: bool
    traffic_light: str  # RED | ORANGE | GREEN


class NotifyIn(BaseModel):
    notified_by: str = Field(..., max_length=200, description="Name / E-Mail der meldenden Person")
    authority_reference: str = Field(
        default="",
        max_length=200,
        description="Aktenzeichen der Datenschutzbehörde (falls bereits vergeben)",
    )


# ---------------------------------------------------------------------------
# In-Memory Store (Fallback analog Slice-008)
# ---------------------------------------------------------------------------

_store: dict[str, dict[str, Any]] = {}


def _store_key(tenant_id: str, breach_id: str) -> str:
    return f"{tenant_id}::{breach_id}"


def _get_all(tenant_id: str) -> list[dict[str, Any]]:
    prefix = f"{tenant_id}::"
    return [v for k, v in _store.items() if k.startswith(prefix)]


def _compute_deadline(breach: dict[str, Any]) -> DeadlineInfo:
    discovered = breach["discovered_at"]
    if isinstance(discovered, str):
        discovered = datetime.fromisoformat(discovered)
    if discovered.tzinfo is None:
        discovered = discovered.replace(tzinfo=timezone.utc)

    deadline = discovered + timedelta(hours=DEADLINE_HOURS)
    now = datetime.now(timezone.utc)
    elapsed = (now - discovered).total_seconds() / 3600
    remaining = (deadline - now).total_seconds() / 3600
    is_notified = breach.get("notified_at") is not None
    is_overdue = not is_notified and now > deadline

    if is_notified:
        traffic_light = "GREEN"
    elif remaining < 24:
        traffic_light = "RED"
    else:
        traffic_light = "ORANGE"

    return DeadlineInfo(
        breach_id=breach["id"],
        discovered_at=discovered,
        deadline_at=deadline,
        hours_remaining=max(0.0, round(remaining, 2)),
        hours_elapsed=round(elapsed, 2),
        is_overdue=is_overdue,
        is_notified=is_notified,
        traffic_light=traffic_light,
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/breaches", response_model=list[BreachOut], summary="Alle Datenpannen auflisten")
def list_breaches(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    rows = _get_all(tenant_id)
    if status:
        rows = [r for r in rows if r.get("status") == status.upper()]
    return rows


@router.post("/breaches", response_model=BreachOut, status_code=201, summary="Datenpanne erfassen")
def create_breach(
    payload: BreachIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Neue Datenpanne nach Art. 33 DSGVO erfassen. Startet die 72h-Meldefrist."""
    if payload.breach_type not in BREACH_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"breach_type muss einer von {list(BREACH_TYPES.keys())} sein",
        )
    if payload.status not in BREACH_STATUSES:
        raise HTTPException(status_code=400, detail=f"Ungültiger Status: {payload.status}")

    now = datetime.now(timezone.utc)
    breach_id = str(uuid4())
    data: dict[str, Any] = {
        "id": breach_id,
        "tenant_id": tenant_id,
        **payload.model_dump(),
        "created_at": now,
        "updated_at": now,
        "notified_at": None,
        "notified_by": None,
        "authority_reference": None,
    }
    _store[_store_key(tenant_id, breach_id)] = data
    logger.info("Datenpanne erfasst: %s (Tenant: %s, Typ: %s)", breach_id, tenant_id, payload.breach_type)
    return data


@router.get("/breaches/{breach_id}", response_model=BreachOut, summary="Datenpanne abrufen")
def get_breach(
    breach_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    row = _store.get(_store_key(tenant_id, breach_id))
    if row is None:
        raise HTTPException(status_code=404, detail=f"Datenpanne {breach_id} nicht gefunden")
    return row


@router.put("/breaches/{breach_id}", response_model=BreachOut, summary="Datenpanne aktualisieren")
def update_breach(
    breach_id: str,
    payload: BreachIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    existing = _store.get(_store_key(tenant_id, breach_id))
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Datenpanne {breach_id} nicht gefunden")
    if payload.status not in BREACH_STATUSES:
        raise HTTPException(status_code=400, detail=f"Ungültiger Status: {payload.status}")
    if payload.breach_type not in BREACH_TYPES:
        raise HTTPException(status_code=400, detail=f"Ungültiger breach_type: {payload.breach_type}")

    updated: dict[str, Any] = {
        **existing,
        **payload.model_dump(),
        "id": breach_id,
        "updated_at": datetime.now(timezone.utc),
    }
    _store[_store_key(tenant_id, breach_id)] = updated
    return updated


@router.get("/breaches/{breach_id}/deadline", response_model=DeadlineInfo, summary="72h-Fristinfo")
def get_deadline(
    breach_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> DeadlineInfo:
    """Gibt den Friststand zurück: verbleibende Stunden, Ampelfarbe, Überfälligkeit."""
    row = _store.get(_store_key(tenant_id, breach_id))
    if row is None:
        raise HTTPException(status_code=404, detail=f"Datenpanne {breach_id} nicht gefunden")
    return _compute_deadline(row)


@router.post("/breaches/{breach_id}/notify", response_model=BreachOut, summary="Als behördengemeldet markieren")
def notify_authority(
    breach_id: str,
    payload: NotifyIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Markiert die Datenpanne als bei der Aufsichtsbehörde gemeldet (Art. 33 Abs. 1)."""
    row = _store.get(_store_key(tenant_id, breach_id))
    if row is None:
        raise HTTPException(status_code=404, detail=f"Datenpanne {breach_id} nicht gefunden")
    if row.get("notified_at") is not None:
        raise HTTPException(
            status_code=409,
            detail="Datenpanne wurde bereits als behördengemeldet markiert",
        )

    now = datetime.now(timezone.utc)
    row["notified_at"] = now
    row["notified_by"] = payload.notified_by
    row["authority_reference"] = payload.authority_reference or None
    row["status"] = "GEMELDET"
    row["updated_at"] = now
    logger.info("Datenpanne %s als behördengemeldet markiert von %s", breach_id, payload.notified_by)
    return row
