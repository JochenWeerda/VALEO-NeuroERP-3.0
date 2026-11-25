"""
Inventory Operations — Bestandskorrektur, Schwund, MHD-Abschreibung
Wave 1+2: Core inventory correction endpoints with automatic GL posting.
DOM-INV-004: Lot-Trace (.2), Inventur-Differenzbeleg (.3), Korrektur-Storno (.4).
"""

from datetime import date
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.tenant import get_tenant_id
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
import logging
from decimal import Decimal

logger = logging.getLogger(__name__)

from app.api.v1.schemas.inventory_operations_schemas import InventoryOperationsOut
from app.services.inventory_movement_direction import direction_sql, signed_quantity
from app.services.inventory_stock_balance import current_stock
from app.api.v1.schemas.inventory_lot_bundle_schemas import (
    InventoryLotOut,
    InventurDifferenzOut,
    LotConsumeOut,
    StornoKorrekturOut,
)
from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


router = APIRouter()


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

def _get_account_mapping(db, tenant_id: str, article_id: str):
    """Look up LagerKontenzuordnung for the article's group; fall back to SKR03 defaults."""
    try:
        # Im Sicherungspunkt: Scheitert die Abfrage, bleibt die Transaktion der Bestandskorrektur heil.
        # Bis 12.10.2026 fragte sie die Spalte ``article_group`` ab, die es nicht gibt; der verschluckte
        # Fehler brach die Transaktion ab, und jede Korrektur meldete "gebucht", ohne etwas zu speichern.
        with db.begin_nested():
            row = db.execute(
                text("""
                    SELECT lkz.bestandskonto, lkz.gegenkonto_zugang, lkz.gegenkonto_abgang
                    FROM domain_einkauf.lager_kontenzuordnung lkz
                    JOIN domain_inventory.articles a ON a.warengruppe = lkz.artikelgruppe
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


def melde_fehlende_bewertung(vorgang: str, beleg: str) -> None:
    """Meldet die fehlende Bestandsbewertung; erzeugt nie eine Buchung mit Ersatzwert.

    Bis 19.11.2026 buchte die Bestandskorrektur (und die Inventur) die **Menge** in Tonnen als Eurobetrag ins Journal
    und legte fehlende Konten selbst an. Eine Bestandsbuchung braucht den Wert der Menge (Bewertungsmodell, M3/M4);
    bis dahin bleibt die Bestandsaenderung operativ gebucht und das Hauptbuch unberuehrt (wie Produktion,
    JOURNAL-AMOUNT-INTEGRITY).
    """
    from app.core.metrics import critical_data_path_errors_total

    critical_data_path_errors_total.labels(endpoint=vorgang, error_type="valuation_missing").inc()
    logger.error("Keine FiBu-Buchung fuer %s: verifizierte Bestandsbewertung fehlt", beleg)


# ── Routes ──────────────────────────────────────────────────────

@router.get("/reason-codes", tags=["lager"], summary="Reason codes auflisten",
    response_model=list[InventoryOperationsOut]
)
async def list_reason_codes():
    """GET alle verfügbaren Korrektur-Gründe."""
    return [{"code": k, "label": v} for k, v in REASON_CODES.items()]


@router.post("/bestandskorrektur", response_model=BestandskorrekturOut, status_code=201, tags=["lager"], summary="Bestandskorrektur anlegen", dependencies=SCHREIBEN["LAGER"])
async def create_bestandskorrektur(
    payload: BestandskorrekturIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Bestandskorrektur buchen — StockMovement + automatische GL-Buchung.

    Positiver Betrag = Zugang (adjustment_in), negativer = Abgang (adjustment_out).
    """
    tid = tenant_id
    if payload.grund not in REASON_CODES:
        raise HTTPException(400, f"Unbekannter Grund-Code: {payload.grund}. Erlaubt: {list(REASON_CODES.keys())}")

    korrektur_id = str(uuid4())
    posting_date = payload.buchungsdatum or date.today()
    movement_type = "adjustment"
    ref_number = f"KORR-{korrektur_id[:8].upper()}"

    # Buchungsentwurf zum gleitenden Durchschnitt - vor der Bewegung, damit der Schnitt den Stand davor zeigt.
    # Fehlt Bewertung oder Kontenzuordnung, bleibt die Korrektur operativ gebucht und die Luecke wird gemeldet.
    from app.services.bestandsbewertung import BuchungNichtMoeglich, entwerfe_bestandsbuchung

    journal_entry_id = None
    try:
        journal_entry_id = entwerfe_bestandsbuchung(
            db, tid, ref_number, f"Bestandskorrektur {REASON_CODES[payload.grund]}", posting_date,
            [(payload.article_id, Decimal(str(payload.menge)), "t")])
    except BuchungNichtMoeglich as grund:
        melde_fehlende_bewertung("inventory_operations_gl", f"{ref_number} ({grund})")

    # Bewegung ueber den kanonischen Buchungsdienst (Konsolidierung, 24.11.2026): Richtung, Vorher-/Nachherbestand
    # aus dem Journal, Artikelbestand, Unterdeckung - bis dahin schrieb die Korrektur previous/new_stock = 0.
    from app.domains.inventory.application.services.inventory_service import InventoryService

    try:
        bewegung = InventoryService(db).process_stock_movement(
            payload.article_id, payload.warehouse_id, movement_type, Decimal(str(payload.menge)), unit="t",
            movement_date=posting_date, reference_number=ref_number, charge=payload.charge, booking_user="system",
            notes=f"{REASON_CODES[payload.grund]}: {payload.bemerkung or ''}".strip(), tenant_id=tid,
            buchungsschluessel=f"korrektur:{korrektur_id}", commit=False)
    except ValueError as fehler:
        db.rollback()
        raise HTTPException(422, str(fehler)) from fehler
    movement_id = str(bewegung.id)

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


@router.post("/schwund", response_model=BestandskorrekturOut, status_code=201, tags=["lager"], summary="Schwund anlegen", dependencies=SCHREIBEN["LAGER"])
async def create_schwund(
    payload: SchwundBuchungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Lagerschwund buchen — Kurzform für Bestandskorrektur mit Grund 'schwund'.

    Die Hauptbuchbuchung folgt erst mit der Bestandsbewertung (s. melde_fehlende_bewertung).
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


@router.post("/mhd-abschreibung", response_model=BestandskorrekturOut, status_code=201, tags=["lager"], summary="Mhd abschreibung anlegen", dependencies=SCHREIBEN["LAGER"])
async def create_mhd_abschreibung(
    payload: MhdAbschreibungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """MHD-Abschreibung — Charge mit abgelaufenem Haltbarkeitsdatum ausbuchen.

    Die Hauptbuchbuchung folgt erst mit der Bestandsbewertung (s. melde_fehlende_bewertung).
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
            {"menge": payload.menge, "tid": tenant_id, "charge": payload.charge, "article_id": payload.article_id},
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
    tenant_id: str = Depends(get_tenant_id),
    article_id: Optional[str] = Query(None),
    grund: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Korrektur-Bewegungen auflisten (gefiltert nach Grund-Code)."""
    tid = tenant_id
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
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einzelne Bestandskorrektur abrufen."""
    tid = tenant_id
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
    summary="Inventory-Lot anlegen (DOM-INV-004.2)", dependencies=SCHREIBEN["LAGER"])
async def create_inventory_lot(
    body: LotCreateIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Neuen Chargen-/MHD-Eintrag anlegen."""
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
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list:
    """FEFO-sortierte Lot-Liste (frühestes MHD zuerst)."""
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
    summary="Lot-Verbrauch (FEFO, fail-closed) (DOM-INV-004.2)", dependencies=SCHREIBEN["LAGER"])
async def consume_inventory_lot(
    lot_id: str,
    body: LotConsumeIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Menge aus einem Lot verbrauchen (fail-closed bei MHD-Ablauf oder Unterdeckung)."""
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
    summary="Inventur-Differenzbeleg automatisch erzeugen (DOM-INV-004.3)", dependencies=SCHREIBEN["LAGER"])
async def inventur_differenz_buchen(
    count_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Für jede Zähldifferenz (gezählt vs. Buchbestand) automatisch Bestandskorrektur anlegen.

    Nur für Inventuren mit status='posted'. Idempotent.
    """
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
    summary="Bestandskorrektur stornieren (idempotent) (DOM-INV-004.4)", dependencies=SCHREIBEN["LAGER"])
async def storno_bestandskorrektur(
    korrektur_id: str,
    body: StornoIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    """Storno-Gegenbuchung zu einer Lagerbewegung (idempotent via storno_ref).

    Der Mandant kommt aus dem Kontext; bis 07.10.2026 aus einem Query-Parameter.
    """
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
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[BestandItem]:
    """Aggregierte Lagerbestände aus StockMovements (Zugang - Abgang)."""
    t_id = tenant_id

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

    where_clause = " AND ".join(filters)

    # DOM-INV-005: Richtung zentral. Vorher hat der ELSE-Zweig jeden nicht
    # aufgezaehlten Typ positiv gezaehlt - ZUGANG und ABGANG landeten damit
    # beide als Zugang im Bestand, und der Bestandswert addierte jeden
    # Warenausgang statt ihn abzuziehen.
    richtung = direction_sql("sm.movement_type", "sm.quantity")
    wert = direction_sql(
        "sm.movement_type",
        "sm.quantity * COALESCE(sm.unit_cost, a.purchase_price, 0)",
    )
    # HAVING muss dieselbe Richtung kennen wie die Menge, sonst filtert es
    # auf einer anderen Zahl als es zurueckgibt.
    having = f"HAVING SUM({richtung}) > 0" if only_positive else ""

    try:
        rows = db.execute(
            text(f"""
                SELECT
                    sm.article_id,
                    a.article_number,
                    a.name AS article_name,
                    sm.warehouse_id,
                    w.name AS warehouse_name,
                    SUM({richtung}) AS menge,
                    a.unit AS einheit,
                    sm.charge,
                    SUM({wert}) AS bestandswert
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
    summary="Lagerbewegung buchen", dependencies=SCHREIBEN["LAGER"])
async def create_lagerbewegung(
    payload: LagerbewegungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> LagerbewegungOut:
    """Generische Lagerbuchung: Wareneingang, -ausgang, Umbuchung oder Inventur."""
    t_id = tenant_id
    from datetime import date as date_type

    allowed_types = {"wareneingang", "warenausgang", "umbuchung", "inventur"}
    if payload.movement_type not in allowed_types:
        raise HTTPException(
            status_code=422,
            detail=f"movement_type muss eines von {allowed_types} sein",
        )

    buch_datum = payload.buchungsdatum or date_type.today()
    movement_id = str(uuid4())
    # Altname der Route: reference_type/reference_id. Spalten: source_document_type
    # und reference_number. Der Adapter schreibt keine Beleg-Id.
    from app.services.inventory_document_reference import buchungsbeleg

    beleg = buchungsbeleg(
        reference_type=payload.reference_type,
        reference_id=payload.reference_id,
    )

    article = db.execute(
        text("SELECT id FROM domain_inventory.articles WHERE id = :id AND tenant_id = :tid"),
        {"id": payload.article_id, "tid": t_id},
    ).scalar()
    if not article:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")

    # previous_stock und new_stock sind NOT NULL in der Tabelle. Saldo und
    # Vorzeichen kommen aus derselben Quelle wie alle anderen Aggregationen.
    prev_stock_row = current_stock(
        db,
        tenant_id=t_id,
        article_id=payload.article_id,
        warehouse_id=payload.warehouse_id,
    )
    new_stock = prev_stock_row + signed_quantity(payload.movement_type, payload.quantity)

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
            "reference_number": beleg.reference_number,
            "source_document_type": beleg.source_document_type,
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
