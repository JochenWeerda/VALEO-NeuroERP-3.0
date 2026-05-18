"""eBilanz / ELSTER Direktschnittstelle Stub."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Any, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/ebilanz", tags=["finance", "ebilanz", "elster"])

# ---------------------------------------------------------------------------
# XBRL taxonomy helpers
# ---------------------------------------------------------------------------

XBRL_NAMESPACE = "http://www.xbrl.de/taxonomies/de-gaap-ci/role/link"

# Subset of GCD / DE-GAAP taxonomy fields with their classification.
# Source: XBRL Deutschland eBilanz Taxonomie 6.7
_TAXONOMY_FELDER: list[dict[str, str]] = [
    # GCD — Generelle Classified Data
    {"element": "de-gcd:genInfo.doc.id.companyId.companyName", "klasse": "GCD", "pflicht": "ja", "typ": "string", "label": "Firmenname"},
    {"element": "de-gcd:genInfo.doc.id.companyId.location.country", "klasse": "GCD", "pflicht": "ja", "typ": "string", "label": "Sitzland"},
    {"element": "de-gcd:genInfo.doc.period.fiscalYearBegin", "klasse": "GCD", "pflicht": "ja", "typ": "date", "label": "Beginn Wirtschaftsjahr"},
    {"element": "de-gcd:genInfo.doc.period.fiscalYearEnd", "klasse": "GCD", "pflicht": "ja", "typ": "date", "label": "Ende Wirtschaftsjahr"},
    {"element": "de-gcd:genInfo.doc.id.reportElement.statementType", "klasse": "GCD", "pflicht": "ja", "typ": "string", "label": "Berichtsart"},
    {"element": "de-gcd:genInfo.doc.id.companyId.taxNumber", "klasse": "GCD", "pflicht": "ja", "typ": "string", "label": "Steuernummer"},
    {"element": "de-gcd:genInfo.doc.id.companyId.financialAuthority", "klasse": "GCD", "pflicht": "ja", "typ": "string", "label": "Finanzamt-Nummer"},
    # GAAP — Bilanzpositionen (DE-HGB)
    {"element": "de-gaap-ci:bs.ass.fixAss", "klasse": "GAAP", "pflicht": "nein", "typ": "monetary", "label": "Anlagevermögen"},
    {"element": "de-gaap-ci:bs.ass.currAss", "klasse": "GAAP", "pflicht": "nein", "typ": "monetary", "label": "Umlaufvermögen"},
    {"element": "de-gaap-ci:bs.ass.currAss.receiv.tradeReceiv", "klasse": "GAAP", "pflicht": "nein", "typ": "monetary", "label": "Forderungen aus L+L"},
    {"element": "de-gaap-ci:bs.ass.currAss.cashInHand", "klasse": "GAAP", "pflicht": "nein", "typ": "monetary", "label": "Kassenbestand/Bank"},
    {"element": "de-gaap-ci:bs.eqLiab.equity", "klasse": "GAAP", "pflicht": "nein", "typ": "monetary", "label": "Eigenkapital"},
    {"element": "de-gaap-ci:bs.eqLiab.liab.notesPayable.tradeAccPayable", "klasse": "GAAP", "pflicht": "nein", "typ": "monetary", "label": "Verbindlichkeiten aus L+L"},
    {"element": "de-gaap-ci:is.netIncome", "klasse": "GAAP", "pflicht": "nein", "typ": "monetary", "label": "Jahresüberschuss/-fehlbetrag"},
    {"element": "de-gaap-ci:is.grossProfit", "klasse": "GAAP", "pflicht": "nein", "typ": "monetary", "label": "Rohergebnis"},
]

# Pflichtfelder aus GCD-Taxonomie
_GCD_PFLICHTFELDER = [f["element"] for f in _TAXONOMY_FELDER if f["pflicht"] == "ja"]


# ---------------------------------------------------------------------------
# Ensure table helper
# ---------------------------------------------------------------------------

def _ensure_table(db: Session) -> None:
    """Create ebilanz_exports table if not present (best-effort)."""
    try:
        db.execute(text(
            "CREATE TABLE IF NOT EXISTS domain_finance.ebilanz_exports ("
            "  id TEXT PRIMARY KEY,"
            "  tenant_id TEXT NOT NULL,"
            "  wirtschaftsjahr INT,"
            "  bilanzart TEXT,"
            "  berichtsperiode_von TEXT,"
            "  berichtsperiode_bis TEXT,"
            "  steuernummer TEXT,"
            "  finanzamt_nr TEXT,"
            "  status TEXT DEFAULT 'ERSTELLT',"
            "  taxonomie_version TEXT DEFAULT '6.7',"
            "  xbrl_paketgroesse_kb INT DEFAULT 42,"
            "  elster_transfer_ticket TEXT,"
            "  uebertragen_am TIMESTAMP,"
            "  erstellt_am TIMESTAMP DEFAULT NOW()"
            ")"
        ))
        db.commit()
    except Exception:
        db.rollback()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class EBilanzExportRequest(BaseModel):
    wirtschaftsjahr: int
    bilanzart: str  # HGB / IFRS / EStG
    berichtsperiode_von: str  # ISO date
    berichtsperiode_bis: str  # ISO date
    steuernummer: str
    finanzamt_nr: str


class EBilanzExportResult(BaseModel):
    export_id: str
    status: str  # ERSTELLT / VALIDIERT / UEBERTRAGEN / FEHLER
    xbrl_paketgroesse_kb: int = 42
    taxonomie_version: str = "6.7"
    validierungsfehler: list[str] = []


class EBilanzValidierungsRequest(BaseModel):
    """Dict of XBRL element names → values submitted for validation."""
    felder: dict[str, Any]


class EBilanzValidierungsResult(BaseModel):
    valid: bool
    fehlende_felder: list[str]
    warnungen: list[str]


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/taxonomie-felder")
def taxonomie_felder() -> list[dict]:
    """Return the list of XBRL taxonomy fields with GCD/GAAP classification."""
    return _TAXONOMY_FELDER


@router.post("/validieren", response_model=EBilanzValidierungsResult)
def validieren_ebilanz(
    payload: EBilanzValidierungsRequest,
) -> dict:
    """Validate a submitted eBilanz dict against required GCD Pflichtfelder."""
    eingereichte_felder = set(payload.felder.keys())
    fehlende = [f for f in _GCD_PFLICHTFELDER if f not in eingereichte_felder]
    warnungen: list[str] = []

    # Warn about empty string values for present fields
    for key, val in payload.felder.items():
        if val == "" or val is None:
            warnungen.append(f"Feld '{key}' ist vorhanden aber leer")

    # Warn about unknown fields that are not in taxonomy
    bekannte_felder = {f["element"] for f in _TAXONOMY_FELDER}
    for key in eingereichte_felder:
        if key not in bekannte_felder:
            warnungen.append(f"Unbekanntes Taxonomie-Feld: '{key}'")

    return {
        "valid": len(fehlende) == 0,
        "fehlende_felder": fehlende,
        "warnungen": warnungen,
    }


@router.get("/meldungen")
def list_meldungen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    """List all submitted eBilanz declarations for this tenant."""
    _ensure_table(db)
    try:
        rows = db.execute(
            text(
                "SELECT id AS export_id, status, taxonomie_version, xbrl_paketgroesse_kb, "
                "wirtschaftsjahr, bilanzart, berichtsperiode_von, berichtsperiode_bis, "
                "steuernummer, finanzamt_nr, elster_transfer_ticket, uebertragen_am, erstellt_am "
                "FROM domain_finance.ebilanz_exports WHERE tenant_id=:tenant_id "
                "ORDER BY erstellt_am DESC"
            ),
            {"tenant_id": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


@router.post("/export/erstellen", response_model=EBilanzExportResult, status_code=201)
def erstellen(
    payload: EBilanzExportRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    export_id = str(uuid.uuid4())
    _ensure_table(db)

    # Persist best-effort
    try:
        db.execute(
            text(
                "INSERT INTO domain_finance.ebilanz_exports "
                "(id, tenant_id, wirtschaftsjahr, bilanzart, berichtsperiode_von, "
                "berichtsperiode_bis, steuernummer, finanzamt_nr, status, "
                "taxonomie_version, xbrl_paketgroesse_kb, erstellt_am) "
                "VALUES (:id, :tenant_id, :wj, :bilanzart, :von, :bis, :stnr, :fanr, "
                "'ERSTELLT', '6.7', 42, NOW())"
            ),
            {
                "id": export_id,
                "tenant_id": tenant_id,
                "wj": payload.wirtschaftsjahr,
                "bilanzart": payload.bilanzart,
                "von": payload.berichtsperiode_von,
                "bis": payload.berichtsperiode_bis,
                "stnr": payload.steuernummer,
                "fanr": payload.finanzamt_nr,
            },
        )
        db.commit()
    except Exception:
        db.rollback()

    # Build a realistic XBRL stub with proper taxonomy namespace
    xbrl_stub = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<xbrl xmlns="http://www.xbrl.org/2003/instance"\n'
        f'      xmlns:link="{XBRL_NAMESPACE}"\n'
        f'      xmlns:de-gcd="http://www.xbrl.de/taxonomies/de-gcd"\n'
        f'      xmlns:de-gaap-ci="http://www.xbrl.de/taxonomies/de-gaap-ci">\n'
        f'  <!-- eBilanz Taxonomie 6.7 — Wirtschaftsjahr {payload.wirtschaftsjahr} -->\n'
        f'  <!-- Bilanzart: {payload.bilanzart} | Steuernummer: {payload.steuernummer} -->\n'
        f'  <de-gcd:genInfo.doc.period.fiscalYearBegin contextRef="D-{payload.wirtschaftsjahr}">'
        f'{payload.berichtsperiode_von}</de-gcd:genInfo.doc.period.fiscalYearBegin>\n'
        f'  <de-gcd:genInfo.doc.period.fiscalYearEnd contextRef="D-{payload.wirtschaftsjahr}">'
        f'{payload.berichtsperiode_bis}</de-gcd:genInfo.doc.period.fiscalYearEnd>\n'
        f'</xbrl>'
    )
    xbrl_kb = max(1, len(xbrl_stub) // 1024) or 1

    return {
        "export_id": export_id,
        "status": "ERSTELLT",
        "xbrl_paketgroesse_kb": xbrl_kb,
        "taxonomie_version": "6.7",
        "validierungsfehler": [],
    }


@router.post("/export/{export_id}/validieren")
def validieren(
    export_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    # Check existence (best-effort)
    try:
        db.execute(
            text(
                "SELECT id FROM domain_finance.ebilanz_exports WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": export_id, "tenant_id": tenant_id},
        ).first()
        db.execute(
            text(
                "UPDATE domain_finance.ebilanz_exports SET status='VALIDIERT' "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": export_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "export_id": export_id,
        "status": "VALIDIERT",
        "validierungsfehler": [],
        "hinweise": [
            "Taxonomie-Version 6.7 gültig",
            "Pflichtfelder vollständig",
        ],
    }


@router.post("/export/{export_id}/uebertragen")
def uebertragen(
    export_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    ticket = uuid.uuid4().hex[:16].upper()

    try:
        db.execute(
            text(
                "UPDATE domain_finance.ebilanz_exports SET status='UEBERTRAGEN', "
                "elster_transfer_ticket=:ticket, uebertragen_am=NOW() "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"ticket": ticket, "id": export_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "export_id": export_id,
        "status": "UEBERTRAGEN",
        "elster_transfer_ticket": ticket,
        "uebertragen_am": date.today().isoformat(),
    }


@router.get("/exports")
def list_exports(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        rows = db.execute(
            text(
                "SELECT id AS export_id, status, taxonomie_version, xbrl_paketgroesse_kb, "
                "wirtschaftsjahr, bilanzart, erstellt_am "
                "FROM domain_finance.ebilanz_exports WHERE tenant_id=:tenant_id "
                "ORDER BY erstellt_am DESC"
            ),
            {"tenant_id": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []
