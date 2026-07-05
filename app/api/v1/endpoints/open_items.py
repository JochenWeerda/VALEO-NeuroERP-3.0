"""
Open Items (OP) management endpoints
RESTful API for open items settlement and matching
FIBU-AR-05: OP-Verwaltung Ausgleich/Verrechnung
"""

from typing import Optional, List
from fastapi import Response, APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from datetime import datetime, date
import json
import logging
from app.core.uuid7 import uuid7

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.config import settings
from ....core.fibu_audit import log_fibu_audit
from pydantic import BaseModel

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.open_items_schemas import OpenItemsOut


router = APIRouter(prefix="/open-items", tags=["finance", "open-items"])


def _get_user_id_from_request(request: Request | None) -> str | None:
    if request is None:
        return None
    uid = request.headers.get("X-User-ID")
    if uid:
        return uid
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        try:
            import base64 as _b64
            import json as _json
            payload = auth[7:].split(".")[1]
            payload += "=" * (4 - len(payload) % 4)
            return _json.loads(_b64.urlsafe_b64decode(payload)).get("sub")
        except Exception:  # noqa: BLE001 â€” JWT decode failed; caller handles None return
            pass
    return None


class OpenItemSettlement(BaseModel):
    """Schema for open item settlement"""
    op_id: str
    payment_amount: Decimal
    payment_date: datetime
    payment_reference: Optional[str] = None
    payment_type: str = "payment"  # payment, discount, credit_note, reversal
    notes: Optional[str] = None


class SettlementResult(BaseModel):
    """Result of settlement operation"""
    op_id: str
    settlement_id: str
    previous_open_amount: Decimal
    settlement_amount: Decimal
    new_open_amount: Decimal
    status: str  # settled, partial, overpaid
    settlement_date: datetime
    audit_trail_id: Optional[str] = None


class BatchSettleRequest(BaseModel):
    """Request for batch settlement (Sammelausgleich)"""
    items: List[OpenItemSettlement]


class BatchSettleError(BaseModel):
    """Single error in batch settlement"""
    op_id: str
    detail: str


class BatchSettleResponse(BaseModel):
    """Result of batch settlement"""
    results: List[SettlementResult]
    success_count: int
    error_count: int
    errors: List[BatchSettleError]


class OpenItemBase(BaseModel):
    konto_nr: Optional[str] = None
    konto_name: Optional[str] = None
    konto_typ: str = "debitoren"  # debitoren|kreditoren
    op_status: str = "offen"  # offen|teilweise|geschlossen|storniert
# Statusmaschine: offen â†’ (teilweise|geschlossen); geschlossen/storniert = unverÃ¤nderbar (nur Storno/Korrektur Ã¼ber reverse_settlement)
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


class OpenItemCreate(OpenItemBase):
    pass


class OpenItemUpdate(BaseModel):
    konto_nr: Optional[str] = None
    konto_name: Optional[str] = None
    konto_typ: Optional[str] = None
    op_status: Optional[str] = None
    rechnungsnr: Optional[str] = None
    rechnungsdatum: Optional[date] = None
    faelligkeit: Optional[date] = None
    valuta: Optional[date] = None
    op_betrag: Optional[Decimal] = None
    saldo: Optional[Decimal] = None
    offen: Optional[Decimal] = None
    op_text: Optional[str] = None
    waehrung: Optional[str] = None
    kunde_id: Optional[str] = None
    kunde_name: Optional[str] = None
    lieferant_id: Optional[str] = None
    lieferant_name: Optional[str] = None
    skonto_prozent: Optional[Decimal] = None
    skonto_bis: Optional[date] = None
    mahn_stufe: Optional[int] = None
    zahlbar: Optional[bool] = None
    letzte_bewegung_am: Optional[date] = None
    kredit_limit: Optional[Decimal] = None
    kv_limit: Optional[Decimal] = None
    sperre_grund: Optional[str] = None


