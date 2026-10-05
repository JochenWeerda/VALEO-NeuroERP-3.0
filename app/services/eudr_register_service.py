"""EUDR-Register — die gemeinsame Mitte der drei Wege.

Hier stehen die Tabellennamen, die abgeleitete Chargenkennzeichnung und die
Helfer, die alle drei Router brauchen. Die Zerlegung folgt derselben Naht, die
eine spaetere Anbindung an das EU-Informationssystem braucht: Das Register
weiss, was gilt; die Chargenkennzeichnung verbindet Ware und Nachweis; die
Anbindung haelt fest, was das EU-System gemeldet hat.

Grundlage: Verordnung (EU) 2023/1115. Siehe
``docs/quality-assurance/eudr-sorgfaltserklaerung-20261001.md``.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.v1.schemas.eudr_register_schemas import (
    GeolokationIn,
    POLYGONGRENZE_HA,
)
from app.core.uuid7 import uuid7

logger = logging.getLogger(__name__)

ERKLAERUNGEN = "domain_compliance.eudr_due_diligence"
GEOLOKATIONEN = "domain_compliance.eudr_geolokationen"
VORGELAGERT = "domain_compliance.eudr_vorgelagerte_erklaerungen"
CHARGEN = "domain_inventory.inventory_lots"
BINDUNGEN = "domain_inventory.lot_eudr_erklaerungen"

#: Der abgeleitete Nachweisstand einer Charge. Nicht gespeichert: eine zweite
#: Wahrheit darueber waere eine, die von der ersten abweichen kann.
KENNZEICHNUNG = f"""
    SELECT l.id              AS lot_id,
           l.lot_number,
           l.article_id,
           l.tenant_id,
           l.eudr_relevant,
           l.current_qty     AS menge_kg,
           COALESCE(b.gedeckt, 0) AS gedeckte_menge_kg,
           COALESCE(b.erklaerungen, ARRAY[]::varchar[]) AS erklaerungen,
           CASE
               WHEN NOT l.eudr_relevant THEN 'NICHT_RELEVANT'
               WHEN COALESCE(b.gedeckt, 0) >= l.current_qty THEN 'NACHGEWIESEN'
               ELSE 'OFFEN'
           END AS kennzeichnung
    FROM {CHARGEN} l
    LEFT JOIN (
        SELECT lot_id,
               SUM(menge_kg) AS gedeckt,
               ARRAY_AGG(erklaerung_id ORDER BY verknuepft_am) AS erklaerungen
        FROM {BINDUNGEN}
        GROUP BY lot_id
    ) b ON b.lot_id = l.id
    WHERE l.tenant_id = :tid
