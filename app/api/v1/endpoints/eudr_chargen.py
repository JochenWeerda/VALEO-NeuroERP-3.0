"""EUDR-Chargenkennzeichnung — welche Erklaerung deckt diese Charge?

Art. 4 verbietet das Inverkehrbringen ohne Sorgfaltserklaerung. Im Landhandel
wird verschnitten, deshalb eine Verbindung **mit Menge** statt einer Spalte:
Eine Silocharge kann von mehreren Erklaerungen gedeckt sein. Der Nachweisstand
ist **abgeleitet**, nicht gespeichert.

Grundlage: Verordnung (EU) 2023/1115. Entscheidung und Beweislage:
``docs/quality-assurance/eudr-sorgfaltserklaerung-20261001.md``.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services import eudr_register_service as dienst

from app.api.v1.schemas.eudr_register_schemas import (
    ChargeKennzeichnungOut,
    ChargenbindungIn,
    ChargenbindungOut,
)

router = APIRouter(prefix="/eudr/sorgfaltserklaerungen", tags=["EUDR", "Compliance"])
logger = logging.getLogger(__name__)


# ── Chargenbezogene Kennzeichnung (Art. 4) ──────────────────────────────────


@router.post(
    "/{erklaerung_id}/chargen",
    response_model=ChargenbindungOut,
    status_code=http_status.HTTP_201_CREATED,
    summary="Charge an die Erklärung binden (Art. 4)",
)
def charge_binden(
    erklaerung_id: str,
    payload: ChargenbindungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Bindet eine Charge mit einer Menge an diese Sorgfaltserklaerung.

    Gebunden wird nur an eine **eingereichte** Erklaerung: Nach Art. 4 darf
    nichts in Verkehr gebracht werden, bevor die Erklaerung abgegeben ist, und
    eine Bindung an einen Entwurf waere ein Nachweis, der noch keiner ist.

    Die gebundene Menge darf die Chargenmenge nicht uebersteigen — sonst wuerde
    mehr Ware als nachgewiesen gelten.
    """
    erklaerung = dienst.erklaerung_holen(db, tenant_id, erklaerung_id)
    if erklaerung["status"] != "EINGEREICHT":
        raise HTTPException(
            status_code=409,
            detail=(
                f"Erklaerung ist {erklaerung['status']}. Gebunden wird nur an eine "
                "eingereichte Erklaerung (Art. 4 Verordnung (EU) 2023/1115)."
            ),
        )

    charge = dienst.charge_holen(db, tenant_id, payload.lot_id)
    if not charge["eudr_relevant"]:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Charge {charge['lot_number']} ist nicht als EUDR-relevant "
                "gekennzeichnet. Erst kennzeichnen, dann nachweisen."
            ),
        )

    try:
        bereits = db.execute(
            text(
                "SELECT COALESCE(SUM(menge_kg), 0) AS gedeckt "
                f"FROM {dienst.BINDUNGEN} WHERE lot_id = :lot AND tenant_id = :tid"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            ),
            {"lot": payload.lot_id, "tid": tenant_id},
        ).scalar() or 0
        menge = float(charge["current_qty"] or 0)
        if float(bereits) + payload.menge_kg > menge + 1e-6:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Charge fuehrt {menge:.3f} kg, davon sind {float(bereits):.3f} kg "
                    f"bereits nachgewiesen. {payload.menge_kg:.3f} kg wuerden die "
                    "Chargenmenge uebersteigen."
                ),
            )

        neue_id = str(uuid7())
        db.execute(
            text(
                f"INSERT INTO {dienst.BINDUNGEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "(id, tenant_id, lot_id, erklaerung_id, menge_kg, verknuepft_durch) "
                "VALUES (:id, :tid, :lot, :eid, :menge, :durch)"
            ),
            {
                "id": neue_id,
                "tid": tenant_id,
                "lot": payload.lot_id,
                "eid": erklaerung_id,
                "menge": payload.menge_kg,
                "durch": payload.verknuepft_durch,
            },
        )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        # Die Eindeutigkeit je Charge und Erklaerung haelt die Datenbank.
        raise HTTPException(
            status_code=409,
            detail={"error": "Bindung abgewiesen", "grund": str(fehler)},
        ) from fehler

    return {
        "id": neue_id,
        "lot_id": payload.lot_id,
        "lot_number": charge["lot_number"],
        "erklaerung_id": erklaerung_id,
        "menge_kg": payload.menge_kg,
        "verknuepft_durch": payload.verknuepft_durch,
    }


@router.get(
    "/chargen/offen",
    response_model=list[ChargeKennzeichnungOut],
    summary="Chargen ohne Nachweis (nicht verkehrsfähig)",
)
def offene_chargen(
    limit: int = Query(200, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die Chargen, die nach Art. 4 **nicht** in Verkehr gebracht werden duerfen.

    Relevant gekennzeichnet, aber ohne — oder ohne ausreichenden — Nachweis.
    """
    try:
        zeilen = db.execute(
            text(
                f"SELECT * FROM ({dienst.KENNZEICHNUNG}) k "  # nosec B608  # reviewed-safe: dienst.KENNZEICHNUNG ist ein Code-Literal, Werte sind gebunden
                "WHERE k.kennzeichnung = 'OFFEN' "
                "ORDER BY (k.menge_kg - k.gedeckte_menge_kg) DESC LIMIT :limit"
            ),
            {"tid": tenant_id, "limit": limit},
        ).mappings().fetchmany(limit)
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Offene EUDR-Chargen", tenant_id) from fehler
    return [dienst.kennzeichnung(z) for z in zeilen]


@router.get(
    "/chargen/{lot_id}",
    response_model=ChargeKennzeichnungOut,
    summary="Nachweisstand einer Charge",
)
def charge_kennzeichnung(
    lot_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Der abgeleitete Nachweisstand einer einzelnen Charge."""
    try:
        zeile = db.execute(
            text(
                f"SELECT * FROM ({dienst.KENNZEICHNUNG}) k WHERE k.lot_id = :lot"  # nosec B608  # reviewed-safe: dienst.KENNZEICHNUNG ist ein Code-Literal, Werte sind gebunden
            ),
            {"tid": tenant_id, "lot": lot_id},
        ).mappings().first()
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "EUDR-Chargenkennzeichnung", tenant_id) from fehler
    if not zeile:
        raise HTTPException(status_code=404, detail="Charge nicht gefunden")
    return dienst.kennzeichnung(zeile)

