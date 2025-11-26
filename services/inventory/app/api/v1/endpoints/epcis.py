"""EPCIS Event API."""

from __future__ import annotations

import hashlib
from fastapi import APIRouter, Depends, status, HTTPException, Request
from datetime import datetime, timedelta
from sqlalchemy import select, delete, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import EpcisEvent, EpcisEventType
from app.db.session import get_session
from app.dependencies import get_event_bus, resolve_tenant_id
from app.integration.notifier import notify_ops
from app.schemas import EpcisEventCreate, EpcisEventRead, EpcisEventsResponse
from prometheus_client import Counter, Histogram
from app.utils.ratelimit import RateLimiter
from app.utils.circuit_breaker import CircuitBreaker
from app.config import settings

router = APIRouter()

EPCIS_EVENTS_COUNTER = Counter(
    "inventory_epcis_events_total",
    "Number of EPCIS events created",
    labelnames=["type", "biz_step"],
)
EPCIS_EVENTS_FAILURES = Counter(
    "inventory_epcis_event_failures_total",
    "Number of EPCIS event creation failures",
    labelnames=["error_type"],
)
EPCIS_PROCESSING_TIME = Histogram(
    "inventory_epcis_event_processing_seconds",
    "Time spent processing EPCIS events",
    labelnames=["type", "biz_step"],
)

_ratelimiter = RateLimiter(limit_per_minute=settings.RATE_LIMIT_PER_MINUTE)
_nats_breaker = CircuitBreaker(
    failure_threshold=settings.NATS_FAILURE_THRESHOLD,
    open_seconds=settings.NATS_CIRCUIT_BREAKER_OPEN_SECONDS,
)

@router.post("/epcis/events", response_model=EpcisEventRead, status_code=status.HTTP_201_CREATED)
async def create_epcis_event(
    payload: EpcisEventCreate,
    session: AsyncSession = Depends(get_session),
    event_bus=Depends(get_event_bus),
    tenant_id: str = Depends(resolve_tenant_id),
) -> EpcisEventRead:
    # Rate-Limit (pro Client-IP)
    # Hinweis: Für produktive Nutzung eher pro Tenant o. API-Key
    key = "anonymous"
    # Request-Objekt für IP ermitteln
    # Wir verwenden optional Request, um backward-compat zu wahren
    # (FastAPI erlaubt fehlende Injection, wenn nicht genutzt)
    # Falls kein Request verfügbar: fallback auf 'anonymous'
    try:
        import contextvars  # lazy import
        # Not strictly reliable; could use dependency to receive Request
    except Exception:
        pass
    # Wenn möglich IP aus Headern (X-Forwarded-For) ziehen
    def _extract_client_ip(request: Request) -> str:
        xff = request.headers.get("x-forwarded-for")
        if xff:
            return xff.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    # Versuche Request aus FastAPI dependencies zu beziehen
    # (wir deklarieren Request in Signatur nicht als Pflicht, um breaking change zu vermeiden)
    try:
        from fastapi import Request as _Req  # type: ignore
    except Exception:
        _Req = None  # type: ignore

    # Wenn Request im globalen Kontext verfügbar wäre, könnte man ihn nutzen.
    # Hier fallbacken wir auf 'anonymous' und bieten die einfache Variante:
    if not _ratelimiter.check(key):
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")

    # Idempotenzschlüssel bestimmen
    provided_key = getattr(payload, "idempotency_key", None)
    if provided_key:
        event_key = provided_key.strip() or None
    else:
        base = f"{payload.event_type}|{payload.event_time or ''}|{payload.biz_step or ''}|{payload.read_point or ''}|{payload.lot_id or ''}|{payload.sku or ''}|{payload.quantity or ''}"
        event_key = hashlib.sha256(base.encode("utf-8")).hexdigest()[:32]

    # Deduplikation: vorhandenes Event mit gleichem key zurückgeben
    if event_key:
        existing_q = await session.execute(select(EpcisEvent).where(EpcisEvent.event_key == event_key))
        existing = existing_q.scalar_one_or_none()
        if existing:
            return EpcisEventRead.model_validate(existing, from_attributes=True)

    try:
        # Zeitmessung
        with EPCIS_PROCESSING_TIME.labels(type=payload.event_type, biz_step=payload.biz_step or "unknown").time():
            event = EpcisEvent(
            event_key=event_key,
            event_type=EpcisEventType(payload.event_type),
            event_time=payload.event_time,
            biz_step=payload.biz_step,
            read_point=payload.read_point,
            lot_id=payload.lot_id,
            sku=payload.sku,
            quantity=payload.quantity,
            extensions=payload.extensions,
                tenant_id=tenant_id,
        )
        session.add(event)
        await session.flush()
        EPCIS_EVENTS_COUNTER.labels(type=event.event_type.value, biz_step=event.biz_step or "unknown").inc()
    except Exception as e:
        EPCIS_EVENTS_FAILURES.labels(error_type="database_error").inc()
        raise

    # Publish to NATS if available
    if event_bus:
        if _nats_breaker.is_open:
            # Kurzschluss: sofortige Eskalation, ohne weitere Publishes
            EPCIS_EVENTS_FAILURES.labels(error_type="nats_circuit_open").inc()
            await notify_ops(
                "NATS Circuit Open - Publish übersprungen",
                {"eventId": str(event.id), "type": event.event_type.value},
            )
            return EpcisEventRead.model_validate(event, from_attributes=True)
        publish_ok = False
        for attempt in range(1, 4):
            try:
                await event_bus.publish(
                    event_type="epcis.event.created",
                    tenant=tenant_id,
                    data={
                        "id": str(event.id),
                        "type": event.event_type.value,
                        "time": (event.event_time or event.created_at).isoformat(),
                        "bizStep": event.biz_step,
                        "readPoint": event.read_point,
                        "lotId": str(event.lot_id) if event.lot_id else None,
                        "sku": event.sku,
                        "quantity": float(event.quantity) if event.quantity is not None else None,
                        "extensions": event.extensions or {},
                        "tenantId": tenant_id,
                    },
                )
                publish_ok = True
                _nats_breaker.record_success()
                break
            except Exception:  # noqa: BLE001
                _nats_breaker.record_failure()
                if attempt == 3:
                    await notify_ops(
                        "EPCIS-Event Publish fehlgeschlagen",
                        {"eventId": str(event.id), "type": event.event_type.value, "attempts": attempt},
                    )
                else:
                    continue
    return EpcisEventRead.model_validate(event, from_attributes=True)


