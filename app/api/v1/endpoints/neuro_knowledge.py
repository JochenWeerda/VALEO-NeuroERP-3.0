"""Knowledge Store REST API — NC-06."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Any, Optional

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.knowledge_store import (
    KnowledgeEntry,
    KnowledgeType,
    store_knowledge,
    get_knowledge,
    search_knowledge,
    delete_knowledge,
    get_knowledge_stats,
)

router = APIRouter(prefix="/neuro/knowledge", tags=["neuro-core", "knowledge"])


class StoreRequest(BaseModel):
    knowledge_type: str = Field("business_rule", description="prompt_template | business_rule | faq | process_description | domain_glossary")
    domain: str = Field(..., description="Fachdomaene (z.B. einkauf, agrar, finance)")
    key: str = Field(..., description="Eindeutiger Schluessel innerhalb der Domaene")
    title: str = Field(...)
    content: str = Field(...)
    metadata: Optional[dict[str, Any]] = Field(default_factory=dict)


class SearchRequest(BaseModel):
    domain: Optional[str] = None
    knowledge_type: Optional[str] = None
    query: Optional[str] = None
    limit: int = Field(50, ge=1, le=200)


@router.post("/")
async def store(
    request: StoreRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Wissen speichern oder aktualisieren (Versionierung automatisch)."""
    entry = KnowledgeEntry(
        knowledge_type=KnowledgeType(request.knowledge_type),
        domain=request.domain,
        key=request.key,
        title=request.title,
        content=request.content,
        metadata=request.metadata or {},
    )
    result = store_knowledge(db, entry, tenant_id)
    return result.to_dict()


@router.get("/{domain}/{key}")
async def get_entry(
    domain: str,
    key: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einen Knowledge-Eintrag abrufen."""
    entry = get_knowledge(db, domain, key, tenant_id)
    if not entry:
        return {"error": "Nicht gefunden", "domain": domain, "key": key}
    return entry.to_dict()


@router.post("/search")
async def search(
    request: SearchRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Knowledge-Eintraege suchen."""
    kt = KnowledgeType(request.knowledge_type) if request.knowledge_type else None
    entries = search_knowledge(db, request.domain, kt, request.query, tenant_id, request.limit)
    return {"count": len(entries), "entries": [e.to_dict() for e in entries]}


@router.delete("/{domain}/{key}")
async def remove(
    domain: str,
    key: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Knowledge-Eintrag deaktivieren (Soft-Delete)."""
    deleted = delete_knowledge(db, domain, key, tenant_id)
    return {"deleted": deleted, "domain": domain, "key": key}


@router.get("/stats")
async def stats(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Statistiken ueber den Knowledge Store."""
    return get_knowledge_stats(db, tenant_id)
