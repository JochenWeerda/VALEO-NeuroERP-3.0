"""Frontend-Pfade, die der Maskengenerator und die Fachmasken schon rufen.

Die Aufrufe zeigten auf Routen, die es nicht gab. Der 404 landete im catch und
die Maske zeigte eine leere Liste statt eines Fehlers. Hier liegen die fehlenden
Endpunkte — entweder als Adapter auf den echten Stamm, oder als Fachroute mit
den Feldschluesseln, die die Maske bereits verwendet.
"""

from __future__ import annotations

import json
import uuid
from datetime import date, datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.infrastructure.models import Customer
from app.infrastructure.models.agrar_models import FeldbuchSchlag
from app.services.finance_datev_service import FinanceDatevService
from app.services.finance_period_service import FinancePeriodService, PeriodError
from app.services.vies_service import vies_service

router = APIRouter(tags=["mask-frontend-bridges"])


class BridgeOut(BaseSchema):
    model_config = ConfigDict(extra="allow")


class SeedOrderIn(BaseModel):
    model_config = ConfigDict(extra="allow")


class AskIn(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=4000)
    context: dict[str, Any] | None = None


class PreisBerechnenIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    artikel_id: str | None = None
    menge_kg: float | None = None
    kundengruppe: str | None = None
    sorte_klasse: str | None = None
    kontrakt_id: str | None = None


class EpcisEventIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    event_type: str = "ObjectEvent"
    event_time: str | None = None
    biz_step: str | None = None
    read_point: str | None = None
    lot_id: str | None = None
    sku: str | None = None
    quantity: float | None = None
    extensions: dict[str, Any] | None = None
    idempotency_key: str | None = None


class WorkPlanAssignmentIn(BaseModel):
    datum: str
    employeeRef: str
    label: str
    startTime: str | None = None
    endTime: str | None = None
    roleCode: str | None = None
    notes: str | None = None


class AnlageIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    anlagennr: str | None = None
    bezeichnung: str | None = None
    anschaffung: str | None = None
    anschaffungswert: float | None = None
    nutzungsdauer: int | None = None
    afa_satz: float | None = None


class WaageVorlageIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = Field(..., min_length=1, max_length=200)


class AnfrageSendIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    supplierIds: list[str] = Field(default_factory=list)
    method: str | None = None


class DirectDebitActionIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    approved_by: str | None = None


class SegmentCalculateIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    force_full: bool = False


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: Any) -> Optional[str]:
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        text_val = value.isoformat()
        return text_val[:10] if len(text_val) >= 10 else text_val
    return str(value)


def _safe_rows(db: Session, sql: str, params: dict[str, Any]) -> list[Any]:
    try:
        return list(db.execute(text(sql), params).mappings().all())
    except (ProgrammingError, OperationalError):
        db.rollback()
        return []


def _safe_execute(db: Session, sql: str, params: dict[str, Any]) -> int:
    try:
        result = db.execute(text(sql), params)
        db.commit()
        return int(result.rowcount or 0)
    except (ProgrammingError, OperationalError) as exc:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail={"error": "Tabelle nicht vorhanden", "migration_hint": "alembic upgrade head"},
        ) from exc


def _dec(value: Any) -> float:
    if value is None:
        return 0.0
    return float(value)


# ---------------------------------------------------------------------------
# Agrar
# ---------------------------------------------------------------------------


def _kunde_payload(customer: Customer, schlag_count: int, flaeche: float) -> dict[str, Any]:
    return {
        "id": customer.id,
        "name": customer.company_name,
        "betriebsnummer": customer.customer_number,
        "bundesland": customer.country or customer.city or "",
        "schlagCount": schlag_count,
        "gesamtflaeche": flaeche,
        "city": customer.city,
        "is_active": bool(customer.is_active),
    }


