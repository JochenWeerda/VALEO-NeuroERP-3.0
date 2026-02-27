"""
Feldbuch Service — Maßnahmen aus Lieferscheinen erzeugen, Import-Logik
"""
from __future__ import annotations

import csv
import io
from datetime import date, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.core.uuid7 import uuid7
from app.infrastructure.models.agrar_models import FeldbuchMassnahme, FeldbuchSchlag


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _get_or_create_schlag_by_name(
    db: Session,
    *,
    name: str,
    tenant_id: str,
    customer_id: str,
) -> FeldbuchSchlag:
    """Holt einen Schlag anhand seines Namens oder legt ihn neu an."""
    schlag = (
        db.query(FeldbuchSchlag)
        .filter(
            FeldbuchSchlag.tenant_id == tenant_id,
            FeldbuchSchlag.customer_id == customer_id,
            FeldbuchSchlag.name == name,
        )
        .first()
    )
    if schlag is None:
        schlag = FeldbuchSchlag(
            id=uuid7(),
            tenant_id=tenant_id,
            customer_id=customer_id,
            name=name,
            flaeche=0.0,
            status="aktiv",
            created_by=f"import:{customer_id}",
        )
        db.add(schlag)
        db.flush()
    return schlag


# ---------------------------------------------------------------------------
# From-Lieferschein
# ---------------------------------------------------------------------------

def create_massnahme_from_lieferschein(
    db: Session,
    *,
    lieferschein_id: str,
    lieferschein_datum: datetime,
    customer_id: str,
    schlag_id: str,
    artikel_name: str,
    menge: float,
    einheit: str,
    flaeche: float,
    anwender: str,
    tenant_id: str,
) -> FeldbuchMassnahme:
    """
    Wird aufgerufen, wenn ein Lieferschein mit PSM-Dienstleistung gedruckt/gebucht wird.
    Legt automatisch eine Feldbuch-Maßnahme an. Verhindert Duplikate via lieferschein_id.
    """
    # Duplikat-Schutz
    existing = (
        db.query(FeldbuchMassnahme)
        .filter(
            FeldbuchMassnahme.lieferschein_id == lieferschein_id,
            FeldbuchMassnahme.tenant_id == tenant_id,
        )
        .first()
    )
    if existing:
        return existing

    massnahme = FeldbuchMassnahme(
        id=uuid7(),
        tenant_id=tenant_id,
        schlag_id=schlag_id,
        customer_id=customer_id,
        datum=lieferschein_datum,
        typ="psm",
        bezeichnung=f"PSM-Ausbringung: {artikel_name}",
        mittel=artikel_name,
        menge=menge,
        einheit=einheit,
        flaeche=flaeche,
        anwender=anwender,
        quelle="erp_lieferschein",
        lieferschein_id=lieferschein_id,
        compliant=True,
    )
    db.add(massnahme)
    db.flush()
    return massnahme


# ---------------------------------------------------------------------------
# CSV-Import
# ---------------------------------------------------------------------------

# Bekannte Spaltenbezeichnungen (dt./engl.) → internes Feld
_COLUMN_MAP: dict[str, str] = {
    "schlag": "schlag_name",
    "feld": "schlag_name",
    "field": "schlag_name",
    "flik": "flik",
    "datum": "datum",
    "date": "datum",
    "maßnahme": "typ",
    "massnahme": "typ",
    "maßnahme-typ": "typ",
    "massnahme-typ": "typ",
    "measure": "typ",
    "typ": "typ",
    "type": "typ",
    "mittel": "mittel",
    "produkt": "mittel",
    "mittel/produkt": "mittel",
    "product": "mittel",
    "menge": "menge",
    "amount": "menge",
    "aufwandmenge": "menge",
    "einheit": "einheit",
    "unit": "einheit",
    "fläche": "flaeche",
    "flaeche": "flaeche",
    "fläche_ha": "flaeche",
    "flaeche_ha": "flaeche",
    "area": "flaeche",
    "area_ha": "flaeche",
    "anwender": "anwender",
    "operator": "anwender",
    "bemerkung": "bemerkung",
    "note": "bemerkung",
    "notes": "bemerkung",
    "comment": "bemerkung",
    "kultur": "kultur",
    "crop": "kultur",
}

