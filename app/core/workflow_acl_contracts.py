"""
Workflow ACL Contracts — Wave 46
Feingranulare Zugangskontrolle auf Workflow-Ressourcen-Ebene:
Permissions, Deny-Override, Policy-Composition und Default-Deny.

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

class AclAktion(str, Enum):
    LESEN = "LESEN"
    SCHREIBEN = "SCHREIBEN"
    AUSFUEHREN = "AUSFUEHREN"
    FREIGEBEN = "FREIGEBEN"
    ADMINISTRIEREN = "ADMINISTRIEREN"


class AclEffekt(str, Enum):
    ERLAUBEN = "ERLAUBEN"
    VERWEIGERN = "VERWEIGERN"


class AclVererbung(str, Enum):
    KEINE = "KEINE"             # Regel gilt nur für diese Ressource
    VON_ELTERN = "VON_ELTERN"   # Regel von übergeordneter Ressource geerbt
    AN_KINDER = "AN_KINDER"     # Regel wird an Unterressourcen weitergegeben


# ---------------------------------------------------------------------------
# ACL-Regel
# ---------------------------------------------------------------------------

@dataclass
class AclRegel:
    """
    Einzelne ACL-Regel: Erlaubt oder verweigert einem Subjekt eine Aktion
    auf einer Ressource.

    Niedrigere `prioritaet` → wird zuerst ausgewertet.
    Bei gleicher Priorität: VERWEIGERN gewinnt (Deny-Override).
    """
    regel_id: str
    ressource_id: str          # Workflow-ID, Domain oder "*" für alle
    subjekt_id: str            # User-ID, Rollen-ID oder "*" für alle
    aktion: AclAktion
    effekt: AclEffekt
    prioritaet: int            # 1 = höchste Priorität
    vererbung: AclVererbung = AclVererbung.KEINE
    beschreibung: str = ""

    @property
    def ist_erlaubnis(self) -> bool:
        return self.effekt == AclEffekt.ERLAUBEN

    @property
    def ist_verweigerung(self) -> bool:
        return self.effekt == AclEffekt.VERWEIGERN

    def _trifft_zu(self, ressource_id: str, subjekt_id: str, aktion: AclAktion) -> bool:
        """Prüft ob die Regel auf die gegebene Kombination zutrifft."""
        ressource_match = self.ressource_id == "*" or self.ressource_id == ressource_id
        subjekt_match = self.subjekt_id == "*" or self.subjekt_id == subjekt_id
        aktion_match = self.aktion == aktion
        return ressource_match and subjekt_match and aktion_match

    def as_dict(self) -> dict[str, Any]:
        return {
            "regel_id": self.regel_id,
            "ressource_id": self.ressource_id,
            "subjekt_id": self.subjekt_id,
            "aktion": self.aktion.value,
            "effekt": self.effekt.value,
            "prioritaet": self.prioritaet,
            "vererbung": self.vererbung.value,
            "ist_erlaubnis": self.ist_erlaubnis,
            "ist_verweigerung": self.ist_verweigerung,
            "beschreibung": self.beschreibung,
        }


# ---------------------------------------------------------------------------
# ACL-Entscheidung
# ---------------------------------------------------------------------------

@dataclass
class AclEntscheidung:
    """Ergebnis einer ACL-Auswertung."""
    ressource_id: str
    subjekt_id: str
    aktion: AclAktion
    effekt: AclEffekt
    angewandte_regel_id: str = ""   # "" wenn Default-Deny
    begruendung: str = ""
    entschieden_am: datetime = field(default_factory=datetime.utcnow)

    @property
    def ist_erlaubt(self) -> bool:
        return self.effekt == AclEffekt.ERLAUBEN

    def as_dict(self) -> dict[str, Any]:
        return {
            "ressource_id": self.ressource_id,
            "subjekt_id": self.subjekt_id,
            "aktion": self.aktion.value,
            "effekt": self.effekt.value,
            "angewandte_regel_id": self.angewandte_regel_id,
            "begruendung": self.begruendung,
            "ist_erlaubt": self.ist_erlaubt,
            "entschieden_am": self.entschieden_am.isoformat(),
        }


# ---------------------------------------------------------------------------
# Logik
# ---------------------------------------------------------------------------

def pruefe_acl(
    ressource_id: str,
    subjekt_id: str,
    aktion: AclAktion,
    regeln: list[AclRegel],
    entschieden_am: datetime | None = None,
) -> AclEntscheidung:
    """
    Wertet ACL-Regeln aus und gibt eine Entscheidung zurück.

    Logik:
    1. Alle passenden Regeln nach Priorität sortieren (aufsteigend)
    2. Bei gleicher Priorität: VERWEIGERN vor ERLAUBEN (Deny-Override)
    3. Erste Regel gewinnt
    4. Kein Match → Default-Deny
    """
    ts = entschieden_am or datetime.utcnow()

    passende = [
        r for r in regeln
        if r._trifft_zu(ressource_id, subjekt_id, aktion)
    ]

    # Sortierung: Priorität aufsteigend, bei Gleichstand VERWEIGERN zuerst
    passende.sort(
        key=lambda r: (r.prioritaet, 0 if r.effekt == AclEffekt.VERWEIGERN else 1)
    )

    if not passende:
        return AclEntscheidung(
            ressource_id=ressource_id,
            subjekt_id=subjekt_id,
            aktion=aktion,
            effekt=AclEffekt.VERWEIGERN,
            angewandte_regel_id="",
            begruendung="Keine passende Regel — Default-Deny.",
            entschieden_am=ts,
        )

    gewinner = passende[0]
    return AclEntscheidung(
        ressource_id=ressource_id,
        subjekt_id=subjekt_id,
        aktion=aktion,
        effekt=gewinner.effekt,
        angewandte_regel_id=gewinner.regel_id,
        begruendung=gewinner.beschreibung or f"Regel {gewinner.regel_id} angewendet.",
        entschieden_am=ts,
    )


# ---------------------------------------------------------------------------
# Standarddaten
# ---------------------------------------------------------------------------

def get_default_acl_regeln() -> list[AclRegel]:
    """Gibt 6 Standard-ACL-Regeln zurück."""
    return [
        AclRegel(
            regel_id="AR-001",
            ressource_id="*",
            subjekt_id="admin",
            aktion=AclAktion.ADMINISTRIEREN,
            effekt=AclEffekt.ERLAUBEN,
            prioritaet=1,
            vererbung=AclVererbung.AN_KINDER,
            beschreibung="Administratoren dürfen alles administrieren",
        ),
        AclRegel(
            regel_id="AR-002",
            ressource_id="workflow:kontrakt_annahme",
            subjekt_id="sachbearbeiter",
            aktion=AclAktion.AUSFUEHREN,
            effekt=AclEffekt.ERLAUBEN,
            prioritaet=10,
            beschreibung="Sachbearbeiter darf Kontrakt-Annahme ausführen",
        ),
        AclRegel(
            regel_id="AR-003",
            ressource_id="workflow:settlement_freigabe",
            subjekt_id="sachbearbeiter",
            aktion=AclAktion.FREIGEBEN,
            effekt=AclEffekt.VERWEIGERN,
            prioritaet=5,
            beschreibung="Sachbearbeiter darf Settlement NICHT freigeben (4-Augen)",
        ),
        AclRegel(
            regel_id="AR-004",
            ressource_id="workflow:settlement_freigabe",
            subjekt_id="leiter",
            aktion=AclAktion.FREIGEBEN,
            effekt=AclEffekt.ERLAUBEN,
            prioritaet=5,
            beschreibung="Abteilungsleiter darf Settlement freigeben",
        ),
        AclRegel(
            regel_id="AR-005",
            ressource_id="*",
            subjekt_id="*",
            aktion=AclAktion.LESEN,
            effekt=AclEffekt.ERLAUBEN,
            prioritaet=100,
            vererbung=AclVererbung.AN_KINDER,
            beschreibung="Alle dürfen alles lesen (Fallback-Erlaubnis)",
        ),
        AclRegel(
            regel_id="AR-006",
            ressource_id="workflow:compliance_pruefung",
            subjekt_id="extern",
            aktion=AclAktion.SCHREIBEN,
            effekt=AclEffekt.VERWEIGERN,
            prioritaet=1,
            beschreibung="Externe dürfen Compliance-Prüfungen nicht schreiben",
        ),
    ]
