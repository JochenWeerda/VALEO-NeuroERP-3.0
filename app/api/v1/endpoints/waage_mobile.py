"""WGE-MOB-001: Mobile-Sync für Waagenbelege.

Fahrer/Lager quittiert Anlieferung am Tablet offline-fähig.
Sync bei Reconnect ohne Datenverlust — erweitert MOB-SYNC-001 um
Waagen-spezifische Ereignistypen mit Wiege-Daten-Validierung.

Endpoints:
- POST /waage/mobile/quittung   → Fahrer-Quittung für Wiegeticket (offline-fähig)
- GET  /waage/mobile/pending    → Ausstehende Quittungen (Device-Sicht)
- POST /waage/mobile/sync       → Batch-Sync von Offline-Quittungen
- GET  /waage/mobile/tickets/{ticket_id} → Wiegeticket + Quittungsstatus
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7

router = APIRouter(prefix="/waage/mobile", tags=["waage", "mobile", "logistik"])


class WaagenQuittungIn(BaseModel):
    weighing_ticket_id: str
    device_id: str
    driver_id: Optional[str] = None
    quittiert_am: Optional[str] = None          # ISO-Timestamp (offline-Zeitstempel)
    gps_lat: Optional[float] = None
    gps_lon: Optional[float] = None
    bemerkung: Optional[str] = None
    idempotency_key: str = Field(default_factory=lambda: str(uuid4()))


class WaagenQuittungBatch(BaseModel):
    device_id: str
    quittungen: list[WaagenQuittungIn]


@router.post("/quittung", response_model=dict, status_code=201,
             summary="Fahrer-Quittung für Wiegeticket erfassen (WGE-MOB-001)")
def create_quittung(
    body: WaagenQuittungIn,
    response: Response = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Erfasst Fahrer-Quittung für ein Wiegeticket. Idempotent via idempotency_key."""
    # Idempotenz-Prüfung
    existing = db.execute(text("""
        SELECT id, status FROM domain_agrar.waagen_quittungen
         WHERE idempotency_key = :key AND tenant_id = :tid
    """), {"key": body.idempotency_key, "tid": tenant_id}).fetchone()
    if existing:
        if response is not None:
            response.status_code = 200
        return {"id": str(existing[0]), "status": str(existing[1]),
                "idempotent": True, "idempotency_key": body.idempotency_key}

    # Wiegeticket validieren
    ticket = db.execute(text("""
        SELECT id, ticket_number, netto_gewicht_kg, status
          FROM domain_agrar.weighing_tickets
         WHERE id = :id AND tenant_id = :tid
    """), {"id": body.weighing_ticket_id, "tid": tenant_id}).fetchone()
    if not ticket:
        raise HTTPException(status_code=404, detail="Wiegeticket nicht gefunden")

    quittung_id = str(uuid7())
    quittiert_am = body.quittiert_am or datetime.now(timezone.utc).isoformat()

    try:
        db.execute(text("""
            INSERT INTO domain_agrar.waagen_quittungen
              (id, tenant_id, weighing_ticket_id, device_id, driver_id,
               quittiert_am, gps_lat, gps_lon, bemerkung, idempotency_key, status)
            VALUES
              (:id, :tid, :ticket, :device, :driver,
               :quittiert, :lat, :lon, :bem, :key, 'quittiert')
        """), {
            "id": quittung_id,
            "tid": tenant_id,
            "ticket": body.weighing_ticket_id,
            "device": body.device_id,
            "driver": body.driver_id,
            "quittiert": quittiert_am,
            "lat": body.gps_lat,
            "lon": body.gps_lon,
            "bem": body.bemerkung,
            "key": body.idempotency_key,
        })
        # Wiegeticket-Status aktualisieren
        db.execute(text("""
            UPDATE domain_agrar.weighing_tickets
               SET quittiert = true, quittiert_am = :qam
             WHERE id = :id AND tenant_id = :tid
        """), {"qam": quittiert_am, "id": body.weighing_ticket_id, "tid": tenant_id})
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "id": quittung_id,
        "weighing_ticket_id": body.weighing_ticket_id,
        "ticket_number": ticket[1],
        "device_id": body.device_id,
        "quittiert_am": quittiert_am,
        "status": "quittiert",
        "idempotency_key": body.idempotency_key,
    }


@router.post("/sync", response_model=dict, status_code=200,
             summary="Offline-Batch-Sync: mehrere Quittungen auf einmal (WGE-MOB-001)")
