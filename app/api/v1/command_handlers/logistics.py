"""Tour commands behind the existing logistics routes."""
import uuid
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional
from app.domains.logistik.strecke import stopp_mit_zielort
from typing import Any, Callable
from fastapi import HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body


class TourStopIn(BaseModel):
    __module__ = "app.api.v1.endpoints.logistics_tours"  # Preserve public OpenAPI schema identity.
    stop_order: Optional[int] = None
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    customer_id: Optional[str] = None
    delivery_note_ref: Optional[str] = None
    planned_arrival: Optional[datetime] = None


class TourIn(BaseModel):
    __module__ = "app.api.v1.endpoints.logistics_tours"  # Preserve public OpenAPI schema identity.
    date: Optional[datetime] = None
    vehicle_id: Optional[str] = None
    driver_id: Optional[str] = None
    status: Optional[str] = "GEPLANT"
    notes: Optional[str] = None
    stops: Optional[List[TourStopIn]] = []


def insert_tour(
    db: Session,
    *,
    tenant_id: str,
    _lookup_sales_delivery_note: Callable,
    date_value: Optional[datetime],
    vehicle_id: Optional[str],
    driver_id: Optional[str],
    notes: Optional[str],
    stops: Optional[List[dict]] = None,
    status: str = "GEPLANT",
    commit: bool = True,
) -> Dict[str, Any]:
    """INSERT Tour + Stopps ausschliesslich fuer ``tenant_id`` (Token-Mandant)."""
    if not tenant_id or not str(tenant_id).strip():
        raise HTTPException(403, "Tenant required")
    tour_id = str(uuid.uuid4())
    db.execute(
        text("""
            INSERT INTO domain_logistics.tours
                (id, date, vehicle_id, driver_id, status, notes, tenant_id)
            VALUES (:id, :date, :vehicle_id, :driver_id, :status, :notes, :tenant_id)
        """),
        {
            "id": tour_id,
            "date": date_value,
            "vehicle_id": vehicle_id,
            "driver_id": driver_id,
            "status": status or "GEPLANT",
            "notes": notes,
            "tenant_id": tenant_id,
        },
    )
    stop_rows: List[Dict[str, Any]] = []
    for i, stop in enumerate(stops or []):
        stop_id = str(uuid.uuid4())
        ref = stop.get("delivery_note_ref")
        if isinstance(ref, str) and ref.strip():
            if _lookup_sales_delivery_note(db, ref.strip(), tenant_id) is None:
                raise HTTPException(
                    404,
                    "Delivery note not found in the authenticated tenant",
                )
        daten = stopp_mit_zielort(db, tenant_id, stop)
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
                "stop_order": stop.get("stop_order") if stop.get("stop_order") is not None else i,
                "address": daten.get("address"),
                "lat": daten.get("lat"),
                "lng": daten.get("lng"),
                "customer_id": stop.get("customer_id"),
                "delivery_note_ref": stop.get("delivery_note_ref"),
                "planned_arrival": stop.get("planned_arrival"),
                "tenant_id": tenant_id,
            },
        )
        stop_rows.append({"id": stop_id, **daten})
    if commit:
        db.commit()
    return {
        "id": tour_id,
        "date": date_value,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "status": status or "GEPLANT",
        "notes": notes,
        "stops": stop_rows,
        "tenant_id": tenant_id,
    }


def action_tour_anlegen(request: Request, body: dict[str, Any], db: Session, tenant_id: str, *, insert_tour: Callable) -> MaskActionResult:
    """CE fuer logistik/tourenplanung:anlegen — dryRun ohne INSERT; Token-Mandant."""
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="anlegen",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )

    date_raw = payload.get("date")
    date_value: Optional[datetime] = None
    if date_raw not in (None, ""):
        try:
            date_value = datetime.fromisoformat(str(date_raw).replace("Z", "+00:00"))
        except ValueError:
            return MaskActionResult(
                actionKey="anlegen",
                mode=mode,
                success=False,
                error="date muss ISO-Datum/Zeit sein.",
                validationErrors=[
                    {"field": "date", "message": "ISO-Datum/Zeit Pflichtformat", "severity": "blocking"}
                ],
            )
    vehicle_id = str(payload["vehicle_id"]).strip() if payload.get("vehicle_id") else None
    driver_id = str(payload["driver_id"]).strip() if payload.get("driver_id") else None
    notes = str(payload["notes"]).strip() if payload.get("notes") not in (None, "") else None
    raw_stops = payload.get("stops") if isinstance(payload.get("stops"), list) else []
    stops = [dict(s) for s in raw_stops if isinstance(s, dict)]

    preview = {
        "date": date_value.isoformat() if date_value else None,
        "vehicle_id": vehicle_id,
        "driver_id": driver_id,
        "notes": notes,
        "stops": stops,
        "tenant_id": tenant_id,
    }
    if mode != "execute":
        db.rollback()
        return MaskActionResult(
            actionKey="anlegen",
            mode=mode,
            success=True,
            summary="Tour wuerde angelegt — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )

    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        row = insert_tour(
            db,
            tenant_id=tenant_id,
            date_value=date_value,
            vehicle_id=vehicle_id,
            driver_id=driver_id,
            notes=notes,
            stops=stops,
            commit=False,
        )
        entity_id = str(row["id"])
        actor = request.headers.get("X-User-ID") or "logistik-user"
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="anlegen",
            entity_type="logistics_tour",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Tour angelegt by {actor}",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="logistik.tour.created",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="anlegen", mode=mode, success=False, error=detail)
    except Exception:
        db.rollback()
        return MaskActionResult(
            actionKey="anlegen",
            mode=mode,
            success=False,
            error="Tour konnte nicht angelegt werden.",
        )

    return MaskActionResult(
        actionKey="anlegen",
        mode=mode,
        success=True,
        summary="Tour angelegt.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


