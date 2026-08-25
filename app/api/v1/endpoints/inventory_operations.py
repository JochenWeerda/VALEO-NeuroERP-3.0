"""
Inventory Operations — Bestandskorrektur, Schwund, MHD-Abschreibung
Wave 1+2: Core inventory correction endpoints with automatic GL posting.
DOM-INV-004: Lot-Trace (.2), Inventur-Differenzbeleg (.3), Korrektur-Storno (.4).
"""

from datetime import date
from decimal import Decimal
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.config import settings
from ....core.database import get_db
import logging

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.inventory_operations_schemas import InventoryOperationsOut
from app.api.v1.schemas.inventory_lot_bundle_schemas import (
    InventoryLotOut,
    InventurDifferenzOut,
    LotConsumeOut,
    StornoKorrekturOut,
)


router = APIRouter()
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


# ── Reason Codes ────────────────────────────────────────────────

REASON_CODES = {
    "schwund": "Lagerschwund",
    "bruch": "Bruch / Beschädigung",
    "mhd_verfall": "MHD-Verfall / Ablauf",
    "diebstahl": "Diebstahl / Verlust",
    "messdifferenz": "Messdifferenz / Zählfehler",
    "qualitaetsmangel": "Qualitätsmangel",
    "sonstige": "Sonstige Korrektur",
}

# SKR03 default accounts
DEFAULT_ACCOUNTS = {
    "bestandskonto": "1500",       # Waren
    "gegenkonto_zugang": "3200",   # Wareneingang
    "gegenkonto_abgang": "3800",   # Wareneinsatz
    "schwund_konto": "5810",       # Lagerschwund
    "bestandsveraenderung": "5800",  # Bestandsveränderungen
}


# ── Schemas ─────────────────────────────────────────────────────

class BestandskorrekturIn(BaseModel):
    article_id: str = Field(..., description="Artikel-ID")
    warehouse_id: str = Field(..., description="Lagerort-ID")
    menge: float = Field(..., description="Korrekturbetrag (positiv=Zugang, negativ=Abgang)")
    grund: str = Field(..., description="Grund-Code: schwund, bruch, mhd_verfall, diebstahl, messdifferenz, qualitaetsmangel, sonstige")
    bemerkung: Optional[str] = Field(None, description="Freitextbemerkung")
    charge: Optional[str] = Field(None, description="Chargen-Nummer (optional)")
    buchungsdatum: Optional[date] = Field(None, description="Buchungsdatum (default: heute)")


class BestandskorrekturOut(BaseModel):
    id: str
    article_id: str
    warehouse_id: str
    menge: float
    grund: str
    grund_text: str
    bemerkung: Optional[str]
    charge: Optional[str]
    buchungsdatum: date
    movement_id: str
    journal_entry_id: Optional[str]
    status: str


class SchwundBuchungIn(BaseModel):
    article_id: str = Field(..., description="Artikel-ID")
    warehouse_id: str = Field(..., description="Lagerort-ID")
    menge: float = Field(..., gt=0, description="Schwundmenge (positiv)")
    bemerkung: Optional[str] = Field(None)
    charge: Optional[str] = Field(None)
    buchungsdatum: Optional[date] = Field(None)


class MhdAbschreibungIn(BaseModel):
    article_id: str = Field(..., description="Artikel-ID")
    warehouse_id: str = Field(..., description="Lagerort-ID")
    menge: float = Field(..., gt=0, description="Abzuschreibende Menge")
    charge: str = Field(..., description="Chargen-Nummer der abgelaufenen Ware")
    mhd: date = Field(..., description="Mindesthaltbarkeitsdatum")
    bemerkung: Optional[str] = Field(None)
    buchungsdatum: Optional[date] = Field(None)


# ── GL Posting Helper ──────────────────────────────────────────

