"""
Outbound Webhook Registration
Analog externe Agrar-ERP-Plattform Webhook-Modul

Dieses Modul schrieb bis zum 01.10.2026 in ``domain_shared.webhooks`` — eine
Tabelle, die keine Migration anlegt. Die Anbindungen eines Hauses liegen in
``domain_shared.webhook_registrations`` (ORM-Modell ``WebhookRegistration``,
migriert, mit ``tenant_id`` und ``secret``). Dieses Modul liest und schreibt
jetzt dort; eine zweite Webhook-Tabelle waere eine zweite Wahrheit darueber,
wohin wir Ereignisse melden.

Ausserdem kannte es keinen Mandanten — kein Import von ``get_tenant_id``, kein
Filter. Siehe ``docs/quality-assurance/webhook-mandant-20261001.md``.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, field_validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.outbound_security import (
    OutboundTargetPolicyError,
    validate_outbound_http_target,
)
from ....core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema


router = APIRouter()
logger = logging.getLogger(__name__)

#: Kopfzeile, in der die Signatur des gesendeten Rumpfes steht. Ohne sie kann
#: ein Empfaenger nicht unterscheiden, ob ein Aufruf von uns kommt oder von
#: jemandem, der die URL kennt.
SIGNATUR_KOPF = "X-Valeo-Signature"

#: Die laufende Nummer ist keine Spalte, sondern die Stellung der Zeile **im
#: eigenen Haus**, nach Anlagezeitpunkt. Vorher kam sie aus ``MAX(nr) + 1``
#: ueber alle Haeuser hinweg.
_MIT_NUMMER = """
    SELECT id, url, event_area, secret, is_active, created_at, updated_at,
           ROW_NUMBER() OVER (ORDER BY created_at, id) AS nr
    FROM domain_shared.webhook_registrations
    WHERE tenant_id = :tid
