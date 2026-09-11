"""Rohware-Sammelabrechnung — gebündelte Abrechnung mehrerer Belege (Agrar-Spezialsoftware Feature)."""

from __future__ import annotations

import json
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, ConfigDict as _ConfigDict, Field
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.tenant import get_tenant_id


class RohwareSammelabrechnungOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter(prefix="/agrar/sammelabrechnung", tags=["agrar", "sammelabrechnung"])

MIGRATION_HINT = "domain_agrar.sammelabrechnungen missing — alembic upgrade head"


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
# Helpers
# ---------------------------------------------------------------------------

def _raise_db_unavailable() -> None:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={"message": "DB unavailable", "migration_hint": MIGRATION_HINT},
    )


def _is_schema_error(exc: BaseException) -> bool:
    return isinstance(exc, (OperationalError, ProgrammingError))


def _load_header(db: Session, sammelabrechnung_id: str, tenant_id: str) -> dict:
    try:
        row = db.execute(
            text(
                "SELECT * FROM domain_agrar.sammelabrechnungen "
                "WHERE id = :id AND tenant_id = :tenant_id"
            ),
            {"id": sammelabrechnung_id, "tenant_id": tenant_id},
        ).mappings().first()
    except Exception as exc:
        if _is_schema_error(exc):
            db.rollback()
            _raise_db_unavailable()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sammelabrechnung konnte nicht geladen werden",
        ) from exc

    if not row:
        raise HTTPException(status_code=404, detail="Sammelabrechnung nicht gefunden")
    return dict(row)


def _erstellt_am_iso(header: dict) -> str:
    value = header.get("erstellt_am")
    if isinstance(value, str):
        return value
    if value is None:
        return date.today().isoformat()
    return value.isoformat() if hasattr(value, "isoformat") else str(value)


def _to_out(row: dict) -> dict:
    positionen = row.get("positionen") or []
    if isinstance(positionen, str):
        try:
            positionen = json.loads(positionen)
        except json.JSONDecodeError:
            positionen = []
    return {
        "id": str(row.get("id")),
        "bezeichnung": row.get("bezeichnung") or "",
        "abrechnungsperiode": row.get("abrechnungsperiode") or "",
        "status": row.get("status") or "ENTWURF",
        "positionen": positionen if isinstance(positionen, list) else [],
        "summe_menge_kg": float(row.get("summe_menge_kg") or 0),
        "summe_betrag_eur": float(row.get("summe_betrag_eur") or 0),
        "erstellt_am": _erstellt_am_iso(row),
    }


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
        return [_to_out(dict(r)) for r in rows]
    except Exception as exc:
        if _is_schema_error(exc):
            db.rollback()
            _raise_db_unavailable()
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sammelabrechnungen konnten nicht geladen werden",
        ) from exc


