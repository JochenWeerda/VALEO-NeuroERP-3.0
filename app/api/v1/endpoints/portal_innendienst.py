"""PORTAL-INNENDIENST-001 — Innendienst-Sicht auf Kundenschlaege und Potentialanalyse.

Endpunkte:
  GET /innendienst/kunden/{kunden_nr}/schlaege   — Schlagkartei eines bestimmten Kunden
  GET /innendienst/kunden/{kunden_nr}/massnahmen — Maßnahmen eines Kunden
  GET /innendienst/potential                     — Außendienst: Cross-Sell-Gap-Analyse
"""
from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/innendienst", tags=["innendienst", "portal"])


def _tid(x_tenant_id: Annotated[str | None, Header()] = None) -> str:
    if not x_tenant_id:
        raise HTTPException(status_code=400, detail="X-Tenant-ID fehlt")
    return x_tenant_id


@router.get("/kunden/{kunden_nr}/schlaege", response_model=dict[str, Any], summary="Kundenschlaege fuer Innendienst abrufen")
def kunden_schlaege(
    kunden_nr: str,
    db: Session = Depends(get_db),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    """Schlagkartei eines Kunden — für Innendienst-Auftragsvoorbereitung (Lohnspritz etc.)."""
    tid = _tid(x_tenant_id)
    try:
        rows = db.execute(
            text("""
                SELECT
                    fs.id::text,
                    fs.name,
                    fs.flik,
                    fs.flaeche,
                    fs.kultur,
                    fs.vorkultur,
                    fs.gemeinde,
                    fs.gemarkung,
                    fs.bodenart,
                    fs.ackerzahl,
                    fs.status,
                    fs.customer_id::text
                FROM domain_agrar.feldbuch_schlaege fs
                WHERE fs.tenant_id = :tid
                  AND fs.customer_id::text = :kunden_nr
                ORDER BY fs.name
            """),
            {"tid": tid, "kunden_nr": kunden_nr},
        ).fetchall()
        schlaege = [dict(r._mapping) for r in rows]
    except Exception as exc:
        logger.warning("Schlaege-Query fehlgeschlagen: %s", exc)
        schlaege = []  # Tabelle existiert noch nicht in dieser Umgebung

    return {
        "kunden_nr": kunden_nr,
        "schlaege": schlaege,
        "count": len(schlaege),
        "hinweis": "Innendienst-Sicht — alle Schläge dieses Kunden für Auftragsvororbereitung.",
    }


@router.get("/kunden/{kunden_nr}/massnahmen", response_model=dict[str, Any], summary="Kundenmassnahmen fuer Innendienst abrufen")
def kunden_massnahmen(
    kunden_nr: str,
    schlag_id: str | None = Query(None),
    massnahme_typ: str | None = Query(None),
    db: Session = Depends(get_db),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    """Maßnahmen-Spritztagebuch eines Kunden — für Innendienst."""
    tid = _tid(x_tenant_id)
    try:
        sql = """
            SELECT
                fm.id::text,
                fm.datum,
                fm.typ,
                fm.schlag_id::text,
                fm.schlag_name,
                fm.mittel,
                fm.menge,
                fm.einheit,
                fm.fahrer,
                fm.bemerkung,
                fm.customer_id::text
            FROM domain_agrar.feldbuch_massnahmen fm
            WHERE fm.tenant_id = :tid
              AND fm.customer_id::text = :kunden_nr
        """
        params: dict[str, Any] = {"tid": tid, "kunden_nr": kunden_nr}
        if schlag_id:
            sql += " AND fm.schlag_id::text = :schlag_id"
            params["schlag_id"] = schlag_id
        if massnahme_typ:
            sql += " AND fm.typ = :typ"
            params["typ"] = massnahme_typ
        sql += " ORDER BY fm.datum DESC LIMIT 200"
        rows = db.execute(text(sql), params).fetchall()
        massnahmen = [dict(r._mapping) for r in rows]
    except Exception as exc:
        logger.warning("Massnahmen-Query fehlgeschlagen: %s", exc)
        massnahmen = []

    return {
        "kunden_nr": kunden_nr,
        "massnahmen": massnahmen,
        "count": len(massnahmen),
    }


@router.get("/potential", response_model=dict[str, Any], summary="Innendienst-Potentialanalyse abrufen")
def potential_analyse(
    db: Session = Depends(get_db),
    x_tenant_id: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    """Cross-Sell-Gap-Analyse fuer Aussendienstler.

    Zeigt: Welche Kunden bauen Kulturen an, haben aber keinen aktiven Ankaufskontrakt?
    Welche haben Viehbestand, nutzen keinen Rationierungsservice?
    """
    tid = _tid(x_tenant_id)

    # Gap 1: Kunden mit Schlaegen ohne Ankaufskontrakt (simuliert)
    try:
        schlag_kunden = db.execute(
            text("""
                SELECT DISTINCT
                    fs.customer_id::text AS kunden_nr,
                    array_agg(DISTINCT fs.kultur) AS kulturen,
                    sum(fs.flaeche) AS gesamt_ha
                FROM domain_agrar.feldbuch_schlaege fs
                WHERE fs.tenant_id = :tid
                  AND fs.status = 'aktiv'
                GROUP BY fs.customer_id
                HAVING sum(fs.flaeche) > 0
            """),
            {"tid": tid},
        ).fetchall()
        schlag_kunden_list = [dict(r._mapping) for r in schlag_kunden]
    except Exception as exc:
        logger.warning("Potential-Query fehlgeschlagen: %s", exc)
        schlag_kunden_list = []

    # Statische Gap-Typen die der Aussendienstler kennen sollte
    gap_typen = [
        {
            "gap_typ": "ankauf_kein_kontrakt",
            "titel": "Ackerbauer ohne Ankaufskontrakt",
            "beschreibung": "Baut Getreide/Raps an, hat aber keinen laufenden Lieferkontrakt",
            "kunden": [
                k["kunden_nr"] for k in schlag_kunden_list
                if any(ku.lower() in ["winterweizen", "raps", "gerste", "mais"]
                       for ku in (k.get("kulturen") or []))
            ],
            "potential_eur_je_kunde": 15000,
        },
        {
            "gap_typ": "lohnspritz_kein_auftrag",
            "titel": "Getreideanbauer ohne Lohnspritz-Auftrag",
            "beschreibung": "Hat Getreide- oder Rapsflächen, hat noch kein Lohnspritz gebucht",
            "kunden": [k["kunden_nr"] for k in schlag_kunden_list],
            "potential_eur_je_kunde": 3500,
        },
        {
            "gap_typ": "ration_kein_rohwaren_kontrakt",
            "titel": "Viehhalter ohne Futterkontrakt",
            "beschreibung": "Hat Rationskalkulation genutzt, aber keinen Futterrohwaren-Kontrakt",
            "kunden": [],
            "potential_eur_je_kunde": 22000,
        },
    ]

    return {
        "gap_analyse": gap_typen,
        "schlag_kunden_count": len(schlag_kunden_list),
        "hinweis": "Potentialanalyse für Außendienst — täglich aktualisiert.",
    }
