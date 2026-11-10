"""Einkauf Lieferschein + Frachtauftrag CRUD endpoints.

Der Mandant kommt aus dem Kontext. Bis 07.10.2026 nahm jeder Weg ihn aus einem
Query-Parameter mit dem Vorgabewert ``"system"`` — ohne Parameter landete jeder
Lieferschein im selben Topf, mit Parameter in jedem beliebigen Mandanten.
"""

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
from app.core.tenant import get_tenant_id


from app.auth.bereich_roles import SCHREIBEN  # Schreibrecht je Bereich (WRITE-ROLES)


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
    tenant_id: str = Depends(get_tenant_id),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    params: dict[str, object] = {"tenant_id": tenant_id}
    where = "tenant_id = :tenant_id"
    if search:
        where += " AND (lieferschein_nr ILIKE :search OR COALESCE(lieferant_name,'') ILIKE :search)"
        params["search"] = f"%{search}%"
    rows = db.execute(
        text(f"SELECT * FROM einkauf_lieferscheine WHERE {where} ORDER BY lieferschein_datum DESC, created_at DESC LIMIT 500"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
        params,
    ).mappings().all()
    result: list[Lieferschein] = []
    for row in rows:
        result.append(Lieferschein(**dict(row), positionen=_list_positions(db, row["id"])))
    return result


@router.get("/lieferscheine/last", response_model=Optional[Lieferschein], summary="Last lieferschein abrufen")
async def get_last_lieferschein(
    lieferant_id: Optional[str] = Query(None, description="Filter by supplier (last LS for this supplier)"),
    tenant_id: str = Depends(get_tenant_id),
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
            f"SELECT * FROM einkauf_lieferscheine WHERE {where} ORDER BY created_at DESC LIMIT 1"  # nosec B608  # reviewed-safe: SQL-Fragmente sind Code-Literale, Werte sind gebunden
        ),
        params,
    ).mappings().first()
    if not row:
        return None
    ls_id = row["id"]
    return Lieferschein(**dict(row), positionen=_list_positions(db, ls_id))


