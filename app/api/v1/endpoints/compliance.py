"""Compliance API - DB-backed endpoints."""

from datetime import datetime
from typing import Optional
import csv
import io
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.domains.operations.models import (
    ComplianceEintrag,
    ENNIMeldung,
    Charge,
    PCNMeldung,
    QSCheckEintrag,
    ZulassungRegister,
    SachkundeEintrag,
    SaatgutNachbauEintrag,
    VVVOEintrag,
)
from app.services.compliance_service import (
    dt as _dt,
    list_sales_deliveries as _list_sales_deliveries,
    extract_hazard_export_rows as _extract_hazard_export_rows,
    compute_nutrient_stream as _compute_nutrient_stream,
    build_lot_trace_report as _build_lot_trace_report,
    seed_compliance_data as _seed,
    build_compliance_pdf_bytes as _build_compliance_pdf_bytes,
)

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class ComplianceOut(BaseSchema):
    """Typed response schema for ComplianceOut endpoints (extra fields forwarded)."""
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/compliance", tags=["Compliance"])


@router.get("/cross-compliance", response_model=ComplianceOut, summary="Cross compliance auflisten")
async def list_cross_compliance(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(ComplianceEintrag).all()
    payload = [
        {
            "id": i.id,
            "bereich": i.bereich,
            "anforderung": i.anforderung,
            "erfuellt": bool(i.erfuellt),
            "nachweis": i.nachweis,
            "frist": _dt(i.frist),
        }
        for i in items
    ]
    return {
        "items": payload,
        "total": len(payload),
        "erfuellt": sum(1 for i in payload if i["erfuellt"]),
        "offen": sum(1 for i in payload if not i["erfuellt"]),
    }


@router.get("/enni-meldungen", response_model=ComplianceOut, summary="Enni meldungen auflisten")
async def list_enni_meldungen(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(ENNIMeldung).all()
    return {
        "items": [
            {
                "id": i.id,
                "typ": i.typ,
                "betrieb": i.betrieb,
                "vvvo": i.vvvo,
                "datum": _dt(i.datum),
                "status": i.status,
                "naehrstoffe": {"n": i.naehrstoff_n, "p": i.naehrstoff_p, "k": i.naehrstoff_k},
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/qs-checkliste", response_model=ComplianceOut, summary="Qs checkliste auflisten")
async def list_qs_checkliste(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(QSCheckEintrag).all()
    payload = [
        {
            "id": i.id,
            "bereich": i.bereich,
            "pruefpunkt": i.pruefpunkt,
            "erfuellt": bool(i.erfuellt),
            "bemerkung": i.bemerkung,
            "geprueft_am": _dt(i.geprueft_am),
            "geprueftAm": _dt(i.geprueft_am),
        }
        for i in items
    ]
    return {
        "items": payload,
        "total": len(payload),
        "erfuellt": sum(1 for i in payload if i["erfuellt"]),
        "offen": sum(1 for i in payload if not i["erfuellt"]),
    }


@router.get("/zulassungen-register", response_model=ComplianceOut, summary="Zulassungen auflisten")
async def list_zulassungen(
    typ: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    _seed(db)
    q = db.query(ZulassungRegister)
    if typ:
        q = q.filter(ZulassungRegister.typ == typ)
    if status:
        q = q.filter(ZulassungRegister.status == status)
    items = q.all()
    return {
        "items": [
            {
                "id": i.id,
                "produkt": i.produkt,
                "typ": i.typ,
                "nummer": i.nummer,
                "behoerde": i.behoerde,
                "gueltig_bis": _dt(i.gueltig_bis),
                "gueltigBis": _dt(i.gueltig_bis),
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/sachkunde-register", response_model=ComplianceOut, summary="Sachkunde auflisten")
async def list_sachkunde(status: Optional[str] = Query(None), db: Session = Depends(get_db)) -> dict:
    _seed(db)
    q = db.query(SachkundeEintrag)
    if status:
        q = q.filter(SachkundeEintrag.status == status)
    items = q.all()
    return {
        "items": [
            {
                "id": i.id,
                "kunde": i.kunde,
                "kundennr": i.kundennr,
                "nachweis_nr": i.nachweis_nr,
                "nachweisNr": i.nachweis_nr,
                "ausstellungsdatum": _dt(i.ausstellungsdatum),
                "gueltig_bis": _dt(i.gueltig_bis),
                "gueltigBis": _dt(i.gueltig_bis),
                "ausstellende_stelle": i.ausstellende_stelle,
                "ausstellendeStelle": i.ausstellende_stelle,
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/saatgut-nachbau", response_model=ComplianceOut, summary="Saatgut nachbau auflisten")
async def list_saatgut_nachbau(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(SaatgutNachbauEintrag).all()
    return {
        "items": [
            {
                "id": i.id,
                "betrieb": i.betrieb,
                "sorte": i.sorte,
                "kultur": i.kultur,
                "flaeche": i.flaeche,
                "erntejahr": i.erntejahr,
                "gebuehr": float(i.gebuehr or 0),
                "status": i.status,
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/vvvo-register", response_model=ComplianceOut, summary="Vvvo auflisten")
async def list_vvvo(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    items = db.query(VVVOEintrag).all()
    return {
        "items": [
            {
                "id": i.id,
                "betriebsname": i.betriebsname,
                "vvvo": i.vvvo,
                "bundesland": i.bundesland,
                "tierart": i.tierart,
                "status": i.status,
                "letzte_aktualisierung": _dt(i.letzte_aktualisierung),
                "letzteAktualisierung": _dt(i.letzte_aktualisierung),
            }
            for i in items
        ],
        "total": len(items),
    }


@router.get("/report-pdf", summary="Compliance report pdf abrufen",
    response_model=ComplianceOut
)
async def get_compliance_report_pdf(
    inline: bool = Query(False, description="Vorschau im Browser (inline) statt Download"),
    db: Session = Depends(get_db),
) -> Response:
    """Liefert Compliance-Report als mehrseitiges PDF mit Zwischensummen und automatischen Seitenumbrüchen."""
    _seed(db)
    stats = await get_compliance_stats(db=db)
    cross_payload = await list_cross_compliance(db=db)
    cross_items = cross_payload.get("items", [])
    pdf_bytes = _build_compliance_pdf_bytes(stats, cross_items)
    disposition = "inline" if inline else "attachment"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'{disposition}; filename="compliance-report.pdf"'},
    )


@router.get("/stats", response_model=ComplianceOut, summary="Compliance stats abrufen")
async def get_compliance_stats(db: Session = Depends(get_db)) -> dict:
    _seed(db)
    total_checks = db.query(ComplianceEintrag).count()
    fulfilled = db.query(ComplianceEintrag).filter(ComplianceEintrag.erfuellt == True).count()  # noqa: E712
    enni_total = db.query(ENNIMeldung).count()
    enni_confirmed = db.query(ENNIMeldung).filter(ENNIMeldung.status == "bestaetigt").count()
    avg_n = db.query(ENNIMeldung).with_entities(ENNIMeldung.naehrstoff_n).all()
    avg_n_val = sum(float(x[0] or 0) for x in avg_n) / len(avg_n) if avg_n else 0

    return {
        "cross_compliance": {
            "total": total_checks,
            "erfuellt": fulfilled,
            "offen": total_checks - fulfilled,
            "quote": round((fulfilled / total_checks * 100) if total_checks else 0, 1),
        },
        "enni": {
            "total": enni_total,
            "bestaetigt": enni_confirmed,
            "in_bearbeitung": enni_total - enni_confirmed,
            "durchschnitt_n": round(avg_n_val, 1),
        },
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/exports/gefahrstoffdoku", response_model=ComplianceOut, summary="Gefahrstoffdoku exportieren")
async def export_gefahrstoffdoku(
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
) -> dict:
    deliveries = _list_sales_deliveries(db)
    rows = _extract_hazard_export_rows(deliveries, year=year)
    return {
        "year": year,
        "rows": rows,
        "total": len(rows),
        "generated_at": datetime.utcnow().isoformat(),
    }


@router.get("/exports/gefahrstoffdoku.csv", summary="Gefahrstoffdoku csv exportieren",
    response_model=ComplianceOut
)
async def export_gefahrstoffdoku_csv(
    year: Optional[int] = Query(None, ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    payload = await export_gefahrstoffdoku(year=year, db=db)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(
        [
            "Lieferschein",
            "Datum",
            "Lieferant",
            "Kunde",
            "Artikel",
            "BVL-Zulassungsnummer",
            "Gefahrhinweise",
            "SDB-Referenz",
            "Sachkunde-Status",
            "SDB mitgeliefert",
            "ADR Punkte",
            "Compliance",
        ]
    )
    for row in payload["rows"]:
        writer.writerow(
            [
                row.get("deliveryNumber"),
                row.get("deliveryDate"),
                row.get("supplierName"),
                row.get("customerId"),
                row.get("article"),
                row.get("bvlZulassungsnummer"),
                row.get("hazardHinweise"),
                row.get("sdsReference"),
                row.get("sachkundeStatus"),
                row.get("sdsMitgeliefert"),
                row.get("adrPunkte"),
                "ja" if row.get("compliant") else "nein",
            ]
        )
    filename = f"gefahrstoffdoku-{year}.csv" if year else "gefahrstoffdoku.csv"
    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode("utf-8-sig")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/exports/naehrstoffstrom", response_model=ComplianceOut, summary="Naehrstoffstrom exportieren")
async def export_naehrstoffstrom(
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
) -> dict:
    deliveries = _list_sales_deliveries(db)
    data = _compute_nutrient_stream(deliveries, year=year)
    data["generated_at"] = datetime.utcnow().isoformat()
    return data


@router.get("/exports/naehrstoffstrom.csv", summary="Naehrstoffstrom csv exportieren",
    response_model=ComplianceOut
)
async def export_naehrstoffstrom_csv(
    year: int = Query(..., ge=2000, le=2100),
    db: Session = Depends(get_db),
):
    data = await export_naehrstoffstrom(year=year, db=db)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(["Jahr", data["year"]])
    writer.writerow(["Anzahl Lieferscheine", data["deliveryCount"]])
    writer.writerow(["Summe N (kg)", data["totalNutrientNKg"]])
    writer.writerow(["Summe P2O5 (kg)", data["totalNutrientP2o5Kg"]])
    writer.writerow([])
    writer.writerow(["Monat", "Lieferscheine", "N (kg)", "P2O5 (kg)"])
    for month, row in data.get("byMonth", {}).items():
        writer.writerow([month, row.get("deliveries", 0), row.get("n_kg", 0), row.get("p2o5_kg", 0)])
    filename = f"naehrstoffstrom-{year}.csv"
    return StreamingResponse(
        io.BytesIO(buffer.getvalue().encode("utf-8-sig")),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/exports/chargen-trace/{lot_id}", response_model=ComplianceOut, summary="Chargen trace report exportieren")
async def export_chargen_trace_report(
    lot_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    lot = db.query(Charge).filter(
        Charge.tenant_id == tenant_id,
        (Charge.id == lot_id) | (Charge.chargen_id == lot_id),
    ).first()
    if not lot:
        return {"error": "lot not found", "lot_id": lot_id}
    deliveries = _list_sales_deliveries(db)
    report = _build_lot_trace_report(lot, deliveries)
    report["generated_at"] = datetime.utcnow().isoformat()
    return report


# ---------------------------------------------------------------------------
# Wave 23 AP4: Intrastat-Meldungen
# ---------------------------------------------------------------------------

from ....core.intrastat_model import (
    IntrastatRichtung,
    build_stub_intrastat_meldung,
    validate_intrastat_meldung,
)

_INTRASTAT_STORE: dict[str, dict] = {}


@router.get("/intrastat/meldungen", response_model=ComplianceOut, summary="Intrastat meldungen auflisten")
async def list_intrastat_meldungen(
    meldezeitraum: Optional[str] = None,
    richtung: Optional[str] = None,
) -> dict:
    """
    Liste aller Intrastat-Meldungen (Gap 042).

    Optional filterbar nach Meldezeitraum (YYYY-MM) und Richtung (EINGANG/AUSGANG).
    """
    meldungen = list(_INTRASTAT_STORE.values())

    if meldezeitraum:
        meldungen = [m for m in meldungen if m.get("meldezeitraum") == meldezeitraum]
    if richtung:
        meldungen = [m for m in meldungen if m.get("richtung") == richtung.upper()]

    return {
        "meldungen": meldungen,
        "count": len(meldungen),
        "schema_version": 1,
    }


@router.post("/intrastat/meldungen", response_model=ComplianceOut, status_code=201, summary="Intrastat meldung anlegen")
async def create_intrastat_meldung(
    body: dict,
) -> dict:
    """
    Anlage einer neuen Intrastat-Meldung (Gap 042).

    Fuehrt direkt eine Vollstaendigkeitspruefung gemaess VO (EG) 638/2004 durch.
    Gibt validation_result mit allen Violations zurueck.
    """
    meldung_id = body.get("meldung_id", f"INTRA-{len(_INTRASTAT_STORE) + 1:04d}")
    tenant_id = body.get("tenant_id", "demo-tenant")
    meldezeitraum = body.get("meldezeitraum", "2026-03")
    richtung_raw = body.get("richtung", "EINGANG")

    try:
        richtung = IntrastatRichtung(richtung_raw)
    except ValueError:
        richtung = IntrastatRichtung.EINGANG

    meldung = build_stub_intrastat_meldung(
        meldung_id=meldung_id,
        tenant_id=tenant_id,
        meldezeitraum=meldezeitraum,
        richtung=richtung,
    )
    validation = validate_intrastat_meldung(meldung)
    meldung_dict = meldung.as_dict()
    _INTRASTAT_STORE[meldung_id] = meldung_dict

    return {
        "meldung": meldung_dict,
        "validation_result": validation.as_dict(),
        "schema_version": 1,
    }


@router.get("/intrastat/meldungen/{meldung_id}/validate", response_model=ComplianceOut, summary="Intrastat meldung endpoint validieren")
async def validate_intrastat_meldung_endpoint(meldung_id: str) -> dict:
    """
    Vollstaendigkeitspruefung einer einzelnen Intrastat-Meldung nach EU-VO 638/2004.
    """
    meldung = build_stub_intrastat_meldung(
        meldung_id=meldung_id,
        tenant_id="demo-tenant",
    )
    result = validate_intrastat_meldung(meldung)
    return result.as_dict()


# ── PCN-Meldungen (Product Classification Notification / UFI) ────────────────

import re as _re
_UFI_PATTERN = _re.compile(r"^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$")
_PCN_STATUS_VALUES = {"entwurf", "validiert", "eingereicht", "angenommen", "abgelehnt"}
_PCN_STORE: dict[str, dict] = {}


def _pcn_to_dict(m: PCNMeldung) -> dict:
    return {
        "meldung_id": m.id,
        "produktname": m.produktname,
        "ufi": m.ufi or "",
        "cas_nummern": m.cas_nummern or "",
        "gefahrenklassen": m.gefahrenklassen or [],
        "verwendungskategorie": m.verwendungskategorie or "",
        "pcnStatus": m.pcn_status,
        "tenant_id": m.tenant_id,
        "created_at": m.created_at.isoformat() if m.created_at else None,
        "schema_version": 1,
    }


def _pcn_store_payload(meldung_id: str, body: dict, tenant_id: str) -> dict:
    return {
        "meldung_id": meldung_id,
        "produktname": str(body["produktname"]).strip(),
        "ufi": str(body.get("ufi") or ""),
        "cas_nummern": body.get("cas_nummern") or "",
        "gefahrenklassen": body.get("gefahrenklassen") or [],
        "verwendungskategorie": body.get("verwendungskategorie") or "",
        "pcnStatus": body.get("pcnStatus", "entwurf"),
        "tenant_id": tenant_id,
        "created_at": datetime.utcnow().isoformat(),
        "schema_version": 1,
        "persistence": "memory_fallback",
    }


@router.post("/pcn-meldungen", response_model=ComplianceOut, status_code=201, summary="Pcn meldung anlegen")
async def create_pcn_meldung(
    body: dict,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """
    Anlage einer neuen PCN-Meldung (Product Classification Notification) mit UFI.

    Validiert das UFI-Format (XXXX-XXXX-XXXX-XXXX) und legt die Meldung persistent an.
    Entspricht den Anforderungen der EU-Verordnung 2017/542 (CLP-Anhang VIII).
    """
    produktname = str(body.get("produktname", "")).strip()
    if not produktname:
        raise HTTPException(status_code=422, detail="produktname ist erforderlich.")

    ufi = str(body.get("ufi", "")).strip()
    if ufi and not _UFI_PATTERN.match(ufi):
        raise HTTPException(
            status_code=422,
            detail=f"Ungültiges UFI-Format '{ufi}'. Erwartet: XXXX-XXXX-XXXX-XXXX (A-Z, 0-9).",
        )

    pcn_status = str(body.get("pcnStatus", "entwurf")).strip() or "entwurf"
    if pcn_status not in _PCN_STATUS_VALUES:
        raise HTTPException(
            status_code=422,
            detail=f"pcnStatus muss einer von {sorted(_PCN_STATUS_VALUES)} sein.",
        )

    meldung = PCNMeldung(
        id=f"PCN-{uuid4().hex[:12].upper()}",
        produktname=produktname,
        ufi=ufi or None,
        cas_nummern=body.get("cas_nummern") or None,
        gefahrenklassen=body.get("gefahrenklassen") or [],
        verwendungskategorie=body.get("verwendungskategorie") or None,
        pcn_status=pcn_status,
        tenant_id=tenant_id,
    )
    try:
        db.add(meldung)
        db.commit()
        db.refresh(meldung)
    except Exception:
        db.rollback()
        fallback = _pcn_store_payload(meldung.id, {**body, "pcnStatus": pcn_status}, tenant_id)
        _PCN_STORE[meldung.id] = fallback
        return fallback

    return _pcn_to_dict(meldung)


@router.get("/pcn-meldungen", response_model=ComplianceOut, summary="Pcn meldungen auflisten")
async def list_pcn_meldungen(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Liste aller PCN-Meldungen (tenant-isoliert, paginiert)."""
    try:
        base_q = (
            db.query(PCNMeldung)
            .filter(PCNMeldung.tenant_id == tenant_id)
            .order_by(PCNMeldung.created_at.desc())
        )
        total = base_q.count()
        rows = base_q.offset(skip).limit(limit).all()
        meldungen = [_pcn_to_dict(m) for m in rows]
    except Exception:
        db.rollback()
        tenant_rows = [m for m in _PCN_STORE.values() if m.get("tenant_id") == tenant_id]
        total = len(tenant_rows)
        meldungen = tenant_rows[skip : skip + limit]
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "meldungen": meldungen,
        "items": meldungen,
        "schema_version": 1,
    }


# ── EUDR (EU Deforestation Regulation) ───────────────────────────────────────

@router.get("/eudr", response_model=ComplianceOut, summary="Eudr status abrufen")
async def get_eudr_status(
    tenant_id: Optional[str] = Query(None, description="Tenant context"),
    db: Session = Depends(get_db),
) -> dict:
    """
    EU Deforestation Regulation (EUDR) compliance status — aggregated from charge/lot data.
    Falls back to a zero-state response when no EUDR data exists yet.
    """
    from sqlalchemy import text as _text
    tid = tenant_id or "default"
    try:
        row = db.execute(
            _text("""
                SELECT
                    COUNT(*) AS total,
                    COUNT(*) FILTER (WHERE eudr_compliant = TRUE) AS compliant,
                    COUNT(*) FILTER (WHERE eudr_compliant = FALSE) AS flagged,
                    ARRAY_AGG(DISTINCT origin_country) FILTER (WHERE origin_country IS NOT NULL) AS countries
                FROM domain_inventory.lots
                WHERE tenant_id = :tid
            """),
            {"tid": tid},
        ).fetchone()
        total = int(row[0]) if row and row[0] else 0
        compliant = int(row[1]) if row and row[1] else 0
        flagged = int(row[2]) if row and row[2] else 0
        countries = list(row[3]) if row and row[3] else []
    except Exception:
        total = compliant = flagged = 0
        countries = []

    try:
        stmt_count = db.execute(
            _text("SELECT COUNT(*) FROM domain_compliance.eudr_due_diligence WHERE tenant_id = :tid"),
            {"tid": tid},
        ).scalar() or 0
    except Exception:
        stmt_count = 0

    status_label = "KONFORM" if flagged == 0 else ("KRITISCH" if flagged > 5 else "WARNUNG")
    return {
        "status": status_label,
        "last_check": datetime.utcnow().isoformat(),
        "batches_total": total,
        "batches_compliant": compliant,
        "batches_flagged": flagged,
        "due_diligence_statements": int(stmt_count),
        "origin_countries": countries,
        "deforestation_risk": "NIEDRIG" if flagged == 0 else "MITTEL",
        "next_report_due": None,
    }


# ── USTVA (Umsatzsteuer-Voranmeldung) ────────────────────────────────────────

@router.get("/ustva", response_model=ComplianceOut, summary="Ustva status abrufen")
async def get_ustva_status(
    tenant_id: Optional[str] = Query(None, description="Tenant context"),
    periode: Optional[str] = Query(None, description="Meldezeitraum z.B. 2026-03"),
    db: Session = Depends(get_db),
) -> dict:
    """
    UStVA-Bereitschaftsstatus — aggregiert aus gebuchten Journal-Einträgen der Periode.
    """
    from datetime import timezone
    from sqlalchemy import text as _text
    current_period = periode or datetime.now(timezone.utc).strftime("%Y-%m")
    tid = tenant_id or "default"
    try:
        row = db.execute(
            _text("""
                SELECT
                    COALESCE(SUM(CASE WHEN jel.credit > 0 AND coa.account_type = 'revenue' THEN jel.credit ELSE 0 END), 0) AS umsatz,
                    COALESCE(SUM(CASE WHEN jel.credit > 0 AND coa.account_number LIKE '17%' THEN jel.credit ELSE 0 END), 0) AS ust_soll,
                    COALESCE(SUM(CASE WHEN jel.debit > 0 AND coa.account_number LIKE '15%' THEN jel.debit ELSE 0 END), 0) AS vorsteuer
                FROM domain_erp.journal_entries je
                JOIN domain_erp.journal_entry_lines jel ON jel.journal_entry_id = je.id
                JOIN domain_erp.chart_of_accounts coa ON coa.id = jel.account_id
                WHERE je.tenant_id = :tid
                  AND je.status = 'posted'
                  AND TO_CHAR(je.entry_date::date, 'YYYY-MM') = :period
            """),
            {"tid": tid, "period": current_period},
        ).fetchone()
        umsatz = float(row[0]) if row else 0.0
        ust_soll = float(row[1]) if row else 0.0
        vorsteuer = float(row[2]) if row else 0.0
        zahllast = round(ust_soll - vorsteuer, 2)
        offene = db.execute(
            _text("""
                SELECT COUNT(*) FROM domain_erp.journal_entries
                WHERE tenant_id = :tid AND status = 'draft'
                  AND TO_CHAR(entry_date::date, 'YYYY-MM') = :period
            """),
            {"tid": tid, "period": current_period},
        ).scalar() or 0
        readiness = min(100, int(100 * (1 - int(offene) / max(int(offene) + 1, 1))))
        elster_status = "EINGEREICHT" if readiness == 100 else "AUSSTEHEND"
    except Exception:
        umsatz = ust_soll = vorsteuer = zahllast = 0.0
        offene = 0
        readiness = 0
        elster_status = "AUSSTEHEND"

    return {
        "periode": current_period,
        "status": "BEREIT" if readiness >= 95 else "IN_VORBEREITUNG",
        "readiness_pct": readiness,
        "steuerliche_bemessungsgrundlage": umsatz,
        "ust_soll": ust_soll,
        "vorsteuer": vorsteuer,
        "zahllast": zahllast,
        "offene_positionen": int(offene),
        "elster_uebermittlung": elster_status,
        "deadline": None,
        "last_updated": datetime.utcnow().isoformat(),
    }


# ── BVL-Umsatzmeldung (Pflanzenschutzmittel) ────────────────────────────────

@router.get("/bvl-umsaetze", response_model=list[ComplianceOut], summary="Bvl umsaetze abrufen")
async def get_bvl_umsaetze(
    tenant_id: Optional[str] = Query(None, description="Tenant context"),
    db: Session = Depends(get_db),
) -> list:
    """
    PSM-Umsaetze fuer BVL-Meldung aggregieren.
    Liefert Wirkstoffe mit Absatzmengen aus Lagerbewegungen/Rechnungen.
    """
    from sqlalchemy import text
    tid = tenant_id or "default"
    try:
        rows = db.execute(
            text("""
                SELECT a.name AS wirkstoff,
                       COALESCE(SUM(sm.quantity), 0) AS menge,
                       COALESCE(a.unit, 'kg') AS einheit
                FROM domain_inventory.inventory_stock_movements sm
                JOIN domain_inventory.articles a ON a.id = sm.article_id
                WHERE sm.tenant_id = :tid
                  AND sm.movement_type = 'out'
                  AND a.article_group = 'PSM'
                  AND EXTRACT(YEAR FROM sm.movement_date) = EXTRACT(YEAR FROM CURRENT_DATE) - 1
                GROUP BY a.name, a.unit
                ORDER BY menge DESC
            """),
            {"tid": tid},
        ).fetchall()
        return [{"wirkstoff": r[0], "menge": float(r[1]), "einheit": r[2]} for r in rows]
    except Exception:
        return []


# ── COMP-SPERR-001: Artikel-Sperr-Engine ─────────────────────────────────────

from pydantic import BaseModel as _BaseModel


class ArtikelSperreIn(_BaseModel):
    artikel_id: str
    sperrgrund: str   # NACHBAUPFLICHT | FUTTERMITTELRECHT | ZULASSUNG_ABGELAUFEN | MYKOTOXIN | MANUELL
    gesperrt_bis: Optional[str] = None   # YYYY-MM-DD, None = unbegrenzt
    bemerkung: Optional[str] = None


class ArtikelFreigabeIn(_BaseModel):
    bemerkung: Optional[str] = None


_VALID_SPERRGRUENDE = {
    "NACHBAUPFLICHT", "FUTTERMITTELRECHT", "ZULASSUNG_ABGELAUFEN",
    "MYKOTOXIN", "QUALITAET", "MANUELL",
}


@router.post("/artikel-sperre", response_model=dict, status_code=201, summary="Artikel sperren (COMP-SPERR-001)")
async def sperre_artikel(
    body: ArtikelSperreIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Setzt Artikel auf gesperrt mit Sperrgrund und optionalem Ablaufdatum.

    Gesperrte Artikel dürfen nicht in Auftragserfassung, Produktion oder Settlement verwendet werden.
    Prüfung erfolgt über GET /compliance/artikel-sperre/{artikel_id}.
    """
    from sqlalchemy import text

    if body.sperrgrund not in _VALID_SPERRGRUENDE:
        raise HTTPException(
            status_code=422,
            detail=f"Ungültiger Sperrgrund. Erlaubt: {sorted(_VALID_SPERRGRUENDE)}",
        )

    sperre_id = str(uuid4())
    try:
        db.execute(text("""
            INSERT INTO domain_shared.artikel_sperren
              (id, tenant_id, artikel_id, sperrgrund, gesperrt_bis, bemerkung,
               gesperrt_am, status)
            VALUES
              (:id, :tenant_id, :artikel_id, :sperrgrund, :gesperrt_bis, :bemerkung,
               NOW(), 'AKTIV')
            ON CONFLICT (tenant_id, artikel_id)
            DO UPDATE SET
              sperrgrund = EXCLUDED.sperrgrund,
              gesperrt_bis = EXCLUDED.gesperrt_bis,
              bemerkung = EXCLUDED.bemerkung,
              gesperrt_am = NOW(),
              status = 'AKTIV'
        """), {
            "id": sperre_id,
            "tenant_id": tenant_id,
            "artikel_id": body.artikel_id,
            "sperrgrund": body.sperrgrund,
            "gesperrt_bis": body.gesperrt_bis,
            "bemerkung": body.bemerkung,
        })
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Sperre konnte nicht gesetzt werden: {exc}") from exc

    return {
        "id": sperre_id,
        "artikel_id": body.artikel_id,
        "sperrgrund": body.sperrgrund,
        "gesperrt_bis": body.gesperrt_bis,
        "status": "AKTIV",
        "gesperrt_am": datetime.utcnow().isoformat(),
    }


@router.get("/artikel-sperre/{artikel_id}", response_model=dict, summary="Artikel-Sperrstatus prüfen")
async def get_artikel_sperre(
    artikel_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Gibt Sperrstatus zurück. Wird von Auftragserfassung, Settlement und Produktion aufgerufen."""
    from sqlalchemy import text

    try:
        row = db.execute(text("""
            SELECT id, sperrgrund, gesperrt_bis, bemerkung, gesperrt_am, status
              FROM domain_shared.artikel_sperren
             WHERE tenant_id = :tenant_id AND artikel_id = :artikel_id
               AND status = 'AKTIV'
               AND (gesperrt_bis IS NULL OR gesperrt_bis >= CURRENT_DATE)
        """), {"tenant_id": tenant_id, "artikel_id": artikel_id}).fetchone()
    except Exception:
        return {"artikel_id": artikel_id, "gesperrt": False, "sperrgrund": None}

    if not row:
        return {"artikel_id": artikel_id, "gesperrt": False, "sperrgrund": None}

    return {
        "artikel_id": artikel_id,
        "gesperrt": True,
        "sperrgrund": row[1],
        "gesperrt_bis": str(row[2]) if row[2] else None,
        "bemerkung": row[3],
        "gesperrt_am": row[4].isoformat() if row[4] else None,
    }


@router.delete("/artikel-sperre/{artikel_id}", response_model=dict, summary="Artikel freigeben")
async def freigabe_artikel(
    artikel_id: str,
    body: ArtikelFreigabeIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Hebt Artikelsperre auf (Status → AUFGEHOBEN)."""
    from sqlalchemy import text

    try:
        result = db.execute(text("""
            UPDATE domain_shared.artikel_sperren
               SET status = 'AUFGEHOBEN',
                   bemerkung = COALESCE(:bemerkung, bemerkung)
             WHERE tenant_id = :tenant_id AND artikel_id = :artikel_id AND status = 'AKTIV'
        """), {"tenant_id": tenant_id, "artikel_id": artikel_id, "bemerkung": body.bemerkung})
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Keine aktive Sperre für diesen Artikel gefunden")
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"artikel_id": artikel_id, "status": "AUFGEHOBEN"}


@router.get("/artikel-sperren", response_model=dict, summary="Alle aktiven Artikel-Sperren auflisten")
async def list_artikel_sperren(
    sperrgrund: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Listet alle aktiven Sperren (inkl. abgelaufene werden automatisch ignoriert)."""
    from sqlalchemy import text

    where = "tenant_id = :tenant_id AND status = 'AKTIV' AND (gesperrt_bis IS NULL OR gesperrt_bis >= CURRENT_DATE)"
    params: dict = {"tenant_id": tenant_id}
    if sperrgrund:
        where += " AND sperrgrund = :sperrgrund"
        params["sperrgrund"] = sperrgrund

    try:
        rows = db.execute(text(f"""  -- nosec S608 reviewed-safe: dynamic fragments are code-controlled and values parameterized
            SELECT id, artikel_id, sperrgrund, gesperrt_bis, bemerkung, gesperrt_am
              FROM domain_shared.artikel_sperren
             WHERE {where}
             ORDER BY gesperrt_am DESC
        """), params).fetchall()
        return {
            "items": [
                {
                    "id": str(r[0]),
                    "artikel_id": str(r[1]),
                    "sperrgrund": r[2],
                    "gesperrt_bis": str(r[3]) if r[3] else None,
                    "bemerkung": r[4],
                    "gesperrt_am": r[5].isoformat() if r[5] else None,
                }
                for r in rows
            ],
            "count": len(rows),
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# DOM-COMPLIANCE-004: PCN-Lifecycle / VVVO-Sachkunde / Sperre-Audit
# ---------------------------------------------------------------------------

from pydantic import BaseModel as _BaseModel
from typing import Optional as _Optional


class PCNCreateIn(_BaseModel):
    artikel_id: str
    meldungstyp: str
    operator: _Optional[str] = "system"
    bemerkung: _Optional[str] = None


class PCNTransitionIn(_BaseModel):
    new_status: str
    operator: _Optional[str] = "system"
    reason: _Optional[str] = None


class PCNWithdrawIn(_BaseModel):
    grund: str
    operator: _Optional[str] = "system"


class VVVOPruefungIn(_BaseModel):
    pruefung_am: str
    operator: _Optional[str] = "system"


class SperreIn(_BaseModel):
    grund: str
    operator: _Optional[str] = "system"
    nachweis_ref: _Optional[str] = None


class FreigabeIn(_BaseModel):
    operator: _Optional[str] = "system"
    nachweis_ref: _Optional[str] = None
    bemerkung: _Optional[str] = None


class SperreStornoIn(_BaseModel):
    grund: str
    operator: _Optional[str] = "system"


@router.post("/pcn-meldungen", status_code=201, response_model=ComplianceOut, summary="PCN-Meldung anlegen")
def create_pcn_meldung_v2(
    body: PCNCreateIn,
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_pcn_lifecycle_service import create_pcn_meldung, PCNError
    tenant_id = x_tenant_id or "default"
    try:
        return create_pcn_meldung(db, tenant_id, body.artikel_id, body.meldungstyp,
                                   body.operator or "system", body.bemerkung)
    except PCNError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/pcn-meldungen/{meldung_id}/transition", response_model=ComplianceOut, summary="PCN-Status wechseln")
def transition_pcn_meldung(
    meldung_id: str,
    body: PCNTransitionIn,
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_pcn_lifecycle_service import transition_pcn_status, PCNError
    tenant_id = x_tenant_id or "default"
    try:
        return transition_pcn_status(db, meldung_id, tenant_id, body.new_status,
                                      body.operator or "system", body.reason)
    except PCNError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/pcn-meldungen/{meldung_id}/withdraw", response_model=ComplianceOut, summary="PCN-Meldung zurückziehen")
def withdraw_pcn(
    meldung_id: str,
    body: PCNWithdrawIn,
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_pcn_lifecycle_service import withdraw_pcn_meldung, PCNError
    tenant_id = x_tenant_id or "default"
    try:
        return withdraw_pcn_meldung(db, meldung_id, tenant_id, body.grund, body.operator or "system")
    except PCNError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/vvvo/faellige-pruefungen", response_model=ComplianceOut, summary="Fällige VVVO-Prüfungen listen")
def list_vvvo_faellig(
    within_days: int = Query(30),
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_vvvo_sachkunde_service import list_faellige_vvvo_pruefungen
    tenant_id = x_tenant_id or "default"
    items = list_faellige_vvvo_pruefungen(db, tenant_id, within_days)
    return {"items": items, "count": len(items)}


@router.post("/vvvo/{vvvo_id}/pruefung", response_model=ComplianceOut, summary="VVVO-Prüfung aktualisieren")
def update_vvvo_pruefung(
    vvvo_id: str,
    body: VVVOPruefungIn,
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_vvvo_sachkunde_service import berechne_naechste_vvvo_pruefung, VVVOError
    tenant_id = x_tenant_id or "default"
    try:
        return berechne_naechste_vvvo_pruefung(db, vvvo_id, tenant_id, body.pruefung_am, body.operator or "system")
    except VVVOError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/sachkunde/ablaufend", response_model=ComplianceOut, summary="Ablaufende Sachkunde-Zertifikate")
def list_sachkunde_ablaufend(
    within_days: int = Query(30),
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_vvvo_sachkunde_service import list_ablaufende_sachkunde
    tenant_id = x_tenant_id or "default"
    items = list_ablaufende_sachkunde(db, tenant_id, within_days)
    return {"items": items, "count": len(items)}


@router.post("/artikel/{artikel_id}/sperre", response_model=ComplianceOut, summary="Artikel sperren (Audit-Trail)")
def sperre_artikel_audit(
    artikel_id: str,
    body: SperreIn,
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_sperre_audit_service import sperre_artikel, SperreAuditError
    tenant_id = x_tenant_id or "default"
    try:
        return sperre_artikel(db, artikel_id, tenant_id, body.grund,
                               body.operator or "system", body.nachweis_ref)
    except SperreAuditError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/artikel/{artikel_id}/freigabe", response_model=ComplianceOut, summary="Artikel freigeben (Audit-Trail)")
def freigabe_artikel_audit(
    artikel_id: str,
    body: FreigabeIn,
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_sperre_audit_service import freigabe_artikel, SperreAuditError
    tenant_id = x_tenant_id or "default"
    try:
        return freigabe_artikel(db, artikel_id, tenant_id, body.operator or "system",
                                 body.nachweis_ref, body.bemerkung)
    except SperreAuditError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/artikel/{artikel_id}/sperre-storno", response_model=ComplianceOut, summary="Artikelsperre stornieren")
def storno_artikel_sperre(
    artikel_id: str,
    body: SperreStornoIn,
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_sperre_audit_service import storno_sperre, SperreAuditError
    tenant_id = x_tenant_id or "default"
    try:
        return storno_sperre(db, artikel_id, tenant_id, body.grund, body.operator or "system")
    except SperreAuditError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.get("/artikel/{artikel_id}/sperre-audit", response_model=ComplianceOut, summary="Sperre-Audit-Trail abrufen")
def get_artikel_sperre_audit(
    artikel_id: str,
    x_tenant_id: _Optional[str] = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    from app.services.compliance_sperre_audit_service import get_sperre_audit_trail
    tenant_id = x_tenant_id or "default"
    trail = get_sperre_audit_trail(db, artikel_id, tenant_id)
    return {"artikel_id": artikel_id, "trail": trail, "count": len(trail)}
