"""Waagenvorlagen / Wiederholfall-Anlieferungen (Agrar-Spezialsoftware Feature)."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/waagen/vorlagen", tags=["agrar", "waage", "vorlagen"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class WaagenVorlageCreate(BaseModel):
    name: str
    waage_id: str
    kontrakt_nr: Optional[str] = None
    lieferant_nr: Optional[str] = None
    fahrer_name: Optional[str] = None
    kfz_kennzeichen: Optional[str] = None
    lager_id: Optional[str] = None
    silo_id: Optional[str] = None
    sorte_nr: Optional[str] = None
    artikel_nr: Optional[str] = None
    charge_nr: Optional[str] = None
    ist_aktiv: bool = True


class WaagenVorlageOut(BaseModel):
    id: str
    name: str
    waage_id: str
    kontrakt_nr: Optional[str] = None
    lieferant_nr: Optional[str] = None
    fahrer_name: Optional[str] = None
    kfz_kennzeichen: Optional[str] = None
    lager_id: Optional[str] = None
    silo_id: Optional[str] = None
    sorte_nr: Optional[str] = None
    artikel_nr: Optional[str] = None
    charge_nr: Optional[str] = None
    ist_aktiv: bool = True
    verwendungen_count: int = 0


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[WaagenVorlageOut], summary="Vorlagen auflisten")
def list_vorlagen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        rows = db.execute(
            text(
                "SELECT id, name, waage_id, kontrakt_nr, lieferant_nr, fahrer_name, "
                "kfz_kennzeichen, lager_id, silo_id, sorte_nr, artikel_nr, charge_nr, "
                "ist_aktiv, verwendungen_count "
                "FROM domain_agrar.waagen_vorlagen "
                "WHERE tenant_id=:tenant_id AND ist_aktiv=TRUE ORDER BY name"
            ),
            {"tenant_id": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


@router.post("", response_model=WaagenVorlageOut, status_code=status.HTTP_201_CREATED, summary="Vorlage anlegen")
def create_vorlage(
    payload: WaagenVorlageCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    new_id = str(uuid.uuid4())
    try:
        db.execute(
            text(
                "INSERT INTO domain_agrar.waagen_vorlagen "
                "(id, tenant_id, name, waage_id, kontrakt_nr, lieferant_nr, fahrer_name, "
                "kfz_kennzeichen, lager_id, silo_id, sorte_nr, artikel_nr, charge_nr, "
                "ist_aktiv, verwendungen_count) "
                "VALUES (:id, :tenant_id, :name, :waage_id, :kontrakt_nr, :lieferant_nr, "
                ":fahrer_name, :kfz_kennzeichen, :lager_id, :silo_id, :sorte_nr, "
                ":artikel_nr, :charge_nr, :ist_aktiv, 0)"
            ),
            {
                "id": new_id,
                "tenant_id": tenant_id,
                **payload.model_dump(),
            },
        )
        db.commit()
    except Exception:
        db.rollback()

    return {"id": new_id, **payload.model_dump(), "verwendungen_count": 0}


@router.put("/{vorlage_id}", response_model=WaagenVorlageOut, summary="Vorlage aktualisieren")
def update_vorlage(
    vorlage_id: str,
    payload: WaagenVorlageCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.waagen_vorlagen SET "
                "name=:name, waage_id=:waage_id, kontrakt_nr=:kontrakt_nr, "
                "lieferant_nr=:lieferant_nr, fahrer_name=:fahrer_name, "
                "kfz_kennzeichen=:kfz_kennzeichen, lager_id=:lager_id, silo_id=:silo_id, "
                "sorte_nr=:sorte_nr, artikel_nr=:artikel_nr, charge_nr=:charge_nr, "
                "ist_aktiv=:ist_aktiv "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": vorlage_id, "tenant_id": tenant_id, **payload.model_dump()},
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": "DB unavailable", "migration_hint": "domain_agrar.waagen_vorlagen missing"},
        )

    return {"id": vorlage_id, **payload.model_dump(), "verwendungen_count": 0}


@router.delete("/{vorlage_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, summary="Vorlage löschen")
def delete_vorlage(
    vorlage_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    """Soft delete — sets ist_aktiv=false."""
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.waagen_vorlagen SET ist_aktiv=FALSE "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": vorlage_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": "DB unavailable", "migration_hint": "domain_agrar.waagen_vorlagen missing"},
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{vorlage_id}/anwenden", summary="Anwenden",
    response_model=None
)
def anwenden(
    vorlage_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Apply template — returns pre-filled Wiegevorgang dict."""
    vorlage: dict = {}

    try:
        row = db.execute(
            text(
                "SELECT id, name, waage_id, kontrakt_nr, lieferant_nr, fahrer_name, "
                "kfz_kennzeichen, lager_id, silo_id, sorte_nr, artikel_nr, charge_nr, "
                "ist_aktiv, verwendungen_count "
                "FROM domain_agrar.waagen_vorlagen WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": vorlage_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row:
            vorlage = dict(row)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": "DB unavailable", "migration_hint": "domain_agrar.waagen_vorlagen missing"},
        )

    if not vorlage:
        raise HTTPException(status_code=404, detail="Vorlage nicht gefunden")

    # Increment verwendungen_count (best-effort)
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.waagen_vorlagen "
                "SET verwendungen_count = COALESCE(verwendungen_count, 0) + 1 "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": vorlage_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()

    vorausgefuellt = {
        "waage_id": vorlage.get("waage_id"),
        "kontrakt_nr": vorlage.get("kontrakt_nr"),
        "lieferant_nr": vorlage.get("lieferant_nr"),
        "fahrer_name": vorlage.get("fahrer_name"),
        "kfz_kennzeichen": vorlage.get("kfz_kennzeichen"),
        "lager_id": vorlage.get("lager_id"),
        "silo_id": vorlage.get("silo_id"),
        "sorte_nr": vorlage.get("sorte_nr"),
        "artikel_nr": vorlage.get("artikel_nr"),
        "charge_nr": vorlage.get("charge_nr"),
    }

    return {
        "vorlage_id": vorlage_id,
        "vorausgefuellt": vorausgefuellt,
        "hinweis": "Vorlage angewendet – bitte Gewicht eintragen",
    }