class OpenItem(OpenItemBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime


class OpenItemListResponse(BaseModel):
    items: List[OpenItem]
    summary: dict


def _val(row: dict, key: str, default=None):
    return row.get(key, default)


def _get_open_items_relation(db: Session) -> tuple[str, set[str]]:
    rel = db.execute(
        text(
            """
            SELECT n.nspname
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE c.oid = to_regclass('offene_posten')
            """
        )
    ).scalar()
    schema = str(rel or "public")
    table_ref = f"{schema}.offene_posten"

    rows = db.execute(
        text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'offene_posten'
              AND table_schema = :table_schema
            """
        ),
        {"table_schema": schema},
    ).fetchall()
    return table_ref, {str(r[0]) for r in rows}


def _expr(cols: set[str], primary: str, fallback: str | None = None, default_sql: str = "NULL") -> str:
    if primary in cols:
        return primary
    if fallback and fallback in cols:
        return fallback
    return default_sql


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


def _validate_op(payload: OpenItemBase) -> None:
    if payload.konto_typ not in {"debitoren", "kreditoren"}:
        raise HTTPException(status_code=400, detail="konto_typ must be debitoren or kreditoren")
    if payload.op_status not in {"offen", "teilweise", "geschlossen", "storniert"}:
        raise HTTPException(status_code=400, detail="op_status invalid")
    if payload.op_betrag < 0 or payload.offen < 0:
        raise HTTPException(status_code=400, detail="Amounts must be non-negative")
    if payload.mahn_stufe < 0 or payload.mahn_stufe > 3:
        raise HTTPException(status_code=400, detail="mahn_stufe must be 0..3")


@router.get("", response_model=OpenItemListResponse, summary="Open items auflisten")
async def list_open_items(
    tenant_id: str = Depends(get_tenant_id),
    konto_typ: Optional[str] = Query(None),
    op_status: Optional[str] = Query(None),
    konto_nr: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=5000),
    db: Session = Depends(get_db),
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
        where_clauses.append("(rechnungsnr ILIKE :search OR COALESCE(kunde_name,'') ILIKE :search OR COALESCE(konto_name,'') ILIKE :search)")
        params["search"] = f"%{search}%"

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
            WHERE {' AND '.join(where_clauses)}
            ORDER BY {_expr(cols, "faelligkeit", "due_date")} ASC, rechnungsnr ASC
            LIMIT :limit
            """

    rows = db.execute(
        text(
            select_sql
        ),
        params,
    ).mappings().all()
    items = [_normalize_open_item(r) for r in rows]
    summary = {
        "count": len(items),
        "op_summe": float(sum((item.op_betrag for item in items), Decimal("0.00"))),
        "faellig": float(sum((item.offen for item in items if item.faelligkeit <= date.today()), Decimal("0.00"))),
        "nicht_faellig": float(sum((item.offen for item in items if item.faelligkeit > date.today()), Decimal("0.00"))),
        "letzte_bewegung_am": max((item.letzte_bewegung_am for item in items if item.letzte_bewegung_am), default=None),
    }
    return OpenItemListResponse(items=items, summary=summary)


@router.get("/{op_id}", response_model=OpenItem, summary="Open item abrufen")
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
            """
    row = db.execute(
        text(
            select_sql
        ),
        {"id": op_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Open item not found")
    return _normalize_open_item(row)


@router.post("", response_model=OpenItem, status_code=201, summary="Open item anlegen")
async def create_open_item(payload: OpenItemCreate, request: Request, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _validate_op(payload)
    op_id = uuid7()
    db.execute(
        text(
            """
            INSERT INTO offene_posten (
                id, tenant_id, konto_nr, konto_name, konto_typ, op_status, rechnungsnr, rechnungsdatum, datum, faelligkeit, valuta,
                op_betrag, betrag, saldo, offen, op_text, waehrung, kunde_id, kunde_name, lieferant_id, lieferant_name,
                skonto_prozent, skonto_bis, mahn_stufe, zahlbar, letzte_bewegung_am, kredit_limit, kv_limit, sperre_grund,
                created_at, updated_at
            ) VALUES (
                :id, :tenant_id, :konto_nr, :konto_name, :konto_typ, :op_status, :rechnungsnr, :rechnungsdatum, :datum, :faelligkeit, :valuta,
                :op_betrag, :betrag, :saldo, :offen, :op_text, :waehrung, :kunde_id, :kunde_name, :lieferant_id, :lieferant_name,
                :skonto_prozent, :skonto_bis, :mahn_stufe, :zahlbar, :letzte_bewegung_am, :kredit_limit, :kv_limit, :sperre_grund,
                NOW(), NOW()
            )
            """
        ),
        {
            "id": op_id,
            "tenant_id": tenant_id,
            "konto_nr": payload.konto_nr,
            "konto_name": payload.konto_name,
            "konto_typ": payload.konto_typ,
            "op_status": payload.op_status,
            "rechnungsnr": payload.rechnungsnr,
            "rechnungsdatum": payload.rechnungsdatum,
            "datum": payload.rechnungsdatum,
            "faelligkeit": payload.faelligkeit,
            "valuta": payload.valuta,
            "op_betrag": payload.op_betrag,
            "betrag": payload.op_betrag,
            "saldo": payload.saldo,
            "offen": payload.offen,
            "op_text": payload.op_text,
            "waehrung": payload.waehrung,
            "kunde_id": payload.kunde_id,
            "kunde_name": payload.kunde_name,
            "lieferant_id": payload.lieferant_id,
            "lieferant_name": payload.lieferant_name,
            "skonto_prozent": payload.skonto_prozent,
            "skonto_bis": payload.skonto_bis,
            "mahn_stufe": payload.mahn_stufe,
            "zahlbar": payload.zahlbar,
            "letzte_bewegung_am": payload.letzte_bewegung_am,
            "kredit_limit": payload.kredit_limit,
            "kv_limit": payload.kv_limit,
            "sperre_grund": payload.sperre_grund,
        },
    )
    db.commit()
    log_fibu_audit(db, tenant_id, "create", "open_item", op_id, {"rechnungsnr": payload.rechnungsnr, "op_betrag": str(payload.op_betrag)}, request=request)
    return await get_open_item(op_id, tenant_id, db)


# Statuswerte, bei denen Update/Delete erlaubt ist (GoBD: nach Verbuchung/SchlieÃŸung nur Storno)
OP_EDITABLE_STATUSES = {"offen", "teilweise"}


@router.put("/{op_id}", response_model=OpenItem, summary="Open item aktualisieren")
async def update_open_item(op_id: str, payload: OpenItemCreate, request: Request, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    _validate_op(payload)
    row = db.execute(
        text("SELECT id, op_status FROM offene_posten WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": op_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Open item not found")
    current_status = (row[1] if len(row) > 1 else None) or "offen"
    if current_status not in OP_EDITABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"Offener Posten mit Status '{current_status}' darf nicht geÃ¤ndert werden. Nur bei Status 'offen' oder 'teilweise' sind Ã„nderungen erlaubt (GoBD).",
        )
    db.execute(
        text(
            """
            UPDATE offene_posten
            SET konto_nr=:konto_nr, konto_name=:konto_name, konto_typ=:konto_typ, op_status=:op_status,
                rechnungsnr=:rechnungsnr, rechnungsdatum=:rechnungsdatum, datum=:datum, faelligkeit=:faelligkeit, valuta=:valuta,
                op_betrag=:op_betrag, betrag=:betrag, saldo=:saldo, offen=:offen, op_text=:op_text, waehrung=:waehrung,
                kunde_id=:kunde_id, kunde_name=:kunde_name, lieferant_id=:lieferant_id, lieferant_name=:lieferant_name,
                skonto_prozent=:skonto_prozent, skonto_bis=:skonto_bis, mahn_stufe=:mahn_stufe, zahlbar=:zahlbar,
                letzte_bewegung_am=:letzte_bewegung_am, kredit_limit=:kredit_limit, kv_limit=:kv_limit, sperre_grund=:sperre_grund,
                updated_at=NOW()
            WHERE id=:id AND tenant_id=:tenant_id
            """
        ),
        {
            "id": op_id,
            "tenant_id": tenant_id,
            "konto_nr": payload.konto_nr,
            "konto_name": payload.konto_name,
            "konto_typ": payload.konto_typ,
            "op_status": payload.op_status,
            "rechnungsnr": payload.rechnungsnr,
            "rechnungsdatum": payload.rechnungsdatum,
            "datum": payload.rechnungsdatum,
            "faelligkeit": payload.faelligkeit,
            "valuta": payload.valuta,
            "op_betrag": payload.op_betrag,
            "betrag": payload.op_betrag,
            "saldo": payload.saldo,
            "offen": payload.offen,
            "op_text": payload.op_text,
            "waehrung": payload.waehrung,
            "kunde_id": payload.kunde_id,
            "kunde_name": payload.kunde_name,
            "lieferant_id": payload.lieferant_id,
            "lieferant_name": payload.lieferant_name,
            "skonto_prozent": payload.skonto_prozent,
            "skonto_bis": payload.skonto_bis,
            "mahn_stufe": payload.mahn_stufe,
            "zahlbar": payload.zahlbar,
            "letzte_bewegung_am": payload.letzte_bewegung_am,
            "kredit_limit": payload.kredit_limit,
            "kv_limit": payload.kv_limit,
            "sperre_grund": payload.sperre_grund,
        },
    )
    db.commit()
    log_fibu_audit(db, tenant_id, "update", "open_item", op_id, {"rechnungsnr": payload.rechnungsnr, "op_status": payload.op_status}, request=request)
    return await get_open_item(op_id, tenant_id, db)


@router.patch("/{op_id}", response_model=OpenItem, summary="Open item aktualisieren")
async def patch_open_item(op_id: str, payload: OpenItemUpdate, request: Request, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    existing = await get_open_item(op_id, tenant_id, db)
    merged = OpenItemCreate(**{**existing.model_dump(exclude={"id", "tenant_id", "created_at", "updated_at"}), **payload.model_dump(exclude_unset=True)})
    return await update_open_item(op_id, merged, tenant_id, db, request)


@router.delete("/{op_id}", status_code=204, response_class=Response, response_model=None, summary="Open item lÃ¶schen")
async def delete_open_item(op_id: str, request: Request, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    row = db.execute(
        text("SELECT id, op_status FROM offene_posten WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": op_id, "tenant_id": tenant_id},
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Open item not found")
    current_status = (row[1] if len(row) > 1 else None) or "offen"
    if current_status not in OP_EDITABLE_STATUSES:
        raise HTTPException(
            status_code=400,
            detail=f"LÃ¶schen nur bei Status 'offen' oder 'teilweise' erlaubt. Aktueller Status: '{current_status}' (GoBD).",
        )
    db.execute(text("DELETE FROM offene_posten WHERE id = :id AND tenant_id = :tenant_id"), {"id": op_id, "tenant_id": tenant_id})
    db.commit()
    log_fibu_audit(db, tenant_id, "delete", "open_item", op_id, {}, request=request)
    return None


@router.post("/batch-settle", response_model=BatchSettleResponse, summary="Settle open items Batch")
async def batch_settle_open_items(
    body: BatchSettleRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Sammelausgleich: Mehrere offene Posten in einem Aufruf ausgleichen.
    Jeder Eintrag wird einzeln gebucht; Fehler pro OP werden gesammelt, der Rest wird ausgefÃ¼hrt.
    """
    results: List[SettlementResult] = []
    errors: List[BatchSettleError] = []
    for item in body.items:
        try:
            r = await settle_open_item(
                item.op_id,
                OpenItemSettlement(
                    payment_amount=item.payment_amount,
                    payment_date=item.payment_date,
                    payment_reference=item.payment_reference,
                    payment_type=item.payment_type,
                    notes=item.notes,
                ),
                tenant_id=tenant_id,
                db=db,
                request=request,
            )
            results.append(r)
        except HTTPException as e:
            errors.append(BatchSettleError(op_id=item.op_id, detail=str(e.detail)))
        except Exception as e:
            errors.append(BatchSettleError(op_id=item.op_id, detail=str(e)))
    return BatchSettleResponse(
        results=results,
        success_count=len(results),
        error_count=len(errors),
        errors=errors,
    )


@router.post("/{op_id}/settle", response_model=SettlementResult, summary="Open item settle")
async def settle_open_item(
    op_id: str,
    settlement: OpenItemSettlement,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Settle an open item with a payment.
    Creates audit trail entry for GoBD compliance.
    """
    try:
        # Get current open item from offene_posten table
        op_query = text("""
            SELECT id, tenant_id, op_status, rechnungsnr, datum, faelligkeit, betrag, offen,
                   kunde_id, kunde_name, mahn_stufe, zahlbar
            FROM offene_posten
            WHERE id = :op_id AND tenant_id = :tenant_id
        """)
        
        op_row = db.execute(op_query, {"op_id": op_id, "tenant_id": tenant_id}).fetchone()
        
        if not op_row:
            raise HTTPException(status_code=404, detail="Open item not found")
        # op_row: 0=id, 1=tenant_id, 2=op_status, 3=rechnungsnr, 4=datum, 5=faelligkeit, 6=betrag, 7=offen, ...
        current_status = (op_row[2] if len(op_row) > 2 else None) or "offen"
        if current_status not in OP_EDITABLE_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Ausgleich nur bei Status 'offen' oder 'teilweise' erlaubt. Aktueller Status: '{current_status}'.",
            )
        current_open_amount = Decimal(str(op_row[7])) if op_row[7] is not None else Decimal("0.00")
        # op_row indices: 0=id, 1=tenant_id, 2=rechnungsnr, 3=datum, 4=faelligkeit, 5=betrag, 6=offen
        settlement_amount = Decimal(str(settlement.payment_amount))
        
        if settlement_amount <= 0:
            raise HTTPException(status_code=400, detail="Settlement amount must be positive")
        
        if settlement_amount > current_open_amount:
            raise HTTPException(
                status_code=400, 
                detail=f"Settlement amount ({settlement_amount}) exceeds open amount ({current_open_amount})"
            )
        
        # Calculate new open amount
        new_open_amount = current_open_amount - settlement_amount
        
        # Determine new status
        if new_open_amount <= Decimal("0.01"):
            new_status = "settled"
            new_open_amount = Decimal("0.00")
        else:
            new_status = "partial"
        
        # Create settlement record
        settlement_id = f"SET-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{op_id[:8]}"
        
        # Update open item in offene_posten table
        update_query = text("""
            UPDATE offene_posten
            SET offen = :new_open_amount,
                updated_at = NOW()
            WHERE id = :op_id
            RETURNING id
        """)
        
        db.execute(update_query, {
            "op_id": op_id,
            "new_open_amount": new_open_amount,
            "new_status": new_status,
            "payment_date": settlement.payment_date
        })
        
        # Create payment record (store in journal_entries as reference)
        # Note: In production, create a separate open_item_payments table
        # For now, we'll store payment info in the journal entry description
        
        # Create audit trail entry (GoBD compliance)
        # Store in infrastructure.audit_log if available
        audit_trail_id = f"AUDIT-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{op_id[:8]}"
        
        try:
            audit_insert = text("""
                INSERT INTO infrastructure.audit_log
                (id, user_id, action, entity_type, entity_id, changes, created_at)
                VALUES (:id, :user_id, :action, :entity_type, :entity_id, :changes::jsonb, NOW())
                RETURNING id
            """)
            
            changes = {
                "previous_open_amount": float(current_open_amount),
                "settlement_amount": float(settlement_amount),
                "new_open_amount": float(new_open_amount),
                "payment_reference": settlement.payment_reference,
                "payment_type": settlement.payment_type
            }
            
            db.execute(audit_insert, {
                "id": audit_trail_id,
                "user_id": _get_user_id_from_request(request),
                "action": "settle_open_item",
                "entity_type": "offener_posten",
                "entity_id": op_id,
                "changes": json.dumps(changes)
            })
        except Exception:
            # If audit_log table doesn't exist, continue without audit trail
            audit_trail_id = None
        
        # Create GL journal entry for the payment
        # This ensures proper accounting
        journal_entry_id = f"JE-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{op_id[:8]}"
        
        # Debit: Bank account (or cash)
        # Credit: Accounts Receivable (Debitoren)
        journal_insert = text("""
            INSERT INTO domain_erp.journal_entries
            (id, tenant_id, entry_number, entry_date, posting_date, description, 
             source, currency, status, total_debit, total_credit, created_at, updated_at)
            VALUES (:id, :tenant_id, :entry_number, :entry_date, :posting_date, :description,
                    :source, :currency, :status, :total_debit, :total_credit, NOW(), NOW())
            RETURNING id
        """)
        
        entry_number = f"OP-SETTLE-{datetime.now().strftime('%Y%m%d')}-{op_id[:8]}"
        description = f"OP-Ausgleich {op_row[3]} - {settlement.payment_reference or 'Zahlung'}"
        
        db.execute(journal_insert, {
            "id": journal_entry_id,
            "tenant_id": tenant_id,
            "entry_number": entry_number,
            "entry_date": settlement.payment_date,
            "posting_date": settlement.payment_date,
            "description": description,
            "source": "op_settlement",
            "currency": "EUR",  # Default currency
            "status": "posted",
            "total_debit": settlement_amount,
            "total_credit": settlement_amount
        })
        
        # Create journal entry lines
        # Line 1: Debit Bank/Cash
        bank_account = settings.DEFAULT_BANK_ACCOUNT_ID
        journal_line1 = text("""
            INSERT INTO domain_erp.journal_entry_lines
            (id, tenant_id, journal_entry_id, account_id, debit, credit,
             line_number, description, created_at)
            VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :debit, :credit,
                    :line_number, :description, NOW())
        """)
        
        db.execute(journal_line1, {
            "id": f"{journal_entry_id}-L1",
            "tenant_id": tenant_id,
            "journal_entry_id": journal_entry_id,
            "account_id": bank_account,
            "debit": settlement_amount,
            "credit": Decimal("0.00"),
            "line_number": 1,
            "description": f"Zahlungseingang {settlement.payment_reference or ''}"
        })
        
        # Line 2: Credit Accounts Receivable
        ar_account = "1200"  # Forderungen aus Lieferungen und Leistungen
        journal_line2 = text("""
            INSERT INTO domain_erp.journal_entry_lines
            (id, tenant_id, journal_entry_id, account_id, debit, credit,
             line_number, description, created_at)
            VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :debit, :credit,
                    :line_number, :description, NOW())
        """)
        
        db.execute(journal_line2, {
            "id": f"{journal_entry_id}-L2",
            "tenant_id": tenant_id,
            "journal_entry_id": journal_entry_id,
            "account_id": ar_account,
            "debit": Decimal("0.00"),
            "credit": settlement_amount,
            "line_number": 2,
            "description": f"OP-Ausgleich {op_row[3] or ''}"
        })
        log_fibu_audit(
            db, tenant_id, "create", "journal_entry", journal_entry_id,
            {"source": "op_settlement", "entry_number": entry_number, "op_id": op_id, "settlement_amount": float(settlement_amount)},
            request=request,
        )
        db.commit()
        log_fibu_audit(
            db, tenant_id, "settle", "open_item", op_id,
            {"settlement_id": settlement_id, "settlement_amount": float(settlement_amount), "new_open_amount": float(new_open_amount)},
            request=request,
        )
        return SettlementResult(
            op_id=op_id,
            settlement_id=settlement_id,
            previous_open_amount=current_open_amount,
            settlement_amount=settlement_amount,
            new_open_amount=new_open_amount,
            status=new_status,
            settlement_date=settlement.payment_date,
            audit_trail_id=audit_trail_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to settle open item: {str(e)}")


@router.get("/{op_id}/settlements", response_model=list[OpenItemsOut], summary="Settlements abrufen")
async def get_settlements(
    op_id: str,
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db)
):
    """
    Get all settlements for an open item (audit trail).
    """
    try:
        # Get settlements from journal entries related to this OP
        query = text("""
            SELECT id, entry_number, entry_date, description, total_debit, created_at
            FROM domain_erp.journal_entries
            WHERE description LIKE :op_pattern 
            AND source = 'op_settlement'
            AND tenant_id = :tenant_id
            ORDER BY entry_date DESC, created_at DESC
        """)
        
        op_pattern = f"%{op_id}%"
        rows = db.execute(query, {"op_id": op_id, "tenant_id": tenant_id, "op_pattern": op_pattern}).fetchall()
        
        return [
            {
                "id": str(row[0]),
                "payment_amount": float(row[4]) if row[4] else 0.0,
                "payment_date": row[2].isoformat() if row[2] else None,
                "payment_reference": row[1],  # Use entry_number as reference
                "payment_type": "payment",
                "notes": row[3],  # Use description as notes
                "created_at": row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]
    except Exception:
        # If table doesn't exist, return empty list
        return []


@router.post("/{op_id}/reverse-settlement", response_model=OpenItemsOut, summary="Settlement reverse")
async def reverse_settlement(
    op_id: str,
    settlement_id: str,
    reason: str = Query(..., min_length=10, description="Reason for reversal (min 10 chars)"),
    tenant_id: str = Query("system", description="Tenant ID"),
    db: Session = Depends(get_db),
    request: Request = None,
):
    """
    Reverse a settlement (Storno).
    Requires reason for GoBD compliance.
    """
    try:
        # Get settlement from journal entry
        settlement_query = text("""
            SELECT id, total_debit, entry_date
            FROM domain_erp.journal_entries
            WHERE id = :settlement_id AND tenant_id = :tenant_id
            AND source = 'op_settlement'
        """)
        
        settlement_row = db.execute(settlement_query, {
            "settlement_id": settlement_id,
            "tenant_id": tenant_id
        }).fetchone()
        
        if not settlement_row:
            raise HTTPException(status_code=404, detail="Settlement not found")
        
        settlement_amount = Decimal(str(settlement_row[1]))
        
        # Get current open item
        op_query = text("""
            SELECT id, offen
            FROM offene_posten
            WHERE id = :op_id AND tenant_id = :tenant_id
        """)
        
        op_row = db.execute(op_query, {"op_id": op_id, "tenant_id": tenant_id}).fetchone()
        
        if not op_row:
            raise HTTPException(status_code=404, detail="Open item not found")
        
        current_open_amount = Decimal(str(op_row[1])) if op_row[1] else Decimal("0.00")
        new_open_amount = current_open_amount + settlement_amount
        
        # Update open item
        update_query = text("""
            UPDATE offene_posten
            SET offen = :new_open_amount,
                updated_at = NOW()
            WHERE id = :op_id
        """)
        
        db.execute(update_query, {
            "op_id": op_id,
            "new_open_amount": new_open_amount
        })
        
        # Mark journal entry as reversed
        reverse_query = text("""
            UPDATE domain_erp.journal_entries
            SET status = 'cancelled',
                description = description || E'\\nSTORNIERT: ' || :reason,
                updated_at = NOW()
            WHERE id = :settlement_id
        """)
        
        db.execute(reverse_query, {
            "settlement_id": settlement_id,
            "reason": reason
        })
        
        # Create audit trail entry
        audit_trail_id = f"AUDIT-REV-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{op_id[:8]}"
        
        try:
            audit_insert = text("""
                INSERT INTO infrastructure.audit_log
                (id, user_id, action, entity_type, entity_id, changes, created_at)
                VALUES (:id, :user_id, :action, :entity_type, :entity_id, :changes::jsonb, NOW())
            """)
            
            changes = {
                "settlement_id": settlement_id,
                "reversed_amount": float(settlement_amount),
                "previous_open_amount": float(current_open_amount),
                "new_open_amount": float(new_open_amount),
                "reason": reason
            }
            
            db.execute(audit_insert, {
                "id": audit_trail_id,
                "user_id": _get_user_id_from_request(request),
                "action": "reverse_settlement",
                "entity_type": "offener_posten",
                "entity_id": op_id,
                "changes": json.dumps(changes)
            })
        except Exception:
            # If audit_log table doesn't exist, continue without audit trail
            audit_trail_id = None
        
        db.commit()
        log_fibu_audit(
            db, tenant_id, "reverse_settlement", "open_item", op_id,
            {"settlement_id": settlement_id, "reason": reason, "new_open_amount": float(new_open_amount)},
            request=request,
        )
        return {
            "success": True,
            "message": "Settlement reversed successfully",
            "settlement_id": settlement_id,
            "audit_trail_id": audit_trail_id,
            "new_open_amount": float(new_open_amount)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reverse settlement: {str(e)}")


@router.post("/{entity_id}/actions/mahnen", response_model=dict, summary="Mahnung erstellen (UIX-046)")
async def action_mahnen(
    entity_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Stub: Mahnung für offenen Posten erstellen — requiresConfirmation, execute folgt."""
    return {
        "success": True,
        "actionKey": "mahnen",
        "entityId": entity_id,
        "tenantId": tenant_id,
        "message": "Mahnung wird erstellt.",
        "proposedChanges": {"mahnstatus": "erste_mahnung", "op_id": entity_id},
    }

