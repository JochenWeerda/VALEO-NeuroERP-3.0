"""
Produktion – Mischfutter: Verfuegbarkeit & Rezepte
Provides component availability and recipe data for the Mischfutter production wizard.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from sqlalchemy.orm import Session


router = APIRouter(prefix="/produktion/mischfutter", tags=["Produktion - Mischfutter"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class KomponenteVerfuegbarkeit(BaseModel):
    name: str
    verfuegbar_t: float
    einheit: str = "t"


class Rezept(BaseModel):
    id: str
    name: str
    code: str
    komponenten: list[dict[str, Any]]
    """Each entry: {name, anteil} where anteil is 0..1 fraction."""


class ProduktionsauftragIn(BaseModel):
    rezeptur: str = Field(..., min_length=1)
    menge: float = Field(..., gt=0)
    chargen_id: str = ""


class ProduktionsauftragOut(BaseModel):
    id: str
    chargen_id: str
    rezeptur: str
    menge: float
    status: str
    erstellt: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/verfuegbarkeit", response_model=list[KomponenteVerfuegbarkeit])
async def get_verfuegbarkeit(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Aktuelle Komponentenverfuegbarkeit fuer Mischfutter-Produktion."""
    # TODO: replace with real inventory query once Lager-Bestaende table is wired
    return [
        KomponenteVerfuegbarkeit(name="Sojaschrot 44%", verfuegbar_t=280.0),
        KomponenteVerfuegbarkeit(name="Weizen", verfuegbar_t=450.0),
        KomponenteVerfuegbarkeit(name="Mais", verfuegbar_t=320.0),
        KomponenteVerfuegbarkeit(name="Mineralfutter", verfuegbar_t=50.0),
        KomponenteVerfuegbarkeit(name="Rapsschrot", verfuegbar_t=190.0),
        KomponenteVerfuegbarkeit(name="Gerste", verfuegbar_t=380.0),
        KomponenteVerfuegbarkeit(name="Melasse", verfuegbar_t=45.0),
    ]


@router.get("/rezepte", response_model=list[Rezept])
async def get_rezepte(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste aller Mischfutter-Rezepturen mit Komponentenanteilen."""
    # TODO: replace with DB-backed recipe table
    return [
        Rezept(
            id="rez-milchvieh",
            name="Milchviehfutter Hochleistung",
            code="milchvieh",
            komponenten=[
                {"name": "Sojaschrot 44%", "anteil": 0.25},
                {"name": "Weizen", "anteil": 0.30},
                {"name": "Mais", "anteil": 0.20},
                {"name": "Mineralfutter", "anteil": 0.05},
                {"name": "Gerste", "anteil": 0.15},
                {"name": "Melasse", "anteil": 0.05},
            ],
        ),
        Rezept(
            id="rez-mast",
            name="Mastbullenfutter",
            code="mast",
            komponenten=[
                {"name": "Mais", "anteil": 0.35},
                {"name": "Sojaschrot 44%", "anteil": 0.20},
                {"name": "Gerste", "anteil": 0.25},
                {"name": "Rapsschrot", "anteil": 0.10},
                {"name": "Mineralfutter", "anteil": 0.05},
                {"name": "Melasse", "anteil": 0.05},
            ],
        ),
        Rezept(
            id="rez-sauen",
            name="Sauenfutter",
            code="sauen",
            komponenten=[
                {"name": "Gerste", "anteil": 0.30},
                {"name": "Weizen", "anteil": 0.25},
                {"name": "Sojaschrot 44%", "anteil": 0.20},
                {"name": "Rapsschrot", "anteil": 0.10},
                {"name": "Mineralfutter", "anteil": 0.05},
                {"name": "Melasse", "anteil": 0.10},
            ],
        ),
    ]


@router.post("/auftrag", response_model=ProduktionsauftragOut, status_code=201)
async def create_produktionsauftrag(
    payload: ProduktionsauftragIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Mischfutter-Produktionsauftrag erstellen."""
    auftrag_id = str(uuid4())
    chargen_id = payload.chargen_id or f"MF-{datetime.now().strftime('%y%m%d')}-{str(uuid4())[:3].upper()}"

    # TODO: persist to produktion_auftraege table + deduct inventory
    return ProduktionsauftragOut(
        id=auftrag_id,
        chargen_id=chargen_id,
        rezeptur=payload.rezeptur,
        menge=payload.menge,
        status="erstellt",
        erstellt=datetime.now().isoformat(),
    )