@router.get("/lieferscheine/{ls_id}", response_model=Lieferschein, summary="Lieferschein abrufen")
async def get_lieferschein(ls_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    row = _get_lieferschein_or_404(db, ls_id, tenant_id)
    return Lieferschein(**dict(row), positionen=_list_positions(db, ls_id))


@router.get("/frachtauftraege", response_model=list[Frachtauftrag], summary="Frachtauftraege auflisten")
async def list_frachtauftraege(tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    try:
        rows = db.execute(
            text("SELECT * FROM einkauf_frachtauftraege WHERE tenant_id = :tenant_id ORDER BY created_at DESC LIMIT 500"),
            {"tenant_id": tenant_id},
        ).mappings().all()
    except Exception:
        # Fallback for environments where table is not migrated yet.
        return []
    return [Frachtauftrag(**dict(r)) for r in rows]


@router.post("/frachtauftraege", response_model=Frachtauftrag, status_code=201, summary="Frachtauftrag anlegen", dependencies=SCHREIBEN["EINKAUF"])
async def create_frachtauftrag(payload: FrachtauftragCreate, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
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


@router.patch("/frachtauftraege/{fa_id}", response_model=Frachtauftrag, summary="Frachtauftrag aktualisieren", dependencies=SCHREIBEN["EINKAUF"])
async def patch_frachtauftrag(
    fa_id: str,
    payload: FrachtauftragUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    row = db.execute(text("SELECT id FROM einkauf_frachtauftraege WHERE id = :id AND tenant_id = :tenant_id"), {"id": fa_id, "tenant_id": tenant_id}).first()
    if not row:
        raise HTTPException(status_code=404, detail="Frachtauftrag not found")
    values = payload.model_dump(exclude_unset=True)
    if values:
        set_clause = ", ".join(f"{k} = :{k}" for k in values.keys())
        db.execute(
            text(f"UPDATE einkauf_frachtauftraege SET {set_clause}, updated_at = NOW() WHERE id = :id AND tenant_id = :tenant_id"),  # nosec B608  # reviewed-safe: column names code-controlled, values parameterized
            {"id": fa_id, "tenant_id": tenant_id, **values},
        )
        db.commit()
    updated = db.execute(text("SELECT * FROM einkauf_frachtauftraege WHERE id = :id"), {"id": fa_id}).mappings().first()
    return Frachtauftrag(**dict(updated))


@router.delete("/frachtauftraege/{fa_id}", status_code=204, response_class=Response, response_model=None, summary="Frachtauftrag löschen", dependencies=SCHREIBEN["EINKAUF"])
async def delete_frachtauftrag(fa_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    row = db.execute(text("SELECT id FROM einkauf_frachtauftraege WHERE id = :id AND tenant_id = :tenant_id"), {"id": fa_id, "tenant_id": tenant_id}).first()
    if not row:
        raise HTTPException(status_code=404, detail="Frachtauftrag not found")
    db.execute(text("DELETE FROM einkauf_frachtauftraege WHERE id = :id AND tenant_id = :tenant_id"), {"id": fa_id, "tenant_id": tenant_id})
    db.commit()
    return None


# ── Wareneingang buchen (Belegbruch: Einkauf-LS → Lager) ──────────────────

def _resolve_article_id(db: Session, tenant_id: str, artikel_nr: Optional[str]) -> Optional[str]:
    """Löst eine Positions-Artikelnummer auf articles.id auf — im Mandanten.

    Reihenfolge: exakte article_number im Artikelstamm, dann direkte id
    (Bestandstests übergeben teils bereits UUIDs in artikel_nr). Bis 07.10.2026
    ohne Mandant: die Nummer eines fremden Artikelstamms wurde eingelagert."""
    if not artikel_nr:
        return None
    row = db.execute(
        text("SELECT id FROM domain_inventory.articles WHERE tenant_id = :tid AND article_number = :nr LIMIT 1"),
        {"tid": tenant_id, "nr": artikel_nr},
    ).first()
    if row:
        return row[0]
    row = db.execute(
        text("SELECT id FROM domain_inventory.articles WHERE tenant_id = :tid AND id = :nr LIMIT 1"),
        {"tid": tenant_id, "nr": artikel_nr},
    ).first()
    return row[0] if row else None


def _referenz(lieferschein_nr: str) -> str:
    return f"LS-EK-{lieferschein_nr}"


def _ist_eingebucht(db: Session, tenant_id: str, lieferschein_nr: str) -> bool:
    """Gibt es schon Lagerbewegungen zu diesem Lieferschein? (die Tatsache, nicht ein Flag)"""
    return bool(db.execute(
        text("SELECT 1 FROM domain_inventory.inventory_stock_movements "
             "WHERE tenant_id = :tid AND reference_number = :ref LIMIT 1"),
        {"tid": tenant_id, "ref": _referenz(lieferschein_nr)},
    ).scalar())


class EinbuchenPayload(BaseModel):
    warehouse_id: str
    default_bin_id: Optional[str] = None
    unit_cost_override: Optional[Decimal] = None


class EinbuchenResult(BaseModel):
    lieferschein_id: str
    movements_created: int
    positions_skipped: int
    detail: list[dict]


# ── Bestellabgleich (Eingangslieferschein ↔ Einkaufsbestellung) ─────────────

class AbgleichPayload(BaseModel):
    bestellung_id: str


class AbgleichPosition(BaseModel):
    artikel_nr: str
    bezeichnung: Optional[str] = None
    menge_bestellt: float = 0.0
    menge_geliefert: float = 0.0
    differenz: float = 0.0
    status: str  # MATCH | UNTERLIEFERUNG | UEBERLIEFERUNG | UNBESTELLT | UNGELIEFERT


class AbgleichResult(BaseModel):
    lieferschein_id: str
    bestellung_id: str
    bestellnummer: Optional[str] = None
    positionen: list[AbgleichPosition]
    match: int
    abweichungen: int
    bestellung_status: str