def _ensure_account(db, tenant_id: str, account_number: str, account_name: str, account_type: str, category: str) -> str:
    """Ensure a chart_of_accounts entry exists, return its id."""
    existing = db.execute(
        text("""
            SELECT id FROM domain_erp.chart_of_accounts
            WHERE tenant_id = :tenant_id AND account_number = :account_number
            LIMIT 1
        """),
        {"tenant_id": tenant_id, "account_number": account_number},
    ).mappings().first()
    if existing:
        return str(existing["id"])
    account_id = str(uuid4())
    db.execute(
        text("""
            INSERT INTO domain_erp.chart_of_accounts
            (id, tenant_id, account_number, account_name, account_type, category, is_active, created_at, updated_at)
            VALUES (:id, :tenant_id, :account_number, :account_name, :account_type, :category, TRUE, NOW(), NOW())
        """),
        {
            "id": account_id,
            "tenant_id": tenant_id,
            "account_number": account_number,
            "account_name": account_name,
            "account_type": account_type,
            "category": category,
        },
    )
    return account_id


def _get_account_mapping(db, tenant_id: str, article_id: str):
    """Look up LagerKontenzuordnung for the article's group; fall back to SKR03 defaults."""
    try:
        row = db.execute(
            text("""
                SELECT lkz.bestandskonto, lkz.gegenkonto_zugang, lkz.gegenkonto_abgang
                FROM domain_einkauf.lager_kontenzuordnung lkz
                JOIN domain_inventory.articles a ON a.article_group = lkz.artikelgruppe
                WHERE lkz.tenant_id = :tenant_id AND a.id = :article_id AND lkz.aktiv = true
                ORDER BY lkz.niederlassung_id NULLS LAST
                LIMIT 1
            """),
            {"tenant_id": tenant_id, "article_id": article_id},
        ).mappings().first()
        if row:
            return {
                "bestandskonto": row["bestandskonto"],
                "gegenkonto_zugang": row["gegenkonto_zugang"] or DEFAULT_ACCOUNTS["gegenkonto_zugang"],
                "gegenkonto_abgang": row["gegenkonto_abgang"] or DEFAULT_ACCOUNTS["gegenkonto_abgang"],
            }
    except Exception:  # noqa: BLE001 — Kontenzuordnung nicht gefunden; Standard-Konten werden verwendet
        pass
    return DEFAULT_ACCOUNTS


def _post_inventory_journal(
    db,
    *,
    tenant_id: str,
    posting_date: date,
    document_type: str,
    document_number: str,
    description: str,
    debit_account: str,
    debit_account_name: str,
    credit_account: str,
    credit_account_name: str,
    amount: Decimal,
    reference: str,
) -> str:
    """Post a balanced journal entry for an inventory operation."""
    entry_id = str(uuid4())
    amount_rounded = amount.quantize(Decimal("0.01"))

    db.execute(
        text("""
            INSERT INTO domain_erp.journal_entries
            (id, tenant_id, entry_number, entry_date, posting_date, document_type, document_number,
             reference, description, total_debit, total_credit, status, posted_at, created_at, updated_at)
            VALUES (:id, :tenant_id, :entry_number, :entry_date, :posting_date, :document_type, :document_number,
                    :reference, :description, :total_debit, :total_credit, :status, NOW(), NOW(), NOW())
        """),
        {
            "id": entry_id,
            "tenant_id": tenant_id,
            "entry_number": document_number,
            "entry_date": posting_date,
            "posting_date": posting_date,
            "document_type": document_type,
            "document_number": document_number,
            "reference": reference,
            "description": description,
            "status": "posted",
            "total_debit": amount_rounded,
            "total_credit": amount_rounded,
        },
    )

    debit_account_id = _ensure_account(db, tenant_id, debit_account, debit_account_name, "expense", "inventory_correction")
    credit_account_id = _ensure_account(db, tenant_id, credit_account, credit_account_name, "asset", "inventory")

    # Debit line
    db.execute(
        text("""
            INSERT INTO domain_erp.journal_entry_lines
            (id, tenant_id, journal_entry_id, account_id, description, debit, credit, line_number, created_at)
            VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :description, :debit, :credit, 1, NOW())
        """),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "journal_entry_id": entry_id,
            "account_id": debit_account_id,
            "debit": amount_rounded,
            "credit": Decimal("0.00"),
            "description": description,
        },
    )

    # Credit line
    db.execute(
        text("""
            INSERT INTO domain_erp.journal_entry_lines
            (id, tenant_id, journal_entry_id, account_id, description, debit, credit, line_number, created_at)
            VALUES (:id, :tenant_id, :journal_entry_id, :account_id, :description, :debit, :credit, 2, NOW())
        """),
        {
            "id": str(uuid4()),
            "tenant_id": tenant_id,
            "journal_entry_id": entry_id,
            "account_id": credit_account_id,
            "debit": Decimal("0.00"),
            "credit": amount_rounded,
            "description": description,
        },
    )

    return entry_id


