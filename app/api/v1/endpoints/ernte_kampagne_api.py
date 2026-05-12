from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.ernte_kampagne import ErnteArt, ErnteKampagne, ErnteKampagneStore, SchlagErnteziel

router = APIRouter(prefix="/ernte-kampagnen", tags=["ernte-kampagnen"])
_store = ErnteKampagneStore()


class SchlagErntezielRequest(BaseModel):
    schlag_id: str
    sorte: str
    flaeche_ha: float
    ziel_ertrag_t_ha: float


class ErnteKampagneCreateRequest(BaseModel):
    tenant_id: str
    wirtschaftsjahr: int
    ernte_art: str
    bezeichnung: str
    schlag_ziele: list[SchlagErntezielRequest] = Field(default_factory=list)


@router.post("", status_code=201)
def create_kampagne(req: ErnteKampagneCreateRequest) -> ErnteKampagne:
    kampagne = ErnteKampagne(
        kampagne_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        wirtschaftsjahr=req.wirtschaftsjahr,
        ernte_art=ErnteArt(req.ernte_art),
        bezeichnung=req.bezeichnung,
        schlag_ziele=[
            SchlagErnteziel(
                schlag_id=item.schlag_id,
                sorte=item.sorte,
                flaeche_ha=item.flaeche_ha,
                ziel_ertrag_t_ha=item.ziel_ertrag_t_ha,
            )
            for item in req.schlag_ziele
        ],
    )
    return _store.add(kampagne)


@router.get("/tenant/{tenant_id}")
def get_kampagnen(tenant_id: str, wirtschaftsjahr: int | None = None) -> list[ErnteKampagne]:
    if wirtschaftsjahr is not None:
        return _store.by_wirtschaftsjahr(tenant_id, wirtschaftsjahr)
    return [kampagne for kampagne in _store.kampagnen.values() if kampagne.tenant_id == tenant_id]


@router.get("/{kampagne_id}")
def get_kampagne(kampagne_id: str) -> ErnteKampagne:
    kampagne = _store.get(kampagne_id)
    if kampagne is None:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    return kampagne


@router.delete("/{kampagne_id}", status_code=204)
def delete_kampagne(kampagne_id: str) -> None:
    kampagne = _store.get(kampagne_id)
    if kampagne is None:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    if kampagne.status.value not in ("geplant",):
        raise HTTPException(status_code=400, detail="Nur geplante Kampagnen können gelöscht werden")
    del _store.kampagnen[kampagne_id]


@router.post("/{kampagne_id}/start")
def start_kampagne(kampagne_id: str) -> ErnteKampagne:
    kampagne = _store.get(kampagne_id)
    if kampagne is None:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    return kampagne.kampagne_starten()


@router.post("/{kampagne_id}/abschliessen")
def abschliessen_kampagne(kampagne_id: str) -> ErnteKampagne:
    kampagne = _store.get(kampagne_id)
    if kampagne is None:
        raise HTTPException(status_code=404, detail="Kampagne nicht gefunden")
    return kampagne.kampagne_abschliessen()
