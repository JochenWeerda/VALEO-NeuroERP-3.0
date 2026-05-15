"""Shared helpers for compat service classes."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.documents.router_helpers import get_repository, list_from_store
from app.domains.shared.events import IntegrationEvent, get_event_publisher
from app.infrastructure.eventbus.outbox import OutboxPublisher


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def doc_repo(db: Session):
    return get_repository(db)


def list_docs(db: Session, doc_type: str, limit: int = 1000, tenant_id: Optional[str] = None) -> list[dict[str, Any]]:
    repo = doc_repo(db)
    filters = {"tenantId": tenant_id} if tenant_id else None
    payload = list_from_store(doc_type, skip=0, limit=limit, filters=filters, repo=repo)
    docs = payload.get("data", []) if isinstance(payload, dict) else []
    if docs:
        return docs
    payload_mem = list_from_store(doc_type, skip=0, limit=limit, filters=filters, repo=None)
    return payload_mem.get("data", []) if isinstance(payload_mem, dict) else []


def cache_key(*parts: Any) -> str:
    return "compat:" + ":".join(str(p) for p in parts if p is not None and str(p) != "")


def safe_float(value: Any) -> float:
    try:
        return float(value or 0)
    except Exception:
        return 0.0


async def enqueue_event(
    db: Session,
    *,
    event_type: str,
    aggregate_id: str,
    payload: dict[str, Any],
    tenant_id: Optional[str] = None,
) -> None:
    outbox = OutboxPublisher(db, get_event_publisher())
    event = IntegrationEvent(
        aggregate_id=aggregate_id,
        timestamp=datetime.utcnow(),
        event_type=event_type,
        payload=payload,
    )
    await outbox.store_event(event, tenant_id=tenant_id)
