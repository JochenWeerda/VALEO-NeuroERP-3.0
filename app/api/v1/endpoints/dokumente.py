"""
Dokumente API - Dokumentenverwaltung (SQLAlchemy Version)
"""

from typing import Optional
from fastapi import Response, APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.repository import DokumentRepository, DokumentVersionRepository

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/dokumente", tags=["Dokumente"])


# === DOKUMENT ENDPOINTS ===

@router.get("", response_model=CompatFlexOut, summary="Dokumente auflisten")
async def list_dokumente(
    kategorie: Optional[str] = Query(None, description="Filter by category"),
    typ: Optional[str] = Query(None, description="Filter by type"),
    suche: Optional[str] = Query(None, description="Search in name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """List all documents with filtering and pagination"""
    repo = DokumentRepository(db)
    
    # Apply filters
    if kategorie:
        items = repo.get_by_kategorie(kategorie)
    elif typ:
        items = repo.get_by_typ(typ)
    elif suche:
        items = repo.search(suche)
    else:
        items = repo.get_all(skip=skip, limit=limit)
    
    # Calculate stats
    stats = repo.get_stats()
    total_size = sum(d.groesse for d in items)
    
    return {
        "items": items,
        "total": len(items),
        "total_size_kb": total_size,
        "stats": stats
    }


@router.get("/kategorien", response_model=CompatFlexOut, summary="Kategorien abrufen")
async def get_kategorien(db: Session = Depends(get_db)):
    """Get all document categories with counts"""
    repo = DokumentRepository(db)
    stats = repo.get_stats()
    return {"kategorien": stats.get("by_category", {})}


@router.get("/{dokument_id}", response_model=CompatFlexOut, summary="Dokument abrufen")
async def get_dokument(dokument_id: str, db: Session = Depends(get_db)):
    """Get a single document by ID"""
    repo = DokumentRepository(db)
    dokument = repo.get_by_id(dokument_id)
    if not dokument:
        raise HTTPException(status_code=404, detail=f"Dokument {dokument_id} not found")
    return dokument


@router.post("", response_model=CompatFlexOut, status_code=201, summary="Dokument anlegen")
async def create_dokument(
    dokument_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new document"""
    repo = DokumentRepository(db)
    try:
        dokument = repo.create(dokument_data)
        return dokument
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{dokument_id}", response_model=CompatFlexOut, summary="Dokument aktualisieren")
async def update_dokument(
    dokument_id: str,
    dokument_data: dict,
    db: Session = Depends(get_db)
):
    """Update a document"""
    repo = DokumentRepository(db)
    dokument = repo.update(dokument_id, dokument_data)
    if not dokument:
        raise HTTPException(status_code=404, detail=f"Dokument {dokument_id} not found")
    return dokument


@router.delete("/{dokument_id}", status_code=204, response_class=Response, response_model=None, summary="Dokument löschen")
async def delete_dokument(
    dokument_id: str,
    hard_delete: bool = Query(False, description="Hard delete vs soft delete"),
    db: Session = Depends(get_db)
):
    """Delete a document (soft delete by default)"""
    repo = DokumentRepository(db)
    if hard_delete:
        if not repo.delete(dokument_id):
            raise HTTPException(status_code=404, detail=f"Dokument {dokument_id} not found")
    else:
        if not repo.soft_delete(dokument_id):
            raise HTTPException(status_code=404, detail=f"Dokument {dokument_id} not found")


# === DOKUMENT VERSION ENDPOINTS ===

@router.get("/{dokument_id}/versionen", response_model=list[CompatFlexOut], summary="Versionen auflisten")
async def list_versionen(
    dokument_id: str,
    db: Session = Depends(get_db)
):
    """List all versions of a document"""
    # Verify dokument exists
    dok_repo = DokumentRepository(db)
    dokument = dok_repo.get_by_id(dokument_id)
    if not dokument:
        raise HTTPException(status_code=404, detail=f"Dokument {dokument_id} not found")
    
    repo = DokumentVersionRepository(db)
    return repo.get_all(dokument_id)


@router.post("/{dokument_id}/versionen", response_model=CompatFlexOut, status_code=201, summary="Version anlegen")
async def create_version(
    dokument_id: str,
    version_data: dict,
    db: Session = Depends(get_db)
):
    """Create a new version of a document"""
    # Verify dokument exists
    dok_repo = DokumentRepository(db)
    dokument = dok_repo.get_by_id(dokument_id)
    if not dokument:
        raise HTTPException(status_code=404, detail=f"Dokument {dokument_id} not found")
    
    version_data["dokument_id"] = dokument_id
    
    # Auto-increment version number
    ver_repo = DokumentVersionRepository(db)
    latest = ver_repo.get_latest(dokument_id)
    version_data["version"] = (latest.version + 1) if latest else 1
    
    try:
        version = ver_repo.create(version_data)
        return version
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
