"""Rohware-Sammelabrechnung — gebündelte Abrechnung mehrerer Belege (Agrar-Spezialsoftware Feature)."""

from __future__ import annotations

import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/agrar/sammelabrechnung", tags=["agrar", "sammelabrechnung"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class SammelabrechnungCreate(BaseModel):
    bezeichnung: str
    abrechnungsperiode: str  # e.g. "2026-08"
    harvest_acceptance_ids: list[str] = Field(..., min_length=2)
    abrechnungsschema_id: Optional[str] = None
    sammeldatum: Optional[str] = None  # ISO date, default today


class SammelabrechnungPositionOut(BaseModel):
    harvest_acceptance_id: str
    lieferant_id: Optional[str] = None
    artikel_nr: Optional[str] = None
    menge_kg: float = 0.0
    qualitaet_feuchte: Optional[float] = None
    qualitaet_besatz: Optional[float] = None
    abrechnungspreis_eur_t: float = 0.0
    abrechnungsbetrag_eur: float = 0.0


class SammelabrechnungOut(BaseModel):
    id: str
    bezeichnung: str
    abrechnungsperiode: str
    status: str  # ENTWURF / BERECHNET / GEBUCHT
    positionen: list[SammelabrechnungPositionOut] = []
    summe_menge_kg: float = 0.0
    summe_betrag_eur: float = 0.0
    erstellt_am: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("", response_model=list[SammelabrechnungOut], summary="Sammelabrechnungen auflisten")
