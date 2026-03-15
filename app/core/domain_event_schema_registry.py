"""
Domain Event Schema Registry — Wave 42
Zentrales Verzeichnis für Domain-Event-Schemata mit Payload-Validierung,
Versionierung und Kompatibilitätsprüfung zwischen Schema-Versionen.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class EventSchemaStatus(str, Enum):
    ENTWURF = "ENTWURF"
    AKTIV = "AKTIV"
    VERALTET = "VERALTET"
    ARCHIVIERT = "ARCHIVIERT"


class KompatibilitaetsTyp(str, Enum):
    VOLL = "VOLL"                # Identische Feldmengen
    ERWEITERUNG = "ERWEITERUNG"  # Neue Felder, keine entfernt (rückwärtskompatibel)
    BREAKING = "BREAKING"        # Felder entfernt oder Pflichtfelder geändert
    UNBEKANNT = "UNBEKANNT"      # Kann nicht klassifiziert werden


# ---------------------------------------------------------------------------
# Event-Schema-Eintrag
# ---------------------------------------------------------------------------

@dataclass
class EventSchemaEintrag:
    """Versioniertes Schema für einen Domain-Event-Typ."""
    schema_id: str
    event_typ: str           # z.B. "kontrakt.erstellt", "wiegeschein.erfasst"
    version: str             # Semver: "1.0.0"
    status: EventSchemaStatus
    payload_felder: list[str] = field(default_factory=list)   # Alle Felder
    pflicht_felder: list[str] = field(default_factory=list)   # Pflichtfelder
    erstellt_am: datetime = field(default_factory=datetime.utcnow)
    tenant_id: str = ""      # "" = global
    beschreibung: str = ""

    @property
    def versions_hash(self) -> str:
        """SHA256[:12] über schema_id + event_typ + version + sortierte payload_felder."""
        payload = json.dumps({
            "schema_id": self.schema_id,
            "event_typ": self.event_typ,
            "version": self.version,
            "payload_felder": sorted(self.payload_felder),
        }, sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()[:12]

    @property
    def ist_aktiv(self) -> bool:
        return self.status == EventSchemaStatus.AKTIV

    def validiere_payload(self, payload: dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Prüft ob alle Pflichtfelder im Payload vorhanden sind.

        Returns:
            (gueltig, fehlende_felder)
        """
        fehlend = [f for f in self.pflicht_felder if f not in payload]
        return len(fehlend) == 0, fehlend

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_id": self.schema_id,
            "event_typ": self.event_typ,
            "version": self.version,
            "status": self.status.value,
            "payload_felder": self.payload_felder,
            "pflicht_felder": self.pflicht_felder,
            "feld_anzahl": len(self.payload_felder),
            "pflicht_anzahl": len(self.pflicht_felder),
            "versions_hash": self.versions_hash,
            "ist_aktiv": self.ist_aktiv,
            "erstellt_am": self.erstellt_am.isoformat(),
            "tenant_id": self.tenant_id,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Kompatibilitätsprüfung
# ---------------------------------------------------------------------------

