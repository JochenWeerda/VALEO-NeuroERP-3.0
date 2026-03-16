"""
Process State Machine Contracts — Wave 47
Formale Zustandsautomaten für Workflow-Prozesse:
Zustände, Übergänge, Wächter-Bedingungen und Ausführungsprotokoll.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class ZustandTyp(str, Enum):
    START = "START"
    NORMAL = "NORMAL"
    WARTE = "WARTE"          # Wartet auf externes Signal
    ENTSCHEIDUNG = "ENTSCHEIDUNG"
    ABSCHLUSS = "ABSCHLUSS"
    FEHLER = "FEHLER"


class UebergangsBedingung(str, Enum):
    IMMER = "IMMER"                  # Übergang immer erlaubt
    FELD_VORHANDEN = "FELD_VORHANDEN"  # Kontextfeld muss existieren
    WERT_GLEICH = "WERT_GLEICH"        # Kontextfeld == wert
    ROLLE_ERLAUBT = "ROLLE_ERLAUBT"    # rolle im Kontext muss passen
    WERT_GROESSER = "WERT_GROESSER"    # Kontextfeld > wert (numerisch)


class AutomatStatus(str, Enum):
    BEREIT = "BEREIT"
    LAUFEND = "LAUFEND"
    ABGESCHLOSSEN = "ABGESCHLOSSEN"
    FEHLGESCHLAGEN = "FEHLGESCHLAGEN"
    SUSPENDIERT = "SUSPENDIERT"


# ---------------------------------------------------------------------------
# Zustand
# ---------------------------------------------------------------------------

@dataclass
class Zustand:
    """Ein Zustand im Zustandsautomaten."""
    zustand_id: str
    zustand_name: str
    typ: ZustandTyp
    beschreibung: str = ""

    @property
    def ist_endpunkt(self) -> bool:
        return self.typ in (ZustandTyp.ABSCHLUSS, ZustandTyp.FEHLER)

    def as_dict(self) -> dict[str, Any]:
        return {
            "zustand_id": self.zustand_id,
            "zustand_name": self.zustand_name,
            "typ": self.typ.value,
            "ist_endpunkt": self.ist_endpunkt,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Übergang
# ---------------------------------------------------------------------------

@dataclass
class Uebergang:
    """Übergang zwischen zwei Zuständen mit optionaler Wächterbedingung."""
    uebergang_id: str
    von_zustand_id: str
    zu_zustand_id: str
    bedingung: UebergangsBedingung
    feld: str = ""   # Relevant für FELD_VORHANDEN, WERT_GLEICH, WERT_GROESSER
    wert: str = ""   # Vergleichswert
    prioritaet: int = 10
    beschreibung: str = ""

    def pruefe(self, kontext: dict[str, Any]) -> bool:
        """Prüft ob dieser Übergang im gegebenen Kontext zulässig ist."""
        if self.bedingung == UebergangsBedingung.IMMER:
            return True
        if self.bedingung == UebergangsBedingung.FELD_VORHANDEN:
            return self.feld in kontext
        if self.bedingung == UebergangsBedingung.WERT_GLEICH:
            return str(kontext.get(self.feld, "")) == self.wert
        if self.bedingung == UebergangsBedingung.ROLLE_ERLAUBT:
            return str(kontext.get("rolle", "")) == self.wert
        if self.bedingung == UebergangsBedingung.WERT_GROESSER:
            try:
                return float(kontext.get(self.feld, 0)) > float(self.wert)
            except (ValueError, TypeError):
                return False
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "uebergang_id": self.uebergang_id,
            "von_zustand_id": self.von_zustand_id,
            "zu_zustand_id": self.zu_zustand_id,
            "bedingung": self.bedingung.value,
            "feld": self.feld,
            "wert": self.wert,
            "prioritaet": self.prioritaet,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Übergangs-Ergebnis
# ---------------------------------------------------------------------------

@dataclass
class UebergangsErgebnis:
    """Ergebnis eines versuchten Zustandsübergangs."""
    instanz_id: str
    von_zustand_id: str
    zu_zustand_id: str
    angewendeter_uebergang_id: str
    erfolg: bool
    begruendung: str = ""
    ausgefuehrt_am: datetime = field(default_factory=datetime.utcnow)

    def as_dict(self) -> dict[str, Any]:
        return {
            "instanz_id": self.instanz_id,
            "von_zustand_id": self.von_zustand_id,
            "zu_zustand_id": self.zu_zustand_id,
            "angewendeter_uebergang_id": self.angewendeter_uebergang_id,
            "erfolg": self.erfolg,
            "begruendung": self.begruendung,
            "ausgefuehrt_am": self.ausgefuehrt_am.isoformat(),
        }


# ---------------------------------------------------------------------------
# Zustandsautomat-Definition
# ---------------------------------------------------------------------------

@dataclass
class ZustandsAutomatDefinition:
    """Definition eines Zustandsautomaten mit Zuständen und Übergängen."""
    automat_id: str
    automat_name: str
    zustande: list[Zustand] = field(default_factory=list)
    uebergaenge: list[Uebergang] = field(default_factory=list)
    beschreibung: str = ""

    @property
    def start_zustand(self) -> Zustand | None:
        """Gibt den START-Zustand zurück."""
        for z in self.zustande:
            if z.typ == ZustandTyp.START:
                return z
        return None

    @property
    def endpunkt_ids(self) -> list[str]:
        """IDs aller Endpunkt-Zustände (ABSCHLUSS, FEHLER)."""
        return [z.zustand_id for z in self.zustande if z.ist_endpunkt]

    def finde_uebergaenge(
        self,
        von_zustand_id: str,
        kontext: dict[str, Any],
    ) -> list[Uebergang]:
        """
        Gibt alle erlaubten Übergänge vom gegebenen Zustand im Kontext zurück,
        sortiert nach Priorität aufsteigend.
        """
        passende = [
            u for u in self.uebergaenge
            if u.von_zustand_id == von_zustand_id and u.pruefe(kontext)
        ]
        passende.sort(key=lambda u: u.prioritaet)
        return passende

    def as_dict(self) -> dict[str, Any]:
        return {
            "automat_id": self.automat_id,
            "automat_name": self.automat_name,
            "anzahl_zustaende": len(self.zustande),
            "anzahl_uebergaenge": len(self.uebergaenge),
            "start_zustand_id": self.start_zustand.zustand_id if self.start_zustand else None,
            "endpunkt_ids": self.endpunkt_ids,
            "beschreibung": self.beschreibung,
            "zustande": [z.as_dict() for z in self.zustande],
            "uebergaenge": [u.as_dict() for u in self.uebergaenge],
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def fuehre_uebergang_aus(
    instanz_id: str,
    automat: ZustandsAutomatDefinition,
    aktueller_zustand_id: str,
    kontext: dict[str, Any],
    ausgefuehrt_am: datetime | None = None,
) -> UebergangsErgebnis:
    """
    Führt den ersten erlaubten Übergang vom aktuellen Zustand aus.

    Logik:
    1. Alle erlaubten Übergänge nach Priorität sortiert
    2. Erster Übergang wird angewendet
    3. Kein Übergang möglich → erfolg=False
    """
    ts = ausgefuehrt_am or datetime.utcnow()
    erlaubte = automat.finde_uebergaenge(aktueller_zustand_id, kontext)

    if not erlaubte:
        return UebergangsErgebnis(
            instanz_id=instanz_id,
            von_zustand_id=aktueller_zustand_id,
            zu_zustand_id=aktueller_zustand_id,
            angewendeter_uebergang_id="",
            erfolg=False,
            begruendung="Kein erlaubter Übergang im aktuellen Kontext.",
            ausgefuehrt_am=ts,
        )

    gewinner = erlaubte[0]
    return UebergangsErgebnis(
        instanz_id=instanz_id,
        von_zustand_id=aktueller_zustand_id,
        zu_zustand_id=gewinner.zu_zustand_id,
        angewendeter_uebergang_id=gewinner.uebergang_id,
        erfolg=True,
        begruendung=gewinner.beschreibung or f"Übergang {gewinner.uebergang_id} angewendet.",
        ausgefuehrt_am=ts,
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_zustandsautomat() -> ZustandsAutomatDefinition:
    """Gibt einen Standard-Zustandsautomaten für Kontrakt-Freigabe zurück."""
    zustande = [
        Zustand("Z-01", "Entwurf",          ZustandTyp.START,        "Kontrakt im Entwurfsstadium"),
        Zustand("Z-02", "Prüfung",           ZustandTyp.NORMAL,       "Fachliche Prüfung läuft"),
        Zustand("Z-03", "Warte auf Leiter",  ZustandTyp.WARTE,        "Wartet auf Leiter-Freigabe"),
        Zustand("Z-04", "Freigabe-Entscheid",ZustandTyp.ENTSCHEIDUNG, "Freigabe oder Ablehnung"),
        Zustand("Z-05", "Genehmigt",         ZustandTyp.ABSCHLUSS,    "Kontrakt genehmigt"),
        Zustand("Z-06", "Abgelehnt",         ZustandTyp.FEHLER,       "Kontrakt abgelehnt"),
    ]
    uebergaenge = [
        Uebergang("U-01", "Z-01", "Z-02", UebergangsBedingung.IMMER,
                  prioritaet=10, beschreibung="Entwurf einreichen"),
        Uebergang("U-02", "Z-02", "Z-03", UebergangsBedingung.WERT_GROESSER,
                  feld="betrag_eur", wert="10000", prioritaet=5,
                  beschreibung="Beträge > 10.000 EUR → Leiter-Freigabe"),
        Uebergang("U-03", "Z-02", "Z-04", UebergangsBedingung.IMMER,
                  prioritaet=10, beschreibung="Standardprüfung abgeschlossen"),
        Uebergang("U-04", "Z-03", "Z-04", UebergangsBedingung.ROLLE_ERLAUBT,
                  wert="leiter", prioritaet=5,
                  beschreibung="Leiter hat geprüft"),
        Uebergang("U-05", "Z-04", "Z-05", UebergangsBedingung.WERT_GLEICH,
                  feld="entscheidung", wert="genehmigt", prioritaet=1,
                  beschreibung="Freigabe erteilt"),
        Uebergang("U-06", "Z-04", "Z-06", UebergangsBedingung.WERT_GLEICH,
                  feld="entscheidung", wert="abgelehnt", prioritaet=2,
                  beschreibung="Freigabe verweigert"),
    ]
    return ZustandsAutomatDefinition(
        automat_id="ZA-KONTRAKT-001",
        automat_name="Kontrakt-Freigabe-Automat",
        zustande=zustande,
        uebergaenge=uebergaenge,
        beschreibung="Formaler Zustandsautomat für die Kontrakt-Freigabe mit 4-Augen-Prinzip",
    )
