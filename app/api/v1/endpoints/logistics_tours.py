"""
Logistik – Tourenplanung-Engine (Feature 1 + Track & Trace / ePOD Feature 3)
Thin-router pattern: sqlalchemy.text() SQL, domain_logistics schema.
Schema/Tabellen: Alembic-Revision ``log_logistics_core_20260612`` (kein Runtime-DDL).
"""

from __future__ import annotations

import math
import uuid
from datetime import datetime
from typing import Optional, List, Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query, Header
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class LogisticsTourOut(BaseSchema):
    """Typed response schema for LogisticsTourOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/logistik", tags=["logistik", "tourenplanung"])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """Haversine-Distanz in km."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _safe_number(value: Any, default: float = 0.0) -> float:
    """Return numeric DB aggregate values without leaking SQLAlchemy/mock sentinels."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _lookup_sales_delivery_note(db: Session, ref: str, tenant_id: str) -> Optional[Dict[str, Any]]:
    """Lieferschein zu tour_stops.delivery_note_ref (UUID oder delivery_note_number), tenant-isoliert."""
    r = ref.strip()
    if not r:
        return None
    row = db.execute(
        text(
            """
            SELECT id, delivery_note_number, status, delivery_date, customer_id, sales_order_id
            FROM domain_sales.delivery_notes
            WHERE tenant_id = :tenant_id
              AND (id::text = :ref OR delivery_note_number = :ref)
            LIMIT 1
            """
        ),
        {"tenant_id": tenant_id, "ref": r},
    ).mappings().first()
    if not row:
        return None
    d = dict(row)
    dd = d.get("delivery_date")
    so = d.get("sales_order_id")
    return {
        "id": str(d["id"]),
        "delivery_note_number": d.get("delivery_note_number"),
        "status": d.get("status"),
        "delivery_date": dd.isoformat() if dd is not None and hasattr(dd, "isoformat") else (str(dd) if dd else None),
        "customer_id": d.get("customer_id"),
        "sales_order_id": str(so) if so is not None else None,
    }


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class TourStopIn(BaseModel):
    stop_order: Optional[int] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    customer_id: Optional[str] = None
    delivery_note_ref: Optional[str] = None
    planned_arrival: Optional[datetime] = None


class TourStopPatch(BaseModel):
    status: Optional[str] = None
    actual_arrival: Optional[datetime] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    delivery_note_ref: Optional[str] = None


class TourIn(BaseModel):
    date: Optional[datetime] = None
    vehicle_id: Optional[str] = None
    driver_id: Optional[str] = None
    status: Optional[str] = "GEPLANT"
    notes: Optional[str] = None
    stops: Optional[List[TourStopIn]] = []


class TourEventIn(BaseModel):
    event_type: str  # START/STOP/PAUSE/GPS/DELIVERY/PROBLEM
    lat: Optional[float] = None
    lng: Optional[float] = None
    notes: Optional[str] = None
    driver_ref: Optional[str] = None


class PodIn(BaseModel):
    signature_base64: str
    recipient_name: str
    delivered_at: str
    notes: Optional[str] = None
    photo_base64: Optional[str] = None


class TourCancelIn(BaseModel):
    grund: Optional[str] = None


# ---------------------------------------------------------------------------
# Read-Spine: Lieferschein-Referenz (LOG-SPINE-RAND-001)
# ---------------------------------------------------------------------------

@router.get(
    "/sales-delivery-note-by-ref",
    summary="Lieferschein zu Referenz (Read)",
    response_model=LogisticsTourOut,
)
def resolve_sales_delivery_note_by_ref(
    ref: str = Query(..., min_length=1, description="Lieferschein-ID oder delivery_note_number"),
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Read-only: Auflösung von ``delivery_note_ref`` gegen ``domain_sales.delivery_notes``."""
    if not x_tenant_id:
        raise HTTPException(
            status_code=422,
            detail="X-Tenant-ID erforderlich zur tenant-sicheren Auflösung.",
        )
    try:
        summary = _lookup_sales_delivery_note(db, ref, x_tenant_id)
        if not summary:
            raise HTTPException(status_code=404, detail="Kein Lieferschein für diese Referenz")
        return summary
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Tours — LIST + CREATE
# ---------------------------------------------------------------------------

