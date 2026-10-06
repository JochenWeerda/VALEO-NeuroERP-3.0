"""Bewerbermanagement — die Recruiting-Pipeline.

Herausgenommen aus `personal.py` am 06.10.2026 (Godfile-Ratsche). Die Zerlegung
hat den Code unveraendert uebernommen und die Maengel ausdruecklich benannt; der
Slice BEWERBERMANAGEMENT-ORDNUNG-20261006 behebt sie:

* ``except Exception: raise HTTPException(503, "applications table not available")``
  machte aus **jedem** Fehler eine Tabellenaussage — auch aus einem Rechtefehler
  oder einer verletzten Pruefbedingung. Jetzt deutet `fehler_deuten` den Fehler:
  eine fehlende Tabelle oder Spalte ist ein 503 mit Migrationshinweis, alles
  andere ein 409 mit dem Grund.
* Die Stufen waren ein ``set`` ohne Uebergaenge: Eine **abgelehnte** Bewerbung
  liess sich auf ``EINGESTELLT`` setzen. Jetzt gilt eine Uebergangstabelle, und
  `EINGESTELLT`/`ABGELEHNT` sind endgueltig.
* Eine Ablehnung braucht einen Grund (§ 22 AGG) — im Weg und in der Datenbank.
* Die Liste ist begrenzt, die Antwortmodelle sind typisiert, die Kennung ist
  `uuid7`.

Entscheidungen: ``docs/quality-assurance/bewerbermanagement-ordnung-20261006.md``.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session

from app.api.v1.schemas.personal_bewerbung_schemas import (
    BewerbungIn,
    BewerbungOut,
    StufeIn,
)
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services import bewerbung_service as dienst

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/personal", tags=["personal", "hr", "recruiting"])


@router.get("/applications", response_model=List[BewerbungOut],
            summary="Bewerbungen auflisten")
async def list_applications(
    status: Optional[str] = Query(None, description="EINGANG | VORAUSWAHL | … | ABGELEHNT"),
    position_id: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die Bewerbungen des Mandanten, optional nach Stufe oder Stelle gefiltert."""
    try:
        return dienst.auflisten(db, tenant_id, status, position_id, limit, offset)
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Bewerbungen lesen", tenant_id) from fehler


@router.post("/applications", status_code=201, response_model=BewerbungOut,
             summary="Bewerbung erfassen")
async def create_application(
    payload: BewerbungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Erfasst eine Bewerbung im Stand `EINGANG`."""
    try:
        ergebnis = dienst.anlegen(db, tenant_id, str(uuid7()), payload)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Bewerbung anlegen", tenant_id) from fehler
    return ergebnis


@router.get("/applications/{application_id}", response_model=BewerbungOut,
            summary="Bewerbung abrufen")
async def get_application(
    application_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    try:
        return dienst.als_dict(dienst.holen(db, tenant_id, application_id))
    except HTTPException:
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Bewerbung lesen", tenant_id) from fehler


@router.patch("/applications/{application_id}/stage", response_model=BewerbungOut,
              summary="Stufe wechseln")
async def update_application_stage(
    application_id: str,
    payload: StufeIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Wechselt die Pipelinestufe.

    `EINGESTELLT` und `ABGELEHNT` sind endgueltig; eine Ablehnung braucht einen
    Grund. Vorher pruefte der Weg nur, ob die Stufe **existiert** — eine abgelehnte
    Bewerbung liess sich damit einstellen.
    """
    try:
        ergebnis = dienst.stufe_setzen(
            db, tenant_id, application_id, payload.stage,
            note=payload.note,
            ablehnungsgrund=payload.ablehnungsgrund,
            entschieden_durch=payload.entschieden_durch,
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Stufenwechsel", tenant_id) from fehler
    return ergebnis


@router.delete(
    "/applications/{application_id}",
    status_code=204,
    response_class=Response,
    response_model=None,
    summary="Bewerbung löschen",
)
async def delete_application(
    application_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Löscht eine Bewerbung (nur eigener Mandant).

    Der Weg stammt von einem anderen Agenten (`f7fcbdd7c`) und bleibt in der Sache,
    wie er war; nur die Fehlerdeutung ist jetzt dieselbe wie bei den anderen Wegen.
    """
    try:
        dienst.loeschen(db, tenant_id, application_id)
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        raise dienst.fehler_deuten(db, fehler, "Bewerbung loeschen", tenant_id) from fehler
    return None
