from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class CompatFlexOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/agrar/p0", tags=["agrar-p0"])

class DuengeBilanzRequest(BaseModel):
    tenant_id: str
    schlag_id: str
    wirtschaftsjahr: int
    eintraege: list[dict]
    bedarf_n_kg_ha: float = 170.0
    bedarf_p_kg_ha: float = 60.0
    bedarf_k_kg_ha: float = 80.0

class PsmProtokolleintragRequest(BaseModel):
    tenant_id: str
    schlag_id: str
    anwendungsdatum: str  # ISO date
    praeparat_name: str
    wirkstoff: str
    aufwandmenge_l_ha: float
    sachkunde_nr: str
    wasser_schutzgebiet: bool = False
    wartezeit_tage: Optional[int] = None
    flaeche_ha: float
    zulassungsnummer: Optional[str] = None

@router.post("/duenge-bilanz", summary="Duenge bilanz berechne",
    response_model=CompatFlexOut
)
def berechne_duenge_bilanz(req: DuengeBilanzRequest):
    from app.core.duenge_bilanz import DuengeBilanz, DuengemittelEintrag, NaehrstoffTyp
    from datetime import date as _date
    eintraege = []
    for e in req.eintraege:
        eintraege.append(DuengemittelEintrag(
            duengemittel_name=e.get("duengemittel_name", ""),
            naehrstoff=NaehrstoffTyp(e["naehrstoff"]),
            menge_kg_ha=float(e["menge_kg_ha"]),
            ausbringdatum=_date.fromisoformat(e["ausbringdatum"]),
            schlag_id=e["schlag_id"],
        ))
    bilanz = DuengeBilanz.berechne(
        tenant_id=req.tenant_id,
        schlag_id=req.schlag_id,
        wirtschaftsjahr=req.wirtschaftsjahr,
        eintraege=eintraege,
        bedarf_n_kg_ha=req.bedarf_n_kg_ha,
        bedarf_p_kg_ha=req.bedarf_p_kg_ha,
        bedarf_k_kg_ha=req.bedarf_k_kg_ha,
    )
    return bilanz

@router.post("/psm-protokoll", status_code=201, summary="Psm protokoll erstelle",
    response_model=CompatFlexOut
)
def erstelle_psm_protokoll(req: PsmProtokolleintragRequest):
    from app.core.psm_protokoll import PsmAnwendungProtokoll
    protokoll = PsmAnwendungProtokoll(
        protokoll_id=str(uuid.uuid4()),
        tenant_id=req.tenant_id,
        schlag_id=req.schlag_id,
        anwendungsdatum=date.fromisoformat(req.anwendungsdatum),
        praeparat_name=req.praeparat_name,
        wirkstoff=req.wirkstoff,
        aufwandmenge_l_ha=req.aufwandmenge_l_ha,
        sachkunde_nr=req.sachkunde_nr,
        wasser_schutzgebiet=req.wasser_schutzgebiet,
        wartezeit_tage=req.wartezeit_tage,
        flaeche_ha=req.flaeche_ha,
        zulassungsnummer=req.zulassungsnummer,
    )
    return {"protokoll_id": protokoll.protokoll_id, "gobd_vollstaendig": protokoll.ist_gobd_vollstaendig(), "schema_version": 1}

@router.get("/schlag/{schlag_id}/flik", summary="Schlag flik abrufen",
    response_model=CompatFlexOut
)
def get_schlag_flik(schlag_id: str):
    """Gibt FLIK-Informationen eines Schlages zurück (Stub für Wave 6)."""
    return {"schlag_id": schlag_id, "flik_id": None, "geometry_wkt": None, "nuts3_region": None, "schema_version": 1}