@router.get("/tours", summary="Tours auflisten",
    response_model=list[LogisticsTourOut]
)
def list_tours(
    date: Optional[str] = Query(None),
    vehicle_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Liste aller Touren mit optionalen Filtern."""
    try:
        conditions = ["1=1"]
        params: Dict[str, Any] = {}
        if x_tenant_id:
            conditions.append("tenant_id = :tenant_id")
            params["tenant_id"] = x_tenant_id
        if date:
            conditions.append("DATE(date) = :date")
            params["date"] = date
        if vehicle_id:
            conditions.append("vehicle_id = :vehicle_id")
            params["vehicle_id"] = vehicle_id
        if status:
            conditions.append("status = :status")
            params["status"] = status
        where = " AND ".join(conditions)
        rows = db.execute(
            text(f"SELECT * FROM domain_logistics.tours WHERE {where} ORDER BY created_at DESC"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            params,
        ).mappings().all()
        tour_rows = [dict(r) for r in rows]
        ids = [str(r["id"]) for r in tour_rows if r.get("id")]
        if ids:
            bind = {f"id{i}": tid for i, tid in enumerate(ids)}
            placeholders = ", ".join(f":id{i}" for i in range(len(ids)))
            counts = db.execute(
                text(
                    f"SELECT tour_id, COUNT(*)::int AS stop_count FROM domain_logistics.tour_stops "  # nosec S608
                    f"WHERE tour_id IN ({placeholders}) GROUP BY tour_id"
                ),
                bind,
            ).mappings().all()
            cmap = {str(c["tour_id"]): int(c["stop_count"] or 0) for c in counts}
            for r in tour_rows:
                r["stop_count"] = cmap.get(str(r["id"]), 0)
        else:
            for r in tour_rows:
                r["stop_count"] = 0
        return tour_rows
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post("/tours", status_code=201, summary="Tour anlegen",
    response_model=LogisticsTourOut
)
def create_tour(
    body: TourIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Tour anlegen inkl. Stopps."""
    try:
        tour_id = str(uuid.uuid4())
        db.execute(
            text("""
                INSERT INTO domain_logistics.tours
                    (id, date, vehicle_id, driver_id, status, notes, tenant_id)
                VALUES (:id, :date, :vehicle_id, :driver_id, :status, :notes, :tenant_id)
            """),
            {
                "id": tour_id,
                "date": body.date,
                "vehicle_id": body.vehicle_id,
                "driver_id": body.driver_id,
                "status": body.status or "GEPLANT",
                "notes": body.notes,
                "tenant_id": x_tenant_id,
            },
        )
        stops = []
        for i, stop in enumerate(body.stops or []):
            stop_id = str(uuid.uuid4())
            db.execute(
                text("""
                    INSERT INTO domain_logistics.tour_stops
                        (id, tour_id, stop_order, address, lat, lng, customer_id,
                         delivery_note_ref, planned_arrival, status, tenant_id)
                    VALUES (:id, :tour_id, :stop_order, :address, :lat, :lng,
                            :customer_id, :delivery_note_ref, :planned_arrival, 'GEPLANT', :tenant_id)
                """),
                {
                    "id": stop_id,
                    "tour_id": tour_id,
                    "stop_order": stop.stop_order if stop.stop_order is not None else i,
                    "address": stop.address,
                    "lat": stop.lat,
                    "lng": stop.lng,
                    "customer_id": stop.customer_id,
                    "delivery_note_ref": stop.delivery_note_ref,
                    "planned_arrival": stop.planned_arrival,
                    "tenant_id": x_tenant_id,
                },
            )
            stops.append({"id": stop_id, **stop.model_dump()})
        db.commit()
        return {"id": tour_id, **body.model_dump(exclude={"stops"}), "stops": stops, "tenant_id": x_tenant_id}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Tour detail
# ---------------------------------------------------------------------------

@router.get("/tours/{tour_id}", summary="Tour abrufen",
    response_model=LogisticsTourOut
)
def get_tour(
    tour_id: str,
    include_delivery_hints: bool = Query(
        False,
        description="Wenn true und X-Tenant-ID: pro Stopp ``delivery_note_hint`` aus domain_sales",
    ),
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Tour-Detail mit Stopps und Ereignissen."""
    try:
        row = db.execute(
            text("SELECT * FROM domain_logistics.tours WHERE id = :id"),
            {"id": tour_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail=f"Tour {tour_id} nicht gefunden")
        stops = db.execute(
            text("SELECT * FROM domain_logistics.tour_stops WHERE tour_id = :tid ORDER BY stop_order"),
            {"tid": tour_id},
        ).mappings().all()
        events = db.execute(
            text("SELECT * FROM domain_logistics.tour_events WHERE tour_id = :tid ORDER BY event_ts"),
            {"tid": tour_id},
        ).mappings().all()
        stops_list: List[Dict[str, Any]] = [dict(s) for s in stops]
        if include_delivery_hints and x_tenant_id:
            cache: Dict[str, Optional[Dict[str, Any]]] = {}
            for s in stops_list:
                rfn = (s.get("delivery_note_ref") or "").strip()
                if not rfn:
                    s["delivery_note_hint"] = None
                    continue
                if rfn not in cache:
                    cache[rfn] = _lookup_sales_delivery_note(db, rfn, x_tenant_id)
                s["delivery_note_hint"] = cache[rfn]
        return {**dict(row), "stops": stops_list, "events": [dict(e) for e in events]}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Stops
# ---------------------------------------------------------------------------

@router.post("/tours/{tour_id}/stops", status_code=201, summary="Stop hinzufügen",
    response_model=LogisticsTourOut
)
def add_stop(
    tour_id: str,
    body: TourStopIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Stopp zur Tour hinzufügen."""
    try:
        stop_id = str(uuid.uuid4())
        # auto-assign next stop_order
        if body.stop_order is None:
            result = db.execute(
                text("SELECT COALESCE(MAX(stop_order), -1) + 1 AS next_order FROM domain_logistics.tour_stops WHERE tour_id = :tid"),
                {"tid": tour_id},
            ).scalar()
            stop_order = result if result is not None else 0
        else:
            stop_order = body.stop_order
        db.execute(
            text("""
                INSERT INTO domain_logistics.tour_stops
                    (id, tour_id, stop_order, address, lat, lng, customer_id,
                     delivery_note_ref, planned_arrival, status, tenant_id)
                VALUES (:id, :tour_id, :stop_order, :address, :lat, :lng,
                        :customer_id, :delivery_note_ref, :planned_arrival, 'GEPLANT', :tenant_id)
            """),
            {
                "id": stop_id,
                "tour_id": tour_id,
                "stop_order": stop_order,
                "address": body.address,
                "lat": body.lat,
                "lng": body.lng,
                "customer_id": body.customer_id,
                "delivery_note_ref": body.delivery_note_ref,
                "planned_arrival": body.planned_arrival,
                "tenant_id": x_tenant_id,
            },
        )
        db.commit()
        return {"id": stop_id, "tour_id": tour_id, "stop_order": stop_order, **body.model_dump()}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.patch("/tours/{tour_id}/stops/{stop_id}", summary="Stop aktualisieren",
    response_model=LogisticsTourOut
)
def patch_stop(
    tour_id: str,
    stop_id: str,
    body: TourStopPatch,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Stopp-Status oder Ankunftszeit aktualisieren."""
    try:
        updates = []
        params: Dict[str, Any] = {"stop_id": stop_id}
        if body.status is not None:
            updates.append("status = :status")
            params["status"] = body.status
        if body.actual_arrival is not None:
            updates.append("actual_arrival = :actual_arrival")
            params["actual_arrival"] = body.actual_arrival
        if body.address is not None:
            updates.append("address = :address")
            params["address"] = body.address
        if body.lat is not None:
            updates.append("lat = :lat")
            params["lat"] = body.lat
        if body.lng is not None:
            updates.append("lng = :lng")
            params["lng"] = body.lng
        if body.delivery_note_ref is not None:
            updates.append("delivery_note_ref = :delivery_note_ref")
            params["delivery_note_ref"] = body.delivery_note_ref
        if not updates:
            raise HTTPException(status_code=422, detail="Keine Felder zum Aktualisieren")
        db.execute(
            text(f"UPDATE domain_logistics.tour_stops SET {', '.join(updates)} WHERE id = :stop_id"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            params,
        )
        db.commit()
        row = db.execute(
            text("SELECT * FROM domain_logistics.tour_stops WHERE id = :stop_id"),
            {"stop_id": stop_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail=f"Stopp {stop_id} nicht gefunden")
        return dict(row)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/tours/{tour_id}/cancel",
    summary="Tour stornieren (fail-closed)",
    response_model=LogisticsTourOut,
)
def cancel_tour(
    tour_id: str,
    body: TourCancelIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Tour nur im Status GEPLANT stornieren; keine gelieferten Stopps (ABGELIEFERT)."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    try:
        row = db.execute(
            text("SELECT * FROM domain_logistics.tours WHERE id = :id"),
            {"id": tour_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail=f"Tour {tour_id} nicht gefunden")
        t = dict(row)
        if t.get("tenant_id") and t["tenant_id"] != x_tenant_id:
            raise HTTPException(status_code=403, detail="Tenant passt nicht zur Tour.")
        st = (t.get("status") or "").upper()
        if st == "STORNIERT":
            raise HTTPException(status_code=409, detail="Tour ist bereits storniert.")
        if st != "GEPLANT":
            raise HTTPException(
                status_code=409,
                detail=f"Tour nicht stornierbar im Status {t.get('status')!r} (nur GEPLANT).",
            )
        delivered = db.execute(
            text(
                "SELECT COUNT(*)::int FROM domain_logistics.tour_stops "
                "WHERE tour_id = :tid AND status = 'ABGELIEFERT'"
            ),
            {"tid": tour_id},
        ).scalar()
        if int(delivered or 0) > 0:
            raise HTTPException(
                status_code=409,
                detail="Tour hat bereits gelieferte Stopps (ABGELIEFERT) — Storno nicht erlaubt.",
            )
        grund = (body.grund or "").strip() or "STORNO"
        note_append = f" [STORNO: {grund}]"
        new_notes = (t.get("notes") or "") + note_append
        db.execute(
            text(
                "UPDATE domain_logistics.tours SET status = 'STORNIERT', notes = :notes WHERE id = :id"
            ),
            {"id": tour_id, "notes": new_notes[:8000]},
        )
        db.commit()
        out = db.execute(
            text("SELECT * FROM domain_logistics.tours WHERE id = :id"),
            {"id": tour_id},
        ).mappings().first()
        return dict(out) if out else {}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/tours/{tour_id}/stops/{stop_id}/cancel",
    summary="Tour-Stopp stornieren (fail-closed)",
    response_model=LogisticsTourOut,
)
def cancel_stop(
    tour_id: str,
    stop_id: str,
    body: TourCancelIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Stopp nur in frühen Status stornieren (GEPLANT, ANGEFAHREN)."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    try:
        srow = db.execute(
            text(
                "SELECT * FROM domain_logistics.tour_stops WHERE id = :sid AND tour_id = :tid"
            ),
            {"sid": stop_id, "tid": tour_id},
        ).mappings().first()
        if not srow:
            raise HTTPException(status_code=404, detail="Stopp nicht gefunden")
        s = dict(srow)
        if s.get("tenant_id") and s["tenant_id"] != x_tenant_id:
            raise HTTPException(status_code=403, detail="Tenant passt nicht zum Stopp.")
        st = (s.get("status") or "").upper()
        if st == "STORNIERT":
            raise HTTPException(status_code=409, detail="Stopp ist bereits storniert.")
        if st == "ABGELIEFERT":
            raise HTTPException(status_code=409, detail="Gelieferter Stopp kann nicht storniert werden.")
        if st not in ("GEPLANT", "ANGEFAHREN"):
            raise HTTPException(
                status_code=409,
                detail=f"Stopp nicht stornierbar im Status {s.get('status')!r}.",
            )
        grund = (body.grund or "").strip() or "STORNO"
        db.execute(
            text(
                "UPDATE domain_logistics.tour_stops SET status = 'STORNIERT', "
                "address = COALESCE(address,'') || :tag WHERE id = :sid"
            ),
            {"sid": stop_id, "tag": f" [STORNO:{grund}]"[:200]},
        )
        db.commit()
        row = db.execute(
            text("SELECT * FROM domain_logistics.tour_stops WHERE id = :sid"),
            {"sid": stop_id},
        ).mappings().first()
        return dict(row) if row else {}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------


@router.post(
    "/tours/{tour_id}/events",
    status_code=201,
    summary="Tour-Ereignis erfassen",
    response_model=LogisticsTourOut,
)
def add_event(
    tour_id: str,
    body: TourEventIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """GPS-Event oder Fahrerereignis speichern."""
    try:
        event_id = str(uuid.uuid4())
        now = datetime.utcnow()
        db.execute(
            text("""
                INSERT INTO domain_logistics.tour_events
                    (id, tour_id, event_type, event_ts, lat, lng, notes, driver_ref, tenant_id)
                VALUES (:id, :tour_id, :event_type, :event_ts, :lat, :lng, :notes, :driver_ref, :tenant_id)
            """),
            {
                "id": event_id,
                "tour_id": tour_id,
                "event_type": body.event_type,
                "event_ts": now,
                "lat": body.lat,
                "lng": body.lng,
                "notes": body.notes,
                "driver_ref": body.driver_ref,
                "tenant_id": x_tenant_id,
            },
        )
        db.commit()
        return {"id": event_id, "tour_id": tour_id, "event_ts": now.isoformat(), **body.model_dump()}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Live-Status
# ---------------------------------------------------------------------------

@router.get("/tours/{tour_id}/live-status", summary="Status live",
    response_model=LogisticsTourOut
)
def live_status(
    tour_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Letzte GPS-Position, nächster Stopp, ETA."""
    try:
        last_gps = db.execute(
            text("""
                SELECT * FROM domain_logistics.tour_events
                WHERE tour_id = :tid AND event_type = 'GPS'
                ORDER BY event_ts DESC LIMIT 1
            """),
            {"tid": tour_id},
        ).mappings().first()
        next_stop = db.execute(
            text("""
                SELECT * FROM domain_logistics.tour_stops
                WHERE tour_id = :tid AND status = 'GEPLANT'
                ORDER BY stop_order LIMIT 1
            """),
            {"tid": tour_id},
        ).mappings().first()
        return {
            "tour_id": tour_id,
            "last_gps_event": dict(last_gps) if last_gps else None,
            "next_stop": dict(next_stop) if next_stop else None,
            "eta": next_stop["planned_arrival"].isoformat() if next_stop and next_stop["planned_arrival"] else None,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Optimierung (Nearest-Neighbor TSP)
# ---------------------------------------------------------------------------

@router.post("/tours/{tour_id}/optimize", summary="Stops optimize",
    response_model=LogisticsTourOut
)
def optimize_stops(
    tour_id: str,
    depot_lat: float = Query(0.0),
    depot_lng: float = Query(0.0),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Nearest-Neighbor-Optimierung der Stopp-Reihenfolge."""
    try:
        rows = db.execute(
            text("SELECT * FROM domain_logistics.tour_stops WHERE tour_id = :tid ORDER BY stop_order"),
            {"tid": tour_id},
        ).mappings().all()
        if not rows:
            raise HTTPException(status_code=404, detail="Keine Stopps gefunden")

        stops = [dict(r) for r in rows]
        # Nearest-Neighbor from depot
        remaining = stops.copy()
        ordered: List[Dict[str, Any]] = []
        cur_lat, cur_lng = depot_lat, depot_lng
        while remaining:
            nearest = min(
                remaining,
                key=lambda s: _haversine(cur_lat, cur_lng, s.get("lat") or 0.0, s.get("lng") or 0.0),
            )
            ordered.append(nearest)
            cur_lat = nearest.get("lat") or 0.0
            cur_lng = nearest.get("lng") or 0.0
            remaining.remove(nearest)

        # Persist new order
        for new_order, stop in enumerate(ordered):
            db.execute(
                text("UPDATE domain_logistics.tour_stops SET stop_order = :o WHERE id = :id"),
                {"o": new_order, "id": stop["id"]},
            )
        db.commit()
        return {"tour_id": tour_id, "optimized_order": [s["id"] for s in ordered]}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Track & Trace (Feature 3)
# ---------------------------------------------------------------------------

@router.get("/tracking/{tour_id}", summary="Tracking public",
    response_model=LogisticsTourOut
)
def public_tracking(
    tour_id: str,
    share_token: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Öffentlicher Tracking-Link – letzte GPS-Position, aktueller Stopp, ETA."""
    try:
        last_gps = db.execute(
            text("""
                SELECT lat, lng, event_ts FROM domain_logistics.tour_events
                WHERE tour_id = :tid AND event_type = 'GPS'
                ORDER BY event_ts DESC LIMIT 1
            """),
            {"tid": tour_id},
        ).mappings().first()
        current_stop = db.execute(
            text("""
                SELECT id, address, status, planned_arrival, actual_arrival
                FROM domain_logistics.tour_stops
                WHERE tour_id = :tid AND status IN ('GEPLANT', 'ANGEFAHREN')
                ORDER BY stop_order LIMIT 1
            """),
            {"tid": tour_id},
        ).mappings().first()
        delivery_status = db.execute(
            text("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'ABGELIEFERT') AS delivered,
                    COUNT(*) AS total
                FROM domain_logistics.tour_stops WHERE tour_id = :tid
            """),
            {"tid": tour_id},
        ).mappings().first()
        return {
            "tour_id": tour_id,
            "last_position": dict(last_gps) if last_gps else None,
            "current_stop": dict(current_stop) if current_stop else None,
            "estimated_arrival": current_stop["planned_arrival"].isoformat() if current_stop and current_stop["planned_arrival"] else None,
            "delivery_status": dict(delivery_status) if delivery_status else None,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# ePOD
# ---------------------------------------------------------------------------

@router.post("/tours/{tour_id}/stops/{stop_id}/pod", status_code=201, summary="Pod save",
    response_model=LogisticsTourOut
)
def save_pod(
    tour_id: str,
    stop_id: str,
    body: PodIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Proof of Delivery speichern – setzt Stopp-Status auf ABGELIEFERT."""
    try:
        import json
        pod_json = json.dumps(body.model_dump())
        db.execute(
            text("""
                UPDATE domain_logistics.tour_stops
                SET pod_data = :pod::jsonb, status = 'ABGELIEFERT'
                WHERE id = :stop_id AND tour_id = :tour_id
            """),
            {"pod": pod_json, "stop_id": stop_id, "tour_id": tour_id},
        )
        db.commit()
        row = db.execute(
            text("SELECT * FROM domain_logistics.tour_stops WHERE id = :stop_id"),
            {"stop_id": stop_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail=f"Stopp {stop_id} nicht gefunden")

        # Belegbruch schließen: Lieferschein-Status auf 'delivered' setzen
        dn_ref = row.get("delivery_note_ref")
        if dn_ref and x_tenant_id:
            try:
                db.execute(
                    text("""
                        UPDATE domain_sales.delivery_notes
                        SET status = 'delivered', updated_at = NOW()
                        WHERE (id = :ref OR delivery_note_number = :ref)
                          AND tenant_id = :tid
                          AND status NOT IN ('delivered', 'BERECHNET')
                    """),
                    {"ref": dn_ref, "tid": x_tenant_id},
                )
                db.commit()
            except Exception:  # noqa: BLE001 — Lieferschein-Update nicht kritisch für POD-Erfolg
                pass

        return dict(row)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get("/tours/{tour_id}/stops/{stop_id}/pod", summary="Pod abrufen",
    response_model=LogisticsTourOut
)
def get_pod(
    tour_id: str,
    stop_id: str,
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """ePOD abrufen."""
    try:
        row = db.execute(
            text("SELECT pod_data FROM domain_logistics.tour_stops WHERE id = :stop_id AND tour_id = :tour_id"),
            {"stop_id": stop_id, "tour_id": tour_id},
        ).mappings().first()
        if not row:
            raise HTTPException(status_code=404, detail=f"Stopp {stop_id} nicht gefunden")
        if not row["pod_data"]:
            raise HTTPException(status_code=404, detail="Kein ePOD vorhanden")
        return {"stop_id": stop_id, "tour_id": tour_id, "pod": row["pod_data"]}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Transportstatistik (Feature 4)
# ---------------------------------------------------------------------------

@router.get("/statistics", summary="Statistics abrufen",
    response_model=LogisticsTourOut
)
def get_statistics(
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    vehicle_id: Optional[str] = Query(None),
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Transportstatistik: Touren, Stopps, km, Pünktlichkeit."""
    try:
        tour_conds = ["1=1"]
        params: Dict[str, Any] = {}
        if x_tenant_id:
            tour_conds.append("t.tenant_id = :tenant_id")
            params["tenant_id"] = x_tenant_id
        if date_from:
            tour_conds.append("t.date >= :date_from")
            params["date_from"] = date_from
        if date_to:
            tour_conds.append("t.date <= :date_to")
            params["date_to"] = date_to
        if vehicle_id:
            tour_conds.append("t.vehicle_id = :vehicle_id")
            params["vehicle_id"] = vehicle_id

        where = " AND ".join(tour_conds)

        stats = db.execute(
            # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            text(f"""
                SELECT
                    COUNT(DISTINCT t.id)                                        AS total_tours,
                    COUNT(s.id) FILTER (WHERE s.status = 'ABGELIEFERT')        AS total_stops_delivered,
                    COUNT(s.id)                                                  AS total_stops,
                    COUNT(s.id) FILTER (WHERE s.status = 'PROBLEM')             AS problem_stops,
                    COUNT(s.id) FILTER (
                        WHERE s.actual_arrival IS NOT NULL
                          AND s.planned_arrival IS NOT NULL
                          AND s.actual_arrival <= s.planned_arrival
                    )                                                            AS on_time_stops
                FROM domain_logistics.tours t
                LEFT JOIN domain_logistics.tour_stops s ON s.tour_id = t.id
                WHERE {where}
            """),
            params,
        ).mappings().first()

        # km aus GPS-Events (Haversine-Summe)
        gps_rows = db.execute(
            # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            text(f"""
                SELECT e.lat, e.lng, e.event_ts
                FROM domain_logistics.tour_events e
                JOIN domain_logistics.tours t ON t.id = e.tour_id
                WHERE e.event_type = 'GPS' AND {where}
                ORDER BY e.tour_id, e.event_ts
            """),
            params,
        ).mappings().all()

        total_km = 0.0
        prev: Optional[Dict] = None
        for gps in gps_rows:
            if prev and gps["lat"] and gps["lng"] and prev["lat"] and prev["lng"]:
                total_km += _haversine(prev["lat"], prev["lng"], gps["lat"], gps["lng"])
            prev = dict(gps)

        stats_dict = dict(stats or {})
        total_tours = _safe_number(stats_dict.get("total_tours"))
        total_stops = _safe_number(stats_dict.get("total_stops"))
        on_time = _safe_number(stats_dict.get("on_time_stops"))
        delivered = _safe_number(stats_dict.get("total_stops_delivered"))
        problems = _safe_number(stats_dict.get("problem_stops"))

        return {
            "total_tours": int(total_tours),
            "total_stops_delivered": int(delivered),
            "total_km_driven": round(total_km, 2),
            "on_time_rate": round(on_time / delivered, 4) if delivered > 0 else None,
            "avg_stops_per_tour": round(total_stops / total_tours, 2) if total_tours > 0 else None,
            "problem_rate": round(problems / total_stops, 4) if total_stops > 0 else None,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
