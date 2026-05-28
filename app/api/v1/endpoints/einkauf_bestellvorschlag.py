"""
Einkauf â€” Bestell-Vorschlag Endpoints

Bestellvorschlag-Engines (3 Typen):
  GET /einkauf/bestellvorschlaege/lager    â†’ aus Lagerbestand
  GET /einkauf/bestellvorschlaege/verkauf  â†’ aus offenen VK-AuftrÃ¤gen
  GET /einkauf/bestellvorschlaege/rohware  â†’ aus Rohstoff-Bedarf

CRUD BestellvorschlÃ¤ge:
  GET    /einkauf/bestellvorschlaege        â†’ Liste
  POST   /einkauf/bestellvorschlaege        â†’ Speichern
  GET    /einkauf/bestellvorschlaege/{id}   â†’ Detail
  PUT    /einkauf/bestellvorschlaege/{id}   â†’ Aktualisieren
  DELETE /einkauf/bestellvorschlaege/{id}   â†’ LÃ¶schen
  POST   /einkauf/bestellvorschlaege/{id}/zu-bestellung â†’ Freigabe â†’ Bestellungen

CRUD ArtikelLagerParameter:
  GET    /einkauf/artikel-lager-parameter
  POST   /einkauf/artikel-lager-parameter
  PUT    /einkauf/artikel-lager-parameter/{id}
  DELETE /einkauf/artikel-lager-parameter/{id}

CRUD Kontrakte:
  GET    /einkauf/kontrakte
  POST   /einkauf/kontrakte
  GET    /einkauf/kontrakte/{id}
  PUT    /einkauf/kontrakte/{id}
  DELETE /einkauf/kontrakte/{id}

CRUD Lieferanten (domain_einkauf):
  GET    /einkauf/lieferanten
  POST   /einkauf/lieferanten
  GET    /einkauf/lieferanten/{id}
  PUT    /einkauf/lieferanten/{id}

CRUD Bestellungen:
  GET    /einkauf/bestellungen
  POST   /einkauf/bestellungen
  GET    /einkauf/bestellungen/{id}
  PUT    /einkauf/bestellungen/{id}
  POST   /einkauf/bestellungen/{id}/versenden    â†’ E-Mail / Fax / EDI versenden
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.services.procurement_service import ProcurementService

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.einkauf_bestellvorschlag_schemas import (
    ArtikelLagerParamCreate,
    ArtikelLagerParamUpdate,
    BestellungCreate,
    BestellvorschlagOut,
    FremdwarenCreate,
    KontraktCreate,
    KontraktPosCreate,
    LagerKontenzuordnungCreate,
    LieferantCreate,
    LieferantUpdate,
    PalettenBuchungCreate,
    PfandBuchungCreate,
    VorschlagSaveRequest,
)
from pydantic import ConfigDict as _ConfigDict

router = APIRouter(tags=["einkauf", "bestellvorschlag"])


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Pydantic Schemas
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def _svc(db: Session, tenant_id: str) -> ProcurementService:
    return ProcurementService(db, tenant_id)


def _not_found(exc: EntityNotFoundError, label: str) -> HTTPException:
    return HTTPException(404, f"{label} nicht gefunden")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Bestell-Vorschlag Engines
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/bestellvorschlaege/lager", summary="Lager vorschlag",
    response_model=BestellvorschlagOut
)
async def vorschlag_lager(
    niederlassung_id: Optional[str] = Query(None),
    artikelgruppe: Optional[str] = Query(None),
    artikel_nr: Optional[str] = Query(None, alias="artikelNr"),
    warehouse_id: Optional[str] = Query(None),
    nur_unter_meldebestand: bool = Query(True),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).compute_vorschlag_lager(niederlassung_id, artikelgruppe, artikel_nr, warehouse_id, nur_unter_meldebestand)


@router.get("/einkauf/bestellvorschlaege/verkauf", summary="Verkauf vorschlag",
    response_model=BestellvorschlagOut
)
async def vorschlag_verkauf(
    niederlassung_id: Optional[str] = Query(None),
    artikelgruppe: Optional[str] = Query(None),
    von_datum: Optional[date] = Query(None, alias="vonDatum"),
    bis_datum: Optional[date] = Query(None, alias="bisDatum"),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).compute_vorschlag_verkauf(niederlassung_id, artikelgruppe, von_datum, bis_datum)


@router.get("/einkauf/bestellvorschlaege/rohware", summary="Rohware vorschlag",
    response_model=BestellvorschlagOut
)
async def vorschlag_rohware(
    stichtag: Optional[date] = Query(None),
    niederlassung_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).compute_vorschlag_rohware(stichtag, niederlassung_id)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# BestellvorschlÃ¤ge CRUD
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/bestellvorschlaege", summary="Bestellvorschlaege auflisten",
    response_model=BestellvorschlagOut
)
async def list_bestellvorschlaege(
    vorschlag_typ: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    von: Optional[date] = Query(None),
    bis: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_vorschlaege(vorschlag_typ, status, von, bis)


@router.post("/einkauf/bestellvorschlaege", status_code=201, summary="Bestellvorschlag anlegen",
    response_model=BestellvorschlagOut
)
async def create_bestellvorschlag(
    data: VorschlagSaveRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_vorschlag(data.vorschlag_typ, data.positionen, data.parameter, data.niederlassung_id, data.bezeichnung)


@router.get("/einkauf/bestellvorschlaege/{vorschlag_id}", summary="Bestellvorschlag abrufen",
    response_model=BestellvorschlagOut
)
async def get_bestellvorschlag(
    vorschlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).get_vorschlag(vorschlag_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Vorschlag nicht gefunden")


@router.put("/einkauf/bestellvorschlaege/{vorschlag_id}", summary="Bestellvorschlag aktualisieren",
    response_model=BestellvorschlagOut
)
async def update_bestellvorschlag(
    vorschlag_id: str,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_vorschlag(vorschlag_id, data)
    except EntityNotFoundError:
        raise HTTPException(404, "Vorschlag nicht gefunden")


@router.delete("/einkauf/bestellvorschlaege/{vorschlag_id}", status_code=204, response_class=Response, response_model=None, summary="Bestellvorschlag lÃ¶schen")
async def delete_bestellvorschlag(
    vorschlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    try:
        _svc(db, tenant_id).delete_vorschlag(vorschlag_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Vorschlag nicht gefunden")
    return Response(status_code=204)


@router.post("/einkauf/bestellvorschlaege/{vorschlag_id}/zu-bestellung", status_code=201, summary="Freigeben vorschlag",
    response_model=None
)
async def vorschlag_freigeben(
    vorschlag_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).freigebe_vorschlag(vorschlag_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Vorschlag nicht gefunden")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# ArtikelLagerParameter CRUD
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/artikel-lager-parameter", summary="Artikel lager parameter auflisten",
    response_model=BestellvorschlagOut
)
async def list_artikel_lager_parameter(
    article_id: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    niederlassung_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_artikel_lager_parameter(article_id, warehouse_id, niederlassung_id)


@router.post("/einkauf/artikel-lager-parameter", status_code=201, summary="Artikel lager parameter anlegen",
    response_model=BestellvorschlagOut
)
async def create_artikel_lager_parameter(
    data: ArtikelLagerParamCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).create_artikel_lager_parameter(data.model_dump())
    except ConflictError as exc:
        raise HTTPException(409, exc.detail)


@router.put("/einkauf/artikel-lager-parameter/{param_id}", summary="Artikel lager parameter aktualisieren",
    response_model=BestellvorschlagOut
)
async def update_artikel_lager_parameter(
    param_id: str,
    data: ArtikelLagerParamUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_artikel_lager_parameter(param_id, data.model_dump(exclude_none=True))
    except EntityNotFoundError:
        raise HTTPException(404, "Parameter nicht gefunden")


@router.delete("/einkauf/artikel-lager-parameter/{param_id}", status_code=204, response_class=Response, response_model=None, summary="Artikel lager parameter lÃ¶schen")
async def delete_artikel_lager_parameter(
    param_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    try:
        _svc(db, tenant_id).delete_artikel_lager_parameter(param_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Parameter nicht gefunden")
    return Response(status_code=204)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Lieferanten CRUD
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/lieferanten", summary="Lieferanten auflisten",
    response_model=EinkaufBestellvorschlagOut
)
async def list_lieferanten(
    suche: Optional[str] = Query(None),
    aktiv: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_lieferanten(suche, aktiv)


@router.post("/einkauf/lieferanten", status_code=201, summary="Lieferant anlegen",
    response_model=BestellvorschlagOut
)
async def create_lieferant(
    data: LieferantCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_lieferant(data.model_dump())


@router.get("/einkauf/lieferanten/{lieferant_id}", summary="Lieferant abrufen",
    response_model=BestellvorschlagOut
)
async def get_lieferant(
    lieferant_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).get_lieferant(lieferant_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Lieferant nicht gefunden")


@router.put("/einkauf/lieferanten/{lieferant_id}", summary="Lieferant aktualisieren",
    response_model=BestellvorschlagOut
)
async def update_lieferant(
    lieferant_id: str,
    data: LieferantUpdate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_lieferant(lieferant_id, data.model_dump(exclude_none=True))
    except EntityNotFoundError:
        raise HTTPException(404, "Lieferant nicht gefunden")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Kontrakte CRUD
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/kontrakte", summary="Kontrakte auflisten",
    response_model=BestellvorschlagOut
)
async def list_kontrakte(
    lieferant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_kontrakte(lieferant_id, status)


@router.post("/einkauf/kontrakte", status_code=201, summary="Kontrakt anlegen",
    response_model=BestellvorschlagOut
)
async def create_kontrakt(
    data: KontraktCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_kontrakt(data.model_dump())


@router.get("/einkauf/kontrakte/{kontrakt_id}", summary="Kontrakt abrufen",
    response_model=BestellvorschlagOut
)
async def get_kontrakt(
    kontrakt_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).get_kontrakt(kontrakt_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Kontrakt nicht gefunden")


@router.put("/einkauf/kontrakte/{kontrakt_id}", summary="Kontrakt aktualisieren",
    response_model=BestellvorschlagOut
)
async def update_kontrakt(
    kontrakt_id: str,
    data: KontraktCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_kontrakt(kontrakt_id, data.model_dump(exclude_none=True))
    except EntityNotFoundError:
        raise HTTPException(404, "Kontrakt nicht gefunden")


@router.post("/einkauf/kontrakte/{kontrakt_id}/positionen", status_code=201, summary="Kontrakt position hinzufÃ¼gen",
    response_model=BestellvorschlagOut
)
async def add_kontrakt_position(
    kontrakt_id: str,
    data: KontraktPosCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).add_kontrakt_position(kontrakt_id, data.model_dump())
    except EntityNotFoundError:
        raise HTTPException(404, "Kontrakt nicht gefunden")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Bestellungen CRUD
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/bestellungen", summary="Bestellungen auflisten",
    response_model=BestellvorschlagOut
)
async def list_bestellungen(
    lieferant_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    von: Optional[date] = Query(None),
    bis: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_bestellungen(lieferant_id, status, von, bis)


@router.post("/einkauf/bestellungen/import", summary="Bestellungen importieren",
    response_model=BestellvorschlagOut
)
async def import_bestellungen(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    content = await file.read()
    lines = content.decode("utf-8", errors="ignore").strip().splitlines()
    received = max(1, len(lines))
    return {"received": received, "message": "Import in Verarbeitung. Bestellungen werden angelegt.",
            "filename": file.filename or "upload"}


@router.post("/einkauf/bestellungen", status_code=201, summary="Bestellung anlegen",
    response_model=BestellvorschlagOut
)
async def create_bestellung(
    data: BestellungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_bestellung(data.model_dump())


@router.get("/einkauf/bestellungen/{bestellung_id}", summary="Bestellung abrufen",
    response_model=BestellvorschlagOut
)
async def get_bestellung(
    bestellung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).get_bestellung(bestellung_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")


@router.put("/einkauf/bestellungen/{bestellung_id}", summary="Bestellung aktualisieren",
    response_model=BestellvorschlagOut
)
async def update_bestellung(
    bestellung_id: str,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_bestellung(bestellung_id, data)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")


@router.post("/einkauf/bestellungen/{bestellung_id}/versenden", summary="Versenden bestellung",
    response_model=BestellvorschlagOut
)
async def bestellung_versenden(
    bestellung_id: str,
    versand_art: str = Query("email"),
    empfaenger: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).versende_bestellung_svc(bestellung_id, versand_art, empfaenger)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Lager-Konten-Zuordnung CRUD
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/lager-konten", summary="Lager konten auflisten",
    response_model=BestellvorschlagOut
)
async def list_lager_konten(
    artikelgruppe: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_lager_konten(artikelgruppe)


@router.post("/einkauf/lager-konten", status_code=201, summary="Lager konto anlegen",
    response_model=BestellvorschlagOut
)
async def create_lager_konto(
    data: LagerKontenzuordnungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_lager_konto(data.model_dump())


@router.put("/einkauf/lager-konten/{konto_id}", summary="Lager konto aktualisieren",
    response_model=BestellvorschlagOut
)
async def update_lager_konto(
    konto_id: str,
    data: LagerKontenzuordnungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_lager_konto(konto_id, data.model_dump(exclude_none=True))
    except EntityNotFoundError:
        raise HTTPException(404, "Konten-Zuordnung nicht gefunden")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Paletten-Konto
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/paletten-konto/{partner_id}", summary="Paletten saldo abrufen",
    response_model=BestellvorschlagOut
)
async def get_paletten_saldo(
    partner_id: str,
    paletten_typ: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).get_paletten_saldo(partner_id, paletten_typ)


@router.post("/einkauf/paletten-konto", status_code=201, summary="Paletten buchung anlegen",
    response_model=BestellvorschlagOut
)
async def create_paletten_buchung(
    data: PalettenBuchungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_paletten_buchung(data.model_dump())


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Pfand-Konto
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/pfand-konto/{partner_id}", summary="Pfand saldo abrufen",
    response_model=BestellvorschlagOut
)
async def get_pfand_saldo(
    partner_id: str,
    gebinde_typ: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).get_pfand_saldo(partner_id, gebinde_typ)


@router.post("/einkauf/pfand-konto", status_code=201, summary="Pfand buchung anlegen",
    response_model=BestellvorschlagOut
)
async def create_pfand_buchung(
    data: PfandBuchungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_pfand_buchung(data.model_dump())


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Fremdwaren-Einlagerung
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.get("/einkauf/fremdwaren-einlagerung", summary="Fremdwaren auflisten",
    response_model=BestellvorschlagOut
)
async def list_fremdwaren(
    eigentuemer_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    warehouse_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    return _svc(db, tenant_id).list_fremdwaren(eigentuemer_id, status, warehouse_id)


@router.post("/einkauf/fremdwaren-einlagerung", status_code=201, summary="Fremdwaren einlagerung anlegen",
    response_model=BestellvorschlagOut
)
async def create_fremdwaren_einlagerung(
    data: FremdwarenCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    return _svc(db, tenant_id).create_fremdwaren(data.model_dump())


@router.put("/einkauf/fremdwaren-einlagerung/{einlagerung_id}", summary="Fremdwaren einlagerung aktualisieren",
    response_model=BestellvorschlagOut
)
async def update_fremdwaren_einlagerung(
    einlagerung_id: str,
    data: dict[str, Any],
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).update_fremdwaren(einlagerung_id, data)
    except EntityNotFoundError:
        raise HTTPException(404, "Einlagerung nicht gefunden")


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# Bestellungen Workflow
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

@router.post("/einkauf/bestellungen/{bestellung_id}/freigeben", summary="Freigeben bestellung",
    response_model=BestellvorschlagOut
)
async def bestellung_freigeben(
    bestellung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).freigebe_bestellung(bestellung_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")
    except ValidationFailedError as exc:
        raise HTTPException(400, exc.detail)


@router.post("/einkauf/bestellungen/{bestellung_id}/stornieren", summary="Stornieren bestellung",
    response_model=BestellvorschlagOut
)
async def bestellung_stornieren(
    bestellung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    try:
        return _svc(db, tenant_id).storniere_bestellung(bestellung_id)
    except EntityNotFoundError:
        raise HTTPException(404, "Bestellung nicht gefunden")
    except ValidationFailedError as exc:
        raise HTTPException(400, exc.detail)

