"""
Terminology API for the Landhandel bilingual terminology registry.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.core.terminology_registry import build_landhandel_terminology_registry

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.terminology_schemas import TerminologyOut


router = APIRouter(prefix="/terminology", tags=["terminology", "i18n"])


class BegriffOut(BaseSchema):
    """Eine Zeile der Studio-Liste ``admin/terminologie`` (Listen flach, Synonyme als Text)."""
    term_key: str
    domain: str
    canonical_de: str
    canonical_en: str
    description_de: str
    synonyms_de: str
    avoid_de: str


@router.get("/begriffe", summary="Fachbegriffe flach (Studio-Liste Terminologie)", response_model=list[BegriffOut])
def list_begriffe(domain: str | None = Query(default=None), q: str | None = Query(default=None)) -> list[BegriffOut]:
    begriffe = build_landhandel_terminology_registry().as_dict(query=q, domain=domain)["terms"]
    return [BegriffOut(**{k: b.get(k) or "" for k in ("term_key", "domain", "canonical_de", "canonical_en",
                                                      "description_de")},
                       synonyms_de=", ".join(b.get("synonyms_de") or []), avoid_de=", ".join(b.get("avoid_de") or []))
            for b in begriffe]


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
