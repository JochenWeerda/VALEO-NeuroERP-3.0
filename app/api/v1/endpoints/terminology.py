"""
Terminology API for the Landhandel bilingual terminology registry.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.terminology_registry import build_landhandel_terminology_registry

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.terminology_schemas import TerminologyOut


router = APIRouter(prefix="/terminology", tags=["terminology", "i18n"])


@router.get("/registry", summary="Landhandel terminology registry",
    response_model=TerminologyOut
)
def get_terminology_registry(
    domain: str | None = Query(default=None, description="Optional domain filter"),
    q: str | None = Query(default=None, description="Optional search query"),
) -> dict:
    registry = build_landhandel_terminology_registry()
    return registry.as_dict(query=q, domain=domain)


@router.get("/terms/{term_key}", summary="Single terminology entry",
    response_model=TerminologyOut
)
def get_terminology_entry(term_key: str) -> dict:
    registry = build_landhandel_terminology_registry()
    entry = registry.by_term_key(term_key)
    if entry is None:
        raise HTTPException(status_code=404, detail=f"Terminology entry {term_key!r} not found")
    return entry.as_dict()
