"""Einkauf Lieferschein + Frachtauftrag CRUD endpoints."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from app.core.uuid7 import uuid7

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db


from app.api.v1.schemas.base import BaseSchema


router = APIRouter(prefix="/einkauf", tags=["einkauf", "lieferschein", "frachtauftrag"])


class LieferscheinPositionBase(BaseModel):
    pos_nr: int = Field(ge=1)
    artikel_nr: Optional[str] = None
    lieferant_artikel_nr: Optional[str] = None
    bezeichnung: Optional[str] = None
    gebinde_nr: Optional[str] = None
    gebinde: Optional[Decimal] = None
    menge: Decimal = Field(ge=Decimal("0"))
    einheit: Optional[str] = None
    einzelpreis: Optional[Decimal] = None
    nettobetrag: Optional[Decimal] = None
    lagerhalle: Optional[str] = None
    lagerfach: Optional[str] = None
    charge: Optional[str] = None
    serien_nr: Optional[str] = None
    kontakt: Optional[str] = None
    prozent: Optional[Decimal] = None
    master_nr: Optional[str] = None


class LieferscheinPositionCreate(LieferscheinPositionBase):
    pass


class LieferscheinPosition(LieferscheinPositionBase):
    id: str


class LieferscheinBase(BaseModel):
    lieferschein_nr: str
    lieferschein_datum: date
    niederlassung: Optional[str] = None
    lieferant_id: Optional[str] = None
    lieferant_name: Optional[str] = None
    zahlungsbedingung: Optional[str] = None
    texte: Optional[str] = None
    zwischenhaendler: Optional[str] = None
    wie_vom_ls: bool = False
    lieferanten_stamm: Optional[str] = None
    liefer_termin: Optional[date] = None
    lieferdatum: Optional[date] = None
    liefer_nr: Optional[str] = None
    bediener: Optional[str] = None
    erledigt: bool = False
    verfuegbarer_bestand: Optional[Decimal] = None
    summe_gewicht: Optional[Decimal] = None
    mwst_betrag: Optional[Decimal] = None
    netto_betrag: Optional[Decimal] = None
    brutto_betrag: Optional[Decimal] = None


class LieferscheinCreate(LieferscheinBase):
    positionen: list[LieferscheinPositionCreate] = []


class LieferscheinUpdate(BaseModel):
    lieferschein_datum: Optional[date] = None
    niederlassung: Optional[str] = None
    lieferant_id: Optional[str] = None
    lieferant_name: Optional[str] = None
    zahlungsbedingung: Optional[str] = None
    texte: Optional[str] = None
    zwischenhaendler: Optional[str] = None
    wie_vom_ls: Optional[bool] = None
    lieferanten_stamm: Optional[str] = None
    liefer_termin: Optional[date] = None
    lieferdatum: Optional[date] = None
    liefer_nr: Optional[str] = None
    bediener: Optional[str] = None
    erledigt: Optional[bool] = None
    verfuegbarer_bestand: Optional[Decimal] = None
    summe_gewicht: Optional[Decimal] = None
    mwst_betrag: Optional[Decimal] = None
    netto_betrag: Optional[Decimal] = None
    brutto_betrag: Optional[Decimal] = None


class Lieferschein(LieferscheinBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime
    positionen: list[LieferscheinPosition] = []


class FrachtauftragBase(BaseModel):
    frachtauftrag_nr: str
    frachtauftrag_erzeugt: Optional[datetime] = None
    niederlassung: Optional[str] = None
    liefertermin: Optional[date] = None
    spediteur_nr: Optional[str] = None
    spediteur_name: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    belegnummer: Optional[str] = None
    lade_datum: Optional[date] = None
    kunde_id: Optional[str] = None
    kunde_name: Optional[str] = None
    debitoren_filter: Optional[str] = None


class FrachtauftragCreate(FrachtauftragBase):
    pass


class FrachtauftragUpdate(BaseModel):
    frachtauftrag_erzeugt: Optional[datetime] = None
    niederlassung: Optional[str] = None
    liefertermin: Optional[date] = None
    spediteur_nr: Optional[str] = None
    spediteur_name: Optional[str] = None
    email: Optional[str] = None
    telefon: Optional[str] = None
    belegnummer: Optional[str] = None
    lade_datum: Optional[date] = None
    kunde_id: Optional[str] = None
    kunde_name: Optional[str] = None
    debitoren_filter: Optional[str] = None


class Frachtauftrag(FrachtauftragBase):
    id: str
    tenant_id: str
    created_at: datetime
    updated_at: datetime


def _get_lieferschein_or_404(db: Session, ls_id: str, tenant_id: str):
    row = db.execute(
        text("SELECT * FROM einkauf_lieferscheine WHERE id = :id AND tenant_id = :tenant_id"),
        {"id": ls_id, "tenant_id": tenant_id},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail="Lieferschein not found")
    return row


def _list_positions(db: Session, ls_id: str) -> list[LieferscheinPosition]:
    rows = db.execute(
        text("SELECT * FROM einkauf_lieferschein_positionen WHERE lieferschein_id = :id ORDER BY pos_nr ASC"),
        {"id": ls_id},
    ).mappings().all()
    return [LieferscheinPosition(**dict(r)) for r in rows]


@router.get("/lieferscheine", response_model=list[Lieferschein], summary="Lieferscheine auflisten")
async def list_lieferscheine(
    tenant_id: str = Query("system"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    params: dict[str, object] = {"tenant_id": tenant_id}
    where = "tenant_id = :tenant_id"
    if search:
        where += " AND (lieferschein_nr ILIKE :search OR COALESCE(lieferant_name,'') ILIKE :search)"
        params["search"] = f"%{search}%"
    rows = db.execute(
        text(f"SELECT * FROM einkauf_lieferscheine WHERE {where} ORDER BY lieferschein_datum DESC, created_at DESC LIMIT 500"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        params,
    ).mappings().all()
    result: list[Lieferschein] = []
    for row in rows:
        result.append(Lieferschein(**dict(row), positionen=_list_positions(db, row["id"])))
    return result


@router.post("/lieferscheine", response_model=Lieferschein, status_code=201, summary="Lieferschein anlegen")
async def create_lieferschein(
    payload: LieferscheinCreate,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
):
    ls_id = uuid7()
    db.execute(
        text(
            """
            INSERT INTO einkauf_lieferscheine (
              id, tenant_id, lieferschein_nr, lieferschein_datum, niederlassung, lieferant_id, lieferant_name,
              zahlungsbedingung, texte, zwischenhaendler, wie_vom_ls, lieferanten_stamm, liefer_termin, lieferdatum,
              liefer_nr, bediener, erledigt, verfuegbarer_bestand, summe_gewicht, mwst_betrag, netto_betrag, brutto_betrag,
              created_at, updated_at
            ) VALUES (
              :id, :tenant_id, :lieferschein_nr, :lieferschein_datum, :niederlassung, :lieferant_id, :lieferant_name,
              :zahlungsbedingung, :texte, :zwischenhaendler, :wie_vom_ls, :lieferanten_stamm, :liefer_termin, :lieferdatum,
              :liefer_nr, :bediener, :erledigt, :verfuegbarer_bestand, :summe_gewicht, :mwst_betrag, :netto_betrag, :brutto_betrag,
              NOW(), NOW()
            )
            """
        ),
        {"id": ls_id, "tenant_id": tenant_id, **payload.model_dump(exclude={"positionen"})},
    )
    for pos in payload.positionen:
        db.execute(
            text(
                """
                INSERT INTO einkauf_lieferschein_positionen (
                  id, lieferschein_id, pos_nr, artikel_nr, lieferant_artikel_nr, bezeichnung, gebinde_nr, gebinde,
                  menge, einheit, einzelpreis, nettobetrag, lagerhalle, lagerfach, charge, serien_nr, kontakt, prozent, master_nr,
                  created_at, updated_at
                ) VALUES (
                  :id, :lieferschein_id, :pos_nr, :artikel_nr, :lieferant_artikel_nr, :bezeichnung, :gebinde_nr, :gebinde,
                  :menge, :einheit, :einzelpreis, :nettobetrag, :lagerhalle, :lagerfach, :charge, :serien_nr, :kontakt, :prozent, :master_nr,
                  NOW(), NOW()
                )
                """
            ),
            {"id": uuid7(), "lieferschein_id": ls_id, **pos.model_dump()},
        )
    db.commit()
    row = _get_lieferschein_or_404(db, ls_id, tenant_id)
    return Lieferschein(**dict(row), positionen=_list_positions(db, ls_id))


@router.get("/lieferscheine/last", response_model=Optional[Lieferschein], summary="Last lieferschein abrufen")
async def get_last_lieferschein(
    lieferant_id: Optional[str] = Query(None, description="Filter by supplier (last LS for this supplier)"),
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
):
    """Last (most recent) Lieferschein for F11 'Wie vorheriger Beleg'."""
    params: dict[str, object] = {"tenant_id": tenant_id}
    where = "tenant_id = :tenant_id"
    if lieferant_id:
        where += " AND lieferant_id = :lieferant_id"
        params["lieferant_id"] = lieferant_id
    row = db.execute(
        text(
            f"SELECT * FROM einkauf_lieferscheine WHERE {where} ORDER BY created_at DESC LIMIT 1"
        ),
        params,
    ).mappings().first()
    if not row:
        return None
    ls_id = row["id"]
    return Lieferschein(**dict(row), positionen=_list_positions(db, ls_id))


@router.get("/lieferscheine/{ls_id}", response_model=Lieferschein, summary="Lieferschein abrufen")
async def get_lieferschein(ls_id: str, tenant_id: str = Query("system"), db: Session = Depends(get_db)):
    row = _get_lieferschein_or_404(db, ls_id, tenant_id)
    return Lieferschein(**dict(row), positionen=_list_positions(db, ls_id))


@router.patch("/lieferscheine/{ls_id}", response_model=Lieferschein, summary="Lieferschein aktualisieren")
async def patch_lieferschein(ls_id: str, payload: LieferscheinUpdate, tenant_id: str = Query("system"), db: Session = Depends(get_db)):
    _get_lieferschein_or_404(db, ls_id, tenant_id)
    values = payload.model_dump(exclude_unset=True)
    if values:
        set_clause = ", ".join(f"{k} = :{k}" for k in values.keys())
        params = {"id": ls_id, "tenant_id": tenant_id, **values}
        db.execute(text(f"UPDATE einkauf_lieferscheine SET {set_clause}, updated_at = NOW() WHERE id = :id AND tenant_id = :tenant_id"), params)  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        db.commit()
    row = _get_lieferschein_or_404(db, ls_id, tenant_id)
    return Lieferschein(**dict(row), positionen=_list_positions(db, ls_id))


@router.delete("/lieferscheine/{ls_id}", status_code=204, response_class=Response, response_model=None, summary="Lieferschein löschen")
async def delete_lieferschein(ls_id: str, tenant_id: str = Query("system"), db: Session = Depends(get_db)):
    _get_lieferschein_or_404(db, ls_id, tenant_id)
    db.execute(text("DELETE FROM einkauf_lieferscheine WHERE id = :id AND tenant_id = :tenant_id"), {"id": ls_id, "tenant_id": tenant_id})
    db.commit()
    return None


@router.post("/lieferscheine/{ls_id}/positionen", response_model=LieferscheinPosition, status_code=201, summary="Lieferschein position hinzufügen")
async def add_lieferschein_position(ls_id: str, payload: LieferscheinPositionCreate, tenant_id: str = Query("system"), db: Session = Depends(get_db)):
    _get_lieferschein_or_404(db, ls_id, tenant_id)
    pos_id = uuid7()
    db.execute(
        text(
            """
            INSERT INTO einkauf_lieferschein_positionen (
              id, lieferschein_id, pos_nr, artikel_nr, lieferant_artikel_nr, bezeichnung, gebinde_nr, gebinde,
              menge, einheit, einzelpreis, nettobetrag, lagerhalle, lagerfach, charge, serien_nr, kontakt, prozent, master_nr,
              created_at, updated_at
            ) VALUES (
              :id, :lieferschein_id, :pos_nr, :artikel_nr, :lieferant_artikel_nr, :bezeichnung, :gebinde_nr, :gebinde,
              :menge, :einheit, :einzelpreis, :nettobetrag, :lagerhalle, :lagerfach, :charge, :serien_nr, :kontakt, :prozent, :master_nr,
              NOW(), NOW()
            )
            """
        ),
        {"id": pos_id, "lieferschein_id": ls_id, **payload.model_dump()},
    )
    db.commit()
    row = db.execute(text("SELECT * FROM einkauf_lieferschein_positionen WHERE id = :id"), {"id": pos_id}).mappings().first()
    return LieferscheinPosition(**dict(row))


@router.patch("/lieferscheine/{ls_id}/positionen/{pos_id}", response_model=LieferscheinPosition, summary="Lieferschein position aktualisieren")
async def patch_lieferschein_position(
    ls_id: str,
    pos_id: str,
    payload: LieferscheinPositionCreate,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
):
    _get_lieferschein_or_404(db, ls_id, tenant_id)
    row = db.execute(text("SELECT id FROM einkauf_lieferschein_positionen WHERE id = :id AND lieferschein_id = :ls_id"), {"id": pos_id, "ls_id": ls_id}).first()
    if not row:
        raise HTTPException(status_code=404, detail="Lieferschein position not found")
    values = payload.model_dump()
    set_clause = ", ".join(f"{k} = :{k}" for k in values.keys())
    db.execute(text(f"UPDATE einkauf_lieferschein_positionen SET {set_clause}, updated_at = NOW() WHERE id = :id"), {"id": pos_id, **values})  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
    db.commit()
    updated = db.execute(text("SELECT * FROM einkauf_lieferschein_positionen WHERE id = :id"), {"id": pos_id}).mappings().first()
    return LieferscheinPosition(**dict(updated))


@router.delete("/lieferscheine/{ls_id}/positionen/{pos_id}", status_code=204, response_class=Response, response_model=None, summary="Lieferschein position löschen")
async def delete_lieferschein_position(ls_id: str, pos_id: str, tenant_id: str = Query("system"), db: Session = Depends(get_db)):
    _get_lieferschein_or_404(db, ls_id, tenant_id)
    row = db.execute(text("SELECT id FROM einkauf_lieferschein_positionen WHERE id = :id AND lieferschein_id = :ls_id"), {"id": pos_id, "ls_id": ls_id}).first()
    if not row:
        raise HTTPException(status_code=404, detail="Lieferschein position not found")
    db.execute(text("DELETE FROM einkauf_lieferschein_positionen WHERE id = :id"), {"id": pos_id})
    db.commit()
    return None


@router.get("/frachtauftraege", response_model=list[Frachtauftrag], summary="Frachtauftraege auflisten")
async def list_frachtauftraege(tenant_id: str = Query("system"), db: Session = Depends(get_db)):
    try:
        rows = db.execute(
            text("SELECT * FROM einkauf_frachtauftraege WHERE tenant_id = :tenant_id ORDER BY created_at DESC LIMIT 500"),
            {"tenant_id": tenant_id},
        ).mappings().all()
    except Exception:
        # Fallback for environments where table is not migrated yet.
        return []
    return [Frachtauftrag(**dict(r)) for r in rows]


@router.post("/frachtauftraege", response_model=Frachtauftrag, status_code=201, summary="Frachtauftrag anlegen")
async def create_frachtauftrag(payload: FrachtauftragCreate, tenant_id: str = Query("system"), db: Session = Depends(get_db)):
    fa_id = uuid7()
    db.execute(
        text(
            """
            INSERT INTO einkauf_frachtauftraege (
              id, tenant_id, frachtauftrag_nr, frachtauftrag_erzeugt, niederlassung, liefertermin, spediteur_nr, spediteur_name,
              email, telefon, belegnummer, lade_datum, kunde_id, kunde_name, debitoren_filter, created_at, updated_at
            ) VALUES (
              :id, :tenant_id, :frachtauftrag_nr, :frachtauftrag_erzeugt, :niederlassung, :liefertermin, :spediteur_nr, :spediteur_name,
              :email, :telefon, :belegnummer, :lade_datum, :kunde_id, :kunde_name, :debitoren_filter, NOW(), NOW()
            )
            """
        ),
        {"id": fa_id, "tenant_id": tenant_id, **payload.model_dump()},
    )
    db.commit()
    row = db.execute(text("SELECT * FROM einkauf_frachtauftraege WHERE id = :id"), {"id": fa_id}).mappings().first()
    return Frachtauftrag(**dict(row))


@router.patch("/frachtauftraege/{fa_id}", response_model=Frachtauftrag, summary="Frachtauftrag aktualisieren")
async def patch_frachtauftrag(
    fa_id: str,
    payload: FrachtauftragUpdate,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
):
    row = db.execute(text("SELECT id FROM einkauf_frachtauftraege WHERE id = :id AND tenant_id = :tenant_id"), {"id": fa_id, "tenant_id": tenant_id}).first()
    if not row:
        raise HTTPException(status_code=404, detail="Frachtauftrag not found")
    values = payload.model_dump(exclude_unset=True)
    if values:
        set_clause = ", ".join(f"{k} = :{k}" for k in values.keys())
        db.execute(
            text(f"UPDATE einkauf_frachtauftraege SET {set_clause}, updated_at = NOW() WHERE id = :id AND tenant_id = :tenant_id"),  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
            {"id": fa_id, "tenant_id": tenant_id, **values},
        )
        db.commit()
    updated = db.execute(text("SELECT * FROM einkauf_frachtauftraege WHERE id = :id"), {"id": fa_id}).mappings().first()
    return Frachtauftrag(**dict(updated))


@router.delete("/frachtauftraege/{fa_id}", status_code=204, response_class=Response, response_model=None, summary="Frachtauftrag löschen")
async def delete_frachtauftrag(fa_id: str, tenant_id: str = Query("system"), db: Session = Depends(get_db)):
    row = db.execute(text("SELECT id FROM einkauf_frachtauftraege WHERE id = :id AND tenant_id = :tenant_id"), {"id": fa_id, "tenant_id": tenant_id}).first()
    if not row:
        raise HTTPException(status_code=404, detail="Frachtauftrag not found")
    db.execute(text("DELETE FROM einkauf_frachtauftraege WHERE id = :id AND tenant_id = :tenant_id"), {"id": fa_id, "tenant_id": tenant_id})
    db.commit()
    return None


# ── Wareneingang buchen (Belegbruch: Einkauf-LS → Lager) ──────────────────

class EinbuchenPayload(BaseModel):
    warehouse_id: str
    default_bin_id: Optional[str] = None
    unit_cost_override: Optional[Decimal] = None


class EinbuchenResult(BaseModel):
    lieferschein_id: str
    movements_created: int
    positions_skipped: int
    detail: list[dict]


@router.post("/lieferscheine/{ls_id}/einbuchen", response_model=EinbuchenResult, status_code=200,
             summary="Wareneingang in Lager einbuchen (Belegbruch-Fix)")
async def einbuchen_lieferschein(
    ls_id: str,
    payload: EinbuchenPayload,
    tenant_id: str = Query("system"),
    db: Session = Depends(get_db),
):
    """Bucht alle Positionen des Einkauf-Lieferscheins als Einlagerung
    (EINLAGERUNG) in domain_inventory.inventory_stock_movements und bin_stock.
    Voraussetzung: Lieferschein muss existieren; kann auch nicht-erledigte LSe verbuchen,
    aber jede Position kann nur einmal verbucht werden (idempotent via movement_reference_check).
    """
    ls = db.execute(
        text("SELECT id, lieferschein_nr, erledigt FROM einkauf_lieferscheine WHERE id = :id AND tenant_id = :tid"),
        {"id": ls_id, "tid": tenant_id},
    ).mappings().first()
    if not ls:
        raise HTTPException(status_code=404, detail="Lieferschein nicht gefunden")

    positions = db.execute(
        text("SELECT * FROM einkauf_lieferschein_positionen WHERE lieferschein_id = :id ORDER BY pos_nr ASC"),
        {"id": ls_id},
    ).mappings().all()

    if not positions:
        raise HTTPException(status_code=422, detail="Lieferschein hat keine Positionen")

    from app.services.warehouse_service import WarehouseService
    svc = WarehouseService(db, tenant_id)

    movements_created = 0
    positions_skipped = 0
    detail = []
    reference = f"LS-EK-{ls['lieferschein_nr']}"

    for pos in positions:
        artikel_id = pos.get("artikel_nr")
        menge = Decimal(str(pos.get("menge") or 0))
        if not artikel_id or menge <= 0:
            positions_skipped += 1
            detail.append({"pos_nr": pos.get("pos_nr"), "skipped": True, "reason": "keine artikel_nr oder menge=0"})
            continue

        # Resolve bin: prefer position's lagerfach, then payload default_bin_id
        bin_id = pos.get("lagerfach") or payload.default_bin_id
        if not bin_id:
            # Auto-suggest best bin via CAPACITY strategy
            suggestions = svc.suggest_putaway_bin(
                warehouse_id=payload.warehouse_id,
                article_id=artikel_id,
                quantity_kg=menge,
                strategy="CAPACITY",
            )
            if not suggestions:
                positions_skipped += 1
                detail.append({"pos_nr": pos.get("pos_nr"), "skipped": True, "reason": "kein Bin mit ausreichend Kapazität"})
                continue
            bin_id = suggestions[0]["bin_id"]

        unit_cost = payload.unit_cost_override or pos.get("einzelpreis")
        if unit_cost is not None:
            unit_cost = Decimal(str(unit_cost))

        try:
            mv_id = svc.book_stock_movement(
                bin_id=bin_id,
                article_id=artikel_id,
                batch_number=pos.get("charge"),
                best_before_date=None,
                quantity_kg=menge,
                unit_cost=unit_cost,
                movement_type="EINLAGERUNG",
                reference=reference,
            )
            movements_created += 1
            detail.append({"pos_nr": pos.get("pos_nr"), "bin_id": bin_id, "menge": float(menge), "mv_id": mv_id})
        except ValueError as exc:
            positions_skipped += 1
            detail.append({"pos_nr": pos.get("pos_nr"), "skipped": True, "reason": str(exc)})

    # Mark lieferschein as erledigt
    if movements_created > 0:
        db.execute(
            text("UPDATE einkauf_lieferscheine SET erledigt = TRUE WHERE id = :id AND tenant_id = :tid"),
            {"id": ls_id, "tid": tenant_id},
        )
        db.commit()

    return EinbuchenResult(
        lieferschein_id=ls_id,
        movements_created=movements_created,
        positions_skipped=positions_skipped,
        detail=detail,
    )
