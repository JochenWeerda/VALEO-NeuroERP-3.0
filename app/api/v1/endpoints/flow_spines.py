from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.core.flow_spine_registry import get_flow_spine_catalog, get_flow_spine_workspace


router = APIRouter(prefix="/process/flow-spines", tags=["process", "flow-spines"])


@router.get("/catalog", response_model=dict)
def get_catalog() -> dict[str, Any]:
    return get_flow_spine_catalog()


@router.get("/{process_key}", response_model=dict)
def get_workspace(process_key: str) -> dict[str, Any]:
    try:
        return get_flow_spine_workspace(process_key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown flow spine process '{process_key}'") from exc
