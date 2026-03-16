"""
Process Routing Contracts — Wave 44
Regelbasiertes Nachrichtenrouting für Workflow-Schritte:
Bedingungsauswertung, priorisierte Routing-Tabellen und Dead-Letter-Handling.

Schichtregeln:
- Kein Import aus app/api/ oder app/infrastructure/
- Nur Stdlib + eigene Core-Module
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


# ---------------------------------------------------------------------------
# Enumerationen
# ---------------------------------------------------------------------------

class RoutingBedingungsTyp(str, Enum):
    IMMER = "IMMER"
    WERT_GLEICH = "WERT_GLEICH"
    WERT_GROESSER = "WERT_GROESSER"
    WERT_KLEINER = "WERT_KLEINER"
    FELD_VORHANDEN = "FELD_VORHANDEN"
    ROLLE_ERLAUBT = "ROLLE_ERLAUBT"


class RoutingZielTyp(str, Enum):
    WORKFLOW_SCHRITT = "WORKFLOW_SCHRITT"
    QUEUE = "QUEUE"
    EXTERN = "EXTERN"
    DEAD_LETTER = "DEAD_LETTER"
    ESKALATION = "ESKALATION"


class RoutingErgebnis(str, Enum):
    GEROUTET = "GEROUTET"
    KEIN_MATCH = "KEIN_MATCH"
    DEAD_LETTER = "DEAD_LETTER"
    FEHLER = "FEHLER"


# ---------------------------------------------------------------------------
# Routing-Bedingung
# ---------------------------------------------------------------------------

@dataclass
class RoutingBedingung:
    """Eine einzelne Bedingung innerhalb einer Routing-Regel."""
    bedingung_id: str
    typ: RoutingBedingungsTyp
    feld: str = ""     # Kontextfeld, das geprüft wird
    wert: str = ""     # Vergleichswert

    def pruefe(self, kontext: dict[str, Any]) -> bool:
        """Wertet die Bedingung gegen den Nachrichtenkontext aus."""
        if self.typ == RoutingBedingungsTyp.IMMER:
            return True
        if self.typ == RoutingBedingungsTyp.FELD_VORHANDEN:
            return self.feld in kontext
        if self.typ == RoutingBedingungsTyp.WERT_GLEICH:
            return str(kontext.get(self.feld, "")) == self.wert
        if self.typ == RoutingBedingungsTyp.ROLLE_ERLAUBT:
            return str(kontext.get("rolle", "")) == self.wert
        if self.typ == RoutingBedingungsTyp.WERT_GROESSER:
            try:
                return float(kontext.get(self.feld, 0)) > float(self.wert)
            except (TypeError, ValueError):
                return False
        if self.typ == RoutingBedingungsTyp.WERT_KLEINER:
            try:
                return float(kontext.get(self.feld, 0)) < float(self.wert)
            except (TypeError, ValueError):
                return False
        return False

    def as_dict(self) -> dict[str, Any]:
        return {
            "bedingung_id": self.bedingung_id,
            "typ": self.typ.value,
            "feld": self.feld,
            "wert": self.wert,
        }


# ---------------------------------------------------------------------------
# Routing-Regel
# ---------------------------------------------------------------------------

@dataclass
class RoutingRegel:
    """
    Priorisierte Routing-Regel für einen Workflow-Typ.

    Niedrigere `prioritaet` → wird zuerst geprüft.
    Alle Bedingungen müssen erfüllt sein (AND-Logik).
    """
    regel_id: str
    workflow_typ: str
    prioritaet: int                    # 1 = höchste Priorität
    bedingungen: list[RoutingBedingung]
    ziel_typ: RoutingZielTyp
    ziel_id: str                       # z.B. Schritt-ID, Queue-Name
    beschreibung: str = ""

    def pruefe_bedingungen(self, kontext: dict[str, Any]) -> bool:
        """True wenn alle Bedingungen erfüllt sind (AND)."""
        return all(b.pruefe(kontext) for b in self.bedingungen)

    def as_dict(self) -> dict[str, Any]:
        return {
            "regel_id": self.regel_id,
            "workflow_typ": self.workflow_typ,
            "prioritaet": self.prioritaet,
            "bedingungen_anzahl": len(self.bedingungen),
            "bedingungen": [b.as_dict() for b in self.bedingungen],
            "ziel_typ": self.ziel_typ.value,
            "ziel_id": self.ziel_id,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# Routing-Entscheidung
# ---------------------------------------------------------------------------

@dataclass
class RoutingEntscheidung:
    """Ergebnis einer Routing-Auswertung."""
    entscheidung_id: str
    workflow_typ: str
    kontext_snapshot: dict[str, Any]
    ergebnis: RoutingErgebnis
    gematchte_regel_id: str = ""
    ziel_typ: RoutingZielTyp = RoutingZielTyp.DEAD_LETTER
    ziel_id: str = ""
    entschieden_am: datetime = field(default_factory=datetime.utcnow)

    @property
    def wurde_geroutet(self) -> bool:
        return self.ergebnis == RoutingErgebnis.GEROUTET

    def as_dict(self) -> dict[str, Any]:
        return {
            "entscheidung_id": self.entscheidung_id,
            "workflow_typ": self.workflow_typ,
            "ergebnis": self.ergebnis.value,
            "gematchte_regel_id": self.gematchte_regel_id,
            "ziel_typ": self.ziel_typ.value,
            "ziel_id": self.ziel_id,
            "wurde_geroutet": self.wurde_geroutet,
            "entschieden_am": self.entschieden_am.isoformat(),
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def route_nachricht(
    workflow_typ: str,
    kontext: dict[str, Any],
    regeln: list[RoutingRegel] | None = None,
    entscheidung_id: str | None = None,
) -> RoutingEntscheidung:
    """
    Routet eine Nachricht anhand der priorisierten Routing-Regeln.

    Logik:
    1. Regeln nach prioritaet aufsteigend sortieren (1 = zuerst geprüft)
    2. Erste passende Regel gewinnt
    3. Kein Match → DEAD_LETTER
    """
    if regeln is None:
        regeln = get_default_routing_regeln()
    if entscheidung_id is None:
        entscheidung_id = f"RE-{uuid.uuid4().hex[:8].upper()}"

    relevante = sorted(
        [r for r in regeln if r.workflow_typ == workflow_typ],
        key=lambda r: r.prioritaet,
    )

    for regel in relevante:
        if regel.pruefe_bedingungen(kontext):
            return RoutingEntscheidung(
                entscheidung_id=entscheidung_id,
                workflow_typ=workflow_typ,
                kontext_snapshot=dict(kontext),
                ergebnis=RoutingErgebnis.GEROUTET,
                gematchte_regel_id=regel.regel_id,
                ziel_typ=regel.ziel_typ,
                ziel_id=regel.ziel_id,
            )

    return RoutingEntscheidung(
        entscheidung_id=entscheidung_id,
        workflow_typ=workflow_typ,
        kontext_snapshot=dict(kontext),
        ergebnis=RoutingErgebnis.DEAD_LETTER,
        ziel_typ=RoutingZielTyp.DEAD_LETTER,
        ziel_id="dead-letter-queue",
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_routing_regeln() -> list[RoutingRegel]:
    """Gibt 6 Standard-Routing-Regeln zurück."""
    return [
        RoutingRegel(
            regel_id="RR-001",
            workflow_typ="kontrakt_annahme",
            prioritaet=1,
            bedingungen=[
                RoutingBedingung("RB-001a", RoutingBedingungsTyp.WERT_GLEICH,
                                 feld="qualitaet_status", wert="ABGELEHNT"),
            ],
            ziel_typ=RoutingZielTyp.ESKALATION,
            ziel_id="eskalation-qualitaet-queue",
            beschreibung="Abgelehnte Qualität → Eskalation",
        ),
        RoutingRegel(
            regel_id="RR-002",
            workflow_typ="kontrakt_annahme",
            prioritaet=2,
            bedingungen=[
                RoutingBedingung("RB-002a", RoutingBedingungsTyp.WERT_GROESSER,
                                 feld="menge_t", wert="500"),
                RoutingBedingung("RB-002b", RoutingBedingungsTyp.ROLLE_ERLAUBT,
                                 wert="sachbearbeiter"),
            ],
            ziel_typ=RoutingZielTyp.WORKFLOW_SCHRITT,
            ziel_id="schritt-leiter-freigabe",
            beschreibung="Großmengen >500t → Leiter-Freigabe",
        ),
        RoutingRegel(
            regel_id="RR-003",
            workflow_typ="kontrakt_annahme",
            prioritaet=10,
            bedingungen=[
                RoutingBedingung("RB-003a", RoutingBedingungsTyp.IMMER),
            ],
            ziel_typ=RoutingZielTyp.WORKFLOW_SCHRITT,
            ziel_id="schritt-standard-freigabe",
            beschreibung="Fallback: Standard-Freigabe",
        ),
        RoutingRegel(
            regel_id="RR-004",
            workflow_typ="ap_approval",
            prioritaet=1,
            bedingungen=[
                RoutingBedingung("RB-004a", RoutingBedingungsTyp.WERT_GROESSER,
                                 feld="betrag_eur", wert="10000"),
            ],
            ziel_typ=RoutingZielTyp.WORKFLOW_SCHRITT,
            ziel_id="schritt-4-augen-pruefung",
            beschreibung="AP >10.000 EUR → 4-Augen-Prüfung",
        ),
        RoutingRegel(
            regel_id="RR-005",
            workflow_typ="ap_approval",
            prioritaet=5,
            bedingungen=[
                RoutingBedingung("RB-005a", RoutingBedingungsTyp.FELD_VORHANDEN,
                                 feld="kostenstelle"),
            ],
            ziel_typ=RoutingZielTyp.WORKFLOW_SCHRITT,
            ziel_id="schritt-kostenstellen-freigabe",
            beschreibung="AP mit Kostenstelle → Kostenstellenverantwortlicher",
        ),
        RoutingRegel(
            regel_id="RR-006",
            workflow_typ="ap_approval",
            prioritaet=10,
            bedingungen=[
                RoutingBedingung("RB-006a", RoutingBedingungsTyp.IMMER),
            ],
            ziel_typ=RoutingZielTyp.QUEUE,
            ziel_id="ap-standard-approval-queue",
            beschreibung="Fallback: Standard-AP-Queue",
        ),
    ]
