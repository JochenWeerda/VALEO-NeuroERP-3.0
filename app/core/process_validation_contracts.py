from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any
from datetime import datetime


class ValidierungsSchwere(str, Enum):
    FEHLER = "FEHLER"       # Blocks processing
    WARNUNG = "WARNUNG"     # Allows processing with warning
    HINWEIS = "HINWEIS"     # Informational only


class RegelTyp(str, Enum):
    PFLICHTFELD = "PFLICHTFELD"         # Field must be present and non-empty
    WERTEBEREICH = "WERTEBEREICH"       # Value within min/max
    FORMAT = "FORMAT"                    # Regex or pattern match
    QUERVERWEIS = "QUERVERWEIS"         # Cross-field dependency
    GESCHAEFTSREGEL = "GESCHAEFTSREGEL" # Custom business logic


class ValidierungsStatus(str, Enum):
    GUELTIG = "GUELTIG"
    UNGUELTIG = "UNGUELTIG"
    WARNUNG = "WARNUNG"


@dataclass
class ValidierungsRegel:
    regel_id: str
    name: str
    regel_typ: RegelTyp
    schwere: ValidierungsSchwere
    feld: str                       # primary field
    beschreibung: str = ""
    min_wert: Optional[float] = None
    max_wert: Optional[float] = None
    pflicht_felder: list = field(default_factory=list)  # for QUERVERWEIS

    def pruefe(self, daten: dict) -> bool:
        """
        PFLICHTFELD: feld in daten and daten[feld] is not None and daten[feld] != ""
        WERTEBEREICH: feld in daten; min_wert <= daten[feld] <= max_wert (None = no bound);
                      False if feld missing or value not numeric
        FORMAT: always True (simplified — real impl would use regex)
        QUERVERWEIS: all pflicht_felder present in daten
        GESCHAEFTSREGEL: True (placeholder)
        Returns False on TypeError/ValueError.
        """
        try:
            if self.regel_typ == RegelTyp.PFLICHTFELD:
                return self.feld in daten and daten[self.feld] is not None and daten[self.feld] != ""
            elif self.regel_typ == RegelTyp.WERTEBEREICH:
                if self.feld not in daten:
                    return False
                wert = float(daten[self.feld])
                if self.min_wert is not None and wert < self.min_wert:
                    return False
                if self.max_wert is not None and wert > self.max_wert:
                    return False
                return True
            elif self.regel_typ == RegelTyp.QUERVERWEIS:
                return all(f in daten for f in self.pflicht_felder)
            else:
                return True
        except (TypeError, ValueError):
            return False


@dataclass
class ValidierungsFehler:
    regel_id: str
    feld: str
    schwere: ValidierungsSchwere
    nachricht: str


@dataclass
class ValidierungsErgebnis:
    status: ValidierungsStatus
    fehler: list = field(default_factory=list)   # list[ValidierungsFehler]
    warnungen: list = field(default_factory=list)
    hinweise: list = field(default_factory=list)

    @property
    def ist_gueltig(self) -> bool:
        return self.status == ValidierungsStatus.GUELTIG


def validiere_daten(daten: dict, regeln: list) -> ValidierungsErgebnis:
    """
    Runs all rules. Collects failures by severity.
    Any FEHLER → UNGUELTIG status.
    Only WARNUNGen (no FEHLER) → WARNUNG status.
    All pass → GUELTIG.
    """
    fehler, warnungen, hinweise = [], [], []
    for regel in regeln:
        if not regel.pruefe(daten):
            vf = ValidierungsFehler(regel.regel_id, regel.feld, regel.schwere,
                                     f"{regel.name}: Validierung fehlgeschlagen")
            if regel.schwere == ValidierungsSchwere.FEHLER:
                fehler.append(vf)
            elif regel.schwere == ValidierungsSchwere.WARNUNG:
                warnungen.append(vf)
            else:
                hinweise.append(vf)
    if fehler:
        status = ValidierungsStatus.UNGUELTIG
    elif warnungen:
        status = ValidierungsStatus.WARNUNG
    else:
        status = ValidierungsStatus.GUELTIG
    return ValidierungsErgebnis(status, fehler, warnungen, hinweise)


def get_default_validierungs_regeln() -> list:
    return [
        ValidierungsRegel("VR-001", "Lieferant Pflichtfeld", RegelTyp.PFLICHTFELD,
                           ValidierungsSchwere.FEHLER, "lieferant_id", "Lieferant muss angegeben sein"),
        ValidierungsRegel("VR-002", "Menge Wertebereich", RegelTyp.WERTEBEREICH,
                           ValidierungsSchwere.FEHLER, "menge_tonnen", "Menge 0.1–10000t",
                           min_wert=0.1, max_wert=10000.0),
        ValidierungsRegel("VR-003", "Preis Wertebereich", RegelTyp.WERTEBEREICH,
                           ValidierungsSchwere.WARNUNG, "preis_eur_t", "Preis 10–1000 EUR/t",
                           min_wert=10.0, max_wert=1000.0),
        ValidierungsRegel("VR-004", "Preis-Menge Querverweis", RegelTyp.QUERVERWEIS,
                           ValidierungsSchwere.FEHLER, "preis_eur_t", "Preis und Menge gemeinsam erforderlich",
                           pflicht_felder=["menge_tonnen", "preis_eur_t"]),
        ValidierungsRegel("VR-005", "Kommentar Hinweis", RegelTyp.PFLICHTFELD,
                           ValidierungsSchwere.HINWEIS, "kommentar", "Kommentar empfohlen"),
    ]
