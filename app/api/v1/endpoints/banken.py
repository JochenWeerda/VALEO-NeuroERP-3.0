"""
Bank Accounts API - Bankkonto Management (SQLAlchemy)
"""

from typing import Optional
from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.domains.operations.repository import BankKontoRepository

router = APIRouter(prefix="/banken", tags=["Banken"])


class BankKontoCreate(BaseModel):
    iban: str = Field(..., description="IBAN")
    bic: str = Field(..., description="BIC/SWIFT")
    bank_name: str = Field(..., description="Bank name")
    kontoart: str = Field(..., description="Account type")
    waehrung: str = Field(default="EUR")
    ist_aktiv: bool = Field(default=True)
    saldo: float = Field(default=0)


class BankKontoUpdate(BaseModel):
    bank_name: Optional[str] = None
    kontoart: Optional[str] = None
    ist_aktiv: Optional[bool] = None
    status: Optional[str] = None
    saldo: Optional[float] = None


def _to_dict(konto) -> dict:
    return {
        "id": konto.id,
        "iban": konto.iban,
        "bic": konto.bic,
        "bank": konto.bank,
        "kontoart": konto.kontoart,
        "saldo": float(konto.saldo or 0),
        "waehrung": konto.waehrung,
        "status": konto.status,
        "ist_aktiv": bool(konto.ist_aktiv),
        "created_at": konto.created_at.isoformat() if konto.created_at else None,
        "updated_at": konto.updated_at.isoformat() if konto.updated_at else None,
    }


@router.get("/konten", response_model=dict)
async def list_bankkonten(
    kontoart: Optional[str] = Query(None, description="Filter by account type"),
    ist_aktiv: Optional[bool] = Query(None, description="Filter by active status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> dict:
    repo = BankKontoRepository(db)
    items = repo.get_all(skip=offset, limit=limit, kontoart=kontoart, ist_aktiv=ist_aktiv)
    total = repo.count(kontoart=kontoart, ist_aktiv=ist_aktiv)
    return {"items": [_to_dict(i) for i in items], "total": total, "limit": limit, "offset": offset}


@router.get("/konten/{konto_id}", response_model=dict)
async def get_bankkonto(konto_id: str, db: Session = Depends(get_db)) -> dict:
    repo = BankKontoRepository(db)
    konto = repo.get_by_id(konto_id)
    if not konto:
        raise HTTPException(status_code=404, detail="Bankkonto not found")
    return _to_dict(konto)


@router.post("/konten", response_model=dict, status_code=201)
async def create_bankkonto(data: BankKontoCreate, db: Session = Depends(get_db)) -> dict:
    repo = BankKontoRepository(db)
    if repo.get_by_iban(data.iban):
        raise HTTPException(status_code=409, detail="IBAN already exists")

    payload = {
        "iban": data.iban.replace(" ", "").upper(),
        "bic": data.bic.upper(),
        "bank": data.bank_name,
        "kontoart": data.kontoart,
        "saldo": data.saldo,
        "waehrung": data.waehrung,
        "status": "aktiv" if data.ist_aktiv else "inaktiv",
        "ist_aktiv": data.ist_aktiv,
    }
    konto = repo.create(payload)
    return _to_dict(konto)


@router.patch("/konten/{konto_id}", response_model=dict)
async def update_bankkonto(konto_id: str, data: BankKontoUpdate, db: Session = Depends(get_db)) -> dict:
    repo = BankKontoRepository(db)
    payload = data.model_dump(exclude_unset=True)
    if "bank_name" in payload:
        payload["bank"] = payload.pop("bank_name")
    konto = repo.update(konto_id, payload)
    if not konto:
        raise HTTPException(status_code=404, detail="Bankkonto not found")
    return _to_dict(konto)


@router.delete("/konten/{konto_id}", status_code=204, response_class=Response, response_model=None)
async def delete_bankkonto(konto_id: str, db: Session = Depends(get_db)):
    repo = BankKontoRepository(db)
    if not repo.deactivate(konto_id):
        raise HTTPException(status_code=404, detail="Bankkonto not found")


@router.get("/salden", response_model=dict)
async def get_salden(db: Session = Depends(get_db)) -> dict:
    repo = BankKontoRepository(db)
    return repo.get_salden()


@router.get("/konten/iban-validate", response_model=dict)
async def validate_iban(iban: str = Query(..., description="IBAN to validate")) -> dict:
    normalized = iban.replace(" ", "").upper()
    is_valid = len(normalized) >= 15 and normalized[:2].isalpha()
    return {
        "iban": iban,
        "valid": is_valid,
        "bic": "UNKNOWN",
        "bank": None,
    }