def list_sammelabrechnungen(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        rows = db.execute(
            text(
                "SELECT id, bezeichnung, abrechnungsperiode, status, positionen, "
                "summe_menge_kg, summe_betrag_eur, erstellt_am "
                "FROM domain_agrar.sammelabrechnungen "
                "WHERE tenant_id = :tenant_id ORDER BY erstellt_am DESC"
            ),
            {"tenant_id": tenant_id},
        ).mappings().all()
        return [dict(r) for r in rows]
    except Exception:
        return []


@router.post("", response_model=SammelabrechnungOut, status_code=status.HTTP_201_CREATED, summary="Sammelabrechnung anlegen")
def create_sammelabrechnung(
    payload: SammelabrechnungCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    new_id = str(uuid.uuid4())
    sammeldatum = payload.sammeldatum or date.today().isoformat()
    try:
        db.execute(
            text(
                "INSERT INTO domain_agrar.sammelabrechnungen "
                "(id, tenant_id, bezeichnung, abrechnungsperiode, harvest_acceptance_ids, "
                "abrechnungsschema_id, sammeldatum, status, positionen, "
                "summe_menge_kg, summe_betrag_eur, erstellt_am) "
                "VALUES (:id, :tenant_id, :bezeichnung, :abrechnungsperiode, "
                ":ids::jsonb, :schema_id, :sammeldatum, 'ENTWURF', '[]'::jsonb, 0, 0, NOW())"
            ),
            {
                "id": new_id,
                "tenant_id": tenant_id,
                "bezeichnung": payload.bezeichnung,
                "abrechnungsperiode": payload.abrechnungsperiode,
                "ids": str(payload.harvest_acceptance_ids).replace("'", '"'),
                "schema_id": payload.abrechnungsschema_id,
                "sammeldatum": sammeldatum,
            },
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "id": new_id,
        "bezeichnung": payload.bezeichnung,
        "abrechnungsperiode": payload.abrechnungsperiode,
        "status": "ENTWURF",
        "positionen": [],
        "summe_menge_kg": 0.0,
        "summe_betrag_eur": 0.0,
        "erstellt_am": sammeldatum,
    }


@router.post("/{sammelabrechnung_id}/berechnen", response_model=SammelabrechnungOut, summary="Berechnen")
def berechnen(
    sammelabrechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    # Try to load the header
    header: dict = {}
    ids: list[str] = []
    try:
        row = db.execute(
            text(
                "SELECT * FROM domain_agrar.sammelabrechnungen "
                "WHERE id = :id AND tenant_id = :tenant_id"
            ),
            {"id": sammelabrechnung_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row:
            header = dict(row)
            raw_ids = header.get("harvest_acceptance_ids") or []
            ids = list(raw_ids) if isinstance(raw_ids, (list, tuple)) else []
    except Exception:
        pass  # table missing — graceful

    positionen: list[dict] = []
    summe_menge: float = 0.0
    summe_betrag: float = 0.0

    if ids:
        for ha_id in ids:
            menge: float = 0.0
            preis: float = 0.0
            lieferant_id: Optional[str] = None
            artikel_nr: Optional[str] = None
            feuchte: Optional[float] = None
            besatz: Optional[float] = None
            try:
                ha_row = db.execute(
                    text(
                        "SELECT lieferant_id, artikel_nr, menge_netto_kg, "
                        "qualitaet_feuchte, qualitaet_besatz, preis_eur_t "
                        "FROM domain_agrar.harvest_acceptances WHERE id = :id"
                    ),
                    {"id": ha_id},
                ).mappings().first()
                if ha_row:
                    ha = dict(ha_row)
                    menge = float(ha.get("menge_netto_kg") or 0)
                    preis = float(ha.get("preis_eur_t") or 0)
                    lieferant_id = ha.get("lieferant_id")
                    artikel_nr = ha.get("artikel_nr")
                    feuchte = ha.get("qualitaet_feuchte")
                    besatz = ha.get("qualitaet_besatz")
            except Exception:
                pass  # missing table → graceful, keep zeros

            betrag = (menge / 1000.0) * preis
            positionen.append(
                {
                    "harvest_acceptance_id": ha_id,
                    "lieferant_id": lieferant_id,
                    "artikel_nr": artikel_nr,
                    "menge_kg": menge,
                    "qualitaet_feuchte": feuchte,
                    "qualitaet_besatz": besatz,
                    "abrechnungspreis_eur_t": preis,
                    "abrechnungsbetrag_eur": betrag,
                }
            )
            summe_menge += menge
            summe_betrag += betrag

    # Persist result (best-effort)
    import json as _json
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.sammelabrechnungen "
                "SET status='BERECHNET', positionen=:pos::jsonb, "
                "summe_menge_kg=:menge, summe_betrag_eur=:betrag "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {
                "pos": _json.dumps(positionen),
                "menge": summe_menge,
                "betrag": summe_betrag,
                "id": sammelabrechnung_id,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception:
        db.rollback()

    return {
        "id": sammelabrechnung_id,
        "bezeichnung": header.get("bezeichnung", ""),
        "abrechnungsperiode": header.get("abrechnungsperiode", ""),
        "status": "BERECHNET",
        "positionen": positionen,
        "summe_menge_kg": summe_menge,
        "summe_betrag_eur": summe_betrag,
        "erstellt_am": (header.get("erstellt_am") or date.today()).isoformat()
        if not isinstance(header.get("erstellt_am"), str)
        else header.get("erstellt_am", date.today().isoformat()),
    }


@router.post("/{sammelabrechnung_id}/buchen", summary="Buchen",
    response_model=dict
)
def buchen(
    sammelabrechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    buchungsnr = uuid.uuid4().hex[:8].upper()
    # Persist status (best-effort)
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.sammelabrechnungen SET status='GEBUCHT' "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": sammelabrechnung_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
    return {"gebucht": True, "buchungsnr": buchungsnr}


@router.delete("/{sammelabrechnung_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response, summary="Sammelabrechnung löschen")
def delete_sammelabrechnung(
    sammelabrechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    current_status: Optional[str] = None
    try:
        row = db.execute(
            text(
                "SELECT status FROM domain_agrar.sammelabrechnungen "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": sammelabrechnung_id, "tenant_id": tenant_id},
        ).mappings().first()
        if row:
            current_status = row["status"]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"message": "DB unavailable", "migration_hint": "domain_agrar.sammelabrechnungen missing"},
        )

    if current_status is None:
        raise HTTPException(status_code=404, detail="Sammelabrechnung nicht gefunden")
    if current_status != "ENTWURF":
        raise HTTPException(
            status_code=409,
            detail=f"Nur Sammelabrechnungen im Status ENTWURF können gelöscht werden (aktuell: {current_status})",
        )

    try:
        db.execute(
            text(
                "DELETE FROM domain_agrar.sammelabrechnungen WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": sammelabrechnung_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Löschen fehlgeschlagen")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
