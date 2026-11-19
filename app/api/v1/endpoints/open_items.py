"""
Offene Posten (FIBU-AR-05): Lesen, Ausgleichshistorie und Mahnen.

Quelle ist domain_erp.offene_posten, das Nebenbuch der Belegbuchung. Ausgeglichen wird ueber den Bankabgleich.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import datetime, date
import logging
from app.services.open_item_read_source import _get_open_items_relation, _expr, read_settlements
from app.auth.finance_roles import finance_write, open_items_read
from app.core.business_time import business_today

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from app.core.akteur import gepruefter_akteur_aus_request
from pydantic import BaseModel, computed_field

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import TypedObjectOut
from app.api.v1.schemas.open_items_schemas import OpenItemsOut


router = APIRouter(prefix="/open-items", tags=["finance", "open-items"])


class OpenItemBase(BaseModel):
    konto_nr: Optional[str] = None
    konto_name: Optional[str] = None
    konto_typ: str = "debitoren"  # debitoren|kreditoren
    op_status: str = "offen"  # offen|teilweise|geschlossen|storniert
    rechnungsnr: str
    rechnungsdatum: date
    faelligkeit: date
    valuta: Optional[date] = None
    op_betrag: Decimal
    saldo: Decimal = Decimal("0.00")
    offen: Decimal
    op_text: Optional[str] = None
    waehrung: str = "EUR"
    kunde_id: Optional[str] = None
    kunde_name: Optional[str] = None
    lieferant_id: Optional[str] = None
    lieferant_name: Optional[str] = None
    skonto_prozent: Optional[Decimal] = None
    skonto_bis: Optional[date] = None
    mahn_stufe: int = 0
    zahlbar: bool = True
    letzte_bewegung_am: Optional[date] = None
    kredit_limit: Optional[Decimal] = None
    kv_limit: Optional[Decimal] = None
    sperre_grund: Optional[str] = None


class OpenItem(OpenItemBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def ueberfaellig(self) -> bool:
        return self.offen > 0 and self.faelligkeit < business_today()


class OpenItemListResponse(BaseModel):
    items: List[OpenItem]
    summary: dict
    total: int


def _val(row: dict, key: str, default=None):
    return row.get(key, default)


def _normalize_open_item(row: dict) -> OpenItem:
    op_amount = Decimal(str(_val(row, "op_betrag") if _val(row, "op_betrag") is not None else _val(row, "betrag", 0)))
    return OpenItem(
        id=str(_val(row, "id")),
        tenant_id=str(_val(row, "tenant_id")),
        konto_nr=_val(row, "konto_nr"),
        konto_name=_val(row, "konto_name"),
        konto_typ=_val(row, "konto_typ", "debitoren") or "debitoren",
        op_status=_val(row, "op_status", "offen") or "offen",
        rechnungsnr=_val(row, "rechnungsnr"),
        rechnungsdatum=_val(row, "rechnungsdatum") or _val(row, "datum"),
        faelligkeit=_val(row, "faelligkeit"),
        valuta=_val(row, "valuta"),
        op_betrag=op_amount,
        saldo=Decimal(str(_val(row, "saldo", 0) if _val(row, "saldo") is not None else 0)),
        offen=Decimal(str(_val(row, "offen", 0))),
        op_text=_val(row, "op_text"),
        waehrung=_val(row, "waehrung", "EUR") or "EUR",
        kunde_id=_val(row, "kunde_id"),
        kunde_name=_val(row, "kunde_name"),
        lieferant_id=_val(row, "lieferant_id"),
        lieferant_name=_val(row, "lieferant_name"),
        skonto_prozent=Decimal(str(_val(row, "skonto_prozent"))) if _val(row, "skonto_prozent") is not None else None,
        skonto_bis=_val(row, "skonto_bis"),
        mahn_stufe=int(_val(row, "mahn_stufe", 0) or 0),
        zahlbar=bool(_val(row, "zahlbar", True)),
        letzte_bewegung_am=_val(row, "letzte_bewegung_am"),
        kredit_limit=Decimal(str(_val(row, "kredit_limit"))) if _val(row, "kredit_limit") is not None else None,
        kv_limit=Decimal(str(_val(row, "kv_limit"))) if _val(row, "kv_limit") is not None else None,
        sperre_grund=_val(row, "sperre_grund"),
        created_at=_val(row, "created_at"),
        updated_at=_val(row, "updated_at"),
    )


@router.get("", response_model=OpenItemListResponse, summary="Open items auflisten",
            dependencies=[Depends(open_items_read)])
async def list_open_items(
    tenant_id: str = Depends(get_tenant_id),
    konto_typ: Optional[str] = Query(None),
    op_status: Optional[str] = Query(None),
    konto_nr: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0, le=1_000_000),
    only_open: bool = Query(False),
):
    table_ref, cols = _get_open_items_relation(db)
    where_clauses = ["tenant_id = :tenant_id"]
    params = {"tenant_id": tenant_id, "limit": limit}
    if konto_typ and "konto_typ" in cols:
        where_clauses.append("konto_typ = :konto_typ")
        params["konto_typ"] = konto_typ
    if op_status and "op_status" in cols:
        where_clauses.append("op_status = :op_status")
        params["op_status"] = op_status
    if konto_nr and "konto_nr" in cols:
        where_clauses.append("konto_nr = :konto_nr")
        params["konto_nr"] = konto_nr
    if search:
        # Nur Spalten, die das Nebenbuch hat: konto_name fuehrt domain_erp nicht (sonst bricht jede Suche).
        felder = [feld for feld in ("rechnungsnr", "kunde_name", "lieferant_name", "konto_name") if feld in cols]
        where_clauses.append("(" + " OR ".join(f"COALESCE({feld},'') ILIKE :search" for feld in felder) + ")")
        params["search"] = f"%{search}%"
    if only_open:
        where_clauses.append(f"{_expr(cols, 'offen', 'open_amount', default_sql='0')} > 0")
        if "op_status" in cols:
            where_clauses.append("op_status IN (:only_open_status, :partially_open_status)")
            params["only_open_status"] = "offen"
            params["partially_open_status"] = "teilweise"

    where_sql = " AND ".join(where_clauses)
    total = db.execute(
        text(f"SELECT COUNT(*) FROM {table_ref} WHERE {where_sql}"),  # nosec B608  # reviewed-safe: relation is allowlisted and where clauses are code-controlled; values are bound
        {key: value for key, value in params.items() if key != "limit"},
    ).scalar_one()

    select_sql = f"""
            SELECT
                id,
                tenant_id,
                {_expr(cols, "konto_nr")} AS konto_nr,
                {_expr(cols, "konto_name")} AS konto_name,
                {_expr(cols, "konto_typ")} AS konto_typ,
                {_expr(cols, "op_status")} AS op_status,
                {_expr(cols, "rechnungsnr")} AS rechnungsnr,
                {_expr(cols, "rechnungsdatum", "datum")} AS rechnungsdatum,
                {_expr(cols, "datum", "rechnungsdatum")} AS datum,
                {_expr(cols, "faelligkeit", "due_date")} AS faelligkeit,
                {_expr(cols, "valuta")} AS valuta,
                {_expr(cols, "op_betrag", "betrag")} AS op_betrag,
                {_expr(cols, "betrag", "op_betrag")} AS betrag,
                {_expr(cols, "saldo", default_sql="0")} AS saldo,
                {_expr(cols, "offen", "open_amount", default_sql="0")} AS offen,
                {_expr(cols, "op_text")} AS op_text,
                {_expr(cols, "waehrung", default_sql="'EUR'")} AS waehrung,
                {_expr(cols, "kunde_id", "debtor_id")} AS kunde_id,
                {_expr(cols, "kunde_name")} AS kunde_name,
                {_expr(cols, "lieferant_id", "creditor_id")} AS lieferant_id,
                {_expr(cols, "lieferant_name")} AS lieferant_name,
                {_expr(cols, "skonto_prozent")} AS skonto_prozent,
                {_expr(cols, "skonto_bis")} AS skonto_bis,
                {_expr(cols, "mahn_stufe", "dunning_level", default_sql="0")} AS mahn_stufe,
                {_expr(cols, "zahlbar", default_sql="TRUE")} AS zahlbar,
                {_expr(cols, "letzte_bewegung_am")} AS letzte_bewegung_am,
                {_expr(cols, "kredit_limit")} AS kredit_limit,
                {_expr(cols, "kv_limit")} AS kv_limit,
                {_expr(cols, "sperre_grund")} AS sperre_grund,
                {_expr(cols, "created_at")} AS created_at,
                {_expr(cols, "updated_at")} AS updated_at
            FROM {table_ref}
            WHERE {where_sql}
            ORDER BY {_expr(cols, "faelligkeit", "due_date")} ASC, rechnungsnr ASC, id ASC
            LIMIT :limit
            OFFSET :offset
            """  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden

    params["offset"] = offset

    rows = db.execute(
        text(
            select_sql
        ),
        params,
    ).mappings().all()
    items = [_normalize_open_item(r) for r in rows]
    business_day = business_today()
    summary = {
        "count": len(items),
        "op_summe": float(sum((item.op_betrag for item in items), Decimal("0.00"))),
        "faellig": float(sum((item.offen for item in items if item.faelligkeit <= business_day), Decimal("0.00"))),
        "nicht_faellig": float(sum((item.offen for item in items if item.faelligkeit > business_day), Decimal("0.00"))),
        "letzte_bewegung_am": max((item.letzte_bewegung_am for item in items if item.letzte_bewegung_am), default=None),
    }
    return OpenItemListResponse(items=items, summary=summary, total=total)


@router.get("/{op_id}", response_model=OpenItem, summary="Open item abrufen",
            dependencies=[Depends(open_items_read)])
async def get_open_item(op_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    table_ref, cols = _get_open_items_relation(db)
    select_sql = f"""
            SELECT
                id,
                tenant_id,
                {_expr(cols, "konto_nr")} AS konto_nr,
                {_expr(cols, "konto_name")} AS konto_name,
                {_expr(cols, "konto_typ")} AS konto_typ,
                {_expr(cols, "op_status")} AS op_status,
                {_expr(cols, "rechnungsnr")} AS rechnungsnr,
                {_expr(cols, "rechnungsdatum", "datum")} AS rechnungsdatum,
                {_expr(cols, "datum", "rechnungsdatum")} AS datum,
                {_expr(cols, "faelligkeit", "due_date")} AS faelligkeit,
                {_expr(cols, "valuta")} AS valuta,
                {_expr(cols, "op_betrag", "betrag")} AS op_betrag,
                {_expr(cols, "betrag", "op_betrag")} AS betrag,
                {_expr(cols, "saldo", default_sql="0")} AS saldo,
                {_expr(cols, "offen", "open_amount", default_sql="0")} AS offen,
                {_expr(cols, "op_text")} AS op_text,
                {_expr(cols, "waehrung", default_sql="'EUR'")} AS waehrung,
                {_expr(cols, "kunde_id", "debtor_id")} AS kunde_id,
                {_expr(cols, "kunde_name")} AS kunde_name,
                {_expr(cols, "lieferant_id", "creditor_id")} AS lieferant_id,
                {_expr(cols, "lieferant_name")} AS lieferant_name,
                {_expr(cols, "skonto_prozent")} AS skonto_prozent,
                {_expr(cols, "skonto_bis")} AS skonto_bis,
                {_expr(cols, "mahn_stufe", "dunning_level", default_sql="0")} AS mahn_stufe,
                {_expr(cols, "zahlbar", default_sql="TRUE")} AS zahlbar,
                {_expr(cols, "letzte_bewegung_am")} AS letzte_bewegung_am,
                {_expr(cols, "kredit_limit")} AS kredit_limit,
                {_expr(cols, "kv_limit")} AS kv_limit,
                {_expr(cols, "sperre_grund")} AS sperre_grund,
                {_expr(cols, "created_at")} AS created_at,
                {_expr(cols, "updated_at")} AS updated_at
            FROM {table_ref} WHERE id = :id AND tenant_id = :tenant_id
            """  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden
    row = db.execute(
        text(
            select_sql
        ),
        {"id": op_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Open item not found")
    return _normalize_open_item(row)


# Offene Posten entstehen aus der Belegbuchung (Ausgangs-/Eingangsrechnung, Gutschrift, Abrechnung) und werden ueber
# den Bankabgleich (payment_matching), die Skonto-Auszifferung und das Mahnwesen fortgeschrieben. Die frueheren
# manuellen Wege hier (Anlegen, Aendern, Loeschen, Ausgleich, Sammelausgleich, Ausgleichsstorno; entfernt 19.11.2026)
# schrieben in den verwaisten Speicher public.offene_posten und buchten den Ausgleich roh ins Journal - auf
# Kontonummern statt Konto-IDs, ohne Periodenpruefung, Debitoren und Kreditoren gleich. Kein Aufrufer.


@router.get("/{op_id}/settlements", response_model=list[OpenItemsOut], summary="Settlements abrufen",
            dependencies=[Depends(open_items_read)])
async def get_settlements(
    op_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    """
    Get all settlements for an open item (audit trail).
    """
    try:
        return read_settlements(db, op_id, tenant_id)
    except HTTPException:
        raise
    except Exception as e:
        # SPEC-P0-03: Finance darf bei DB-Fehlern nie still leere Daten liefern.
        from app.core.critical_data_path import raise_critical_data_unavailable

        raise_critical_data_unavailable(
            endpoint="open_items_settlements",
            exc=e,
            label="OP-Ausgleichshistorie",
        )


@router.post("/{entity_id}/actions/mahnen", response_model=TypedObjectOut, summary="Mahnung erstellen (SPEC-P1-04)",
            dependencies=[Depends(finance_write)])
async def action_mahnen(
    entity_id: str,
    request: Request,
    body: dict = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    # Bis 07.10.2026 meldete diese Aktion "Mahnung erstellt", ohne etwas zu erstellen.
    # Bis 28.10.2026 kam der Bearbeiter aus dem Rumpf ("operator", sonst "Maske"); jetzt aus der Anmeldung.
    akteur = gepruefter_akteur_aus_request(request)
    from app.services.finance_mahnstufe_service import eskaliere_mahnstufe
    from app.services.mask_action_runtime_service import run_delegated_mask_action

    async def nummer(db_: Session, eid: str, tid: str) -> str:
        posten = await get_open_item(eid, tenant_id=tid, db=db_)
        return str((posten if isinstance(posten, dict) else posten.model_dump()).get("rechnungsnr") or "").strip()

    async def pruefen(db_: Session, payload: dict, eid: str, tid: str) -> list[dict]:
        try:
            ok = bool(await nummer(db_, eid, tid))
            grund = "Der Posten hat keine Rechnungsnummer; ohne sie keine Mahnstufe."
        except HTTPException:
            ok, grund = False, "Offener Posten nicht gefunden."
        return [] if ok else [{"field": "_entity", "message": grund, "severity": "blocking"}]

    async def mahnen(db_: Session, payload: dict, eid: str, tid: str) -> str:
        stufe = eskaliere_mahnstufe(db_, await nummer(db_, eid, tid), tid, akteur)
        return f"Mahnstufe {stufe.get('stufe')} gesetzt."

    result = await run_delegated_mask_action(
        db, action_key="mahnen", entity_type="ar_open_item", entity_id=entity_id, tenant_id=tenant_id,
        body=body, check_fn=pruefen, delegate_fn=mahnen, outbox_event_type="finance.ar_open_item.dunning_created",
    )
    return result.model_dump()

