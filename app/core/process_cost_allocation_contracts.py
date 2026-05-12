from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class KostenTyp(str, Enum):
    PERSONAL = "PERSONAL"
    SYSTEM = "SYSTEM"
    EXTERN = "EXTERN"
    OVERHEAD = "OVERHEAD"


class AllokationsMethode(str, Enum):
    DIREKT = "DIREKT"           # 1:1 to cost center
    ANTEILIG = "ANTEILIG"       # proportional split
    GLEICH = "GLEICH"           # equal split across centers
    GEWICHTET = "GEWICHTET"     # weighted by factor


class KostenStatus(str, Enum):
    GEPLANT = "GEPLANT"
    GEBUCHT = "GEBUCHT"
    STORNIERT = "STORNIERT"


@dataclass
class KostenPosition:
    position_id: str
    kosten_typ: KostenTyp
    betrag: float               # always positive
    waehrung: str = "EUR"
    beschreibung: str = ""
    status: KostenStatus = KostenStatus.GEPLANT


@dataclass
class KostenAllokation:
    allokation_id: str
    workflow_instanz_id: str
    kostenstelle_id: str
    positionen: list = field(default_factory=list)  # list[KostenPosition]
    methode: AllokationsMethode = AllokationsMethode.DIREKT
    allokations_anteil: float = 1.0   # 0.0–1.0, used for ANTEILIG/GEWICHTET

    def gesamtkosten(self) -> float:
        """Sum of all non-STORNIERT positions * allokations_anteil."""
        aktiv = [p for p in self.positionen if p.status != KostenStatus.STORNIERT]
        return sum(p.betrag for p in aktiv) * self.allokations_anteil

    def kosten_nach_typ(self) -> dict:
        """Returns {KostenTyp: float} for non-STORNIERT positions * allokations_anteil."""
        result = {t: 0.0 for t in KostenTyp}
        for p in self.positionen:
            if p.status != KostenStatus.STORNIERT:
                result[p.kosten_typ] += p.betrag * self.allokations_anteil
        return result


def verteile_kosten(
    gesamt_betrag: float,
    kostenstellen: list,     # list of {"kostenstelle_id": str, "gewicht": float}
    methode: AllokationsMethode,
) -> list:
    """
    Returns list of {"kostenstelle_id": str, "anteil": float, "betrag": float}.
    DIREKT: first kostenstelle gets 100%, rest 0%.
    GLEICH: equal split (1/n each).
    ANTEILIG/GEWICHTET: proportional by "gewicht" field.
    Empty list → returns [].
    """
    if not kostenstellen:
        return []
    if methode == AllokationsMethode.DIREKT:
        ergebnis = [{"kostenstelle_id": kostenstellen[0]["kostenstelle_id"], "anteil": 1.0, "betrag": gesamt_betrag}]
        for k in kostenstellen[1:]:
            ergebnis.append({"kostenstelle_id": k["kostenstelle_id"], "anteil": 0.0, "betrag": 0.0})
        return ergebnis
    elif methode == AllokationsMethode.GLEICH:
        anteil = 1.0 / len(kostenstellen)
        betrag = gesamt_betrag / len(kostenstellen)
        return [{"kostenstelle_id": k["kostenstelle_id"], "anteil": anteil, "betrag": betrag} for k in kostenstellen]
    else:  # ANTEILIG / GEWICHTET
        gesamt_gewicht = sum(k.get("gewicht", 1.0) for k in kostenstellen)
        if gesamt_gewicht == 0:
            return [{"kostenstelle_id": k["kostenstelle_id"], "anteil": 0.0, "betrag": 0.0} for k in kostenstellen]
        return [
            {
                "kostenstelle_id": k["kostenstelle_id"],
                "anteil": k.get("gewicht", 1.0) / gesamt_gewicht,
                "betrag": gesamt_betrag * k.get("gewicht", 1.0) / gesamt_gewicht,
            }
            for k in kostenstellen
        ]


def get_default_kosten_allokationen() -> list:
    _now = datetime(2026, 3, 16, 10, 0, 0)  # noqa: F841
    a1 = KostenAllokation("KA-001", "WI-K-001", "KST-AGRAR", [], AllokationsMethode.DIREKT, 1.0)
    a1.positionen = [
        KostenPosition("KP-001", KostenTyp.PERSONAL, 120.0, "EUR", "Bearbeitung", KostenStatus.GEBUCHT),
        KostenPosition("KP-002", KostenTyp.SYSTEM, 15.0, "EUR", "IT-Nutzung", KostenStatus.GEBUCHT),
        KostenPosition("KP-003", KostenTyp.EXTERN, 50.0, "EUR", "EDI-Kosten", KostenStatus.STORNIERT),
    ]
    a2 = KostenAllokation("KA-002", "WI-S-002", "KST-FIBU", [], AllokationsMethode.ANTEILIG, 0.6)
    a2.positionen = [
        KostenPosition("KP-004", KostenTyp.PERSONAL, 200.0, "EUR", "Buchhaltung", KostenStatus.GEBUCHT),
        KostenPosition("KP-005", KostenTyp.OVERHEAD, 40.0, "EUR", "Overhead", KostenStatus.GEPLANT),
    ]
    return [a1, a2]
