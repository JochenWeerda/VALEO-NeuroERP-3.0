from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import uuid

router = APIRouter(prefix="/silo", tags=["silo-operations"])

_store_registry: dict[str, object] = {}

def _get_store(tenant_id: str):
    from app.core.silo_operations import SiloCellStore
    if tenant_id not in _store_registry:
        _store_registry[tenant_id] = SiloCellStore()
    return _store_registry[tenant_id]

class SiloZelleCreateRequest(BaseModel):
    tenant_id: str
    bezeichnung: str
    kapazitaet_t: float

class EinlagerungRequest(BaseModel):
    tenant_id: str
    silo_id: str
    menge_t: float
    sorte: str
    beleg_nr: Optional[str] = None

class AuslagerungRequest(BaseModel):
    tenant_id: str
    silo_id: str
    menge_t: float
    beleg_nr: Optional[str] = None

@router.post("/zellen", status_code=201)
def create_silo_zelle(req: SiloZelleCreateRequest):
    from app.core.silo_operations import SiloCell
    zelle = SiloCell(
        silo_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        bezeichnung=req.bezeichnung,
        kapazitaet_t=req.kapazitaet_t,
    )
    store = _get_store(req.tenant_id)
    store.add_zelle(zelle)
    return zelle

@router.post("/einlagern", status_code=201)
def einlagern(req: EinlagerungRequest):
    store = _get_store(req.tenant_id)
    try:
        transfer = store.einlagern(req.silo_id, req.menge_t, req.sorte, req.beleg_nr)
        return transfer
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=str(e))

@router.post("/auslagern", status_code=201)
def auslagern(req: AuslagerungRequest):
    store = _get_store(req.tenant_id)
    try:
        transfer = store.auslagern(req.silo_id, req.menge_t, req.beleg_nr)
        return transfer
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/bestand/{tenant_id}")
def get_bestand(tenant_id: str):
    store = _get_store(tenant_id)
    return {"tenant_id": tenant_id, "gesamtbestand_t": store.gesamtbestand_t(tenant_id), "schema_version": 1}
