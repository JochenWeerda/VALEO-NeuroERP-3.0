from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/contract-pricing", tags=["contract-pricing"])

class PriceMatrixCreateRequest(BaseModel):
    tenant_id: str
    wirtschaftsjahr: int
    eintraege: list[dict]

class LotCreateRequest(BaseModel):
    tenant_id: str
    kontrakt_id: str
    lieferant_id: str
    menge_t: float
    sorte: str
    qualitaet: str
    vereinbarter_preis_eur_t: float
    preis_typ: str = "fest"
    lieferdatum_soll: str

@router.post("/price-matrix", status_code=201, summary="Price matrix anlegen")
def create_price_matrix(req: PriceMatrixCreateRequest):
    from app.core.contract_pricing import PriceMatrix, PriceMatrixEintrag, PreisTyp
    from datetime import date as _date
    eintraege = []
    for e in req.eintraege:
        eintraege.append(PriceMatrixEintrag(
            sorte=e["sorte"],
            qualitaet=e["qualitaet"],
            preis_eur_t=float(e["preis_eur_t"]),
            gueltig_von=_date.fromisoformat(e["gueltig_von"]),
            gueltig_bis=_date.fromisoformat(e["gueltig_bis"]),
            preis_typ=PreisTyp(e.get("preis_typ", "fest")),
        ))
    matrix = PriceMatrix(
        matrix_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        wirtschaftsjahr=req.wirtschaftsjahr,
        eintraege=eintraege,
    )
    return matrix

@router.post("/lots", status_code=201, summary="Lot anlegen")
def create_lot(req: LotCreateRequest):
    from app.core.contract_pricing import KonContractLot, PreisTyp
    from datetime import date as _date
    lot = KonContractLot(
        lot_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        kontrakt_id=req.kontrakt_id,
        lieferant_id=req.lieferant_id,
        menge_t=req.menge_t,
        sorte=req.sorte,
        qualitaet=req.qualitaet,
        vereinbarter_preis_eur_t=req.vereinbarter_preis_eur_t,
        preis_typ=PreisTyp(req.preis_typ),
        lieferdatum_soll=_date.fromisoformat(req.lieferdatum_soll),
    )
    return lot