"""

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
    #: Ob ein Geheimnis hinterlegt ist — **nicht** das Geheimnis selbst.
    signiert: bool = False


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


def _zeile_zu_webhook(row: Any) -> WebhookOut:
    return WebhookOut(
        id=str(row["id"]),
        nr=int(row["nr"]),
        url=row["url"],
        bereich=row["event_area"],
        beschreibung=None,
        is_active=bool(row["is_active"]) if row["is_active"] is not None else True,
        erstellt_am=row["created_at"].isoformat() if row["created_at"] else None,
        letzte_auslosung_am=None,
        fehler_count=0,
        signiert=bool(row["secret"]),
    )


@router.get("", response_model=list[WebhookOut], tags=["webhooks"], summary="Webhooks auflisten")
def list_webhooks(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[WebhookOut]:
    """Die Webhooks des eigenen Hauses."""
    try:
        rows = db.execute(
            text(_MIT_NUMMER + " ORDER BY nr"), {"tid": tenant_id}
        ).mappings().all()
    except Exception as exc:  # noqa: BLE001
        # Keine leere Liste: "kein Webhook eingerichtet" und "die Tabelle ist
        # nicht lesbar" sahen gleich aus. Im zweiten Fall haette ein Haus eine
        # bestehende Anbindung fuer abgemeldet gehalten und doppelt registriert.
        db.rollback()
        logger.exception("Webhooks nicht lesbar (Mandant %s)", tenant_id)
        raise HTTPException(
            status_code=503, detail="Webhooks sind derzeit nicht abrufbar"
        ) from exc
    return [_zeile_zu_webhook(r) for r in rows]


@router.get("/bereiche", response_model=list[str], tags=["webhooks"], summary="Bereiche auflisten")
def list_bereiche() -> list[str]:
    """List available webhook event areas."""
    return VALID_BEREICHE


@router.post("/bereiche/{bereich}", response_model=WebhookOut, status_code=201, tags=["webhooks"], summary="Webhook registrieren")
def register_webhook(
    bereich: str,
    payload: WebhookCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> WebhookOut:
    """Register a new outbound webhook for a given event area."""
    # Validate bereich via model (will also be validated by Pydantic on the body, but bereich comes from path)
    if bereich not in VALID_BEREICHE:
        raise HTTPException(status_code=422, detail=f"Unbekannter Bereich '{bereich}'. Gültig: {VALID_BEREICHE}")
    if not payload.url.startswith("https://"):
        raise HTTPException(status_code=422, detail="URL muss mit https:// beginnen")
    # Dieselbe Pruefung, die `webhooks.py` schon anwendet: eine Ziel-URL darf
    # nicht in das eigene Netz zeigen (SSRF). `https://` allein genuegt nicht.
    try:
        validate_outbound_http_target(payload.url)
    except OutboundTargetPolicyError as fehler:
        raise HTTPException(status_code=422, detail=str(fehler)) from fehler

    from app.core.uuid7 import uuid7

    new_id = str(uuid7())
    now = datetime.now(timezone.utc)
    try:
        db.execute(
            text(
                "INSERT INTO domain_shared.webhook_registrations "
                "(id, tenant_id, url, event_area, secret, is_active, created_at, updated_at) "
                "VALUES (:id, :tid, :url, :bereich, :secret, :is_active, :now, :now)"
            ),
            {
                "id": new_id,
                "tid": tenant_id,
                "url": payload.url,
                "bereich": bereich,
                # Das Geheimnis wurde bis zum 01.10.2026 entgegengenommen und
                # verworfen. Jetzt wird es hinterlegt und signiert jeden
                # Aufruf — ausgegeben wird es nie wieder.
                "secret": payload.secret or None,
                "is_active": payload.is_active,
                "now": now,
            },
        )
        db.commit()
        nr = db.execute(
            text(f"SELECT nr FROM ({_MIT_NUMMER}) AS m WHERE id = :id"),  # nosec B608  # reviewed-safe: _MIT_NUMMER ist ein Code-Literal, Werte sind gebunden
            {"tid": tenant_id, "id": new_id},
        ).scalar_one()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return WebhookOut(
        id=new_id,
        nr=int(nr),
        url=payload.url,
        bereich=bereich,
        beschreibung=payload.beschreibung,
        is_active=payload.is_active,
        erstellt_am=now.isoformat(),
        fehler_count=0,
        signiert=bool(payload.secret),
    )


@router.delete("/abmelden/{nr}", status_code=204, response_class=Response, tags=["webhooks"], response_model=None, summary="Webhook abmelden")
def unregister_webhook(
    nr: int,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Response:
    """Meldet den Webhook mit dieser laufenden Nummer im eigenen Haus ab.

    Der Weg hiess vorher ``DELETE /webhooks/{nr}`` und war **unerreichbar**:
    Unter demselben Prefix haengt ``webhooks.py`` mit ``DELETE /{webhook_id}``
    und ist zuerst eingebunden, also traf jede Abmeldung dort eine Kennung, die
    keine laufende Nummer ist. Deshalb ``/abmelden/{nr}``.
    """
    try:
        ziel = db.execute(
            text(f"SELECT id FROM ({_MIT_NUMMER}) AS m WHERE nr = :nr"),  # nosec B608  # reviewed-safe: _MIT_NUMMER ist ein Code-Literal, Werte sind gebunden
            {"tid": tenant_id, "nr": nr},
        ).scalar()
        if ziel is None:
            raise HTTPException(status_code=404, detail=f"Webhook nr={nr} nicht gefunden")
        db.execute(
            text(
                "DELETE FROM domain_shared.webhook_registrations "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": ziel, "tid": tenant_id},
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Internal helper (not exposed as endpoint)
# ---------------------------------------------------------------------------

def _signatur(secret: str, rumpf: bytes) -> str:
    """HMAC-SHA256 ueber den gesendeten Rumpf, hexadezimal."""
    return "sha256=" + hmac.new(secret.encode("utf-8"), rumpf, hashlib.sha256).hexdigest()


async def _trigger_webhook(
    bereich: str,
    payload: dict[str, Any],
    db: Session,
    tenant_id: str,
) -> None:
    """Best-effort: feuert die aktiven Webhooks **dieses Hauses**.

    ``tenant_id`` ist Pflicht und ohne Vorgabewert. Ein Ereignis ohne Haus darf
    nirgendwohin gehen: Vorher waehlte die Abfrage alle Webhooks eines Bereichs,
    also haette ein Vorgang aus Haus A an die URL von Haus B gemeldet. Die
    Funktion hat derzeit keinen Aufrufer — der Abfluss war angelegt, nicht in
    Betrieb.
    """
    if not tenant_id:
        logger.error("_trigger_webhook ohne Mandant (%s) — nichts gesendet", bereich)
        return
    try:
        rows = db.execute(
            text(
                "SELECT id, url, secret FROM domain_shared.webhook_registrations "
                "WHERE tenant_id = :tid AND event_area = :b "
                "  AND COALESCE(is_active, TRUE) = TRUE"
            ),
            {"tid": tenant_id, "b": bereich},
        ).mappings().all()
    except Exception:  # noqa: BLE001
        db.rollback()
        logger.warning("_trigger_webhook: cannot read webhook table")
        return

    rumpf = json.dumps(payload).encode("utf-8")
    for row in rows:
        url = row["url"]
        try:
            import httpx  # optional dependency
            kopf = {"Content-Type": "application/json"}
            if row["secret"]:
                kopf[SIGNATUR_KOPF] = _signatur(row["secret"], rumpf)
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(url, content=rumpf, headers=kopf)
            db.execute(
                text(
                    "UPDATE domain_shared.webhook_registrations SET updated_at = NOW() "
                    "WHERE id = :id AND tenant_id = :tid"
                ),
                {"id": row["id"], "tid": tenant_id},
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("Webhook %s failed: %s", url, exc)
    try:
        db.commit()
    except Exception:  # noqa: BLE001
        # Der Zeitstempel ist Begleitdatum des Zustellversuchs, nicht der
        # Vorgang selbst — sein Verlust darf den Vorgang nicht scheitern lassen.
        db.rollback()
