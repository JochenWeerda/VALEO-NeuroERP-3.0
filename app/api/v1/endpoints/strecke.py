"""
Strecke – Streckengeschaefte CRUD
Drop-ship / pass-through trade management.
"""

from datetime import date, datetime
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id


router = APIRouter(prefix="/strecke/streckengeschaefte", tags=["Strecke"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class StreckengeschaeftBase(BaseModel):
    datum: str
    niederlassung: str = ""
    partie_nr: str = ""
    kostenstelle: str = ""
    lagerhalle: str = ""
    nls_nr: str = ""
    erledigt: bool = False
    lieferant_name: str = ""
    lieferant_nr: str = ""
    kontrakt_nr: str = ""
    artikel: str = ""
    netto: float = 0.0
    mwst: float = 0.0
    brutto: float = 0.0
    rechnungsnr: str = ""
    bediener: str = ""
    notiz: str = ""


class StreckengeschaeftCreate(StreckengeschaeftBase):
    pass


class StreckengeschaeftOut(StreckengeschaeftBase):
    id: str
    strecke_nr: str
    erstellt: str


class StreckengeschaeftUpdate(BaseModel):
    datum: Optional[str] = None
    niederlassung: Optional[str] = None
    partie_nr: Optional[str] = None
    kostenstelle: Optional[str] = None
    lagerhalle: Optional[str] = None
    nls_nr: Optional[str] = None
    erledigt: Optional[bool] = None
    lieferant_name: Optional[str] = None
    lieferant_nr: Optional[str] = None
    kontrakt_nr: Optional[str] = None
    artikel: Optional[str] = None
    netto: Optional[float] = None
    mwst: Optional[float] = None
    brutto: Optional[float] = None
    rechnungsnr: Optional[str] = None
    bediener: Optional[str] = None
    notiz: Optional[str] = None


# ---------------------------------------------------------------------------
# In-memory store (TODO: replace with DB table)
# ---------------------------------------------------------------------------

_DEMO_DATA: list[dict[str, Any]] = [
    {
        "id": "stg-001",
        "strecke_nr": "STR-2026-0001",
        "datum": "2026-02-25",
        "niederlassung": "Hauptlager",
        "partie_nr": "P-4410",
        "kostenstelle": "KS-110",
        "lagerhalle": "H3",
        "nls_nr": "NLS-01",
        "erledigt": False,
        "lieferant_name": "Agrar Müller GmbH",
        "lieferant_nr": "LF-1001",
        "kontrakt_nr": "KT-2026-0042",
        "artikel": "Weizen B",
        "netto": 12500.00,
        "mwst": 875.00,
        "brutto": 13375.00,
        "rechnungsnr": "",
        "bediener": "Meier",
        "notiz": "",
        "erstellt": "2026-02-25T08:00:00",
    },
    {
        "id": "stg-002",
        "strecke_nr": "STR-2026-0002",
        "datum": "2026-03-10",
        "niederlassung": "Außenlager West",
        "partie_nr": "P-4422",
        "kostenstelle": "KS-210",
        "lagerhalle": "H1",
        "nls_nr": "NLS-02",
        "erledigt": True,
        "lieferant_name": "Raiffeisen Handel eG",
        "lieferant_nr": "LF-2030",
        "kontrakt_nr": "KT-2026-0055",
        "artikel": "Raps 00",
        "netto": 28900.00,
        "mwst": 2023.00,
        "brutto": 30923.00,
        "rechnungsnr": "RE-2026-1122",
        "bediener": "Schmidt",
        "notiz": "Expresslieferung",
        "erstellt": "2026-03-10T10:30:00",
    },
    {
        "id": "stg-003",
        "strecke_nr": "STR-2026-0003",
        "datum": "2026-04-01",
        "niederlassung": "Hauptlager",
        "partie_nr": "P-4480",
        "kostenstelle": "KS-110",
        "lagerhalle": "H5",
        "nls_nr": "NLS-01",
        "erledigt": False,
        "lieferant_name": "BayWa AG",
        "lieferant_nr": "LF-3100",
        "kontrakt_nr": "KT-2026-0071",
        "artikel": "Gerste",
        "netto": 8750.00,
        "mwst": 612.50,
        "brutto": 9362.50,
        "rechnungsnr": "",
        "bediener": "Meier",
        "notiz": "",
        "erstellt": "2026-04-01T09:15:00",
    },
]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[StreckengeschaeftOut])
async def list_streckengeschaefte(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    erledigt: Optional[bool] = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste aller Streckengeschaefte."""
    data = _DEMO_DATA
    if erledigt is not None:
        data = [d for d in data if d["erledigt"] == erledigt]
    return [StreckengeschaeftOut(**d) for d in data[skip : skip + limit]]


@router.get("/{strecke_id}", response_model=StreckengeschaeftOut)
async def get_streckengeschaeft(
    strecke_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einzelnes Streckengeschaeft laden."""
    for d in _DEMO_DATA:
        if d["id"] == strecke_id:
            return StreckengeschaeftOut(**d)
    raise HTTPException(status_code=404, detail=f"Streckengeschaeft {strecke_id} nicht gefunden")


@router.post("", response_model=StreckengeschaeftOut, status_code=201)
async def create_streckengeschaeft(
    payload: StreckengeschaeftCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neues Streckengeschaeft anlegen."""
    new_id = str(uuid4())
    seq = len(_DEMO_DATA) + 1
    strecke_nr = f"STR-{datetime.now().year}-{seq:04d}"

    entry = {
        **payload.model_dump(),
        "id": new_id,
        "strecke_nr": strecke_nr,
        "erstellt": datetime.now().isoformat(),
    }
    _DEMO_DATA.append(entry)
    return StreckengeschaeftOut(**entry)


@router.patch("/{strecke_id}", response_model=StreckengeschaeftOut)
async def update_streckengeschaeft(
    strecke_id: str,
    payload: StreckengeschaeftUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Streckengeschaeft aktualisieren."""
    for d in _DEMO_DATA:
        if d["id"] == strecke_id:
            updates = payload.model_dump(exclude_unset=True)
            d.update(updates)
            return StreckengeschaeftOut(**d)
    raise HTTPException(status_code=404, detail=f"Streckengeschaeft {strecke_id} nicht gefunden")


@router.delete("/{strecke_id}", status_code=204, response_class=Response)
async def delete_streckengeschaeft(
    strecke_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Streckengeschaeft loeschen."""
    for i, d in enumerate(_DEMO_DATA):
        if d["id"] == strecke_id:
            _DEMO_DATA.pop(i)
            return Response(status_code=204)
    raise HTTPException(status_code=404, detail=f"Streckengeschaeft {strecke_id} nicht gefunden")
