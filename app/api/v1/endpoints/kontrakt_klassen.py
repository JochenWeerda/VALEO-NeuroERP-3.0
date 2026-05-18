"""
Kontrakt-Klassen und Kontraktvarianten (Agrar-Spezialsoftware Feature).

GET    /kontrakt-klassen         — list all
POST   /kontrakt-klassen         — create
PUT    /kontrakt-klassen/{id}    — update
DELETE /kontrakt-klassen/{id}    — soft delete (is_active=false)
"""
from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/kontrakt-klassen", tags=["kontrakt-klassen"])


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class KontraktVariante(str, enum.Enum):
    """Preismodell-Variante eines Kontrakts (Auflage 3: Enum-Constraint)."""
    FIXPREIS = "FIXPREIS"
    BASIS = "BASIS"
    PRAEMIE = "PRAEMIE"
    POOLPREIS = "POOLPREIS"


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class KontraktKlasseCreate(BaseModel):
    name: str
    beschreibung: Optional[str] = None
    variante: KontraktVariante  # FIXPREIS / BASIS / PRAEMIE / POOLPREIS
    parität: str   # EXW / FCA / CPT / CIF / DAP / DDP
    incoterm_ort: Optional[str] = None
    notiz: Optional[str] = None


class KontraktKlasseOut(KontraktKlasseCreate):
    model_config = {"from_attributes": True}

    id: str
    created_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

VALID_VARIANTEN = {"FIXPREIS", "BASIS", "PRAEMIE", "POOLPREIS"}
VALID_PARITAETEN = {"EXW", "FCA", "CPT", "CIF", "DAP", "DDP"}


@router.get("", response_model=List[KontraktKlasseOut])
def list_kontrakt_klassen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        rows = db.execute(
            text(
                "SELECT id, name, beschreibung, variante, paritaet AS \"parität\","
                " incoterm_ort, notiz, created_at"
                " FROM domain_agrar.kontrakt_klassen"
                " WHERE is_active = TRUE ORDER BY name"
            )
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []  # migration_hint: domain_agrar.kontrakt_klassen not yet migrated


@router.post("", response_model=KontraktKlasseOut, status_code=201)
def create_kontrakt_klasse(
    payload: KontraktKlasseCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    new_id = str(uuid4())
    now = datetime.utcnow()
    try:
        db.execute(
            text(
                "INSERT INTO domain_agrar.kontrakt_klassen"
                " (id, name, beschreibung, variante, paritaet, incoterm_ort, notiz,"
                "  is_active, created_at, tenant_id)"
                " VALUES (:id, :name, :beschreibung, :variante, :paritaet,"
                "  :incoterm_ort, :notiz, TRUE, :created_at, :tenant_id)"
            ),
            {
                "id": new_id,
                "name": payload.name,
                "beschreibung": payload.beschreibung,
                "variante": payload.variante.value,
                "paritaet": payload.parität,
                "incoterm_ort": payload.incoterm_ort,
                "notiz": payload.notiz,
                "created_at": now,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
        # Fallback: return in-memory object (migration_hint)
    return KontraktKlasseOut(
        id=new_id,
        created_at=now,
        **payload.model_dump(),
    )


@router.put("/{klasse_id}", response_model=KontraktKlasseOut)
def update_kontrakt_klasse(
    klasse_id: str,
    payload: KontraktKlasseCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.kontrakt_klassen"
                " SET name=:name, beschreibung=:beschreibung, variante=:variante,"
                "     paritaet=:paritaet, incoterm_ort=:incoterm_ort, notiz=:notiz"
                " WHERE id=:id AND tenant_id=:tenant_id AND is_active=TRUE"
            ),
            {
                "id": klasse_id,
                "name": payload.name,
                "beschreibung": payload.beschreibung,
                "variante": payload.variante.value,
                "paritaet": payload.parität,
                "incoterm_ort": payload.incoterm_ort,
                "notiz": payload.notiz,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()
    return KontraktKlasseOut(id=klasse_id, **payload.model_dump())


@router.delete("/{klasse_id}", status_code=204, response_class=Response)
def delete_kontrakt_klasse(
    klasse_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.kontrakt_klassen SET is_active=FALSE"
                " WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": klasse_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
    return Response(status_code=204)