@router.post(
    "",
    response_model=SammelabrechnungOut,
    status_code=status.HTTP_201_CREATED,
    summary="Sammelabrechnung anlegen",
)
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
                "CAST(:ids AS jsonb), :schema_id, :sammeldatum, 'ENTWURF', "
                "'[]'::jsonb, 0, 0, NOW())"
            ),
            {
                "id": new_id,
                "tenant_id": tenant_id,
                "bezeichnung": payload.bezeichnung,
                "abrechnungsperiode": payload.abrechnungsperiode,
                "ids": json.dumps(payload.harvest_acceptance_ids),
                "schema_id": payload.abrechnungsschema_id,
                "sammeldatum": sammeldatum,
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        if _is_schema_error(exc):
            _raise_db_unavailable()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Sammelabrechnung konnte nicht angelegt werden",
        ) from exc

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
    header = _load_header(db, sammelabrechnung_id, tenant_id)
    if header.get("status") == "GEBUCHT":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Gebuchte Sammelabrechnung kann nicht erneut berechnet werden",
        )

    raw_ids = header.get("harvest_acceptance_ids") or []
    if isinstance(raw_ids, str):
        try:
            raw_ids = json.loads(raw_ids)
        except json.JSONDecodeError:
            raw_ids = []
    ids = list(raw_ids) if isinstance(raw_ids, (list, tuple)) else []

    positionen: list[dict] = []
    summe_menge: float = 0.0
    summe_betrag: float = 0.0
    harvest_lookup_enabled = True

    for ha_id in ids:
        menge: float = 0.0
        preis: float = 0.0
        lieferant_id: Optional[str] = None
        artikel_nr: Optional[str] = None
        feuchte: Optional[float] = None
        besatz: Optional[float] = None
        if harvest_lookup_enabled:
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
            except Exception as exc:
                # Harvest-Tabelle optional. Postgres bricht die Tx nach Fehler ab —
                # Rollback, sonst schlaegt der nachfolgende UPDATE fehl.
                db.rollback()
                if _is_schema_error(exc):
                    harvest_lookup_enabled = False

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

    try:
        db.execute(
            text(
                "UPDATE domain_agrar.sammelabrechnungen "
                "SET status='BERECHNET', positionen=CAST(:pos AS jsonb), "
                "summe_menge_kg=:menge, summe_betrag_eur=:betrag "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {
                "pos": json.dumps(positionen),
                "menge": summe_menge,
                "betrag": summe_betrag,
                "id": sammelabrechnung_id,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        if _is_schema_error(exc):
            _raise_db_unavailable()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Berechnung konnte nicht gespeichert werden",
        ) from exc

    return {
        "id": sammelabrechnung_id,
        "bezeichnung": header.get("bezeichnung", ""),
        "abrechnungsperiode": header.get("abrechnungsperiode", ""),
        "status": "BERECHNET",
        "positionen": positionen,
        "summe_menge_kg": summe_menge,
        "summe_betrag_eur": summe_betrag,
        "erstellt_am": _erstellt_am_iso(header),
    }


@router.post(
    "/{sammelabrechnung_id}/buchen",
    summary="Buchen",
    response_model=RohwareSammelabrechnungOut,
)
def buchen(
    sammelabrechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    header = _load_header(db, sammelabrechnung_id, tenant_id)
    current_status = header.get("status")
    if current_status != "BERECHNET":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Nur berechnete Sammelabrechnungen können gebucht werden "
                f"(aktuell: {current_status})"
            ),
        )

    buchungsnr = uuid.uuid4().hex[:8].upper()
    try:
        db.execute(
            text(
                "UPDATE domain_agrar.sammelabrechnungen SET status='GEBUCHT' "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": sammelabrechnung_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        if _is_schema_error(exc):
            _raise_db_unavailable()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Buchung konnte nicht gespeichert werden",
        ) from exc

    # Kreditoren-OP (Belegbruch) — best-effort; Buchung selbst ist bereits persisted.
    betrag = header.get("summe_betrag_eur")
    if betrag and float(betrag) > 0:
        try:
            today = date.today().isoformat()
            due = date.today().replace(day=min(date.today().day + 30, 28)).isoformat()
            db.execute(
                text(
                    """
                    INSERT INTO domain_erp.offene_posten
                        (id, tenant_id, konto_typ, rechnungsnr, rechnungsdatum, datum, faelligkeit,
                         betrag, offen, lieferant_name, op_status)
                    VALUES (:id, :tid, 'kreditoren', :rnr, :rdat, :dat, :faell,
                            :betrag, :betrag, :lname, 'offen')
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "id": str(uuid.uuid4()),
                    "tid": tenant_id,
                    "rnr": buchungsnr,
                    "rdat": today,
                    "dat": today,
                    "faell": due,
                    "betrag": float(betrag),
                    "lname": str(header.get("bezeichnung") or "Sammelabrechnung"),
                },
            )
            db.commit()
        except Exception:
            db.rollback()

    return {"gebucht": True, "buchungsnr": buchungsnr}


@router.delete(
    "/{sammelabrechnung_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Sammelabrechnung löschen",
)
def delete_sammelabrechnung(
    sammelabrechnung_id: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> Response:
    header = _load_header(db, sammelabrechnung_id, tenant_id)
    current_status = header.get("status")
    if current_status != "ENTWURF":
        raise HTTPException(
            status_code=409,
            detail=(
                "Nur Sammelabrechnungen im Status ENTWURF können gelöscht werden "
                f"(aktuell: {current_status})"
            ),
        )

    try:
        db.execute(
            text(
                "DELETE FROM domain_agrar.sammelabrechnungen "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": sammelabrechnung_id, "tenant_id": tenant_id},
        )
        db.commit()
    except Exception as exc:
        db.rollback()
        if _is_schema_error(exc):
            _raise_db_unavailable()
        raise HTTPException(
            status_code=500,
            detail="Löschen fehlgeschlagen",
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
