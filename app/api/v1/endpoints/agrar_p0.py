from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.agrar_p0_schemas import AgrarP0Out


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
    response_model=AgrarP0Out
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
    return bilanz.model_dump()

@router.post("/psm-protokoll", status_code=201, summary="Psm protokoll erstelle",
    response_model=AgrarP0Out
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
    response_model=AgrarP0Out
)
def get_schlag_flik(schlag_id: str):
    """Gibt FLIK-Informationen eines Schlages zurück (Stub für Wave 6)."""
    return {"schlag_id": schlag_id, "flik_id": None, "geometry_wkt": None, "nuts3_region": None, "schema_version": 1}


# ---------------------------------------------------------------------------
# DOM-AGRAR-004.2 — Partie-Aggregation
# ---------------------------------------------------------------------------

from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db


class PartieCreateIn(BaseModel):
    acceptance_ids: list[str]
    campaign_id: Optional[str] = None


class TrocknungIn(BaseModel):
    moisture_out_pct: float
    cost_eur_per_pct_ton: Optional[float] = None


class StatusTransitionIn(BaseModel):
    new_status: str
    operator: Optional[str] = "system"
    reason: Optional[str] = None


class StornoIn(BaseModel):
    grund: Optional[str] = None
    operator: Optional[str] = "system"


@router.post(
    "/partien",
    status_code=201,
    summary="Partie aus Ernteannahmen aggregieren (DOM-AGRAR-004.2)",
    response_model=AgrarP0Out,
)
def create_partie(
    body: PartieCreateIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """Aggregiert mehrere Ernteannahmen zu einer Handelspartie."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    from app.services.agrar_partie_aggregate_service import create_partie as svc, PartieError
    try:
        return svc(db=db, tenant_id=x_tenant_id, acceptance_ids=body.acceptance_ids, campaign_id=body.campaign_id)
    except PartieError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get(
    "/partien/{partie_id}",
    summary="Partie abrufen (DOM-AGRAR-004.2)",
    response_model=AgrarP0Out,
)
def get_partie(
    partie_id: str,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    from app.services.agrar_partie_aggregate_service import get_partie as svc, PartieError
    try:
        return svc(db=db, partie_id=partie_id, tenant_id=x_tenant_id)
    except PartieError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# DOM-AGRAR-004.3 — Trocknungsabrechnung
# ---------------------------------------------------------------------------

@router.post(
    "/partien/{partie_id}/trocknung",
    status_code=201,
    summary="Trocknungsabrechnung berechnen (DOM-AGRAR-004.3)",
    response_model=AgrarP0Out,
)
def berechne_trocknung(
    partie_id: str,
    body: TrocknungIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """Berechnet und persistiert Trocknungskosten für eine Partie (idempotent)."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    from app.services.agrar_trocknung_abrechnung_service import berechne_trocknung as svc, TrocknungError
    try:
        return svc(db=db, partie_id=partie_id, tenant_id=x_tenant_id,
                   moisture_out_pct=body.moisture_out_pct,
                   cost_eur_per_pct_ton=body.cost_eur_per_pct_ton)
    except TrocknungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# DOM-AGRAR-004.4 — Selbstabrechnung-Lifecycle
# ---------------------------------------------------------------------------

@router.post(
    "/selbstabrechnung/{rechnung_id}/issue",
    summary="Selbstabrechnung auf ISSUED setzen (DOM-AGRAR-004.4)",
    response_model=AgrarP0Out,
)
def issue_selbstabrechnung(
    rechnung_id: str,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """Selbstabrechnung von DRAFT → ISSUED (fail-closed)."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    from app.services.agrar_selbstabrechnung_lifecycle_service import transition_status, SelbstabrechnungError
    try:
        return transition_status(db=db, rechnung_id=rechnung_id, tenant_id=x_tenant_id, new_status="ISSUED")
    except SelbstabrechnungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/selbstabrechnung/{rechnung_id}/status",
    summary="Selbstabrechnung-Status wechseln (DOM-AGRAR-004.4)",
    response_model=AgrarP0Out,
)
def set_selbstabrechnung_status(
    rechnung_id: str,
    body: StatusTransitionIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """Allgemeiner Status-Übergang für Selbstabrechnung."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    from app.services.agrar_selbstabrechnung_lifecycle_service import transition_status, SelbstabrechnungError
    try:
        return transition_status(db=db, rechnung_id=rechnung_id, tenant_id=x_tenant_id,
                                 new_status=body.new_status, operator=body.operator or "system",
                                 reason=body.reason)
    except SelbstabrechnungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/selbstabrechnung/{rechnung_id}/storno",
    status_code=201,
    summary="Selbstabrechnung stornieren (idempotent) (DOM-AGRAR-004.4)",
    response_model=AgrarP0Out,
)
def storno_selbstabrechnung(
    rechnung_id: str,
    body: StornoIn,
    x_tenant_id: Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """Storniert eine Selbstabrechnung (nur aus DRAFT oder ISSUED, idempotent)."""
    if not x_tenant_id:
        raise HTTPException(status_code=422, detail="X-Tenant-ID erforderlich.")
    from app.services.agrar_selbstabrechnung_lifecycle_service import storno_selbstabrechnung as svc, SelbstabrechnungError
    try:
        return svc(db=db, rechnung_id=rechnung_id, tenant_id=x_tenant_id,
                   grund=body.grund, operator=body.operator or "system")
    except SelbstabrechnungError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
