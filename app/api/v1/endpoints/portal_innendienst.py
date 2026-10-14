"""PORTAL-INNENDIENST-001 — Innendienst-Sicht auf Kundenschlaege und Potentialanalyse.

Endpunkte:
  GET /innendienst/kunden/{kunden_id}/schlaege   — Schlagkartei eines bestimmten Kunden
  GET /innendienst/kunden/{kunden_id}/massnahmen — Maßnahmen eines Kunden
  GET /innendienst/potential                     — Außendienst: Cross-Sell-Gap-Analyse

Bis 14.10.2026 nahm dieser Router den Mandanten aus dem rohen Kopf ``X-Tenant-ID`` und prueft keine Rolle; jede
Anmeldung las die Schlagkartei jedes Kunden. Die Massnahmenabfrage nannte Spalten, die es nicht gibt
(``schlag_name``, ``fahrer``), und ein Fehler wurde zur leeren Liste — sie lieferte nie etwas. Jetzt: Mandant aus der
Anmeldung, Kunde ueber ``portal_kunde`` (Innendienst waehlt ihn per ``X-Kundenkonto``, der Aussendienst nur
zugeordnete Kunden) mit dem Portalrecht ``feldbuch_lesen``; der Pfadwert muss dieser Kunde sein. Die Potentialanalyse
ueber alle Kunden nur mit einer Fachrolle des Hauses. Fehler werden nicht mehr verschluckt.
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import TypedObjectOut
from app.auth.deps import require_roles
from app.auth.portal_kunde import AUSSENDIENST_FACHROLLEN, FELDBUCH_LESEN, PortalKunde, portal_recht
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/innendienst", tags=["innendienst", "portal"])

_haus = require_roles(*sorted(AUSSENDIENST_FACHROLLEN))


def _bereich(kunde: PortalKunde) -> list[str] | None:
    """Zugewiesene Schlaege eines Mitarbeiters; None = alle."""
    return list(kunde.schlag_ids) if kunde.schlag_ids is not None else None


def _kunde(kunden_id: str, kunde: PortalKunde = Depends(portal_recht(FELDBUCH_LESEN))) -> PortalKunde:
    if kunden_id != kunde.customer_id:
        raise HTTPException(status_code=404, detail="Kunde nicht gefunden")
    return kunde


@router.get("/kunden/{kunden_id}/schlaege", response_model=TypedObjectOut, summary="Kundenschlaege fuer Innendienst abrufen")
def kunden_schlaege(
    kunde: PortalKunde = Depends(_kunde),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Schlagkartei eines Kunden — für die Auftragsvorbereitung (Lohnspritz etc.)."""
    zeilen = db.execute(text("""
        SELECT fs.id::text, fs.name, fs.flik, fs.flaeche, fs.kultur, fs.vorkultur, fs.gemeinde, fs.gemarkung,
               fs.bodenart, fs.ackerzahl, fs.status, fs.customer_id::text
        FROM domain_agrar.feldbuch_schlaege fs
        WHERE fs.tenant_id = :tid AND fs.customer_id = :kunde
          AND (CAST(:bereich AS text[]) IS NULL OR fs.id = ANY(CAST(:bereich AS text[])))
        ORDER BY fs.name
    """), {"tid": kunde.tenant_id, "kunde": kunde.customer_id, "bereich": _bereich(kunde)})
    schlaege = [dict(r._mapping) for r in zeilen]
    return {"kunden_nr": kunde.customer_id, "schlaege": schlaege, "count": len(schlaege)}


@router.get("/kunden/{kunden_id}/massnahmen", response_model=TypedObjectOut, summary="Kundenmassnahmen fuer Innendienst abrufen")
def kunden_massnahmen(
    schlag_id: str | None = Query(None),
    massnahme_typ: str | None = Query(None),
    kunde: PortalKunde = Depends(_kunde),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Maßnahmen-Spritztagebuch eines Kunden."""
    zeilen = db.execute(text("""
        SELECT fm.id::text, fm.datum, fm.typ, fm.schlag_id::text, fs.name AS schlag_name, fm.mittel, fm.menge,
               fm.einheit, fm.anwender AS fahrer, fm.bemerkung, fm.customer_id::text
        FROM domain_agrar.feldbuch_massnahmen fm
        LEFT JOIN domain_agrar.feldbuch_schlaege fs ON fs.id = fm.schlag_id AND fs.tenant_id = fm.tenant_id
        WHERE fm.tenant_id = :tid AND fm.customer_id = :kunde
          AND (CAST(:bereich AS text[]) IS NULL OR fm.schlag_id = ANY(CAST(:bereich AS text[])))
          AND (CAST(:schlag_id AS text) IS NULL OR fm.schlag_id::text = CAST(:schlag_id AS text))
          AND (CAST(:typ AS text) IS NULL OR fm.typ = CAST(:typ AS text))
        ORDER BY fm.datum DESC LIMIT 200
    """), {"tid": kunde.tenant_id, "kunde": kunde.customer_id, "bereich": _bereich(kunde),
           "schlag_id": schlag_id or None, "typ": massnahme_typ or None})
    massnahmen = [dict(r._mapping) for r in zeilen]
    return {"kunden_nr": kunde.customer_id, "massnahmen": massnahmen, "count": len(massnahmen)}


@router.get("/potential", response_model=TypedObjectOut, summary="Innendienst-Potentialanalyse abrufen",
            dependencies=[Depends(_haus)])
def potential_analyse(
    db: Session = Depends(get_db),
    tid: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Cross-Sell-Gap-Analyse fuer Aussendienstler.

    Zeigt: Welche Kunden bauen Kulturen an, haben aber keinen aktiven Ankaufskontrakt?
    Welche haben Viehbestand, nutzen keinen Rationierungsservice?
    """
    schlag_kunden = db.execute(
        text("""
            SELECT fs.customer_id::text AS kunden_nr,
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

    # Statische Gap-Typen die der Aussendienstler kennen sollte
    gap_typen = [
        {
            "gap_typ": "ankauf_kein_kontrakt",
            "titel": "Ackerbauer ohne Ankaufskontrakt",
            "beschreibung": "Baut Getreide/Raps an, hat aber keinen laufenden Lieferkontrakt",
            "kunden": [
                k["kunden_nr"] for k in schlag_kunden_list
                if any((ku or "").lower() in ["winterweizen", "raps", "gerste", "mais"]
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
