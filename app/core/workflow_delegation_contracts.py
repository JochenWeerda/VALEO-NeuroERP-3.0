"""
Workflow Delegation Contracts — Wave 47
Aufgaben-Delegation, Vertretungsregeln und Eskalationsketten für Workflow-Tasks.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class DelegationsTyp(str, Enum):
    DIREKT = "DIREKT"              # Direkte Zuweisung an eine Person
    STELLVERTRETER = "STELLVERTRETER"  # Automatische Vertretung (Abwesenheit)
    ESKALATION = "ESKALATION"      # Zeitgesteuerte Eskalation
    POOL = "POOL"                  # Zuweisung an eine Gruppe/Pool


class DelegationsStatus(str, Enum):
    AKTIV = "AKTIV"
    ABGELAUFEN = "ABGELAUFEN"
    WIDERRUFEN = "WIDERRUFEN"
    ANGENOMMEN = "ANGENOMMEN"
    ABGELEHNT = "ABGELEHNT"


class EskalationsStufe(str, Enum):
    STUFE_1 = "STUFE_1"   # Teamleiter
    STUFE_2 = "STUFE_2"   # Abteilungsleiter
    STUFE_3 = "STUFE_3"   # Geschäftsführung
    KEINE = "KEINE"


# ---------------------------------------------------------------------------
# Delegationsregel
# ---------------------------------------------------------------------------

@dataclass
class DelegationsRegel:
    """
    Regel für die Aufgaben-Delegation eines Subjekts an ein anderes.

    Bei ESKALATION wird `eskalations_nach_minuten` ausgewertet, um den
    Zeitpunkt der Eskalation zu berechnen.
    """
    regel_id: str
    von_subjekt_id: str        # Delegierendes Subjekt
    zu_subjekt_id: str         # Empfangendes Subjekt
    delegations_typ: DelegationsTyp
    status: DelegationsStatus
    gueltig_ab: datetime
    gueltig_bis: datetime | None = None
    eskalations_nach_minuten: int = 60
    eskalations_stufe: EskalationsStufe = EskalationsStufe.KEINE
    aufgaben_typen: list[str] = field(default_factory=list)  # Leer = alle Aufgaben
    beschreibung: str = ""

    @property
    def ist_aktiv(self) -> bool:
        """True wenn Status AKTIV."""
        return self.status == DelegationsStatus.AKTIV

    def ist_gueltig(self, zum_zeitpunkt: datetime) -> bool:
        """True wenn die Regel zum gegebenen Zeitpunkt gültig ist."""
        if not self.ist_aktiv:
            return False
        if zum_zeitpunkt < self.gueltig_ab:
            return False
        if self.gueltig_bis is not None and zum_zeitpunkt > self.gueltig_bis:
            return False
        return True

    def gilt_fuer_aufgabe(self, aufgaben_typ: str) -> bool:
        """True wenn die Regel für den gegebenen Aufgabentyp gilt."""
        if not self.aufgaben_typen:
            return True  # Leer = alle Aufgaben
        return aufgaben_typ in self.aufgaben_typen

    def eskalations_zeitpunkt(self, erstellt_am: datetime) -> datetime:
        """Berechnet den Eskalationszeitpunkt ausgehend vom Erstellzeitpunkt."""
        return erstellt_am + timedelta(minutes=self.eskalations_nach_minuten)

    def as_dict(self) -> dict[str, Any]:
        return {
            "regel_id": self.regel_id,
            "von_subjekt_id": self.von_subjekt_id,
            "zu_subjekt_id": self.zu_subjekt_id,
            "delegations_typ": self.delegations_typ.value,
            "status": self.status.value,
            "ist_aktiv": self.ist_aktiv,
            "gueltig_ab": self.gueltig_ab.isoformat(),
            "gueltig_bis": self.gueltig_bis.isoformat() if self.gueltig_bis else None,
            "eskalations_nach_minuten": self.eskalations_nach_minuten,
            "eskalations_stufe": self.eskalations_stufe.value,
            "aufgaben_typen": self.aufgaben_typen,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Delegations-Entscheidung
# ---------------------------------------------------------------------------

@dataclass
class DelegationsEntscheidung:
    """Ergebnis der Delegation-Auflösung für ein Subjekt und einen Aufgabentyp."""
    original_subjekt_id: str
    aufgaben_typ: str
    delegiert_an: str              # Zielsubjekt (= original wenn keine Delegation)
    angewendete_regel_id: str      # "" wenn keine Delegation
    delegations_typ: DelegationsTyp | None
    eskalations_stufe: EskalationsStufe
    ist_delegiert: bool
    begruendung: str = ""
    entschieden_am: datetime = field(default_factory=datetime.utcnow)

    def as_dict(self) -> dict[str, Any]:
        return {
            "original_subjekt_id": self.original_subjekt_id,
            "aufgaben_typ": self.aufgaben_typ,
            "delegiert_an": self.delegiert_an,
            "angewendete_regel_id": self.angewendete_regel_id,
            "delegations_typ": self.delegations_typ.value if self.delegations_typ else None,
            "eskalations_stufe": self.eskalations_stufe.value,
            "ist_delegiert": self.ist_delegiert,
            "begruendung": self.begruendung,
            "entschieden_am": self.entschieden_am.isoformat(),
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def loeseauf_delegation(
    subjekt_id: str,
    aufgaben_typ: str,
    regeln: list[DelegationsRegel],
    zum_zeitpunkt: datetime | None = None,
) -> DelegationsEntscheidung:
    """
    Löst die Delegation für ein Subjekt und einen Aufgabentyp auf.

    Logik:
    1. Gültige Regeln für subjekt_id und aufgaben_typ filtern
    2. ESKALATION vor anderen Typen (niedrigere Priorität → zuerst)
    3. Erste passende Regel gewinnt
    4. Kein Match → original Subjekt bleibt zuständig
    """
    ts = zum_zeitpunkt or datetime.utcnow()

    passende = [
        r for r in regeln
        if r.von_subjekt_id == subjekt_id
        and r.ist_gueltig(ts)
        and r.gilt_fuer_aufgabe(aufgaben_typ)
    ]

    # ESKALATION zuerst, dann nach Gültigkeitsstart sortieren (neueste zuerst)
    passende.sort(key=lambda r: (
        0 if r.delegations_typ == DelegationsTyp.ESKALATION else 1,
        -r.gueltig_ab.timestamp(),
    ))

    if not passende:
        return DelegationsEntscheidung(
            original_subjekt_id=subjekt_id,
            aufgaben_typ=aufgaben_typ,
            delegiert_an=subjekt_id,
            angewendete_regel_id="",
            delegations_typ=None,
            eskalations_stufe=EskalationsStufe.KEINE,
            ist_delegiert=False,
            begruendung="Keine aktive Delegationsregel — Subjekt bleibt zuständig.",
            entschieden_am=ts,
        )

    gewinner = passende[0]
    return DelegationsEntscheidung(
        original_subjekt_id=subjekt_id,
        aufgaben_typ=aufgaben_typ,
        delegiert_an=gewinner.zu_subjekt_id,
        angewendete_regel_id=gewinner.regel_id,
        delegations_typ=gewinner.delegations_typ,
        eskalations_stufe=gewinner.eskalations_stufe,
        ist_delegiert=True,
        begruendung=gewinner.beschreibung or f"Regel {gewinner.regel_id} angewendet.",
        entschieden_am=ts,
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_delegations_regeln() -> list[DelegationsRegel]:
    """Gibt 5 Standard-Delegationsregeln zurück."""
    basis = datetime(2026, 3, 1, 0, 0)
    return [
        DelegationsRegel(
            regel_id="DR-001",
            von_subjekt_id="mueller",
            zu_subjekt_id="schneider",
            delegations_typ=DelegationsTyp.STELLVERTRETER,
            status=DelegationsStatus.AKTIV,
            gueltig_ab=basis,
            gueltig_bis=datetime(2026, 3, 31, 23, 59),
            beschreibung="Müller im Urlaub — Schneider als Stellvertreter",
        ),
        DelegationsRegel(
            regel_id="DR-002",
            von_subjekt_id="sachbearbeiter",
            zu_subjekt_id="teamleiter",
            delegations_typ=DelegationsTyp.ESKALATION,
            status=DelegationsStatus.AKTIV,
            gueltig_ab=basis,
            eskalations_nach_minuten=120,
            eskalations_stufe=EskalationsStufe.STUFE_1,
            aufgaben_typen=["kontrakt_freigabe", "settlement_freigabe"],
            beschreibung="Freigabe-Tasks nach 2h an Teamleiter eskalieren",
        ),
        DelegationsRegel(
            regel_id="DR-003",
            von_subjekt_id="teamleiter",
            zu_subjekt_id="abteilungsleiter",
            delegations_typ=DelegationsTyp.ESKALATION,
            status=DelegationsStatus.AKTIV,
            gueltig_ab=basis,
            eskalations_nach_minuten=240,
            eskalations_stufe=EskalationsStufe.STUFE_2,
            aufgaben_typen=["kontrakt_freigabe", "settlement_freigabe"],
            beschreibung="Freigabe-Tasks nach 4h an Abteilungsleiter eskalieren",
        ),
        DelegationsRegel(
            regel_id="DR-004",
            von_subjekt_id="einkauf_pool",
            zu_subjekt_id="fischer",
            delegations_typ=DelegationsTyp.POOL,
            status=DelegationsStatus.AKTIV,
            gueltig_ab=basis,
            aufgaben_typen=["bestellvorschlag_pruefung"],
            beschreibung="Bestellvorschlag-Prüfung aus Pool an Fischer zugeteilt",
        ),
        DelegationsRegel(
            regel_id="DR-005",
            von_subjekt_id="weber",
            zu_subjekt_id="mueller",
            delegations_typ=DelegationsTyp.DIREKT,
            status=DelegationsStatus.WIDERRUFEN,
            gueltig_ab=basis,
            beschreibung="Direkte Delegation Weber→Müller (widerrufen)",
        ),
    ]