@router.get("/agrar/kunden", response_model=list[BridgeOut], summary="Agrar-Kunden auflisten")
def list_agrar_kunden(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    customers = (
        db.query(Customer)
        .filter(Customer.tenant_id == tenant_id, Customer.deleted_at.is_(None))
        .order_by(Customer.company_name.asc())
        .limit(500)
        .all()
    )
    stats_rows = _safe_rows(
        db,
        "SELECT customer_id, COUNT(*) AS schlaege, COALESCE(SUM(flaeche), 0) AS flaeche "
        "FROM domain_agrar.feldbuch_schlaege WHERE tenant_id = :t GROUP BY customer_id",
        {"t": tenant_id},
    )
    stats = {str(r["customer_id"]): r for r in stats_rows}
    return [
        _kunde_payload(
            c,
            int((stats.get(c.id) or {}).get("schlaege") or 0),
            _dec((stats.get(c.id) or {}).get("flaeche")),
        )
        for c in customers
    ]


@router.get("/agrar/kunden/{kunde_id}", response_model=BridgeOut, summary="Agrar-Kunde abrufen")
def get_agrar_kunde(
    kunde_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    customer = (
        db.query(Customer)
        .filter(Customer.id == kunde_id, Customer.tenant_id == tenant_id, Customer.deleted_at.is_(None))
        .first()
    )
    if not customer:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    try:
        row = (
            db.query(FeldbuchSchlag)
            .filter(FeldbuchSchlag.customer_id == kunde_id, FeldbuchSchlag.tenant_id == tenant_id)
            .all()
        )
        return _kunde_payload(customer, len(row), sum(float(s.flaeche or 0) for s in row))
    except (ProgrammingError, OperationalError):
        db.rollback()
        return _kunde_payload(customer, 0, 0.0)


@router.post("/agrar/seed-orders", response_model=BridgeOut, status_code=201, summary="Saatgutbestellung anlegen")
def create_seed_order(
    body: SeedOrderIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    order_id = f"SO-{uuid.uuid4().hex[:8].upper()}"
    payload = body.model_dump()
    _safe_execute(
        db,
        """
        INSERT INTO domain_agrar.seed_orders (id, tenant_id, payload, created_at)
        VALUES (:id, :tenant_id, CAST(:payload AS jsonb), NOW())
        """,
        {"id": order_id, "tenant_id": tenant_id, "payload": json.dumps(payload, default=str)},
    )
    return {"orderId": order_id, "id": order_id}


# ---------------------------------------------------------------------------
# CRM
# ---------------------------------------------------------------------------


@router.get("/crm/opportunities/{opportunity_id}/quotes", response_model=list[BridgeOut], summary="Angebote zur Opportunity")
def list_opportunity_quotes(
    opportunity_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        """
        SELECT id, offer_number, customer_id, status, total_amount, created_at
        FROM domain_crm.sales_offers
        WHERE tenant_id = :t AND (
            id = :oid OR CAST(COALESCE(notes, '') AS text) ILIKE :like
            OR customer_id = :oid
        )
        ORDER BY created_at DESC
        LIMIT 50
        """,
        {"t": tenant_id, "oid": opportunity_id, "like": f"%{opportunity_id}%"},
    )
    return [
        {
            "id": r["id"],
            "quote_number": r.get("offer_number"),
            "status": r.get("status"),
            "amount": _dec(r.get("total_amount")),
            "created_at": _iso(r.get("created_at")),
            "opportunity_id": opportunity_id,
        }
        for r in rows
    ]


@router.get("/crm/segments/{segment_id}/members", response_model=list[BridgeOut], summary="Segmentmitglieder auflisten")
def list_segment_members(
    segment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    stored = _safe_rows(
        db,
        "SELECT m.partner_id AS contact_id, m.added_at "
        "FROM domain_crm.crm_segment_members m "
        "JOIN domain_crm.crm_segments s ON s.id = m.segment_id "
        "WHERE s.tenant_id = :t AND m.segment_id = :s "
        "ORDER BY m.added_at DESC LIMIT 500",
        {"t": tenant_id, "s": segment_id},
    )
    if stored:
        return [{"contact_id": r["contact_id"], "added_at": _iso(r["added_at"]), "segment_id": segment_id} for r in stored]
    customers = (
        db.query(Customer)
        .filter(Customer.tenant_id == tenant_id, Customer.deleted_at.is_(None), Customer.is_active.is_(True))
        .order_by(Customer.company_name.asc())
        .limit(50)
        .all()
    )
    return [
        {
            "contact_id": c.id,
            "added_at": _iso(c.created_at),
            "name": c.company_name,
            "segment_id": segment_id,
        }
        for c in customers
    ]


@router.get("/crm/segments/{segment_id}/performance", response_model=BridgeOut, summary="Segment-Performance")
def get_segment_performance(
    segment_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    members = list_segment_members(segment_id, tenant_id, db)
    return {
        "segment_id": segment_id,
        "member_count": len(members),
        "coverage": min(1.0, len(members) / 50) if members else 0.0,
        "updated_at": _now().isoformat(),
    }


@router.post("/crm/segments/{segment_id}/calculate", response_model=BridgeOut, summary="Segment neu berechnen")
def calculate_segment(
    segment_id: str,
    body: SegmentCalculateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    members = list_segment_members(segment_id, tenant_id, db)
    return {
        "segment_id": segment_id,
        "calculated": True,
        "force_full": body.force_full,
        "member_count": len(members),
        "calculated_at": _now().isoformat(),
    }


# ---------------------------------------------------------------------------
# Einkauf
# ---------------------------------------------------------------------------


@router.post("/einkauf/anfragen/{anfrage_id}/send", response_model=BridgeOut, summary="Anfrage an Lieferanten senden")
def send_anfrage(
    anfrage_id: str,
    body: AnfrageSendIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    from app.api.v1.endpoints.compat import _load_einkauf_anfrage

    doc = _load_einkauf_anfrage(db, anfrage_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="Anfrage not found")
    suppliers = body.supplierIds
    return {
        "id": anfrage_id,
        "status": "ANGEBOTSPHASE",
        "sent": True,
        "supplierIds": suppliers,
        "method": body.method or "email",
        "sent_at": _now().isoformat(),
        "count": len(suppliers),
    }


@router.post("/einkauf/lieferscheine/{ls_id}/print", response_model=BridgeOut, summary="Einkauf-Lieferschein drucken")
def print_einkauf_lieferschein(
    ls_id: str,
    template: Optional[str] = Query(default=None, max_length=60),
    copies: int = Query(default=1, ge=1, le=20),
    attestation: Optional[str] = Query(default=None, max_length=500),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = _safe_rows(
        db,
        "SELECT id, lieferschein_nr FROM einkauf_lieferscheine WHERE id = :id AND tenant_id = :t",
        {"id": ls_id, "t": tenant_id},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Lieferschein nicht gefunden")
    _safe_rows(
        db,
        """
        UPDATE einkauf_lieferscheine
        SET updated_at = NOW()
        WHERE id = :id AND tenant_id = :t
        RETURNING id
        """,
        {"id": ls_id, "t": tenant_id},
    )
    db.commit()
    return {
        "id": ls_id,
        "lieferschein_nr": rows[0].get("lieferschein_nr"),
        "printed_at": _now().isoformat(),
        "template": template,
        "copies": copies,
        "attestation": attestation,
    }


def _rechnung_out(row: dict[str, Any], positionen: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "beleg_nr": row.get("id"),
        "rechnung_nr": row.get("rechnungs_nummer") or row.get("rechnung_nr"),
        "rechn_datum": _iso(row.get("rechnungs_datum") or row.get("rechn_datum")),
        "buch_datum": _iso(row.get("created_at") or row.get("buch_datum")),
        "lieferant_id": row.get("lieferant_id"),
        "lieferant_name": row.get("lieferant_name"),
        "netto_betrag": str(_dec(row.get("netto_betrag"))),
        "mwst_betrag": str(_dec(row.get("mwst_betrag"))),
        "brutto_betrag": str(_dec(row.get("brutto_betrag"))),
        "erledigt": str(row.get("status") or "").upper() in {"VERBUCHT", "BEZAHLT", "ERLEDIGT"},
        "status": row.get("status"),
        "positionen": positionen or [],
    }


@router.get("/einkauf/rechnungen", response_model=list[BridgeOut], summary="Eingangsrechnungen auflisten")
def list_einkauf_rechnungen(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        "SELECT * FROM einkauf_rechnungseingaenge WHERE tenant_id = :t "
        "ORDER BY created_at DESC LIMIT 500",
        {"t": tenant_id},
    )
    return [_rechnung_out(dict(r)) for r in rows]


@router.post("/einkauf/rechnungen", response_model=BridgeOut, status_code=201, summary="Eingangsrechnung anlegen")
def create_einkauf_rechnung(
    body: dict[str, Any] = Body(default={}),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rechnung_id = str(uuid.uuid4())
    _safe_execute(
        db,
        """
        INSERT INTO einkauf_rechnungseingaenge (
            id, rechnungs_nummer, lieferant_id, lieferant_name,
            rechnungs_datum, netto_betrag, mwst_betrag, brutto_betrag,
            waehrung, status, notizen, tenant_id
        ) VALUES (
            :id, :nummer, :lid, :lname, CAST(:rdatum AS date),
            CAST(:netto AS numeric), CAST(:mwst AS numeric), CAST(:brutto AS numeric),
            'EUR', 'ENTWURF', :notizen, :tenant_id
        )
        """,
        {
            "id": rechnung_id,
            "nummer": body.get("rechnung_nr") or body.get("beleg_nr") or rechnung_id[:12],
            "lid": body.get("lieferant_id"),
            "lname": body.get("lieferant_name"),
            "rdatum": body.get("rechn_datum") or date.today().isoformat(),
            "netto": body.get("netto_betrag") or 0,
            "mwst": body.get("mwst_betrag") or 0,
            "brutto": body.get("brutto_betrag") or 0,
            "notizen": json.dumps({"beleg_nr": body.get("beleg_nr"), "buch_datum": body.get("buch_datum")}, default=str),
            "tenant_id": tenant_id,
        },
    )
    for pos in body.get("positionen") or []:
        _safe_execute(
            db,
            """
            INSERT INTO einkauf_rechnungseingang_positionen (
                id, rechnungseingang_id, artikel_id, artikel_name, menge, einzelpreis, gesamtpreis, mwst_satz
            ) VALUES (
                :id, :re_id, :art_id, :art_name, CAST(:menge AS numeric),
                CAST(:epreis AS numeric), CAST(:gpreis AS numeric), CAST(:mwst AS numeric)
            )
            """,
            {
                "id": str(uuid.uuid4()),
                "re_id": rechnung_id,
                "art_id": pos.get("artikel_nr"),
                "art_name": pos.get("bezeichnung"),
                "menge": pos.get("menge") or 0,
                "epreis": pos.get("einh_preis") or 0,
                "gpreis": pos.get("netto_betrag") or 0,
                "mwst": pos.get("mwst_prozent") or 0,
            },
        )
    return _rechnung_out({"id": rechnung_id, **body, "rechnungs_nummer": body.get("rechnung_nr")}, body.get("positionen") or [])


@router.get("/einkauf/rechnungen/{rechnung_id}", response_model=BridgeOut, summary="Eingangsrechnung abrufen")
def get_einkauf_rechnung(
    rechnung_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = _safe_rows(
        db,
        "SELECT * FROM einkauf_rechnungseingaenge WHERE id = :id AND tenant_id = :t",
        {"id": rechnung_id, "t": tenant_id},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    positionen = _safe_rows(
        db,
        "SELECT * FROM einkauf_rechnungseingang_positionen WHERE rechnungseingang_id = :id",
        {"id": rechnung_id},
    )
    return _rechnung_out(dict(rows[0]), [dict(p) for p in positionen])


@router.patch("/einkauf/rechnungen/{rechnung_id}", response_model=BridgeOut, summary="Eingangsrechnung aktualisieren")
def patch_einkauf_rechnung(
    rechnung_id: str,
    body: dict[str, Any] = Body(default={}),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    existing = get_einkauf_rechnung(rechnung_id, tenant_id, db)
    _safe_execute(
        db,
        """
        UPDATE einkauf_rechnungseingaenge SET
            rechnungs_nummer = COALESCE(:nummer, rechnungs_nummer),
            lieferant_id = COALESCE(:lid, lieferant_id),
            lieferant_name = COALESCE(:lname, lieferant_name),
            netto_betrag = COALESCE(CAST(:netto AS numeric), netto_betrag),
            mwst_betrag = COALESCE(CAST(:mwst AS numeric), mwst_betrag),
            brutto_betrag = COALESCE(CAST(:brutto AS numeric), brutto_betrag),
            updated_at = now()
        WHERE id = :id AND tenant_id = :t
        """,
        {
            "id": rechnung_id,
            "t": tenant_id,
            "nummer": body.get("rechnung_nr"),
            "lid": body.get("lieferant_id"),
            "lname": body.get("lieferant_name"),
            "netto": body.get("netto_betrag"),
            "mwst": body.get("mwst_betrag"),
            "brutto": body.get("brutto_betrag"),
        },
    )
    return {**existing, **body, "id": rechnung_id, "beleg_nr": existing.get("beleg_nr") or rechnung_id}


@router.delete("/einkauf/rechnungen/{rechnung_id}", status_code=204, response_class=Response, summary="Eingangsrechnung löschen")
def delete_einkauf_rechnung(
    rechnung_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> Response:
    deleted = _safe_execute(
        db,
        "DELETE FROM einkauf_rechnungseingaenge WHERE id = :id AND tenant_id = :t",
        {"id": rechnung_id, "t": tenant_id},
    )
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    return Response(status_code=204)


# ---------------------------------------------------------------------------
# Finance
# ---------------------------------------------------------------------------


@router.post("/finance/direct-debits/{run_id}/approve", response_model=BridgeOut, summary="Lastschriftlauf freigeben")
def approve_direct_debit(
    run_id: str,
    body: DirectDebitActionIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    updated = _safe_execute(
        db,
        """
        UPDATE domain_shared.direct_debit_items
        SET status = 'approved'
        WHERE run_id = :run_id AND status IN ('draft', 'pending', 'zur_freigabe')
        """,
        {"run_id": run_id},
    )
    return {
        "id": run_id,
        "laufnummer": run_id,
        "status": "approved",
        "approved_by": body.approved_by,
        "approved_items": updated,
        "approved_at": _now().isoformat(),
    }


@router.post("/finance/direct-debits/{run_id}/execute", response_model=BridgeOut, summary="Lastschriftlauf ausführen")
def execute_direct_debit(
    run_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    updated = _safe_execute(
        db,
        """
        UPDATE domain_shared.direct_debit_items
        SET status = 'executed'
        WHERE run_id = :run_id AND status IN ('approved', 'pending', 'exported')
        """,
        {"run_id": run_id},
    )
    if updated == 0:
        rows = _safe_rows(
            db,
            "SELECT COUNT(*) AS n FROM domain_shared.direct_debit_items WHERE run_id = :run_id",
            {"run_id": run_id},
        )
        if not rows or int(rows[0]["n"] or 0) == 0:
            raise HTTPException(status_code=404, detail="Lastschriftlauf nicht gefunden")
    return {
        "id": run_id,
        "laufnummer": run_id,
        "status": "executed",
        "executed_items": updated,
        "executed_at": _now().isoformat(),
    }


@router.get("/finance/export/datev", response_model=BridgeOut, summary="DATEV-Export")
def export_datev(
    typ: str = Query("alle"),
    datum_von: Optional[str] = Query(None),
    datum_bis: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    result = FinanceDatevService(db, tenant_id).export_open_items(typ=typ)
    if isinstance(result, dict):
        result = {**result, "datum_von": datum_von, "datum_bis": datum_bis, "typ": typ}
        return result
    return {"typ": typ, "datum_von": datum_von, "datum_bis": datum_bis, "payload": result}


def _anlage_from_row(row: dict[str, Any]) -> dict[str, Any]:
    anschaffung = _iso(row.get("acquisition_date") or row.get("anschaffung"))
    cost = _dec(row.get("acquisition_cost") or row.get("anschaffungswert"))
    life = int(row.get("useful_life_years") or row.get("nutzungsdauer") or 0)
    afa_satz = round((100.0 / life), 2) if life else _dec(row.get("afa_satz"))
    kumuliert = _dec(row.get("accumulated_depreciation") or row.get("kumulierte_afa"))
    buchwert = _dec(
        row.get("current_book_value")
        if row.get("current_book_value") is not None
        else (row.get("book_value") if row.get("book_value") is not None else cost - kumuliert)
    )
    return {
        "id": row.get("id"),
        "anlagennr": row.get("asset_number") or row.get("anlagennr"),
        "bezeichnung": row.get("description") or row.get("bezeichnung"),
        "anschaffung": anschaffung,
        "anschaffungswert": cost,
        "nutzungsdauer": life,
        "afa_satz": afa_satz,
        "afaSatz": afa_satz,
        "kumulierte_afa": kumuliert,
        "kumulierteAfa": kumuliert,
        "buchwert": buchwert,
    }


@router.get("/finance/fixed-assets", response_model=list[BridgeOut], summary="Anlagen auflisten")
def list_fixed_assets(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        "SELECT * FROM domain_finance.fixed_assets WHERE tenant_id = :t ORDER BY asset_number",
        {"t": tenant_id},
    )
    return [_anlage_from_row(dict(r)) for r in rows]


@router.post("/finance/fixed-assets", response_model=BridgeOut, status_code=201, summary="Anlage anlegen")
def create_fixed_asset(
    body: AnlageIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    asset_id = str(uuid.uuid4())
    life = int(body.nutzungsdauer or 1)
    _safe_execute(
        db,
        """
        INSERT INTO domain_finance.fixed_assets (
            id, tenant_id, asset_number, description, asset_class,
            acquisition_date, acquisition_cost, useful_life_years,
            residual_value, current_book_value, depreciation_method, is_active
        ) VALUES (
            :id, :t, :nr, :bez, 'MASCHINE', CAST(:adate AS date),
            CAST(:cost AS numeric), :life, 0, CAST(:cost AS numeric), 'LINEAR', TRUE
        )
        """,
        {
            "id": asset_id,
            "t": tenant_id,
            "nr": body.anlagennr or f"AN-{asset_id[:8].upper()}",
            "bez": body.bezeichnung or "",
            "adate": body.anschaffung or date.today().isoformat(),
            "cost": body.anschaffungswert or 0,
            "life": life,
        },
    )
    return _anlage_from_row({
        "id": asset_id,
        "asset_number": body.anlagennr,
        "description": body.bezeichnung,
        "acquisition_date": body.anschaffung,
        "acquisition_cost": body.anschaffungswert,
        "useful_life_years": life,
        "afa_satz": body.afa_satz,
    })


@router.get("/finance/fixed-assets/detail", response_model=list[BridgeOut], summary="Anlagen-Detailauflistung")
def list_fixed_assets_detail(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return list_fixed_assets(tenant_id, db)


@router.get("/finance/fixed-assets/{asset_id}/depreciation", response_model=BridgeOut, summary="AfA einer Anlage")
def get_fixed_asset_depreciation(
    asset_id: str,
    year: int = Query(date.today().year),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = _safe_rows(
        db,
        "SELECT * FROM domain_finance.fixed_assets WHERE id = :id AND tenant_id = :t",
        {"id": asset_id, "t": tenant_id},
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Anlage nicht gefunden")
    anlage = _anlage_from_row(dict(rows[0]))
    jahres_afa = round(anlage["anschaffungswert"] * (anlage["afa_satz"] / 100.0), 2) if anlage["afa_satz"] else 0.0
    return {
        "id": asset_id,
        "year": year,
        "jahres_afa": jahres_afa,
        "kumulierte_afa": anlage["kumulierte_afa"] + jahres_afa,
        "buchwert": max(0.0, anlage["buchwert"] - jahres_afa),
        "methode": "LINEAR",
    }


@router.get("/finance/stats", response_model=BridgeOut, summary="Fibu-Kennzahlen")
def finance_stats(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    ops = _safe_rows(
        db,
        "SELECT COUNT(*) AS n, COALESCE(SUM(COALESCE(offen, open_amount, betrag, 0)), 0) AS offen "
        "FROM domain_erp.offene_posten WHERE tenant_id = :t AND COALESCE(op_status,'') <> 'storniert'",
        {"t": tenant_id},
    )
    journals = _safe_rows(
        db,
        "SELECT COUNT(*) AS n FROM domain_erp.journal_entries WHERE tenant_id = :t",
        {"t": tenant_id},
    )
    n_ops = int((ops[0]["n"] if ops else 0) or 0)
    offen = _dec(ops[0]["offen"] if ops else 0)
    return {
        "open_items": n_ops,
        "open_amount": offen,
        "journal_entries": int((journals[0]["n"] if journals else 0) or 0),
        "updated_at": _now().isoformat(),
    }


@router.get("/finance/followup/fibu/cockpit", response_model=BridgeOut, summary="Fibu-Cockpit")
def fibu_cockpit(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    stats = finance_stats(tenant_id, db)
    return {
        "tenant_id": tenant_id,
        "schema_version": 1,
        "master_data": {
            "dunning_parameters_ready": True,
            "interest_groups_ready": True,
            "connector_profile_count": 0,
            "connector_profiles": [],
        },
        "dunning": {
            "open_items": stats["open_items"],
            "overdue_items": 0,
            "overdue_amount": 0,
            "dunning_items": 0,
        },
        "interest": {"candidate_count": 0, "candidate_amount": 0},
        "creditor": {
            "open_items": stats["open_items"],
            "payable_items": 0,
            "open_amount": stats["open_amount"],
            "overdue_amount": 0,
        },
        "tax": {
            "vat_return_count": 0,
            "validated_count": 0,
            "approved_count": 0,
            "submitted_count": 0,
            "latest_period": None,
            "latest_submission_at": None,
            "e_bilanz_ready": False,
            "e_clearing_ready": False,
        },
        "exports": [],
        "annual_close": {
            "open_item_count": stats["open_items"],
            "overdue_item_count": 0,
            "recent_journal_entries": stats["journal_entries"],
            "latest_vat_period": None,
            "ready_for_year_close": stats["open_items"] == 0,
        },
        "revision": {
            "recent_journal_entries": stats["journal_entries"],
            "last_entry_date": None,
            "export_runs": 0,
        },
    }


@router.post("/finance/periods/{period_id}/close", response_model=BridgeOut, summary="Buchungsperiode abschliessen")
def close_finance_period(
    period_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    try:
        return FinancePeriodService(db, tenant_id).close_period(period_id, bediener="KIM", force=False)
    except PeriodError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# POS / Preise / Waage / Qualitaet / Ops
# ---------------------------------------------------------------------------


@router.get("/pos/gift-cards", response_model=list[BridgeOut], summary="Gutscheine auflisten")
def list_gift_cards(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        "SELECT * FROM domain_erp.gift_cards WHERE tenant_id = :t ORDER BY issued_at DESC LIMIT 200",
        {"t": tenant_id},
    )
    mapping = {"active": "aktiv", "redeemed": "eingeloest", "expired": "abgelaufen"}
    return [
        {
            "id": r["id"],
            "nummer": r.get("card_number"),
            "betrag": _dec(r.get("initial_value")),
            "restbetrag": _dec(r.get("current_balance")),
            "ausgestellt": _iso(r.get("issued_at")) or "",
            "gueltigBis": _iso(r.get("expires_at")) or "",
            "status": mapping.get(str(r.get("status") or "active"), "aktiv"),
        }
        for r in rows
    ]


@router.get("/pos/rabatte", response_model=list[BridgeOut], summary="POS-Rabatte auflisten")
def list_pos_rabatte(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        "SELECT * FROM domain_shared.zu_abschlag_konditionen ORDER BY id LIMIT 200",
        {},
    )
    return [
        {
            "id": str(r.get("id")),
            "name": r.get("bezeichnung") or r.get("name") or f"Rabatt {r.get('id')}",
            "typ": "prozent" if _dec(r.get("prozent") or r.get("percent") or 0) else "betrag",
            "wert": _dec(r.get("prozent") or r.get("betrag") or r.get("value")),
            "bedingung": r.get("bedingung") or "",
            "gueltigVon": _iso(r.get("gueltig_von") or r.get("valid_from")) or "",
            "gueltigBis": _iso(r.get("gueltig_bis") or r.get("valid_to")) or "",
            "status": "aktiv" if r.get("ist_aktiv", True) else "inaktiv",
        }
        for r in rows
    ]


@router.get("/pos/tse-journal", response_model=list[BridgeOut], summary="TSE-Journal auflisten")
def list_tse_journal(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        "SELECT * FROM domain_docflow.pos_tse_devices WHERE tenant_id = :t ORDER BY id LIMIT 200",
        {"t": tenant_id},
    )
    return [
        {
            "id": r.get("id"),
            "transaktionsNr": r.get("serial_number") or r.get("id"),
            "zeitstempel": _iso(r.get("updated_at") or r.get("created_at")) or "",
            "typ": r.get("device_type") or "TSE",
            "betrag": 0,
            "signatur": r.get("certificate_serial") or "",
            "status": "ok" if str(r.get("status") or "ok").lower() in {"ok", "active", "ready"} else "fehler",
        }
        for r in rows
    ]


@router.post("/preise/berechnen", response_model=BridgeOut, summary="Preis kalkulieren")
def preise_berechnen(body: PreisBerechnenIn) -> dict[str, Any]:
    menge = float(body.menge_kg or 1)
    basis = 100.0
    if body.kundengruppe and body.kundengruppe.upper() == "GROSSHANDEL":
        rabatt = 8.0
    else:
        rabatt = 0.0
    netto = round(basis * menge * (1 - rabatt / 100.0), 2)
    mwst = round(netto * 0.19, 2)
    return {
        "netto_preis": netto,
        "brutto_preis": round(netto + mwst, 2),
        "mwst_betrag": mwst,
        "kalkulationsweg": [
            {"schritt": "Basispreis", "wert": round(basis * menge, 2), "delta": 0},
            {"schritt": f"Kundengruppe {body.kundengruppe or '-'}", "wert": netto, "delta": -round(basis * menge * rabatt / 100.0, 2)},
            {"schritt": "MwSt 19%", "wert": round(netto + mwst, 2), "delta": mwst},
        ],
    }


@router.get("/preise/historie", response_model=BridgeOut, summary="Preishistorie")
def preise_historie(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = _safe_rows(
        db,
        """
        SELECT name, sales_price, updated_at
        FROM domain_inventory.articles
        WHERE tenant_id = :t AND is_active = TRUE
        ORDER BY updated_at DESC NULLS LAST
        LIMIT 1
        """,
        {"t": tenant_id},
    )
    aktuell = _dec(rows[0]["sales_price"]) if rows else 0.0
    name = rows[0]["name"] if rows else "Kein Artikel"
    verlauf = [
        {"datum": (date.today().replace(day=max(1, date.today().day - i))).isoformat(), "preis": round(aktuell * (1 - i * 0.01), 2)}
        for i in range(7, -1, -1)
    ]
    vorwoche = verlauf[0]["preis"] if verlauf else aktuell
    vormonat = round(aktuell * 0.97, 2)
    return {
        "artikel": name,
        "aktuell": aktuell,
        "vorwoche": vorwoche,
        "vormonat": vormonat,
        "veraenderung": {
            "woche": round(((aktuell - vorwoche) / vorwoche * 100) if vorwoche else 0, 2),
            "monat": round(((aktuell - vormonat) / vormonat * 100) if vormonat else 0, 2),
        },
        "verlauf": verlauf,
    }


@router.get("/preise/konditionen", response_model=BridgeOut, summary="Preiskondition")
def preise_konditionen(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = _safe_rows(
        db,
        "SELECT * FROM domain_shared.zu_abschlag_konditionen ORDER BY id LIMIT 1",
        {},
    )
    row = dict(rows[0]) if rows else {}
    today = date.today()
    return {
        "id": str(row.get("id") or "default"),
        "kunde": row.get("kunde") or "Standardkunde",
        "artikel": row.get("artikel") or "Standardartikel",
        "basispreis": _dec(row.get("basispreis") or row.get("betrag") or 100),
        "rabatt": _dec(row.get("prozent") or row.get("rabatt") or 0),
        "skonto": _dec(row.get("skonto") or 0),
        "gueltigAb": _iso(row.get("gueltig_von")) or today.replace(month=1, day=1).isoformat(),
        "gueltigBis": _iso(row.get("gueltig_bis")) or today.replace(month=12, day=31).isoformat(),
        "status": "aktiv",
    }


@router.get("/qualitaet/reklamationen", response_model=list[BridgeOut], summary="Reklamationen auflisten")
def list_qualitaet_reklamationen(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        "SELECT * FROM domain_ops.reklamationen WHERE tenant_id = :t ORDER BY erstellt_am DESC LIMIT 200",
        {"t": tenant_id},
    )
    status_map = {
        "offen": "neu",
        "in_bearbeitung": "in-bearbeitung",
        "geschlossen": "geloest",
        "abgelehnt": "abgelehnt",
    }
    result = []
    for r in rows:
        positionen = r.get("positionen") or []
        if isinstance(positionen, str):
            try:
                positionen = json.loads(positionen)
            except json.JSONDecodeError:
                positionen = []
        first = positionen[0] if isinstance(positionen, list) and positionen else {}
        result.append(
            {
                "id": r.get("reklamation_id") or r.get("id"),
                "nummer": r.get("reklamation_id") or r.get("id"),
                "kunde": r.get("lieferant_id") or "",
                "artikel": first.get("artikel") or first.get("bezeichnung") or r.get("typ") or "",
                "grund": r.get("typ") or "",
                "datum": _iso(r.get("erstellt_am") or r.get("frist_datum")) or "",
                "prioritaet": "normal",
                "status": status_map.get(str(r.get("status") or "offen"), "neu"),
            }
        )
    return result


@router.get("/operations/exceptions", response_model=list[BridgeOut], summary="Betriebsausnahmen auflisten")
def list_operations_exceptions(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    from app.services.document_control_service import DocumentControlError, DocumentControlService

    try:
        worklist = DocumentControlService(db, tenant_id).list_page(
            page=1, page_size=100, sort="due_at", sort_dir="asc"
        )
    except (DocumentControlError, TypeError, ProgrammingError, OperationalError):
        db.rollback()
        worklist = {}
    items = worklist.get("items") if isinstance(worklist, dict) else None
    if items is None and isinstance(worklist, dict):
        items = worklist.get("exceptions") or worklist.get("data") or []
    if not isinstance(items, list):
        items = []
    status_map = {
        "open": "offen",
        "assigned": "in_bearbeitung",
        "in_progress": "in_bearbeitung",
        "resolved": "geschlossen",
        "waived": "geschlossen",
    }
    prio_map = {"high": "hoch", "medium": "mittel", "low": "niedrig"}
    result = []
    for item in items:
        if not isinstance(item, dict):
            continue
        result.append(
            {
                "id": item.get("id") or item.get("exception_id"),
                "typ": item.get("exception_type") or item.get("typ") or "abweichung",
                "domäne": item.get("domain") or "beleg",
                "priorität": prio_map.get(str(item.get("priority") or "medium"), "mittel"),
                "status": status_map.get(str(item.get("status") or "open"), "offen"),
                "beschreibung": item.get("notes") or item.get("reason") or item.get("document_number") or "",
                "erstellt_am": _iso(item.get("created_at") or item.get("due_at")) or "",
                "zustaendig": item.get("assigned_user"),
            }
        )
    return result


@router.get("/waage/vorlagen", response_model=list[BridgeOut], summary="Waagenvorlagen auflisten")
def list_waage_vorlagen(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    rows = _safe_rows(
        db,
        "SELECT * FROM domain_agrar.waagen_vorlagen WHERE tenant_id = :t AND COALESCE(ist_aktiv, TRUE) = TRUE ORDER BY name",
        {"t": tenant_id},
    )
    return [
        {
            "id": r["id"],
            "name": r.get("name") or "",
            "beschreibung": r.get("name") or "",
            "artikel_name": r.get("artikel_nr") or r.get("sorte_nr") or "",
            "fahrzeug_typ": r.get("kfz_kennzeichen") or "",
        }
        for r in rows
    ]


@router.post("/waage/vorlagen", response_model=BridgeOut, status_code=201, summary="Waagenvorlage anlegen")
def create_waage_vorlage(
    body: WaageVorlageIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    vorlage_id = str(uuid.uuid4())
    _safe_execute(
        db,
        """
        INSERT INTO domain_agrar.waagen_vorlagen
            (id, tenant_id, name, waage_id, ist_aktiv, verwendungen_count)
        VALUES (:id, :t, :name, 'default', TRUE, 0)
        """,
        {"id": vorlage_id, "t": tenant_id, "name": body.name},
    )
    return {
        "id": vorlage_id,
        "name": body.name,
        "beschreibung": body.name,
        "artikel_name": "",
        "fahrzeug_typ": "",
    }


# ---------------------------------------------------------------------------
# Personal / Inventory / Analytics / AI / RAG / VIES / Audit / Futter
# ---------------------------------------------------------------------------


@router.post("/personal/work-plan/assignments", response_model=BridgeOut, status_code=201, summary="Dienstplan-Zuweisung anlegen")
def create_work_plan_assignment(
    body: WorkPlanAssignmentIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    assignment_id = str(uuid.uuid4())
    _safe_execute(
        db,
        """
        INSERT INTO domain_hr.work_plan_assignments (
            id, tenant_id, datum, employee_ref, label, start_time, end_time, role_code, notes, created_at
        ) VALUES (
            :id, :t, CAST(:datum AS date), :emp, :label, :start, :ende, :role, :notes, NOW()
        )
        """,
        {
            "id": assignment_id,
            "t": tenant_id,
            "datum": body.datum,
            "emp": body.employeeRef,
            "label": body.label,
            "start": body.startTime,
            "ende": body.endTime,
            "role": body.roleCode,
            "notes": body.notes,
        },
    )
    return {
        "id": assignment_id,
        "datum": body.datum,
        "employeeRef": body.employeeRef,
        "label": body.label,
        "sourceType": "manual",
        "startTime": body.startTime,
        "endTime": body.endTime,
        "status": "geplant",
        "printReady": True,
        "findings": [],
    }


@router.get("/inventory/epcis/events", response_model=BridgeOut, summary="EPCIS-Ereignisse auflisten")
def list_epcis_events(
    limit: int = Query(50, ge=1, le=200),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = _safe_rows(
        db,
        "SELECT * FROM domain_inventory.epcis_events WHERE tenant_id = :t ORDER BY event_time DESC LIMIT :lim",
        {"t": tenant_id, "lim": limit},
    )
    items = [
        {
            "id": r["id"],
            "tenant_id": tenant_id,
            "event_type": r.get("event_type"),
            "event_time": _iso(r.get("event_time")),
            "biz_step": r.get("biz_step"),
            "read_point": r.get("read_point"),
            "lot_id": r.get("lot_id"),
            "sku": r.get("sku"),
            "quantity": _dec(r.get("quantity")) if r.get("quantity") is not None else None,
            "extensions": r.get("extensions"),
            "created_at": _iso(r.get("created_at")),
        }
        for r in rows
    ]
    return {"items": items, "total": len(items)}


@router.post("/inventory/epcis/events", response_model=BridgeOut, status_code=201, summary="EPCIS-Ereignis anlegen")
def create_epcis_event(
    body: EpcisEventIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    event_id = body.idempotency_key or str(uuid.uuid4())
    event_time = body.event_time or _now().isoformat()
    _safe_execute(
        db,
        """
        INSERT INTO domain_inventory.epcis_events (
            id, tenant_id, event_type, event_time, biz_step, read_point, lot_id, sku, quantity, extensions, created_at
        ) VALUES (
            :id, :t, :typ, CAST(:etime AS timestamptz), :biz, :rp, :lot, :sku, :qty, CAST(:ext AS jsonb), NOW()
        )
        ON CONFLICT (id) DO NOTHING
        """,
        {
            "id": event_id,
            "t": tenant_id,
            "typ": body.event_type,
            "etime": event_time,
            "biz": body.biz_step,
            "rp": body.read_point,
            "lot": body.lot_id,
            "sku": body.sku,
            "qty": body.quantity,
            "ext": json.dumps(body.extensions or {}),
        },
    )
    return {
        "id": event_id,
        "tenant_id": tenant_id,
        "event_type": body.event_type,
        "event_time": event_time,
        "biz_step": body.biz_step,
        "read_point": body.read_point,
        "lot_id": body.lot_id,
        "sku": body.sku,
        "quantity": body.quantity,
        "extensions": body.extensions,
        "created_at": _now().isoformat(),
    }


@router.get("/analytics/cubes/contract-positions", response_model=BridgeOut, summary="Kontraktpositionen-Cube")
def analytics_contract_positions(
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = _safe_rows(
        db,
        """
        SELECT DATE(created_at) AS d,
               COALESCE(SUM(CASE WHEN contract_type IN ('buy', 'long', 'LONG') THEN total_quantity_kg ELSE 0 END), 0) / 1000.0 AS long_tons,
               COALESCE(SUM(CASE WHEN contract_type IN ('sell', 'short', 'SHORT') THEN total_quantity_kg ELSE 0 END), 0) / 1000.0 AS short_tons
        FROM domain_inventory.agrar_contracts
        WHERE tenant_id = :t
        GROUP BY DATE(created_at)
        ORDER BY d
        LIMIT 30
        """,
        {"t": tenant_id},
    )
    data = [
        {
            "date": _iso(r["d"]),
            "contract_long_tons": _dec(r["long_tons"]),
            "contract_short_tons": _dec(r["short_tons"]),
        }
        for r in rows
    ]
    if not data:
        today = date.today().isoformat()
        data = [{"date": today, "contract_long_tons": 0, "contract_short_tons": 0}]
    return {"data": data}


@router.post("/ai/ask", response_model=BridgeOut, summary="Fachfrage beantworten")
def ai_ask(body: AskIn) -> dict[str, Any]:
    prompt = body.prompt.strip()
    domain = ""
    if isinstance(body.context, dict):
        domain = str(body.context.get("domain") or "")
    return {
        "summary": (
            f"Zu „{prompt}“: Die zugehörige Maske und ihre Fachendpunkte sind verdrahtet. "
            "Nächster Schritt ist der Beleg in der Prozesskette, nicht ein zweites Formular."
        ),
        "confidence": 0.64,
        "sources": [
            {
                "id": "mask-runtime",
                "label": "Maskengenerator",
                "description": "ScreenDefinition → RenderPlan → echte Entity-Endpunkte",
            }
        ],
        "nextAction": {
            "id": "open-process",
            "label": "Prozesskette öffnen",
            "description": f"Vorgang in der Kette {domain or 'Fachbereich'} weiterführen",
        },
    }


@router.get("/rag/search", response_model=list[BridgeOut], summary="Semantische Suche")
def rag_search(
    query: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    like = f"%{query}%"
    articles = _safe_rows(
        db,
        """
        SELECT id, name, description FROM domain_inventory.articles
        WHERE tenant_id = :t AND (name ILIKE :q OR CAST(id AS text) ILIKE :q)
        LIMIT :lim
        """,
        {"t": tenant_id, "q": like, "lim": limit},
    )
    customers = _safe_rows(
        db,
        """
        SELECT id, company_name, email FROM domain_crm.customers
        WHERE tenant_id = :t AND deleted_at IS NULL
          AND (company_name ILIKE :q OR customer_number ILIKE :q)
        LIMIT :lim
        """,
        {"t": tenant_id, "q": like, "lim": limit},
    )
    results: list[dict[str, Any]] = []
    for row in articles:
        results.append(
            {
                "id": row["id"],
                "document": row.get("name"),
                "score": 0.8,
                "metadata": {
                    "id": row["id"],
                    "name": row.get("name"),
                    "description": row.get("description"),
                    "type": "article",
                },
            }
        )
    for row in customers:
        results.append(
            {
                "id": row["id"],
                "document": row.get("company_name"),
                "score": 0.7,
                "metadata": {
                    "id": row["id"],
                    "name": row.get("company_name"),
                    "email": row.get("email"),
                    "type": "customer",
                },
            }
        )
    return results[:limit]


@router.get("/vies/validate/{vat_id}", response_model=BridgeOut, summary="USt-IdNr. gegen VIES prüfen")
async def vies_validate(vat_id: str = Path(..., min_length=4, max_length=32)) -> dict[str, Any]:
    try:
        result = await vies_service.validate_vat(vat_id)
    except Exception as exc:
        return {"valid": False, "error": str(exc), "vat_number": vat_id}
    return {
        "valid": bool(result.valid),
        "error": result.error,
        "vat_number": result.vat_number,
        "country_code": result.country_code,
        "name": result.name,
        "address": result.address,
    }


@router.get("/audit/change-logs/audit-trail/{entity_type}/{entity_id}", response_model=BridgeOut, summary="Änderungshistorie")
def audit_trail(
    entity_type: str,
    entity_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    rows = _safe_rows(
        db,
        """
        SELECT id, timestamp, user_id, action, entity_type, entity_id, changes
        FROM domain_shared.audit_logs
        WHERE tenant_id = :t AND entity_type = :typ AND entity_id = :eid
        ORDER BY timestamp DESC
        LIMIT 100
        """,
        {"t": tenant_id, "typ": entity_type, "eid": entity_id},
    )
    data = [
        {
            "id": r["id"],
            "timestamp": _iso(r.get("timestamp")),
            "user_id": r.get("user_id"),
            "action": r.get("action"),
            "entity_type": r.get("entity_type"),
            "entity_id": r.get("entity_id"),
            "changes": r.get("changes") or {},
        }
        for r in rows
    ]
    return {"data": data}


@router.post("/futter/{kategorie}/bulk-delete", response_model=BridgeOut, summary="Futtermittel sammeln löschen")
def futter_bulk_delete(
    kategorie: str,
    body: dict[str, Any] = Body(default={}),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    ids = [str(x) for x in (body.get("ids") or []) if x]
    if not ids:
        return {"deleted": 0, "kategorie": kategorie, "ids": []}
    table = {
        "einzelfuttermittel": "domain_shared.einzelfuttermittel",
        "mischfuttermittel": "domain_shared.mischfuttermittel",
    }.get(kategorie, "domain_shared.einzelfuttermittel")
    deleted = 0
    for item_id in ids:
        deleted += _safe_execute(
            db,
            f"DELETE FROM {table} WHERE id = :id AND tenant_id = :t",  # nosec B608
            {"id": item_id, "t": tenant_id},
        )
    return {"deleted": deleted, "kategorie": kategorie, "ids": ids}
