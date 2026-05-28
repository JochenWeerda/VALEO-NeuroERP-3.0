from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.core.read_model_persistence import ReadModelSnapshotStore, ReadModelSnapshot, SnapshotCursor
from app.core.event_consumer_wiring import build_default_wiring
from app.core.database import get_db
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.read_model_snapshots_schemas import ReadModelSnapshotsOut


router = APIRouter(prefix="/read-models", tags=["read-model-snapshots"])

_wiring = build_default_wiring()


def _get_store(db: Session = Depends(get_db)) -> ReadModelSnapshotStore:
    return ReadModelSnapshotStore(db_session=db)

@router.post("/snapshots", status_code=201, summary="Snapshot anlegen",
    response_model=ReadModelSnapshotsOut
)
def create_snapshot(
    model_name: str,
    tenant_id: str,
    payload: dict,
    store: ReadModelSnapshotStore = Depends(_get_store),
):
    snapshot = ReadModelSnapshot.build(model_name=model_name, tenant_id=tenant_id, payload=payload)
    return store.save(snapshot)

@router.get("/snapshots/latest", summary="Latest snapshot abrufen",
    response_model=ReadModelSnapshotsOut
)
def get_latest_snapshot(
    model_name: str = Query(...),
    tenant_id: str = Query(...),
    store: ReadModelSnapshotStore = Depends(_get_store),
):
    snapshot = store.get_latest(model_name=model_name, tenant_id=tenant_id)
    if snapshot is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Kein Snapshot vorhanden")
    return snapshot

@router.get("/snapshots/page", summary="Snapshot page abrufen",
    response_model=ReadModelSnapshotsOut
)
def get_snapshot_page(
    model_name: str = Query(...),
    tenant_id: str = Query(...),
    last_snapshot_id: Optional[str] = Query(None),
    limit: int = Query(20),
    store: ReadModelSnapshotStore = Depends(_get_store),
):
    cursor = SnapshotCursor(last_snapshot_id=last_snapshot_id, limit=limit)
    page = store.get_page(model_name=model_name, tenant_id=tenant_id, cursor=cursor)
    return {"items": page, "count": len(page), "schema_version": 1}

@router.get("/wiring-health", summary="Wiring health abrufen",
    response_model=ReadModelSnapshotsOut
)
def get_wiring_health():
    return _wiring.health_check()

@router.get("/wiring-subjects", summary="Wiring subjects abrufen",
    response_model=ReadModelSnapshotsOut
)
def get_wiring_subjects():
    return {
        "mappings": _wiring.mappings,
        "total": len(_wiring.mappings),
        "schema_version": 1
    }