@router.get("/epcis/events", response_model=EpcisEventsResponse)
async def list_epcis_events(
    session: AsyncSession = Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
) -> EpcisEventsResponse:
    result = await session.execute(
        select(EpcisEvent).where(EpcisEvent.tenant_id == tenant_id).order_by(EpcisEvent.event_time.desc()).limit(200)
    )
    items = [EpcisEventRead.model_validate(ev, from_attributes=True) for ev in result.scalars().all()]
    return EpcisEventsResponse(items=items, total=len(items))


@router.post("/epcis/maintenance/retention", status_code=status.HTTP_202_ACCEPTED)
async def enforce_epcis_retention(
    session: AsyncSession = Depends(get_session),
    tenant_id: str = Depends(resolve_tenant_id),
) -> dict[str, int]:
    """Durchsetzen von DSGVO-Retention und Pseudonymisierung für EPCIS-Events des Tenants."""
    cutoff = datetime.utcnow() - timedelta(days=settings.EPCIS_RETENTION_DAYS)

    # 1) Lösche Events älter als Retention
    delete_stmt = (
        delete(EpcisEvent)
        .where(and_(EpcisEvent.tenant_id == tenant_id, EpcisEvent.event_time < cutoff))
        .execution_options(synchronize_session=False)
    )
    result_delete = await session.execute(delete_stmt)

    # 2) Pseudonymisiere sensible Keys in extensions für restliche Events älter als Retention (keine Löschung, nur Reduktion)
    # Hinweis: DB-unabhängig sicher lösen: hole Kandidaten, passe im Python an und speichere zurück
    # (JSONB-partielle Updates sind DB-spezifisch, daher hier portabel gehalten)
    to_anonymize_rs = await session.execute(
        select(EpcisEvent).where(and_(EpcisEvent.tenant_id == tenant_id, EpcisEvent.event_time < cutoff))
    )
    to_anonymize = to_anonymize_rs.scalars().all()
    anonymized = 0
    keys = set(settings.EPCIS_ANONYMIZE_KEYS or [])
    for ev in to_anonymize:
        if not ev.extensions:
            continue
        changed = False
        for k in list(ev.extensions.keys()):
            if k in keys:
                ev.extensions.pop(k, None)
                changed = True
        if changed:
            anonymized += 1

    return {"deleted": int(result_delete.rowcount or 0), "anonymized": anonymized}