# ── Routes ──────────────────────────────────────────────────────

@router.get("/reason-codes", tags=["lager"], summary="Reason codes auflisten",
    response_model=list[InventoryOperationsOut]
)
async def list_reason_codes():
    """GET alle verfügbaren Korrektur-Gründe."""
    return [{"code": k, "label": v} for k, v in REASON_CODES.items()]


@router.post("/bestandskorrektur", response_model=BestandskorrekturOut, status_code=201, tags=["lager"], summary="Bestandskorrektur anlegen")
async def create_bestandskorrektur(
    payload: BestandskorrekturIn,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Bestandskorrektur buchen — StockMovement + automatische GL-Buchung.

    Positiver Betrag = Zugang (adjustment_in), negativer = Abgang (adjustment_out).
    """
    tid = tenant_id or DEFAULT_TENANT
    if payload.grund not in REASON_CODES:
        raise HTTPException(400, f"Unbekannter Grund-Code: {payload.grund}. Erlaubt: {list(REASON_CODES.keys())}")

    korrektur_id = str(uuid4())
    movement_id = str(uuid4())
    posting_date = payload.buchungsdatum or date.today()
    movement_type = "adjustment" if payload.menge >= 0 else "adjustment"
    ref_number = f"KORR-{korrektur_id[:8].upper()}"

    # Insert stock movement
    db.execute(
        text("""
            INSERT INTO domain_inventory.inventory_stock_movements
            (id, article_id, warehouse_id, movement_type, quantity, unit, charge,
             reference_number, movement_date, movement_time,
             notes, booking_user, auto_created, ownership_type, tenant_id,
             previous_stock, new_stock, created_at)
            VALUES (:id, :article_id, :warehouse_id, :movement_type, :quantity, 't', :charge,
                    :ref, :date, NOW()::time,
                    :notes, 'system', false, 'owned', :tenant_id,
                    0, 0, NOW())
        """),
        {
            "id": movement_id,
            "article_id": payload.article_id,
            "warehouse_id": payload.warehouse_id,
            "movement_type": movement_type,
            "quantity": payload.menge,
            "charge": payload.charge,
            "ref": ref_number,
            "date": posting_date,
            "notes": f"{REASON_CODES[payload.grund]}: {payload.bemerkung or ''}".strip(),
            "tenant_id": tid,
        },
    )

    # Update article stock
    if payload.menge != 0:
        db.execute(
            text("""
                UPDATE domain_inventory.articles
                SET current_stock = COALESCE(current_stock, 0) + :delta,
                    available_stock = COALESCE(available_stock, 0) + :delta,
                    updated_at = NOW()
                WHERE id = :article_id
            """),
            {"delta": payload.menge, "article_id": payload.article_id},
        )

    # GL posting
    journal_entry_id = None
    try:
        accounts = _get_account_mapping(db, tid, payload.article_id)
        amount = Decimal(str(abs(payload.menge)))
        if payload.menge < 0:
            # Abgang: DEBIT Bestandsveränderung/Schwund, CREDIT Bestandskonto
            debit_konto = DEFAULT_ACCOUNTS["schwund_konto"] if payload.grund == "schwund" else DEFAULT_ACCOUNTS["bestandsveraenderung"]
            debit_name = "Lagerschwund" if payload.grund == "schwund" else "Bestandsveränderungen"
            journal_entry_id = _post_inventory_journal(
                db,
                tenant_id=tid,
                posting_date=posting_date,
                document_type="stock_correction",
                document_number=ref_number,
                description=f"Bestandskorrektur ({REASON_CODES[payload.grund]})",
                debit_account=debit_konto,
                debit_account_name=debit_name,
                credit_account=accounts["bestandskonto"],
                credit_account_name="Warenbestand",
                amount=amount,
                reference=ref_number,
            )
        else:
            # Zugang: DEBIT Bestandskonto, CREDIT Bestandsveränderung
            journal_entry_id = _post_inventory_journal(
                db,
                tenant_id=tid,
                posting_date=posting_date,
                document_type="stock_correction",
                document_number=ref_number,
                description=f"Bestandskorrektur Zugang ({REASON_CODES[payload.grund]})",
                debit_account=accounts["bestandskonto"],
                debit_account_name="Warenbestand",
                credit_account=DEFAULT_ACCOUNTS["bestandsveraenderung"],
                credit_account_name="Bestandsveränderungen",
                amount=amount,
                reference=ref_number,
            )
    except Exception:
        # GL posting is best-effort; don't block the correction
        pass

    db.commit()

    return BestandskorrekturOut(
        id=korrektur_id,
        article_id=payload.article_id,
        warehouse_id=payload.warehouse_id,
        menge=payload.menge,
        grund=payload.grund,
        grund_text=REASON_CODES[payload.grund],
        bemerkung=payload.bemerkung,
        charge=payload.charge,
        buchungsdatum=posting_date,
        movement_id=movement_id,
        journal_entry_id=journal_entry_id,
        status="gebucht",
    )


@router.post("/schwund", response_model=BestandskorrekturOut, status_code=201, tags=["lager"], summary="Schwund anlegen")
async def create_schwund(
    payload: SchwundBuchungIn,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Lagerschwund buchen — Kurzform für Bestandskorrektur mit Grund 'schwund'.

    Bucht automatisch: DEBIT 5810 Lagerschwund, CREDIT 1500 Warenbestand.
    """
    korrektur = BestandskorrekturIn(
        article_id=payload.article_id,
        warehouse_id=payload.warehouse_id,
        menge=-abs(payload.menge),
        grund="schwund",
        bemerkung=payload.bemerkung,
        charge=payload.charge,
        buchungsdatum=payload.buchungsdatum,
    )
    return await create_bestandskorrektur(korrektur, tenant_id, db)


@router.post("/mhd-abschreibung", response_model=BestandskorrekturOut, status_code=201, tags=["lager"], summary="Mhd abschreibung anlegen")
async def create_mhd_abschreibung(
    payload: MhdAbschreibungIn,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """MHD-Abschreibung — Charge mit abgelaufenem Haltbarkeitsdatum ausbuchen.

    Bucht automatisch: DEBIT 5800 Bestandsveränderungen, CREDIT 1500 Warenbestand.
    Aktualisiert ggf. die Chargen-Menge auf 0.
    """
    posting_date = payload.buchungsdatum or date.today()

    # Update batch quantity to 0
    try:
        db.execute(
            text("""
                UPDATE domain_inventory.article_batches
                SET quantity = GREATEST(0, quantity - :menge)
                WHERE tenant_id = :tid AND batch_number = :charge AND article_id = :article_id
            """),
            {"menge": payload.menge, "tid": tenant_id or DEFAULT_TENANT, "charge": payload.charge, "article_id": payload.article_id},
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("Chargen-UPDATE fehlgeschlagen (Tabelle evtl. nicht vorhanden): %s", e)

    korrektur = BestandskorrekturIn(
        article_id=payload.article_id,
        warehouse_id=payload.warehouse_id,
        menge=-abs(payload.menge),
        grund="mhd_verfall",
        bemerkung=payload.bemerkung or f"MHD abgelaufen: {payload.mhd.isoformat()}, Charge: {payload.charge}",
        charge=payload.charge,
        buchungsdatum=posting_date,
    )
    return await create_bestandskorrektur(korrektur, tenant_id, db)


@router.get("/korrekturen", tags=["lager"], summary="Korrekturen auflisten",
    response_model=InventoryOperationsOut
)
async def list_korrekturen(
    tenant_id: Optional[str] = Query(None),
    article_id: Optional[str] = Query(None),
    grund: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Korrektur-Bewegungen auflisten (gefiltert nach Grund-Code)."""
    tid = tenant_id or DEFAULT_TENANT
    conditions = ["tenant_id = :tid", "movement_type = 'adjustment'"]
    params: dict = {"tid": tid, "skip": skip, "limit": limit}

    if article_id:
        conditions.append("article_id = :article_id")
        params["article_id"] = article_id
    if grund and grund in REASON_CODES:
        conditions.append("notes LIKE :grund_pattern")
        params["grund_pattern"] = f"%{REASON_CODES[grund]}%"

    where = " AND ".join(conditions)
    rows = db.execute(
        text(f"""
            SELECT id, article_id, warehouse_id, quantity, charge, reference_number,
                   movement_date, notes, created_at
            FROM domain_inventory.inventory_stock_movements
            WHERE {where}
            ORDER BY created_at DESC
            OFFSET :skip LIMIT :limit
        """),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    ).mappings().all()

    total = db.execute(
        text(f"SELECT COUNT(*) FROM domain_inventory.inventory_stock_movements WHERE {where}"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    ).scalar() or 0

    return {
        "items": [
            {
                "id": str(r["id"]),
                "article_id": str(r["article_id"]),
                "warehouse_id": str(r["warehouse_id"]),
                "menge": float(r["quantity"]),
                "charge": r["charge"],
                "reference_number": r["reference_number"],
                "buchungsdatum": str(r["movement_date"]) if r["movement_date"] else None,
                "bemerkung": r["notes"],
                "created_at": str(r["created_at"]),
            }
            for r in rows
        ],
        "total": total,
    }


@router.get("/korrekturen/{korrektur_id}", tags=["lager"], summary="Korrektur abrufen",
    response_model=InventoryOperationsOut
)
async def get_korrektur(
    korrektur_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Einzelne Bestandskorrektur abrufen."""
    tid = tenant_id or DEFAULT_TENANT
    try:
        row = db.execute(
            text("""
                SELECT id, article_id, warehouse_id, quantity, charge, reference_number,
                       movement_date, notes, created_at
                FROM domain_inventory.inventory_stock_movements
                WHERE id = :id AND tenant_id = :tid AND movement_type = 'adjustment'
            """),
            {"id": korrektur_id, "tid": tid},
        ).mappings().fetchone()
    except Exception:
        row = None
    if not row:
        raise HTTPException(status_code=404, detail="Korrektur nicht gefunden")
    return {
        "id": str(row["id"]),
        "article_id": str(row["article_id"]),
        "warehouse_id": str(row["warehouse_id"]),
        "menge": float(row["quantity"]),
        "charge": row["charge"],
        "reference_number": row["reference_number"],
        "buchungsdatum": str(row["movement_date"]) if row["movement_date"] else None,
        "bemerkung": row["notes"],
        "created_at": str(row["created_at"]),
    }


# ---------------------------------------------------------------------------
# DOM-INV-004.2 — Lot/Charge-Traceability (FEFO)
# ---------------------------------------------------------------------------

from pydantic import Field as _Field
from typing import List as _List


class LotCreateIn(BaseModel):
    article_id: str
    warehouse_id: str
    lot_number: str
    initial_qty: float = _Field(..., gt=0)
    unit: str = "kg"
    mhd: Optional[date] = None


class LotConsumeIn(BaseModel):
    quantity: float = _Field(..., gt=0)
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None


@router.post(
    "/lots",
    status_code=201,
    response_model=InventoryLotOut,
    tags=["lager", "inventory", "lots"],
    summary="Inventory-Lot anlegen (DOM-INV-004.2)",
)
async def create_inventory_lot(
    body: LotCreateIn,
    x_tenant_id: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Neuen Chargen-/MHD-Eintrag anlegen."""
    tenant_id = x_tenant_id or DEFAULT_TENANT
    from app.services.inventory_lot_trace_service import create_lot, LotTraceError
    try:
        return create_lot(
            db=db,
            tenant_id=tenant_id,
            article_id=body.article_id,
            warehouse_id=body.warehouse_id,
            lot_number=body.lot_number,
            initial_qty=body.initial_qty,
            unit=body.unit,
            mhd=body.mhd,
        )
    except LotTraceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.get(
    "/lots",
    response_model=list[InventoryLotOut],
    tags=["lager", "inventory", "lots"],
    summary="Inventory-Lots (FEFO) auflisten (DOM-INV-004.2)",
)
async def list_inventory_lots(
    article_id: Optional[str] = None,
    warehouse_id: Optional[str] = None,
    include_exhausted: bool = False,
    x_tenant_id: Optional[str] = None,
    db: Session = Depends(get_db),
) -> list:
    """FEFO-sortierte Lot-Liste (frühestes MHD zuerst)."""
    tenant_id = x_tenant_id or DEFAULT_TENANT
    from app.services.inventory_lot_trace_service import list_lots_fefo
    try:
        return list_lots_fefo(
            db=db,
            tenant_id=tenant_id,
            article_id=article_id,
            warehouse_id=warehouse_id,
            include_exhausted=include_exhausted,
        )
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@router.post(
    "/lots/{lot_id}/consume",
    response_model=LotConsumeOut,
    tags=["lager", "inventory", "lots"],
    summary="Lot-Verbrauch (FEFO, fail-closed) (DOM-INV-004.2)",
)
async def consume_inventory_lot(
    lot_id: str,
    body: LotConsumeIn,
    x_tenant_id: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Menge aus einem Lot verbrauchen (fail-closed bei MHD-Ablauf oder Unterdeckung)."""
    tenant_id = x_tenant_id or DEFAULT_TENANT
    from app.services.inventory_lot_trace_service import consume_lot, LotTraceError
    try:
        return consume_lot(
            db=db,
            lot_id=lot_id,
            tenant_id=tenant_id,
            quantity=body.quantity,
            reference_id=body.reference_id,
            reference_type=body.reference_type,
        )
    except LotTraceError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# DOM-INV-004.3 — Inventur-Differenzbeleg
# ---------------------------------------------------------------------------

@router.post(
    "/inventur/{count_id}/differenz-buchen",
    response_model=InventurDifferenzOut,
    status_code=201,
    tags=["lager", "inventory", "inventur"],
    summary="Inventur-Differenzbeleg automatisch erzeugen (DOM-INV-004.3)",
)
async def inventur_differenz_buchen(
    count_id: str,
    x_tenant_id: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Für jede Zähldifferenz (gezählt vs. Buchbestand) automatisch Bestandskorrektur anlegen.

    Nur für Inventuren mit status='posted'. Idempotent.
    """
    tenant_id = x_tenant_id or DEFAULT_TENANT
    from app.services.inventory_count_close_service import differenz_buchen, CountCloseError
    try:
        return differenz_buchen(db=db, count_id=count_id, tenant_id=tenant_id)
    except CountCloseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# DOM-INV-004.4 — Bestandskorrektur-Storno
# ---------------------------------------------------------------------------

class StornoIn(BaseModel):
    bemerkung: Optional[str] = None


@router.post(
    "/korrekturen/{korrektur_id}/storno",
    response_model=StornoKorrekturOut,
    status_code=201,
    tags=["lager", "inventory", "korrekturen"],
    summary="Bestandskorrektur stornieren (idempotent) (DOM-INV-004.4)",
)
async def storno_bestandskorrektur(
    korrektur_id: str,
    body: StornoIn,
    x_tenant_id: Optional[str] = None,
    db: Session = Depends(get_db),
) -> dict:
    """Storno-Gegenbuchung zur Bestandskorrektur (idempotent via storno_ref)."""
    tenant_id = x_tenant_id or DEFAULT_TENANT
    from app.services.inventory_correction_service import storno_korrektur, CorrectionError
    try:
        return storno_korrektur(
            db=db,
            korrektur_id=korrektur_id,
            tenant_id=tenant_id,
            bemerkung=body.bemerkung,
        )
    except CorrectionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Lagerbestand-Abfrage  GET /lager/bestaende
# ---------------------------------------------------------------------------

class BestandItem(BaseModel):
    article_id: str
    article_number: Optional[str]
    article_name: Optional[str]
    warehouse_id: str
    warehouse_name: Optional[str]
    menge: float
    einheit: Optional[str]
    charge: Optional[str]
    bestandswert: Optional[float]


@router.get(
    "/bestaende",
    response_model=list[BestandItem],
    tags=["lager"],
    summary="Lagerbestände abfragen",
)
async def get_bestaende(
    warehouse_id: Optional[str] = Query(None, description="Filter auf Lager"),
    article_id: Optional[str] = Query(None, description="Filter auf Artikel"),
    article_number: Optional[str] = Query(None, description="Filter auf Artikelnummer"),
    charge: Optional[str] = Query(None, description="Filter auf Charge"),
    only_positive: bool = Query(True, description="Nur positive Bestände"),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> list[BestandItem]:
    """Aggregierte Lagerbestände aus StockMovements (Zugang - Abgang)."""
    t_id = tenant_id or DEFAULT_TENANT

    filters = ["sm.tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": t_id}

    if warehouse_id:
        filters.append("sm.warehouse_id = :warehouse_id")
        params["warehouse_id"] = warehouse_id
    if article_id:
        filters.append("sm.article_id = :article_id")
        params["article_id"] = article_id
    if article_number:
        filters.append("a.article_number = :article_number")
        params["article_number"] = article_number
    if charge:
        filters.append("sm.charge = :charge")
        params["charge"] = charge

    having = "HAVING SUM(sm.quantity) > 0" if only_positive else ""
    where_clause = " AND ".join(filters)

    try:
        rows = db.execute(
            text(f"""
                SELECT
                    sm.article_id,
                    a.article_number,
                    a.name AS article_name,
                    sm.warehouse_id,
                    w.name AS warehouse_name,
                    SUM(CASE WHEN sm.movement_type IN ('wareneingang','inventur','umbuchung_eingang')
                             THEN sm.quantity
                             WHEN sm.movement_type IN ('warenausgang','umbuchung_ausgang')
                             THEN -sm.quantity
                             ELSE sm.quantity END) AS menge,
                    a.unit AS einheit,
                    sm.charge,
                    SUM(sm.quantity * COALESCE(sm.unit_cost, a.purchase_price, 0)) AS bestandswert
                FROM domain_inventory.inventory_stock_movements sm
                LEFT JOIN domain_inventory.articles a ON a.id = sm.article_id
                LEFT JOIN domain_inventory.warehouses w ON w.id = sm.warehouse_id
                WHERE {where_clause}
                GROUP BY sm.article_id, a.article_number, a.name, sm.warehouse_id, w.name, a.unit, sm.charge
                {having}
                ORDER BY a.name, sm.warehouse_id
            """),  # nosec B608  # where_clause/having aus festen Literalen dieser Funktion, alle Werte via Bind-Params
            params,
        ).mappings().all()
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        # SPEC-P0-03 harte Regel: Bestands-Endpoints duerfen bei DB-Fehlern
        # niemals still leere Daten liefern — RFC-7807-Fehler + Alerting-Metrik.
        from app.core.metrics import critical_data_path_errors_total
        critical_data_path_errors_total.labels(endpoint="inventory_bestand", error_type="db_error").inc()
        raise HTTPException(
            status_code=503,
            detail=f"Lagerbestand nicht verfuegbar — Datenbank-/Schemafehler: {exc.__class__.__name__}",
        ) from exc

    return [BestandItem(**dict(r)) for r in rows]


# ---------------------------------------------------------------------------
# Generische Lagerbuchung  POST /lager/bewegungen
# ---------------------------------------------------------------------------

class LagerbewegungIn(BaseModel):
    article_id: str = Field(..., description="Artikel-ID")
    warehouse_id: str = Field(..., description="Lager-ID")
    quantity: float = Field(..., description="Menge (positiv=Zugang, negativ=Abgang)")
    movement_type: str = Field(..., description="Typ: wareneingang|warenausgang|umbuchung|inventur")
    charge: Optional[str] = Field(None)
    reference_id: Optional[str] = Field(None, description="Belegnummer (Bestellung, Lieferschein, ...)")
    reference_type: Optional[str] = Field(None, description="Belegtyp: bestellung|lieferschein|etc.")
    unit_cost: Optional[float] = Field(None, description="Einstandspreis (optional)")
    bemerkung: Optional[str] = Field(None)
    buchungsdatum: Optional[date] = Field(None)


class LagerbewegungOut(BaseModel):
    id: str
    article_id: str
    warehouse_id: str
    quantity: float
    movement_type: str
    charge: Optional[str]
    reference_id: Optional[str]
    reference_type: Optional[str]
    unit_cost: Optional[float]
    bemerkung: Optional[str]
    buchungsdatum: date
    status: str


@router.post(
    "/bewegungen",
    response_model=LagerbewegungOut,
    status_code=201,
    tags=["lager"],
    summary="Lagerbewegung buchen",
)
async def create_lagerbewegung(
    payload: LagerbewegungIn,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
) -> LagerbewegungOut:
    """Generische Lagerbuchung: Wareneingang, -ausgang, Umbuchung oder Inventur."""
    t_id = tenant_id or DEFAULT_TENANT
    from datetime import date as date_type

    allowed_types = {"wareneingang", "warenausgang", "umbuchung", "inventur"}
    if payload.movement_type not in allowed_types:
        raise HTTPException(
            status_code=422,
            detail=f"movement_type muss eines von {allowed_types} sein",
        )

    buch_datum = payload.buchungsdatum or date_type.today()
    movement_id = str(uuid4())

    article = db.execute(
        text("SELECT id FROM domain_inventory.articles WHERE id = :id AND tenant_id = :tid"),
        {"id": payload.article_id, "tid": t_id},
    ).scalar()
    if not article:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")

    # previous_stock und new_stock sind NOT NULL in der Tabelle
    prev_stock_row = db.execute(
        text("""
            SELECT COALESCE(SUM(CASE
                WHEN movement_type IN ('wareneingang','inventur') THEN quantity
                WHEN movement_type IN ('warenausgang') THEN -quantity
                ELSE quantity END), 0)
            FROM domain_inventory.inventory_stock_movements
            WHERE tenant_id = :tid AND article_id = :aid AND warehouse_id = :wid
        """),
        {"tid": t_id, "aid": payload.article_id, "wid": payload.warehouse_id},
    ).scalar() or 0
    direction = -1 if payload.movement_type == "warenausgang" else 1
    new_stock = float(prev_stock_row) + direction * payload.quantity

    db.execute(
        text("""
            INSERT INTO domain_inventory.inventory_stock_movements
                (id, tenant_id, article_id, warehouse_id, quantity, movement_type,
                 charge, reference_number, source_document_type, unit_cost, notes,
                 movement_date, previous_stock, new_stock, auto_created, ownership_type,
                 storage_fee_relevant)
            VALUES
                (:id, :tenant_id, :article_id, :warehouse_id, :quantity, :movement_type,
                 :charge, :reference_number, :source_document_type, :unit_cost, :notes,
                 :movement_date, :prev_stock, :new_stock, false, 'owned', false)
        """),
        {
            "id": movement_id,
            "tenant_id": t_id,
            "article_id": payload.article_id,
            "warehouse_id": payload.warehouse_id,
            "quantity": payload.quantity,
            "movement_type": payload.movement_type,
            "charge": payload.charge,
            "reference_number": payload.reference_id,
            "source_document_type": payload.reference_type,
            "unit_cost": payload.unit_cost,
            "notes": payload.bemerkung,
            "movement_date": buch_datum,
            "prev_stock": float(prev_stock_row),
            "new_stock": new_stock,
        },
    )
    db.commit()

    return LagerbewegungOut(
        id=movement_id,
        article_id=payload.article_id,
        warehouse_id=payload.warehouse_id,
        quantity=payload.quantity,
        movement_type=payload.movement_type,
        charge=payload.charge,
        reference_id=payload.reference_id,
        reference_type=payload.reference_type,
        unit_cost=payload.unit_cost,
        bemerkung=payload.bemerkung,
        buchungsdatum=buch_datum,
        status="posted",
    )
