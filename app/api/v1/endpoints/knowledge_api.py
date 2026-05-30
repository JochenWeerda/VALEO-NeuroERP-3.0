"""
Knowledge Core API — Wave 69
Zentraler Wissensspeicher für VALEO NeuroERP.
Endpoints für CRUD, Versionierung, Suche und Statistiken.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.uuid7 import uuid7
from app.models.knowledge import KnowledgeObjectRecord, KnowledgeVersionRecord
from app.repositories.knowledge_repository import KnowledgeRepository

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class KnowledgeOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter()

# ── Pydantic Schemas ────────────────────────────────────────────────────────────


class KnowledgeObjectCreate(BaseModel):
    titel: str
    typ: str
    beschreibung: str = ""
    tags: list[str] = []
    zielrollen: list[str] = []
    agentenfreigabe: bool = True
    initiale_version: str = ""
    format: str = "MARKDOWN"


class KnowledgeObjectUpdate(BaseModel):
    titel: Optional[str] = None
    beschreibung: Optional[str] = None
    tags: Optional[list[str]] = None
    zielrollen: Optional[list[str]] = None
    status: Optional[str] = None
    agentenfreigabe: Optional[bool] = None


class KnowledgeVersionCreate(BaseModel):
    inhalt: str
    format: str = "MARKDOWN"
    quelle: str = "api"


class KnowledgeObjectResponse(BaseModel):
    knowledge_id: str
    titel: str
    typ: str
    status: str
    beschreibung: str
    tags: list[str]
    zielrollen: list[str]
    agentenfreigabe: bool
    created_at: str
    updated_at: str
    versionen_count: int
    aktuelle_version: Optional[int]
    vorschau: str


class KnowledgeSearchResult(BaseModel):
    items: list[KnowledgeObjectResponse]
    total: int
    query: str


class KnowledgeStatsResponse(BaseModel):
    gesamt: int
    nach_typ: dict[str, int]
    nach_status: dict[str, int]
    nach_format: dict[str, int]
    agentenfreigabe_aktiv: int


# ── Helper ──────────────────────────────────────────────────────────────────────


def _record_to_response(record: KnowledgeObjectRecord) -> KnowledgeObjectResponse:
    versionen = list(record.versionen or [])
    versionen_sorted = sorted(versionen, key=lambda v: v.version)
    aktuelle_version = versionen_sorted[-1].version if versionen_sorted else None
    vorschau_inhalt = versionen_sorted[-1].inhalt if versionen_sorted else ""
    vorschau = vorschau_inhalt[:200] if vorschau_inhalt else ""

    return KnowledgeObjectResponse(
        knowledge_id=record.knowledge_id,
        titel=record.titel,
        typ=record.typ,
        status=record.status,
        beschreibung=record.beschreibung or "",
        tags=list(record.tags or []),
        zielrollen=list(record.zielrollen or []),
        agentenfreigabe=bool(record.agentenfreigabe),
        created_at=record.created_at.isoformat() if record.created_at else "",
        updated_at=record.updated_at.isoformat() if record.updated_at else "",
        versionen_count=len(versionen),
        aktuelle_version=aktuelle_version,
        vorschau=vorschau,
    )


# ── Endpoints ───────────────────────────────────────────────────────────────────


@router.get("/search", response_model=KnowledgeSearchResult, summary="Knowledge suchen")
def search_knowledge(
    q: str = Query("", description="Suchbegriff (ILIKE auf Titel und Inhalt)"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> KnowledgeSearchResult:
    """Volltextsuche in Titeln und Versionsinhalten."""
    try:
        tenant_id = settings.DEFAULT_TENANT_ID
        stmt = (
            select(KnowledgeObjectRecord)
            .where(KnowledgeObjectRecord.tenant_id == tenant_id)
            .where(KnowledgeObjectRecord.status != "ARCHIVIERT")
        )
        if q.strip():
            pattern = f"%{q.strip()}%"
            stmt = stmt.where(
                or_(
                    KnowledgeObjectRecord.titel.ilike(pattern),
                    KnowledgeObjectRecord.beschreibung.ilike(pattern),
                )
            )
        stmt = stmt.order_by(KnowledgeObjectRecord.updated_at.desc()).limit(limit)
        records = list(db.execute(stmt).unique().scalars().all())
        items = [_record_to_response(r) for r in records]
        return KnowledgeSearchResult(items=items, total=len(items), query=q)
    except Exception as exc:
        logger.warning("Knowledge search error: %s", exc)
        return KnowledgeSearchResult(items=[], total=0, query=q)


@router.get("/stats", response_model=KnowledgeStatsResponse, summary="Knowledge stats abrufen")
def get_knowledge_stats(db: Session = Depends(get_db)) -> KnowledgeStatsResponse:
    """Statistiken: Anzahl je Typ, Status und Format."""
    try:
        tenant_id = settings.DEFAULT_TENANT_ID

        gesamt_result = db.execute(
            select(func.count()).select_from(KnowledgeObjectRecord).where(
                KnowledgeObjectRecord.tenant_id == tenant_id
            )
        ).scalar_one()

        typ_rows = db.execute(
            select(KnowledgeObjectRecord.typ, func.count().label("n"))
            .where(KnowledgeObjectRecord.tenant_id == tenant_id)
            .group_by(KnowledgeObjectRecord.typ)
        ).all()

        status_rows = db.execute(
            select(KnowledgeObjectRecord.status, func.count().label("n"))
            .where(KnowledgeObjectRecord.tenant_id == tenant_id)
            .group_by(KnowledgeObjectRecord.status)
        ).all()

        format_rows = db.execute(
            select(KnowledgeVersionRecord.format, func.count().label("n"))
            .join(
                KnowledgeObjectRecord,
                KnowledgeVersionRecord.knowledge_id == KnowledgeObjectRecord.knowledge_id,
            )
            .where(KnowledgeObjectRecord.tenant_id == tenant_id)
            .group_by(KnowledgeVersionRecord.format)
        ).all()

        agenten_result = db.execute(
            select(func.count()).select_from(KnowledgeObjectRecord).where(
                KnowledgeObjectRecord.tenant_id == tenant_id,
                KnowledgeObjectRecord.agentenfreigabe.is_(True),
                KnowledgeObjectRecord.status == "FREIGEGEBEN",
            )
        ).scalar_one()

        return KnowledgeStatsResponse(
            gesamt=int(gesamt_result),
            nach_typ={row.typ: row.n for row in typ_rows},
            nach_status={row.status: row.n for row in status_rows},
            nach_format={row.format: row.n for row in format_rows},
            agentenfreigabe_aktiv=int(agenten_result),
        )
    except Exception as exc:
        logger.warning("Knowledge stats error: %s", exc)
        return KnowledgeStatsResponse(
            gesamt=0,
            nach_typ={},
            nach_status={},
            nach_format={},
            agentenfreigabe_aktiv=0,
        )


@router.get("/", response_model=list[KnowledgeObjectResponse], summary="Knowledge auflisten")
def list_knowledge(
    typ: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    tags: Optional[str] = Query(None, description="Kommagetrennte Tag-Liste"),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[KnowledgeObjectResponse]:
    """Liste aller Wissensobjekte mit optionalen Filtern."""
    try:
        tenant_id = settings.DEFAULT_TENANT_ID
        stmt = select(KnowledgeObjectRecord).where(
            KnowledgeObjectRecord.tenant_id == tenant_id
        )
        if typ:
            stmt = stmt.where(KnowledgeObjectRecord.typ == typ)
        if status:
            stmt = stmt.where(KnowledgeObjectRecord.status == status)
        if search:
            pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    KnowledgeObjectRecord.titel.ilike(pattern),
                    KnowledgeObjectRecord.beschreibung.ilike(pattern),
                )
            )
        # Tag-Filter: JSONB contains any of the provided tags
        if tags:
            tag_list = [t.strip() for t in tags.split(",") if t.strip()]
            for tag in tag_list:
                stmt = stmt.where(KnowledgeObjectRecord.tags.contains([tag]))

        stmt = (
            stmt.order_by(KnowledgeObjectRecord.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        records = list(db.execute(stmt).unique().scalars().all())
        return [_record_to_response(r) for r in records]
    except Exception as exc:
        logger.warning("Knowledge list error: %s", exc)
        return []


@router.post("/", response_model=KnowledgeObjectResponse, status_code=201, summary="Knowledge anlegen")
def create_knowledge(
    payload: KnowledgeObjectCreate,
    db: Session = Depends(get_db),
) -> KnowledgeObjectResponse:
    """Neues Wissensobjekt mit initialer Version erstellen."""
    tenant_id = settings.DEFAULT_TENANT_ID
    repo = KnowledgeRepository(db)
    knowledge_id = str(uuid7())
    record = repo.create_object(
        knowledge_id=knowledge_id,
        titel=payload.titel,
        typ=payload.typ,
        status="ENTWURF",
        tenant_id=tenant_id,
        beschreibung=payload.beschreibung,
        tags=payload.tags,
        zielrollen=payload.zielrollen,
        agentenfreigabe=payload.agentenfreigabe,
        version_payload={
            "version": 1,
            "format": payload.format,
            "inhalt": payload.initiale_version,
            "quelle": "api",
        },
    )
    return _record_to_response(record)


@router.get("/{knowledge_id}", response_model=KnowledgeObjectResponse, summary="Knowledge abrufen")
def get_knowledge(
    knowledge_id: str,
    db: Session = Depends(get_db),
) -> KnowledgeObjectResponse:
    """Einzelnes Wissensobjekt mit allen Versionen abrufen."""
    tenant_id = settings.DEFAULT_TENANT_ID
    stmt = select(KnowledgeObjectRecord).where(
        KnowledgeObjectRecord.knowledge_id == knowledge_id,
        KnowledgeObjectRecord.tenant_id == tenant_id,
    )
    record = db.execute(stmt).unique().scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Wissensobjekt nicht gefunden")
    return _record_to_response(record)


@router.put("/{knowledge_id}", response_model=KnowledgeObjectResponse, summary="Knowledge aktualisieren")
def update_knowledge(
    knowledge_id: str,
    payload: KnowledgeObjectUpdate,
    db: Session = Depends(get_db),
) -> KnowledgeObjectResponse:
    """Metadaten eines Wissensobjekts aktualisieren."""
    tenant_id = settings.DEFAULT_TENANT_ID
    stmt = select(KnowledgeObjectRecord).where(
        KnowledgeObjectRecord.knowledge_id == knowledge_id,
        KnowledgeObjectRecord.tenant_id == tenant_id,
    )
    record = db.execute(stmt).unique().scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Wissensobjekt nicht gefunden")

    if payload.titel is not None:
        record.titel = payload.titel
    if payload.beschreibung is not None:
        record.beschreibung = payload.beschreibung
    if payload.tags is not None:
        record.tags = payload.tags
    if payload.zielrollen is not None:
        record.zielrollen = payload.zielrollen
    if payload.status is not None:
        record.status = payload.status
    if payload.agentenfreigabe is not None:
        record.agentenfreigabe = payload.agentenfreigabe

    db.commit()
    db.refresh(record)
    return _record_to_response(record)


@router.delete("/{knowledge_id}", status_code=204, response_class=Response, response_model=None, summary="Knowledge archivieren")
def archive_knowledge(
    knowledge_id: str,
    db: Session = Depends(get_db),
) -> Response:
    """Wissensobjekt archivieren (Soft-Delete: Status → ARCHIVIERT)."""
    tenant_id = settings.DEFAULT_TENANT_ID
    stmt = select(KnowledgeObjectRecord).where(
        KnowledgeObjectRecord.knowledge_id == knowledge_id,
        KnowledgeObjectRecord.tenant_id == tenant_id,
    )
    record = db.execute(stmt).unique().scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Wissensobjekt nicht gefunden")
    record.status = "ARCHIVIERT"
    db.commit()
    return Response(status_code=204)


@router.post("/{knowledge_id}/versionen", response_model=KnowledgeObjectResponse, status_code=201, summary="Version hinzufügen")
def add_version(
    knowledge_id: str,
    payload: KnowledgeVersionCreate,
    db: Session = Depends(get_db),
) -> KnowledgeObjectResponse:
    """Neue Version zu einem Wissensobjekt hinzufügen."""
    tenant_id = settings.DEFAULT_TENANT_ID
    stmt = select(KnowledgeObjectRecord).where(
        KnowledgeObjectRecord.knowledge_id == knowledge_id,
        KnowledgeObjectRecord.tenant_id == tenant_id,
    )
    record = db.execute(stmt).unique().scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="Wissensobjekt nicht gefunden")

    repo = KnowledgeRepository(db)
    updated = repo.add_version(
        knowledge_id,
        {
            "format": payload.format,
            "inhalt": payload.inhalt,
            "quelle": payload.quelle,
        },
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="Wissensobjekt nicht gefunden")
    return _record_to_response(updated)