_TYP_MAP: dict[str, str] = {
    "psm": "psm",
    "pflanzenschutz": "psm",
    "pflanzenschutzmittel": "psm",
    "herbizid": "psm",
    "fungizid": "psm",
    "insektizid": "psm",
    "düngung": "duengung",
    "duengung": "duengung",
    "dünger": "duengung",
    "duenger": "duengung",
    "fertilizer": "duengung",
    "aussaat": "aussaat",
    "sowing": "aussaat",
    "seeding": "aussaat",
    "ernte": "ernte",
    "harvest": "ernte",
    "bodenbearbeitung": "bodenbearbeitung",
    "tillage": "bodenbearbeitung",
    "soil": "bodenbearbeitung",
}


def import_csv(
    db: Session,
    *,
    file_content: bytes,
    tenant_id: str,
    customer_id: str,
) -> dict[str, Any]:
    """
    CSV-Import aus externer Ackerschlagkartei.
    Erkennt bekannte Spaltenbezeichnungen (dt./engl.).
    Erstellt Schläge wenn nicht vorhanden (by name).
    Erstellt Maßnahmen mit quelle='portal'.
    Gibt {created, updated, errors} zurück.
    """
    text = file_content.decode("utf-8-sig", errors="replace")
    # Semikolon oder Komma als Trennzeichen erkennen
    delimiter = ";" if ";" in text.split("\n")[0] else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

    created = 0
    errors: list[str] = []

    for row_num, row in enumerate(reader, start=2):
        # Normalisiere Keys
        normalized: dict[str, str] = {}
        for key, value in row.items():
            if key is None:
                continue
            mapped = _COLUMN_MAP.get(key.strip().lower().replace(" ", "_"))
            if mapped:
                normalized[mapped] = (value or "").strip()

        # Pflichtfeld: Datum
        datum_raw = normalized.get("datum", "")
        if not datum_raw:
            errors.append(f"Zeile {row_num}: Datum fehlt, Zeile übersprungen")
            continue

        try:
            # Verschiedene Datumsformate versuchen
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
                try:
                    parsed_date = datetime.strptime(datum_raw, fmt)
                    break
                except ValueError:
                    continue
            else:
                raise ValueError(f"Unbekanntes Datumsformat: {datum_raw}")
        except ValueError as e:
            errors.append(f"Zeile {row_num}: {e}")
            continue

        # Schlag ermitteln oder anlegen
        schlag_name = normalized.get("schlag_name", "").strip()
        if not schlag_name:
            errors.append(f"Zeile {row_num}: Schlag-Name fehlt, Zeile übersprungen")
            continue

        try:
            schlag = _get_or_create_schlag_by_name(
                db,
                name=schlag_name,
                tenant_id=tenant_id,
                customer_id=customer_id,
            )
            # Kultur aktualisieren wenn angegeben
            if normalized.get("kultur"):
                schlag.kultur = normalized["kultur"]
            if normalized.get("flik"):
                schlag.flik = normalized["flik"]
            if normalized.get("flaeche"):
                try:
                    schlag.flaeche = float(normalized["flaeche"].replace(",", "."))
                except ValueError:
                    pass
        except Exception as e:
            errors.append(f"Zeile {row_num}: Schlag-Fehler: {e}")
            continue

        # Typ normalisieren
        typ_raw = normalized.get("typ", "sonstiges").lower().strip()
        typ = _TYP_MAP.get(typ_raw, "sonstiges")

        # Menge / Fläche
        def _parse_float(s: str) -> float | None:
            if not s:
                return None
            try:
                return float(s.replace(",", "."))
            except ValueError:
                return None

        massnahme = FeldbuchMassnahme(
            id=uuid7(),
            tenant_id=tenant_id,
            schlag_id=schlag.id,
            customer_id=customer_id,
            datum=parsed_date,
            typ=typ,
            bezeichnung=normalized.get("mittel") or typ,
            mittel=normalized.get("mittel"),
            menge=_parse_float(normalized.get("menge", "")),
            einheit=normalized.get("einheit"),
            flaeche=_parse_float(normalized.get("flaeche", "")),
            anwender=normalized.get("anwender"),
            quelle="portal",
            bemerkung=normalized.get("bemerkung"),
            compliant=True,
        )
        db.add(massnahme)
        created += 1

    db.flush()
    return {"created": created, "updated": 0, "errors": errors}
