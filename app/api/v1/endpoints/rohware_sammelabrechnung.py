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

SAMMEL_RELATION = "domain_agrar.sammelabrechnungen"
HARVEST_RELATION = "domain_agrar.harvest_acceptances"
OP_RELATION = "domain_erp.offene_posten"
SAMMEL_MIGRATION = "alembic upgrade head (agrar_sammelabrechnungen_20260911)"
HARVEST_MIGRATION = "alembic upgrade head (agrar_harvest_acceptances_sammel_20260911)"


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

def _exc_message(exc: BaseException) -> str:
    orig = getattr(exc, "orig", None)
    return str(orig or exc)


def _looks_like_missing_relation(exc: BaseException, relation: str) -> bool:
    msg = _exc_message(exc).lower()
    short = relation.split(".")[-1].lower()
    return (
        "does not exist" in msg
        or "undefinedtable" in msg
        or "undefined column" in msg
    ) and (relation.lower() in msg or short in msg or "relation" in msg)


def _raise_db_error(
    exc: BaseException,
    *,
    relation: str,
    migration: str,
    fallback_message: str,
    status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
) -> None:
    cause = _exc_message(exc)
    detail: dict = {
        "message": fallback_message,
        "cause": cause,
    }
    if _looks_like_missing_relation(exc, relation):
        detail["migration_hint"] = f"{relation} missing — {migration}"
        detail["message"] = f"{relation} nicht verfügbar"
    raise HTTPException(status_code=status_code, detail=detail) from exc


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
        db.rollback()
        if _is_schema_error(exc):
            _raise_db_error(
                exc,
                relation=SAMMEL_RELATION,
                migration=SAMMEL_MIGRATION,
                fallback_message="Sammelabrechnung konnte nicht geladen werden",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Sammelabrechnung konnte nicht geladen werden",
                "cause": _exc_message(exc),
            },
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


def _load_harvest_row(db: Session, ha_id: str) -> dict:
    """Lädt eine Harvest-Annahme; Schemafehler und fehlende Zeilen fail-closed."""
    try:
        ha_row = db.execute(
            text(
                "SELECT lieferant_id, artikel_nr, menge_netto_kg, "
                "qualitaet_feuchte, qualitaet_besatz, preis_eur_t "
                "FROM domain_agrar.harvest_acceptances WHERE id = :id"
            ),
            {"id": ha_id},
        ).mappings().first()
    except Exception as exc:
        db.rollback()
        if _is_schema_error(exc):
            _raise_db_error(
                exc,
                relation=HARVEST_RELATION,
                migration=HARVEST_MIGRATION,
                fallback_message="Harvest-Annahmen können nicht gelesen werden",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Harvest-Annahme konnte nicht geladen werden",
                "cause": _exc_message(exc),
                "harvest_acceptance_id": ha_id,
            },
        ) from exc

    if not ha_row:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Harvest-Annahme nicht gefunden",
                "harvest_acceptance_id": ha_id,
            },
        )
    return dict(ha_row)


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
        db.rollback()
        if _is_schema_error(exc):
            _raise_db_error(
                exc,
                relation=SAMMEL_RELATION,
                migration=SAMMEL_MIGRATION,
                fallback_message="Sammelabrechnungen konnten nicht geladen werden",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Sammelabrechnungen konnten nicht geladen werden",
                "cause": _exc_message(exc),
            },
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
            _raise_db_error(
                exc,
                relation=SAMMEL_RELATION,
                migration=SAMMEL_MIGRATION,
                fallback_message="Sammelabrechnung konnte nicht angelegt werden",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Sammelabrechnung konnte nicht angelegt werden",
                "cause": _exc_message(exc),
            },
        ) from exc

    # Persistenz nachweisbar zurückgeben (keine erfundene 201 ohne DB-Zeile).
    return _to_out(_load_header(db, new_id, tenant_id))


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
    if len(ids) < 2:
        raise HTTPException(
            status_code=422,
            detail="Mindestens zwei Harvest-Annahmen erforderlich",
        )

    positionen: list[dict] = []
    summe_menge: float = 0.0
    summe_betrag: float = 0.0

    for ha_id in ids:
        ha = _load_harvest_row(db, str(ha_id))
        menge = float(ha.get("menge_netto_kg") or 0)
        preis = float(ha.get("preis_eur_t") or 0)
        betrag = (menge / 1000.0) * preis
        positionen.append(
            {
                "harvest_acceptance_id": str(ha_id),
                "lieferant_id": ha.get("lieferant_id"),
                "artikel_nr": ha.get("artikel_nr"),
                "menge_kg": menge,
                "qualitaet_feuchte": ha.get("qualitaet_feuchte"),
                "qualitaet_besatz": ha.get("qualitaet_besatz"),
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
            _raise_db_error(
                exc,
                relation=SAMMEL_RELATION,
                migration=SAMMEL_MIGRATION,
                fallback_message="Berechnung konnte nicht gespeichert werden",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Berechnung konnte nicht gespeichert werden",
                "cause": _exc_message(exc),
            },
        ) from exc

    return _to_out(_load_header(db, sammelabrechnung_id, tenant_id))


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
    """Bucht atomar: Status GEBUCHT und Kreditoren-OP in einer Transaktion.

    Bei Betrag > 0 ohne erfolgreiche OP-Anlage kein ``gebucht: true`` (Belegbruch).
    """
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

    betrag = float(header.get("summe_betrag_eur") or 0)
    buchungsnr = uuid.uuid4().hex[:8].upper()
    op_angelegt = False

    try:
        db.execute(
            text(
                "UPDATE domain_agrar.sammelabrechnungen SET status='GEBUCHT' "
                "WHERE id=:id AND tenant_id=:tenant_id"
            ),
            {"id": sammelabrechnung_id, "tenant_id": tenant_id},
        )

        if betrag > 0:
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
                    "betrag": betrag,
                    "lname": str(header.get("bezeichnung") or "Sammelabrechnung"),
                },
            )
            op_angelegt = True

        db.commit()
    except Exception as exc:
        db.rollback()
        if _is_schema_error(exc):
            relation = OP_RELATION if betrag > 0 else SAMMEL_RELATION
            migration = (
                "alembic upgrade head"
                if relation == OP_RELATION
                else SAMMEL_MIGRATION
            )
            _raise_db_error(
                exc,
                relation=relation,
                migration=migration,
                fallback_message="Buchung abgebrochen — Belegbruch (Status+OP) nicht geschlossen",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Buchung abgebrochen — Belegbruch (Status+OP) nicht geschlossen",
                "cause": _exc_message(exc),
            },
        ) from exc

    return {
        "gebucht": True,
        "buchungsnr": buchungsnr,
        "op_angelegt": op_angelegt,
        "betrag_eur": betrag,
    }


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
            _raise_db_error(
                exc,
                relation=SAMMEL_RELATION,
                migration=SAMMEL_MIGRATION,
                fallback_message="Löschen fehlgeschlagen",
            )
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Löschen fehlgeschlagen",
                "cause": _exc_message(exc),
            },
        ) from exc

    return Response(status_code=status.HTTP_204_NO_CONTENT)
