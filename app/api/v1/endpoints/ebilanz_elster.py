"""eBilanz / ELSTER export and ERiC submission endpoint."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Optional
from uuid import UUID
from fastapi.responses import Response
from app.services.ebilanz_xbrl_service import VERSION, CORE_FIELDS, catalog_page, fact_text, build_draft

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.auth.finance_roles import finance_read, finance_write, finance_admin

from app.api.v1.schemas.ebilanz_elster_schemas import EbilanzElsterOut


router = APIRouter(prefix="/ebilanz", tags=["finance", "ebilanz", "elster"], dependencies=[Depends(finance_read)])

# ---------------------------------------------------------------------------
# XBRL taxonomy helpers
# ---------------------------------------------------------------------------

# Local application draft prerequisites, not an official Mussfeld matrix.
_GCD_PFLICHTFELDER = list(CORE_FIELDS)


# Schema ownership belongs to Alembic, never to a request handler.
_NOT_READY = "Keine echte ELSTER-Anbindung konfiguriert; es wurde nichts uebertragen."


def _unavailable(db):
    db.rollback()
    return HTTPException(503, "eBilanz-Datenbank nicht verfuegbar; kein Erfolg bestaetigt.")


def _export(db, tenant_id, export_id):
    try:
        row = db.execute(text("SELECT * FROM domain_finance.ebilanz_exports WHERE id = :id AND tenant_id = :tid"),
                         {"id": export_id, "tid": tenant_id}).mappings().first()
    except SQLAlchemyError as exc:
        raise _unavailable(db) from exc
    if row is None:
        raise HTTPException(404, "Export nicht gefunden")
    return dict(row)


def _projection(row):
    result = dict(row)
    result["export_id"] = str(result.pop("id"))
    # Historical records came from the removed simulator, never from ERiC.
    uncertain = result.get("status") in ("VALIDIERT", "UEBERTRAGEN", "ANGENOMMEN") or bool(result.get("elster_transfer_ticket"))
    result["status"] = "NICHT_BESTAETIGT" if uncertain else result.get("status", "ERSTELLT")
    result["elster_transfer_ticket"] = None
    result["uebertragen_am"] = None
    result["xbrl_paketgroesse_kb"] = 0  # No complete XBRL document is stored here.
    result["uebertragung_bestaetigt"] = False
    return result


def _list_exports(db, tenant_id, limit, skip):
    try:
        rows = db.execute(text("SELECT * FROM domain_finance.ebilanz_exports WHERE tenant_id = :tid ORDER BY erstellt_am DESC, id LIMIT :limit OFFSET :skip"),
                          {"tid": tenant_id, "limit": limit, "skip": skip}).mappings().fetchmany(limit)
    except SQLAlchemyError as exc:
        raise _unavailable(db) from exc
    return [_projection(row) for row in rows]


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class EBilanzExportRequest(BaseModel):
    wirtschaftsjahr: int = Field(ge=1900, le=9999)
    bilanzart: str = Field(min_length=1, max_length=20)
    berichtsperiode_von: date
    berichtsperiode_bis: date
    steuernummer: str = Field(min_length=1, max_length=40)
    finanzamt_nr: str = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def valid_period(self):
        if self.berichtsperiode_von > self.berichtsperiode_bis:
            raise ValueError("Berichtsperiode beginnt nach ihrem Ende")
        if self.bilanzart not in ("HGB", "IFRS", "EStG"):
            raise ValueError("Unbekannte Bilanzart")
        if not self.steuernummer.strip() or not self.finanzamt_nr.strip():
            raise ValueError("Steuernummer und Finanzamt duerfen nicht leer sein")
        if self.berichtsperiode_von.year not in (2025, 2026):
            raise ValueError("Taxonomie 6.9 nur fuer Periodenbeginn 2025/2026 abgenommen")
        if self.wirtschaftsjahr != self.berichtsperiode_von.year:
            raise ValueError("Wirtschaftsjahr und Periodenbeginn widersprechen sich")
        return self


class EBilanzExportResult(BaseModel):
    export_id: str
    status: str  # ERSTELLT / VALIDIERT / UEBERTRAGEN / FEHLER
    xbrl_paketgroesse_kb: int = 0
    taxonomie_version: str = VERSION
    validierungsfehler: list[str] = Field(default_factory=list)
    hinweise: list[str] = Field(default_factory=list)


class EBilanzValidierungsRequest(BaseModel):
    """Dict of XBRL element names → values submitted for validation."""
    felder: dict[str, Any]


class EBilanzValidierungsResult(BaseModel):
    valid: bool
    fehlende_felder: list[str]
    warnungen: list[str]


class EricReadinessOut(BaseModel):
    status: str
    repo_contract_ready: bool
    xbrl_taxonomie_version: str
    supported_paths: list[str]
    external_gates: list[str]
    next_action: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/taxonomie-felder", summary="Felder taxonomie",
    response_model=list[EbilanzElsterOut]
)
def taxonomie_felder(limit: int = Query(100, ge=1, le=1000), skip: int = Query(0, ge=0)) -> list[dict]:
    """Paged official 6.9 GCD/core concepts, not industry or ERiC rule coverage."""
    return catalog_page(limit, skip)


@router.get("/eric-readiness", response_model=EricReadinessOut, summary="Readiness eric")
def eric_readiness() -> dict:
    """Report actual repository capabilities; external transmission is unavailable."""
    return {"status": "NOT_READY_EXTERNAL_GATE", "repo_contract_ready": False,
            "xbrl_taxonomie_version": VERSION,
            "supported_paths": ["Amtlicher 6.9 GCD-/Kernkonzeptkatalog", "Lokale Entwurfsvorpruefung", "XML-Entwurf einfacher expliziter Fakten (unvalidiert)", "Export-Entwurfsmetadaten", "Unbestaetigter lokaler Status"],
            "external_gates": ["Steuerliche Tupel-/Dimensions-/Kontenzuordnung und amtliche Validierung fehlen",
                               "ERiC-Bibliothek/Zertifikat und echte Empfangsquittung fehlen"],
            "next_action": "Vollstaendigen XBRL- und ERiC-Fachweg implementieren und extern abnehmen"}


@router.post("/validieren", response_model=EBilanzValidierungsResult, summary="Ebilanz validieren")
def validieren_ebilanz(payload: EBilanzValidierungsRequest) -> dict:
    """Local presence checks only, never official XBRL/ERiC validation."""
    fehlende = [key for key in _GCD_PFLICHTFELDER if payload.felder.get(key) is None or str(payload.felder[key]).strip() == ""]
    warnungen = []
    for key, value in sorted(payload.felder.items()):
        try:
            fact_text(key, value)
        except ValueError as exc:
            warnungen.append(str(exc))
    lokale_fehler = bool(warnungen)
    warnungen.append("Nur lokale Pflichtfeldpruefung; keine vollstaendige XBRL-/ERiC-Validierung.")
    return {"valid": not fehlende and not lokale_fehler, "fehlende_felder": fehlende, "warnungen": warnungen}


@router.get("/meldungen", summary="Meldungen auflisten",
    response_model=list[EbilanzElsterOut]
)
def list_meldungen(limit: int = Query(100, ge=1, le=1000), skip: int = Query(0, ge=0),
                   db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict]:
    return _list_exports(db, tenant_id, limit, skip)


@router.post("/export/erstellen", response_model=EBilanzExportResult, status_code=201, summary="Export-Entwurfsmetadaten speichern", dependencies=[Depends(finance_write)])
def erstellen(payload: EBilanzExportRequest, db: Session = Depends(get_db),
              tenant_id: str = Depends(get_tenant_id)) -> dict:
    """Persist draft metadata. No XBRL generation or transmission is claimed."""
    export_id = str(uuid.uuid4())
    try:
        db.execute(text("""INSERT INTO domain_finance.ebilanz_exports
            (id, tenant_id, wirtschaftsjahr, bilanzart, berichtsperiode_von, berichtsperiode_bis,
             steuernummer, finanzamt_nr, status, taxonomie_version, xbrl_paketgroesse_kb)
            VALUES (:id, :tid, :wj, :art, :von, :bis, :stnr, :fanr, 'ERSTELLT', :taxonomie, 0)"""),
            {"taxonomie": VERSION, "id": export_id, "tid": tenant_id, "wj": payload.wirtschaftsjahr, "art": payload.bilanzart,
             "von": payload.berichtsperiode_von.isoformat(), "bis": payload.berichtsperiode_bis.isoformat(),
             "stnr": payload.steuernummer, "fanr": payload.finanzamt_nr})
        db.commit()
    except SQLAlchemyError as exc:
        raise _unavailable(db) from exc
    return {"export_id": export_id, "status": "ERSTELLT", "xbrl_paketgroesse_kb": 0,
            "taxonomie_version": VERSION, "validierungsfehler": [],
            "hinweise": ["Entwurfsmetadaten gespeichert; einfacher XML-Entwurf separat abrufbar, amtliche Validierung und ELSTER-Uebertragung fehlen."]}


class XbrlDraftRequest(BaseModel):
    entity_identifier: str = Field(min_length=1, max_length=100)
    entity_scheme: str = Field(min_length=1, max_length=500)
    facts: dict[str, str | None] = Field(min_length=1, max_length=2000)


@router.post("/export/{export_id}/xbrl-entwurf", response_class=Response,
             summary="Unvalidierten XBRL-Entwurf als XML herunterladen",
             responses={200: {"content": {"application/xml": {"schema": {"type": "string"}}}}},
             dependencies=[Depends(finance_write)])
def xbrl_entwurf(export_id: UUID, payload: XbrlDraftRequest, db: Session = Depends(get_db),
                 tenant_id: str = Depends(get_tenant_id)) -> Response:
    row = _export(db, tenant_id, str(export_id))
    if row["taxonomie_version"] != VERSION or row["bilanzart"] not in ("HGB", "EStG"):
        raise HTTPException(409, "Exportversion nicht im amtlichen 6.9-Entwurfsweg abgenommen")
    try:
        content = build_draft(payload.facts, date.fromisoformat(str(row["berichtsperiode_von"])),
                              date.fromisoformat(str(row["berichtsperiode_bis"])),
                              payload.entity_identifier, payload.entity_scheme)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return Response(content, media_type="application/xml", headers={
        "Content-Disposition": f'attachment; filename="ebilanz-{export_id}-entwurf.xml"',
        "X-XBRL-Status": "DRAFT_UNVALIDATED", "X-XBRL-Taxonomy": VERSION,
        "Cache-Control": "no-store",
    })


@router.post("/export/{export_id}/validieren", response_model=EbilanzElsterOut,
    summary="Export-Validierungsverfuegbarkeit pruefen", dependencies=[Depends(finance_write)]
)
def validieren(export_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict:
    _export(db, tenant_id, export_id)
    raise HTTPException(409, "Kein vollstaendiges XBRL-Dokument vorhanden; Export wurde nicht validiert.")


@router.post("/export/{export_id}/uebertragen", response_model=EbilanzElsterOut,
    summary="ELSTER-Verfuegbarkeit pruefen", dependencies=[Depends(finance_admin)]
)
def uebertragen(export_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict:
    _export(db, tenant_id, export_id)
    raise HTTPException(409, _NOT_READY)


@router.get("/export/{export_id}/uebertragungsstatus", summary="Uebertragungsstatus",
    response_model=EbilanzElsterOut
)
def uebertragungsstatus(export_id: str, db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> dict:
    row = _projection(_export(db, tenant_id, export_id))
    return {"export_id": export_id, "status": row["status"], "ticket": None,
            "uebertragung_bestaetigt": False, "hinweis": _NOT_READY}


@router.get("/exports", summary="Exports auflisten",
    response_model=list[EbilanzElsterOut]
)
def list_exports(limit: int = Query(100, ge=1, le=1000), skip: int = Query(0, ge=0),
                 db: Session = Depends(get_db), tenant_id: str = Depends(get_tenant_id)) -> list[dict]:
    return _list_exports(db, tenant_id, limit, skip)


# ── UStVA (Umsatzsteuervoranmeldung § 18 UStG) ───────────────────────────────

class UStVARequest(BaseModel):
    steuernummer: str = Field(..., description="Steuernummer des Unternehmens")
    finanzamt_nr: str = Field(..., description="Finanzamtsnummer (4-stellig)")
    voranmeldungszeitraum: str = Field(..., description="Monat YYYY-MM oder Quartal YYYY-Q1/Q2/Q3/Q4")
    # Kennzahlen gemäß § 18 UStG Anlage UR
    kz_81_steuerpflichtige_ums_19: float = Field(0.0, description="KZ 81: Steuerpfl. Umsätze 19 %")
    kz_86_steuerpflichtige_ums_7:  float = Field(0.0, description="KZ 86: Steuerpfl. Umsätze 7 %")
    kz_35_innergemeinschaftliche_lieferungen: float = Field(0.0, description="KZ 41/86: Innergem. Lieferungen")
    kz_66_vorsteuer_rechnungen:    float = Field(0.0, description="KZ 66: Vorsteuer aus Rechnungen")
    kz_61_einfuhrvorsteuer:        float = Field(0.0, description="KZ 61: Einfuhrumsatzsteuervorsteuer")
    kz_67_innergemeinschaftlicher_erwerb_vorsteuer: float = Field(0.0, description="KZ 67: Vorsteuer innergem. Erwerb")
    dauerfreistellung: bool = Field(False, description="§ 18 Abs. 2 UStG: Dauerfreist. von Voranmeldung")


class UStVAErgebnis(BaseModel):
    voranmeldungszeitraum: str
    steuernummer: str
    finanzamt_nr: str
    zahllast_eur: float
    erstattung_eur: float
    elster_status: str
    transfer_ticket: Optional[str] = None
    hinweis: str


@router.post("/elster/ustva", response_model=UStVAErgebnis, summary="UStVA-Uebertragungsverfuegbarkeit pruefen", dependencies=[Depends(finance_admin)])
async def submit_ustva(body: UStVARequest, db: Session = Depends(get_db),
                       tenant_id: str = Depends(get_tenant_id)) -> UStVAErgebnis:
    """Transmission is unavailable; never create simulated tickets or rows."""
    raise HTTPException(409, _NOT_READY)


@router.get("/elster/ustva", summary="UStVA-Übermittlungen auflisten",
    response_model=list[EbilanzElsterOut]
)
async def list_ustva(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> list[dict]:
    try:
        rows = db.execute(text("""SELECT id, steuernummer, finanzamt_nr, voranmeldungszeitraum,
            zahllast_eur, erstattung_eur, erstellt_am FROM domain_finance.ustva_voranmeldungen
            WHERE tenant_id = :tid ORDER BY erstellt_am DESC, id LIMIT 100"""), {"tid": tenant_id}).mappings().fetchmany(100)
    except SQLAlchemyError as exc:
        raise _unavailable(db) from exc
    return [{**dict(row), "elster_status": "NICHT_BESTAETIGT", "transfer_ticket": None} for row in rows]
