"""EUDR — die zwei Richtungen zum EU-Informationssystem (Art. 33).

Hinaus: die eigene Erklaerung uebermitteln und Referenz- und
Verifizierungsnummer zurueckbekommen. Herein: eine **vorgelagerte** Erklaerung
anhand beider Nummern nachpruefen — die Richtung, die ein Haendler die meiste
Zeit braucht, weil er oefter Zwischenhaendler als Erst-Inverkehrbringer ist.

Beide Wege halten **das Ergebnis** fest und sagen nichts darueber, wer es
erzeugt hat: ein Dienst oder ein Mensch. Der Transport selbst gehoert in einen
eigenen Adapter.

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
    PRUEFQUELLEN,
    PRUEFUNG_STAENDE,
    PruefungIn,
    SorgfaltserklaerungOut,
    UEBERMITTLUNG_STAENDE,
    UMGEBUNGEN,
    UebermittlungIn,
    VorgelagertePruefungOut,
)

router = APIRouter(prefix="/eudr/sorgfaltserklaerungen", tags=["EUDR", "Compliance"])
logger = logging.getLogger(__name__)


# ── Anbindung an das EU-Informationssystem (Art. 33) ────────────────────────
#
# Zwei Richtungen, zwei Wege. Beide halten **das Ergebnis** fest und sagen
# nichts darueber, wer es erzeugt hat: ein Dienst oder ein Mensch. Der Transport
# selbst — Dienst, Fassung, Operationen, WS-Security-Zugangsdaten — gehoert in
# die Konfiguration und ist gegen die Beschreibung der Kommission zu pruefen.


@router.post(
    "/{erklaerung_id}/uebermittlung",
    response_model=SorgfaltserklaerungOut,
    summary="Ergebnis der Übermittlung festhalten (Art. 33, hinaus)",
)
def uebermittlung_festhalten(
    erklaerung_id: str,
    payload: UebermittlungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Haelt fest, was das EU-Informationssystem zurueckgemeldet hat.

    ``UEBERMITTELT`` verlangt eine Referenznummer, ``ABGEWIESEN`` einen Grund.
    Dieselben Bedingungen haelt die Datenbank.

    Uebermittelt wird nur, was fachlich abgegeben ist (Art. 4): Ein Entwurf
    gehoert nicht in das EU-System.
    """
    if payload.uebermittlung_status not in UEBERMITTLUNG_STAENDE:
        raise HTTPException(
            status_code=422,
            detail=f"Zustand muss einer von {', '.join(UEBERMITTLUNG_STAENDE)} sein",
        )
    erklaerung = dienst.erklaerung_holen(db, tenant_id, erklaerung_id)
    if payload.uebermittlung_status == "UEBERMITTELT":
        if erklaerung["status"] != "EINGEREICHT":
            raise HTTPException(
                status_code=409,
                detail=(
                    f"Erklaerung ist {erklaerung['status']}. Uebermittelt wird nur, "
                    "was fachlich abgegeben ist (Art. 4)."
                ),
            )
        if not (payload.referenznummer or erklaerung.get("referenznummer")):
            raise HTTPException(
                status_code=422,
                detail="Eine Uebermittlung ohne Referenznummer ist ein Versuch, keine Uebermittlung.",
            )
        umgebung = payload.umgebung or erklaerung.get("uebermittlung_umgebung")
        if umgebung not in UMGEBUNGEN:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Eine Uebermittlung braucht ihre Umgebung "
                    f"({' oder '.join(UMGEBUNGEN)}): Sonst ist nicht einzuordnen, ob "
                    "sie rechtlich gilt oder eine Probe war."
                ),
            )
    if payload.umgebung is not None and payload.umgebung not in UMGEBUNGEN:
        raise HTTPException(
            status_code=422,
            detail=f"Umgebung muss eine von {', '.join(UMGEBUNGEN)} sein",
        )
    if payload.uebermittlung_status == "ABGEWIESEN" and not (payload.fehler or "").strip():
        raise HTTPException(
            status_code=422,
            detail="Eine Abweisung ohne Grund hilft beim naechsten Versuch nicht.",
        )

    try:
        db.execute(
            text(
                f"UPDATE {dienst.ERKLAERUNGEN} SET "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "    uebermittlung_status = :zustand, "
                "    referenznummer = COALESCE(:ref, referenznummer), "
                "    verifizierungsnummer = COALESCE(:verif, verifizierungsnummer), "
                "    eu_system_id = COALESCE(:eu_id, eu_system_id), "
                "    uebermittlung_dienst = COALESCE(:dienst, uebermittlung_dienst), "
                "    uebermittlung_umgebung = COALESCE(:umgebung, uebermittlung_umgebung), "
                "    uebermittelt_am = CASE WHEN :zustand = 'UEBERMITTELT' "
                "                           THEN NOW() ELSE uebermittelt_am END, "
                "    uebermittlung_fehler = :fehler, "
                "    uebermittlung_versuche = uebermittlung_versuche + 1, "
                "    updated_at = NOW() "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {
                "zustand": payload.uebermittlung_status,
                "ref": payload.referenznummer,
                "verif": payload.verifizierungsnummer,
                "eu_id": payload.eu_system_id,
                "dienst": payload.dienst,
                "umgebung": payload.umgebung,
                "fehler": payload.fehler,
                "id": erklaerung_id,
                "tid": tenant_id,
            },
        )
        db.commit()
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"error": "Uebermittlung abgewiesen", "grund": str(fehler)},
        ) from fehler
    return dienst.erklaerung_holen(db, tenant_id, erklaerung_id)