"""

MIGRATIONS_HINWEIS = {
    "X-Migration-Hint": "Run: alembic upgrade head (eudr_sorgfaltserklaerung_20261001)"
}

FELDER = (
    "id, tenant_id, status, betreiber_name, betreiber_adresse, eori_nummer, "
    "rohstoff, hs_code, warenbeschreibung, menge_netto_kg, menge_volumen_m3, "
    "ergaenzende_einheit, produktionsland, produktion_von, produktion_bis, "
    "lieferant_name, lieferant_adresse, lieferant_email, "
    "nachweis_abholzungsfrei, nachweis_abholzungsfrei_quelle, "
    "nachweis_rechtskonform, nachweis_rechtskonform_quelle, "
    "risikostufe, risikobewertung_am, risikobewertung_durch, minderungsmassnahmen, "
    "erklaerung_abgegeben_am, erklaerung_durch_name, erklaerung_durch_funktion, "
    "referenznummer, verifizierungsnummer, eingereicht_am, "
    "uebermittlung_status, eu_system_id, uebermittelt_am, uebermittlung_versuche, "
    "uebermittlung_fehler, uebermittlung_dienst, uebermittlung_umgebung, created_at"
)

ZEITFELDER = (
    "produktion_von",
    "produktion_bis",
    "risikobewertung_am",
    "erklaerung_abgegeben_am",
    "eingereicht_am",
    "uebermittelt_am",
    "created_at",
)



def als_dict(row: Any) -> dict:
    """Eine Datenbankzeile als Abbildung mit ISO-Zeitpunkten."""
    d = dict(row)
    for schluessel in ZEITFELDER:
        wert = d.get(schluessel)
        if wert is not None and hasattr(wert, "isoformat"):
            d[schluessel] = wert.isoformat()
    for schluessel in ("menge_netto_kg", "menge_volumen_m3"):
        if d.get(schluessel) is not None:
            d[schluessel] = float(d[schluessel])
    return d


def nicht_lesbar(db: Session, fehler: Exception, was: str, tenant_id: str) -> HTTPException:
    """Ein Lesefehler ist keine leere Lage.

    Ein EUDR-Register, das bei einer Stoerung "nichts gefunden" antwortet, sagt
    einem Haus, es habe keine Nachweise zu fuehren. Nach Art. 3/4 ist das
    Inverkehrbringen ohne Sorgfaltserklaerung verboten.
    """
    db.rollback()
    logger.exception("%s nicht lesbar (Mandant %s)", was, tenant_id)
    return HTTPException(
        status_code=503,
        detail={"error": str(fehler), "migration_hint": MIGRATIONS_HINWEIS["X-Migration-Hint"]},
        headers=MIGRATIONS_HINWEIS,
    )


def erklaerung_holen(db: Session, tenant_id: str, erklaerung_id: str) -> dict:
    zeile = db.execute(
        text(f"SELECT {FELDER} FROM {ERKLAERUNGEN} WHERE id = :id AND tenant_id = :tid"),  # nosec B608  # reviewed-safe: FELDER und Tabellenname sind Code-Literale
        {"id": erklaerung_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Sorgfaltserklaerung nicht gefunden")
    return als_dict(zeile)


def geolokation_pruefen(ort: GeolokationIn) -> None:
    """Art. 9: Ab vier Hektar ist die Geolokation als Polygon anzugeben."""
    if ort.flaeche_ha is not None and ort.flaeche_ha > POLYGONGRENZE_HA and not ort.polygon:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Flurstueck mit {ort.flaeche_ha} ha: Ab {POLYGONGRENZE_HA} ha verlangt "
                "Art. 9 der Verordnung (EU) 2023/1115 ein Polygon, kein Punkt."
            ),
        )


def geolokation_schreiben(
    db: Session, tenant_id: str, erklaerung_id: str, ort: GeolokationIn
) -> str:
    import json

    neue_id = str(uuid7())
    db.execute(
        text(
            f"INSERT INTO {GEOLOKATIONEN} "  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
            "(id, tenant_id, erklaerung_id, flurstueck_kennung, breitengrad, "
            " laengengrad, flaeche_ha, polygon) "
            "VALUES (:id, :tid, :eid, :kennung, :breite, :laenge, :flaeche, "
            "        CAST(:polygon AS jsonb))"
        ),
        {
            "id": neue_id,
            "tid": tenant_id,
            "eid": erklaerung_id,
            "kennung": ort.flurstueck_kennung,
            "breite": ort.breitengrad,
            "laenge": ort.laengengrad,
            "flaeche": ort.flaeche_ha,
            "polygon": json.dumps(ort.polygon) if ort.polygon else None,
        },
    )
    return neue_id


def kennzeichnung(row: Any) -> dict:
    menge = float(row["menge_kg"] or 0)
    gedeckt = float(row["gedeckte_menge_kg"] or 0)
    return {
        "lot_id": row["lot_id"],
        "lot_number": row["lot_number"],
        "article_id": row["article_id"],
        "tenant_id": row["tenant_id"],
        "eudr_relevant": bool(row["eudr_relevant"]),
        "menge_kg": menge,
        "gedeckte_menge_kg": gedeckt,
        "offene_menge_kg": max(0.0, menge - gedeckt),
        "kennzeichnung": row["kennzeichnung"],
        "erklaerungen": list(row["erklaerungen"] or []),
    }


def charge_holen(db: Session, tenant_id: str, lot_id: str) -> dict:
    zeile = db.execute(
        text(
            "SELECT id, lot_number, tenant_id, eudr_relevant, current_qty "
            f"FROM {CHARGEN} WHERE id = :id AND tenant_id = :tid"  # nosec B608  # reviewed-safe: Tabellenname ist ein Code-Literal
        ),
        {"id": lot_id, "tid": tenant_id},
    ).mappings().first()
    if not zeile:
        raise HTTPException(status_code=404, detail="Charge nicht gefunden")
    return dict(zeile)