def batch_sync(
    body: WaagenQuittungBatch,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Synchronisiert Offline-Quittungen eines Geräts. Idempotent — Duplikate werden übersprungen."""
    results: list[dict] = []
    for q in body.quittungen:
        q.device_id = body.device_id  # Gerät aus Batch übernehmen
        try:
            # Inline-Logik (keine HTTP-Redirect nötig)
            existing = db.execute(text("""
                SELECT id FROM domain_agrar.waagen_quittungen
                 WHERE idempotency_key = :key AND tenant_id = :tid
            """), {"key": q.idempotency_key, "tid": tenant_id}).fetchone()
            if existing:
                results.append({"idempotency_key": q.idempotency_key, "status": "already_synced"})
                continue

            ticket = db.execute(text("""
                SELECT id FROM domain_agrar.weighing_tickets
                 WHERE id = :id AND tenant_id = :tid
            """), {"id": q.weighing_ticket_id, "tid": tenant_id}).fetchone()
            if not ticket:
                results.append({"idempotency_key": q.idempotency_key,
                                 "status": "rejected", "reason": "ticket_not_found"})
                continue

            quittung_id = str(uuid7())
            qam = q.quittiert_am or datetime.now(timezone.utc).isoformat()
            db.execute(text("""
                INSERT INTO domain_agrar.waagen_quittungen
                  (id, tenant_id, weighing_ticket_id, device_id, driver_id,
                   quittiert_am, gps_lat, gps_lon, bemerkung, idempotency_key, status)
                VALUES
                  (:id, :tid, :ticket, :device, :driver,
                   :qam, :lat, :lon, :bem, :key, 'quittiert')
            """), {
                "id": quittung_id, "tid": tenant_id,
                "ticket": q.weighing_ticket_id, "device": q.device_id,
                "driver": q.driver_id, "qam": qam,
                "lat": q.gps_lat, "lon": q.gps_lon,
                "bem": q.bemerkung, "key": q.idempotency_key,
            })
            db.execute(text("""
                UPDATE domain_agrar.weighing_tickets
                   SET quittiert = true, quittiert_am = :qam
                 WHERE id = :id AND tenant_id = :tid
            """), {"qam": qam, "id": q.weighing_ticket_id, "tid": tenant_id})
            results.append({"idempotency_key": q.idempotency_key,
                             "status": "synced", "id": quittung_id})
        except Exception as exc:
            results.append({"idempotency_key": q.idempotency_key,
                             "status": "error", "error": str(exc)})

    db.commit()
    synced = sum(1 for r in results if r["status"] == "synced")
    return {"device_id": body.device_id, "total": len(results),
            "synced": synced, "results": results}


@router.get("/pending", response_model=dict[str, Any], summary="Ausstehende Quittungen eines Geräts")
def get_pending(
    device_id: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Gibt Wiegetickets zurück, die auf Quittung durch das Gerät warten."""
    try:
        rows = db.execute(text("""
            SELECT wt.id, wt.ticket_number, wt.netto_gewicht_kg,
                   wt.created_at, wt.status
              FROM domain_agrar.weighing_tickets wt
             WHERE wt.tenant_id = :tid
               AND (wt.quittiert IS NULL OR wt.quittiert = false)
               AND wt.status NOT IN ('storniert')
             ORDER BY wt.created_at DESC
             LIMIT :lim
        """), {"tid": tenant_id, "lim": limit}).fetchall()
        return {
            "device_id": device_id,
            "pending_count": len(rows),
            "items": [
                {"id": str(r[0]), "ticket_number": r[1],
                 "netto_gewicht_kg": float(r[2]) if r[2] else None,
                 "created_at": r[3].isoformat() if r[3] else None,
                 "status": r[4]}
                for r in rows
            ],
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/tickets/{ticket_id}", response_model=dict[str, Any], summary="Wiegeticket + Quittungsstatus")
def get_ticket_with_quittung(
    ticket_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    ticket = db.execute(text("""
        SELECT id, ticket_number, netto_gewicht_kg, brutto_gewicht_kg,
               tara_gewicht_kg, status, quittiert, quittiert_am, created_at
          FROM domain_agrar.weighing_tickets
         WHERE id = :id AND tenant_id = :tid
    """), {"id": ticket_id, "tid": tenant_id}).fetchone()
    if not ticket:
        raise HTTPException(status_code=404, detail="Wiegeticket nicht gefunden")

    quittungen = db.execute(text("""
        SELECT id, device_id, driver_id, quittiert_am, gps_lat, gps_lon, bemerkung
          FROM domain_agrar.waagen_quittungen
         WHERE weighing_ticket_id = :id AND tenant_id = :tid
         ORDER BY quittiert_am DESC
    """), {"id": ticket_id, "tid": tenant_id}).fetchall()

    return {
        "id": str(ticket[0]),
        "ticket_number": ticket[1],
        "netto_gewicht_kg": float(ticket[2]) if ticket[2] else None,
        "brutto_gewicht_kg": float(ticket[3]) if ticket[3] else None,
        "tara_gewicht_kg": float(ticket[4]) if ticket[4] else None,
        "status": ticket[5],
        "quittiert": bool(ticket[6]),
        "quittiert_am": ticket[7].isoformat() if ticket[7] else None,
        "quittungen": [
            {"id": str(q[0]), "device_id": q[1], "driver_id": q[2],
             "quittiert_am": q[3].isoformat() if q[3] else None,
             "gps_lat": q[4], "gps_lon": q[5], "bemerkung": q[6]}
            for q in quittungen
        ],
    }