@router.post(
    "/vorgelagerte/{vorgelagert_id}/pruefung",
    response_model=VorgelagertePruefungOut,
    summary="Vorgelagerte Erklärung prüfen (Art. 4/5, herein)",
)
def vorgelagerte_pruefung(
    vorgelagert_id: str,
    payload: PruefungIn,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> dict:
    """Haelt fest, ob eine **zugekaufte** Erklaerung nachgeprueft wurde.

    Das ist die Richtung, die ein Haendler die meiste Zeit braucht: Er ist
    oefter Zwischenhaendler als Erst-Inverkehrbringer und gibt fremde
    Referenznummern weiter. Bis hierhin trug das Register die Nummern, aber
    nichts darueber, ob sie jemand geprueft hat — eine abgeschriebene Nummer
    sah aus wie ein Nachweis.

    Eine Bestaetigung aus dem EU-Informationssystem setzt Referenz- **und**
    Verifizierungsnummer voraus: Abgefragt wird eine Erklaerung ueber beide.
    """
    if payload.pruefung_status not in PRUEFUNG_STAENDE:
        raise HTTPException(
            status_code=422,
            detail=f"Zustand muss einer von {', '.join(PRUEFUNG_STAENDE)} sein",
        )
    if payload.quelle not in PRUEFQUELLEN:
        raise HTTPException(
            status_code=422, detail=f"Quelle muss eine von {', '.join(PRUEFQUELLEN)} sein"
        )

    zeile = db.execute(
        text(
            "SELECT id, referenznummer, verifizierungsnummer "
            f"FROM {dienst.VORGELAGERT} WHERE id = :id AND tenant_id = :tid"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ),
        {"id": vorgelagert_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Vorgelagerte Erklaerung nicht gefunden")

    verif = payload.verifizierungsnummer or zeile["verifizierungsnummer"]
    if (
        payload.pruefung_status == "BESTAETIGT"
        and payload.quelle == "EU_INFORMATIONSSYSTEM"
        and not verif
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "Eine Bestaetigung aus dem EU-Informationssystem setzt die "
                "Verifizierungsnummer voraus — abgefragt wird ueber Referenz- und "
                "Verifizierungsnummer."
            ),
        )

    try:
        db.execute(
            text(
                f"UPDATE {dienst.VORGELAGERT} SET "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "    pruefung_status = :zustand, "
                "    verifizierungsnummer = COALESCE(:verif, verifizierungsnummer), "
                "    geprueft_am = CASE WHEN :zustand = 'UNGEPRUEFT' THEN NULL ELSE NOW() END, "
                "    pruefung_quelle = CASE WHEN :zustand = 'UNGEPRUEFT' THEN NULL ELSE :quelle END, "
                "    pruefung_hinweis = :hinweis "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {
                "zustand": payload.pruefung_status,
                "verif": payload.verifizierungsnummer,
                "quelle": payload.quelle,
                "hinweis": payload.hinweis,
                "id": vorgelagert_id,
                "tid": tenant_id,
            },
        )
        db.commit()
    except Exception as fehler:  # noqa: BLE001
        db.rollback()
        raise HTTPException(
            status_code=409, detail={"error": "Pruefung abgewiesen", "grund": str(fehler)}
        ) from fehler

    ergebnis = db.execute(
        text(
            "SELECT id, referenznummer, verifizierungsnummer, lieferant_name, "
            "       pruefung_status, geprueft_am, pruefung_quelle, pruefung_hinweis "
            f"FROM {dienst.VORGELAGERT} WHERE id = :id AND tenant_id = :tid"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ),
        {"id": vorgelagert_id, "tid": tenant_id},
    ).mappings().one()
    return {
        **dict(ergebnis),
        "geprueft_am": ergebnis["geprueft_am"].isoformat() if ergebnis["geprueft_am"] else None,
    }


@router.get(
    "/vorgelagerte/ungeprueft",
    response_model=list[VorgelagertePruefungOut],
    summary="Zugekaufte Erklärungen ohne Prüfung",
)
def ungepruefte_vorgelagerte(
    limit: int = Query(200, ge=1, le=1000),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
) -> list[dict]:
    """Die fremden Referenznummern, die noch niemand nachgeprueft hat."""
    try:
        zeilen = db.execute(
            text(
                "SELECT id, referenznummer, verifizierungsnummer, lieferant_name, "
                "       pruefung_status, geprueft_am, pruefung_quelle, pruefung_hinweis "
                f"FROM {dienst.VORGELAGERT} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
                "WHERE tenant_id = :tid AND pruefung_status <> 'BESTAETIGT' "
                "ORDER BY erfasst_am LIMIT :limit"
            ),
            {"tid": tenant_id, "limit": limit},
        ).mappings().all()
    except Exception as fehler:  # noqa: BLE001
        raise dienst.nicht_lesbar(db, fehler, "Vorgelagerte EUDR-Erklaerungen", tenant_id) from fehler
    return [
        {
            **dict(z),
            "geprueft_am": z["geprueft_am"].isoformat() if z["geprueft_am"] else None,
        }
        for z in zeilen
    ]
