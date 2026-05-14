"""
Strecke – Streckengeschaefte CRUD
Drop-ship / pass-through trade management.
Persistenz: public.streckengeschaefte (M-11).
"""

from __future__ import annotations

import re
from decimal import Decimal
from datetime import date, datetime
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel
from sqlalchemy import desc, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.metrics import strecke_operations_total
from app.models.streckengeschaeft import Streckengeschaeft

router = APIRouter(prefix="/strecke/streckengeschaefte", tags=["Strecke"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class StreckengeschaeftBase(BaseModel):
    datum: str
    niederlassung: str = ""
    partie_nr: str = ""
    kostenstelle: str = ""
    lagerhalle: str = ""
    nls_nr: str = ""
    erledigt: bool = False
    lieferant_name: str = ""
    lieferant_nr: str = ""
    kontrakt_nr: str = ""
    artikel: str = ""
    netto: float = 0.0
    mwst: float = 0.0
    brutto: float = 0.0
    rechnungsnr: str = ""
    bediener: str = ""
    notiz: str = ""


class StreckengeschaeftCreate(StreckengeschaeftBase):
    pass


class StreckengeschaeftOut(StreckengeschaeftBase):
    id: str
    strecke_nr: str
    erstellt: str


class StreckengeschaeftUpdate(BaseModel):
    datum: Optional[str] = None
    niederlassung: Optional[str] = None
    partie_nr: Optional[str] = None
    kostenstelle: Optional[str] = None
    lagerhalle: Optional[str] = None
    nls_nr: Optional[str] = None
    erledigt: Optional[bool] = None
    lieferant_name: Optional[str] = None
    lieferant_nr: Optional[str] = None
    kontrakt_nr: Optional[str] = None
    artikel: Optional[str] = None
    netto: Optional[float] = None
    mwst: Optional[float] = None
    brutto: Optional[float] = None
    rechnungsnr: Optional[str] = None
    bediener: Optional[str] = None
    notiz: Optional[str] = None


# ---------------------------------------------------------------------------
# Hilfen
# ---------------------------------------------------------------------------


def _parse_datum(s: str) -> date:
    try:
        return date.fromisoformat(s[:10])
    except (TypeError, ValueError) as e:
        raise HTTPException(status_code=400, detail="Ungültiges Datum (erwartet YYYY-MM-DD)") from e


def _numeric_advisory_key(tenant_id: str, year: int) -> int:
    """Stabiler 31-bit Key für pg_advisory_xact_lock (Parallel-Inserts pro Tenant/Jahr serialisieren)."""
    h = hash(f"strecke:{tenant_id}:{year}") & 0x7FFF_FFFF
    return h if h != 0 else 1


def _next_strecke_nr(db: Session, tenant_id: str, fiscal_year: int | None = None) -> str:
    year = fiscal_year if fiscal_year is not None else datetime.now().year
    prefix = f"STR-{year}-"
    rows = (
        db.query(Streckengeschaeft.strecke_nr)
        .filter(
            Streckengeschaeft.tenant_id == tenant_id,
            Streckengeschaeft.strecke_nr.like(f"{prefix}%"),
        )
        .all()
    )
    escaped = re.escape(prefix)
    pat = re.compile(rf"^{escaped}(\d+)$")
    max_seq = 0
    for (nr,) in rows:
        if not nr:
            continue
        m = pat.match(nr)
        if m:
            max_seq = max(max_seq, int(m.group(1)))
    return f"{prefix}{max_seq + 1:04d}"


def _to_out(row: Streckengeschaeft) -> StreckengeschaeftOut:
    return StreckengeschaeftOut(
        id=row.id,
        strecke_nr=row.strecke_nr,
        datum=row.datum.isoformat() if row.datum else "",
        niederlassung=row.niederlassung or "",
        partie_nr=row.partie_nr or "",
        kostenstelle=row.kostenstelle or "",
        lagerhalle=row.lagerhalle or "",
        nls_nr=row.nls_nr or "",
        erledigt=bool(row.erledigt),
        lieferant_name=row.lieferant_name or "",
        lieferant_nr=row.lieferant_nr or "",
        kontrakt_nr=row.kontrakt_nr or "",
        artikel=row.artikel or "",
        netto=float(row.netto or 0),
        mwst=float(row.mwst or 0),
        brutto=float(row.brutto or 0),
        rechnungsnr=row.rechnungsnr or "",
        bediener=row.bediener or "",
        notiz=row.notiz or "",
        erstellt=row.erstellt.isoformat() if row.erstellt else "",
    )


def _get_row(db: Session, tenant_id: str, strecke_id: str) -> Streckengeschaeft | None:
    return (
        db.query(Streckengeschaeft)
        .filter(Streckengeschaeft.id == strecke_id, Streckengeschaeft.tenant_id == tenant_id)
        .first()
    )


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get("", response_model=list[StreckengeschaeftOut])
async def list_streckengeschaefte(
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=1000),
    erledigt: Optional[bool] = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Liste aller Streckengeschaefte für den Tenant."""
    try:
        q = db.query(Streckengeschaeft).filter(Streckengeschaeft.tenant_id == tenant_id)
        if erledigt is not None:
            q = q.filter(Streckengeschaeft.erledigt == erledigt)
        rows = q.order_by(desc(Streckengeschaeft.erstellt)).offset(skip).limit(limit).all()
        return [_to_out(r) for r in rows]
    except Exception:
        db.rollback()
        return []


@router.get("/{strecke_id}", response_model=StreckengeschaeftOut)
async def get_streckengeschaeft(
    strecke_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Einzelnes Streckengeschaeft laden."""
    row = _get_row(db, tenant_id, strecke_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Streckengeschaeft {strecke_id} nicht gefunden")
    return _to_out(row)


@router.post("", response_model=StreckengeschaeftOut, status_code=201)
async def create_streckengeschaeft(
    payload: StreckengeschaeftCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Neues Streckengeschaeft anlegen."""
    data = payload.model_dump()
    d = _parse_datum(data["datum"])
    fy = d.year
    db.execute(text("SELECT pg_advisory_xact_lock(:k)"), {"k": _numeric_advisory_key(tenant_id, fy)})
    strecke_nr = _next_strecke_nr(db, tenant_id, fiscal_year=fy)
    row = Streckengeschaeft(
        id=str(uuid4()),
        tenant_id=tenant_id,
        strecke_nr=strecke_nr,
        datum=d,
        niederlassung=data.get("niederlassung") or "",
        partie_nr=data.get("partie_nr") or "",
        kostenstelle=data.get("kostenstelle") or "",
        lagerhalle=data.get("lagerhalle") or "",
        nls_nr=data.get("nls_nr") or "",
        erledigt=bool(data.get("erledigt", False)),
        lieferant_name=data.get("lieferant_name") or "",
        lieferant_nr=data.get("lieferant_nr") or "",
        kontrakt_nr=data.get("kontrakt_nr") or "",
        artikel=data.get("artikel") or "",
        netto=Decimal(str(data.get("netto", 0))),
        mwst=Decimal(str(data.get("mwst", 0))),
        brutto=Decimal(str(data.get("brutto", 0))),
        rechnungsnr=data.get("rechnungsnr") or "",
        bediener=data.get("bediener") or "",
        notiz=data.get("notiz") or "",
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Konflikt beim Anlegen (Strecken-Nr.)")
    db.refresh(row)
    strecke_operations_total.labels(operation="create").inc()
    return _to_out(row)


@router.patch("/{strecke_id}", response_model=StreckengeschaeftOut)
async def update_streckengeschaeft(
    strecke_id: str,
    payload: StreckengeschaeftUpdate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Streckengeschaeft aktualisieren."""
    row = _get_row(db, tenant_id, strecke_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Streckengeschaeft {strecke_id} nicht gefunden")

    updates = payload.model_dump(exclude_unset=True)
    if "datum" in updates:
        row.datum = _parse_datum(updates.pop("datum"))
    for key in ("netto", "mwst", "brutto"):
        if key in updates:
            setattr(row, key, Decimal(str(updates.pop(key))))
    for key, val in updates.items():
        setattr(row, key, val)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Konflikt beim Aktualisieren")
    db.refresh(row)
    strecke_operations_total.labels(operation="update").inc()
    return _to_out(row)


@router.delete("/{strecke_id}", status_code=204, response_class=Response)
async def delete_streckengeschaeft(
    strecke_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Streckengeschaeft löschen."""
    row = _get_row(db, tenant_id, strecke_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Streckengeschaeft {strecke_id} nicht gefunden")
    db.delete(row)
    db.commit()
    return Response(status_code=204)


@router.post("/{strecke_id}/close", response_model=StreckengeschaeftOut)
async def close_streckengeschaeft(
    strecke_id: str,
    rechnungsnr: str = Query(..., description="Rechnungsnummer des Lieferanten"),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Schließt ein Streckengeschäft ab (setzt erledigt=True + Rechnungsnummer)."""
    row = _get_row(db, tenant_id, strecke_id)
    if not row:
        raise HTTPException(status_code=404, detail=f"Streckengeschaeft {strecke_id} nicht gefunden")
    if row.erledigt:
        raise HTTPException(status_code=400, detail="Streckengeschaeft ist bereits abgeschlossen")
    row.erledigt = True
    row.rechnungsnr = rechnungsnr
    db.commit()
    db.refresh(row)
    return StreckengeschaeftOut(
        id=str(row.id),
        strecke_nr=str(row.strecke_nr),
        erstellt=str(row.erstellt),
        datum=str(row.datum),
        niederlassung=row.niederlassung or "",
        partie_nr=row.partie_nr or "",
        kostenstelle=row.kostenstelle or "",
        lagerhalle=row.lagerhalle or "",
        nls_nr=row.nls_nr or "",
        erledigt=row.erledigt,
        lieferant_name=row.lieferant_name or "",
        lieferant_nr=row.lieferant_nr or "",
        kontrakt_nr=row.kontrakt_nr or "",
        artikel=row.artikel or "",
        netto=float(row.netto or 0),
        mwst=float(row.mwst or 0),
        brutto=float(row.brutto or 0),
        rechnungsnr=row.rechnungsnr or "",
        bediener=row.bediener or "",
        notiz=row.notiz or "",
    )
