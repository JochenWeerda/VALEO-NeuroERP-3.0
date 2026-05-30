"""
Inventory Operations — Bestandskorrektur, Schwund, MHD-Abschreibung
Wave 1+2: Core inventory correction endpoints with automatic GL posting.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
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
        # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        text(f"""
            SELECT id, article_id, warehouse_id, quantity, charge, reference_number,
                   movement_date, notes, created_at
            FROM domain_inventory.inventory_stock_movements
            WHERE {where}
            ORDER BY created_at DESC
            OFFSET :skip LIMIT :limit
        """),
        params,
    ).mappings().all()

    total = db.execute(
        text(f"SELECT COUNT(*) FROM domain_inventory.inventory_stock_movements WHERE {where}"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
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