@dataclass
class KompatibilitaetsPruefung:
    """Ergebnis der Kompatibilitätsprüfung zwischen zwei Schema-Versionen."""
    von_schema_id: str
    zu_schema_id: str
    kompatibilitaets_typ: KompatibilitaetsTyp
    fehlende_felder: list[str] = field(default_factory=list)   # In zu entfernte Felder
    neue_felder: list[str] = field(default_factory=list)        # In zu hinzugefügte Felder
    nachrichten: list[str] = field(default_factory=list)

    @property
    def ist_kompatibel(self) -> bool:
        return self.kompatibilitaets_typ in {
            KompatibilitaetsTyp.VOLL,
            KompatibilitaetsTyp.ERWEITERUNG,
        }

    def as_dict(self) -> dict[str, Any]:
        return {
            "von_schema_id": self.von_schema_id,
            "zu_schema_id": self.zu_schema_id,
            "kompatibilitaets_typ": self.kompatibilitaets_typ.value,
            "fehlende_felder": self.fehlende_felder,
            "neue_felder": self.neue_felder,
            "nachrichten": self.nachrichten,
            "ist_kompatibel": self.ist_kompatibel,
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def pruefe_schema_kompatibilitaet(
    von: EventSchemaEintrag,
    zu: EventSchemaEintrag,
) -> KompatibilitaetsPruefung:
    """
    Prüft die Kompatibilität zwischen zwei Schema-Versionen.

    Logik:
    - VOLL: payload_felder-Mengen sind gleich
    - ERWEITERUNG: zu enthält alle Felder von von (+ neue) — rückwärtskompatibel
    - BREAKING: von enthält Felder, die in zu fehlen (Consumer würde brechen)
    """
    von_felder = set(von.payload_felder)
    zu_felder = set(zu.payload_felder)

    fehlend = sorted(von_felder - zu_felder)   # In zu entfernt
    neu = sorted(zu_felder - von_felder)        # In zu hinzugefügt

    if von_felder == zu_felder:
        typ = KompatibilitaetsTyp.VOLL
        nachrichten = ["Schemata sind vollständig kompatibel — identische Feldmenge."]
    elif not fehlend:
        typ = KompatibilitaetsTyp.ERWEITERUNG
        nachrichten = [
            f"Schema erweitert um {len(neu)} Feld(er): {', '.join(neu)}. Rückwärtskompatibel."
        ]
    else:
        typ = KompatibilitaetsTyp.BREAKING
        nachrichten = [
            f"BREAKING: {len(fehlend)} Feld(er) entfernt: {', '.join(fehlend)}."
        ]
        if neu:
            nachrichten.append(f"Zusätzlich {len(neu)} neue Felder: {', '.join(neu)}.")

    return KompatibilitaetsPruefung(
        von_schema_id=von.schema_id,
        zu_schema_id=zu.schema_id,
        kompatibilitaets_typ=typ,
        fehlende_felder=fehlend,
        neue_felder=neu,
        nachrichten=nachrichten,
    )


def finde_aktives_schema(
    event_typ: str,
    schemata: list[EventSchemaEintrag],
    tenant_id: str = "",
) -> EventSchemaEintrag | None:
    """
    Gibt das aktive Schema für einen Event-Typ zurück.
    Tenant-spezifisch hat Vorrang vor global; max(version) gewinnt.
    """
    if tenant_id:
        tenant_aktiv = [
            s for s in schemata
            if s.event_typ == event_typ
            and s.status == EventSchemaStatus.AKTIV
            and s.tenant_id == tenant_id
        ]
        if tenant_aktiv:
            return max(tenant_aktiv, key=lambda s: s.version)

    global_aktiv = [
        s for s in schemata
        if s.event_typ == event_typ
        and s.status == EventSchemaStatus.AKTIV
        and s.tenant_id == ""
    ]
    if global_aktiv:
        return max(global_aktiv, key=lambda s: s.version)

    return None


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_event_schemas() -> list[EventSchemaEintrag]:
    """Gibt 6 Standard-Event-Schemata zurück."""
    basis = datetime(2026, 1, 1)
    return [
        EventSchemaEintrag(
            schema_id="ES-001",
            event_typ="kontrakt.erstellt",
            version="1.0.0",
            status=EventSchemaStatus.VERALTET,
            payload_felder=["kontrakt_id", "lieferant_id", "datum", "menge_t"],
            pflicht_felder=["kontrakt_id", "lieferant_id", "datum"],
            erstellt_am=basis,
            beschreibung="Kontrakt-Erstellt v1 (Basis)",
        ),
        EventSchemaEintrag(
            schema_id="ES-002",
            event_typ="kontrakt.erstellt",
            version="2.0.0",
            status=EventSchemaStatus.AKTIV,
            payload_felder=["kontrakt_id", "lieferant_id", "datum", "menge_t", "qualitaet", "preis_je_t"],
            pflicht_felder=["kontrakt_id", "lieferant_id", "datum", "menge_t"],
            erstellt_am=datetime(2026, 2, 1),
            beschreibung="Kontrakt-Erstellt v2 mit Qualität und Preis",
        ),
        EventSchemaEintrag(
            schema_id="ES-003",
            event_typ="wiegeschein.erfasst",
            version="1.0.0",
            status=EventSchemaStatus.AKTIV,
            payload_felder=["wiegeschein_id", "kontrakt_id", "brutto_kg", "tara_kg", "netto_kg", "zeitstempel"],
            pflicht_felder=["wiegeschein_id", "kontrakt_id", "brutto_kg", "tara_kg"],
            erstellt_am=datetime(2026, 1, 15),
            beschreibung="Wiegeschein-Erfassung Standard",
        ),
        EventSchemaEintrag(
            schema_id="ES-004",
            event_typ="settlement.freigegeben",
            version="1.0.0",
            status=EventSchemaStatus.AKTIV,
            payload_felder=["settlement_id", "kontrakt_id", "betrag_eur", "freigeber_id", "freigabe_datum"],
            pflicht_felder=["settlement_id", "kontrakt_id", "betrag_eur", "freigeber_id"],
            erstellt_am=datetime(2026, 1, 20),
            beschreibung="Settlement-Freigabe 4-Augen",
        ),
        EventSchemaEintrag(
            schema_id="ES-005",
            event_typ="ap_rechnung.eingegangen",
            version="1.0.0",
            status=EventSchemaStatus.AKTIV,
            payload_felder=["rechnung_id", "lieferant_id", "betrag_eur", "faellig_am", "kostenstelle"],
            pflicht_felder=["rechnung_id", "lieferant_id", "betrag_eur"],
            erstellt_am=datetime(2026, 2, 1),
            beschreibung="AP-Rechnungseingang",
        ),
        EventSchemaEintrag(
            schema_id="ES-006",
            event_typ="compliance.pruefung_abgeschlossen",
            version="1.0.0",
            status=EventSchemaStatus.ENTWURF,
            payload_felder=["pruefung_id", "objekt_id", "pruef_typ", "ergebnis", "pruefer_id", "datum", "zertifikat_nr"],
            pflicht_felder=["pruefung_id", "objekt_id", "pruef_typ", "ergebnis"],
            erstellt_am=datetime(2026, 3, 1),
            beschreibung="Compliance-Prüfungsabschluss (Entwurf)",
        ),
    ]
