from __future__ import annotations
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid
from app.core.zertifikate import Zertifikat, ZertifikatStore, ZertifikatTyp

router = APIRouter(prefix="/zertifikate", tags=["zertifikate"])
_store = ZertifikatStore()

class ZertifikatCreateRequest(BaseModel):
    tenant_id: str
    typ: str
    zertifizierungsstelle: str
    gueltig_von: str
    gueltig_bis: str
    zertifikatsnummer: Optional[str] = None

@router.post("", status_code=201)
def create_zertifikat(req: ZertifikatCreateRequest):
    z = Zertifikat(
        zertifikat_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        typ=ZertifikatTyp(req.typ),
        zertifizierungsstelle=req.zertifizierungsstelle,
        gueltig_von=date.fromisoformat(req.gueltig_von),
        gueltig_bis=date.fromisoformat(req.gueltig_bis),
        zertifikatsnummer=req.zertifikatsnummer,
    )
    _store.add(z)
    return z

@router.get("/tenant/{tenant_id}")
def get_by_tenant(tenant_id: str):
    return _store.by_tenant(tenant_id)

@router.get("/ablaufend")
def get_ablaufend(tage_vorwarnung: int = Query(30)):
    return _store.ablaufende_zertifikate(tage_vorwarnung)
