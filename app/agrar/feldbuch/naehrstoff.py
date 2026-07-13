"""
Reinnaehrstoff- und Duengebilanz-Berechnung fuer die Ackerschlagkartei.

Fachliche Grundlage: Duengeverordnung (DueV 2017/2020) und die
Reinnaehrstoff-Deklaration von Duengemitteln (N, P2O5, K2O, MgO, S als
Prozent des Produkts). Reine, testbare Rechenschicht ohne Persistenz —
Basis fuer die Wellen AS-W1 (Reinnaehrstoffe), AS-W2 (Duengebedarf) und
AS-W3 (Naehrstoff-/Stoffstrombilanz).

Konvention: Naehrstoffgehalte werden als **deklarierte Oxidprozente** des
Produkts erwartet (so wie auf dem Duengemittelsack ausgewiesen):
N, P2O5, K2O, MgO, S in % der Frischmasse/des Produkts. Mengen werden als
Produktmenge je ha angegeben; die Flaeche skaliert auf die Gesamtausbringung.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

# DueV: organische Duengung max. 170 kg Gesamt-N je ha und Jahr (betriebs-/
# schlagbezogen; in mit Nitrat belasteten "roten" Gebieten koennen strengere
# Werte gelten — hier als Parameter uebergebbar).
DUEV_N_ORG_LIMIT_KG_HA = 170.0

NUTRIENT_KEYS = ("n", "p2o5", "k2o", "mgo", "s")


@dataclass(frozen=True)
class NaehrstoffGehalt:
    """Deklarierte Reinnaehrstoffgehalte eines Duengemittels [% des Produkts]."""
    n: float = 0.0
    p2o5: float = 0.0
    k2o: float = 0.0
    mgo: float = 0.0
    s: float = 0.0
    organisch: bool = False


def reinnaehrstoffe_kg(
    menge_pro_ha: float,
    flaeche_ha: float,
    gehalt: NaehrstoffGehalt,
) -> Dict[str, float]:
    """Reinnaehrstoff-Zufuhr einer Duengemassnahme [kg je Naehrstoff, gesamt].

    kg Naehrstoff = Produktmenge/ha * Flaeche(ha) * Gehalt%/100.
    """
    product_total = max(menge_pro_ha, 0.0) * max(flaeche_ha, 0.0)
    return {
        "n": round(product_total * gehalt.n / 100.0, 2),
        "p2o5": round(product_total * gehalt.p2o5 / 100.0, 2),
        "k2o": round(product_total * gehalt.k2o / 100.0, 2),
        "mgo": round(product_total * gehalt.mgo / 100.0, 2),
        "s": round(product_total * gehalt.s / 100.0, 2),
    }


@dataclass
class Duengemassnahme:
    """Eine Duengemassnahme fuer die Bilanz (Produktmenge/ha, Flaeche, Gehalte)."""
    menge_pro_ha: float
    flaeche_ha: float
    gehalt: NaehrstoffGehalt
    n_wirksamkeit: float = 1.0  # Anrechenbarer N-Anteil (org. Duenger < 1,0)


def duengebilanz(massnahmen: Iterable[Duengemassnahme]) -> Dict[str, object]:
    """Aggregiert Reinnaehrstoffe ueber Massnahmen und trennt org./mineralisch.

    Liefert Gesamt-Summen je Naehrstoff, die org. und mineralische N-Zufuhr
    sowie die anrechenbare (wirksame) N-Menge.
    """
    total = {k: 0.0 for k in NUTRIENT_KEYS}
    n_org = 0.0
    n_min = 0.0
    n_wirksam = 0.0
    for m in massnahmen:
        rn = reinnaehrstoffe_kg(m.menge_pro_ha, m.flaeche_ha, m.gehalt)
        for k in NUTRIENT_KEYS:
            total[k] += rn[k]
        if m.gehalt.organisch:
            n_org += rn["n"]
        else:
            n_min += rn["n"]
        n_wirksam += rn["n"] * max(0.0, min(m.n_wirksamkeit, 1.0))
    return {
        "reinnaehrstoffe_kg": {k: round(total[k], 2) for k in NUTRIENT_KEYS},
        "n_organisch_kg": round(n_org, 2),
        "n_mineralisch_kg": round(n_min, 2),
        "n_wirksam_kg": round(n_wirksam, 2),
    }


def duev_n_org_check(
    n_organisch_kg: float,
    flaeche_ha: float,
    grenzwert_kg_ha: float = DUEV_N_ORG_LIMIT_KG_HA,
) -> Dict[str, object]:
    """DueV-Pruefung der organischen N-Obergrenze (Default 170 kg N/ha)."""
    ha = flaeche_ha if flaeche_ha > 0 else 1.0
    n_pro_ha = n_organisch_kg / ha
    return {
        "n_organisch_pro_ha": round(n_pro_ha, 2),
        "grenzwert_kg_ha": grenzwert_kg_ha,
        "ueberschritten": n_pro_ha > grenzwert_kg_ha + 1e-9,
        "auslastung_pct": round(n_pro_ha / grenzwert_kg_ha * 100.0, 1) if grenzwert_kg_ha > 0 else None,
    }


def duengebedarf_n(
    sollwert_kg_ha: float,
    nmin_kg_ha: float,
    zuschlaege_kg_ha: float = 0.0,
    abschlaege_kg_ha: float = 0.0,
) -> float:
    """Vereinfachte N-Duengebedarfsermittlung nach DueV (AS-W2-Basis).

    N-Bedarf = Sollwert - Nmin + Zuschlaege - Abschlaege (nicht negativ).
    Zu-/Abschlaege bilden Vorkultur, org. Duengung, Ertragsdifferenz etc. ab.
    """
    bedarf = sollwert_kg_ha - max(nmin_kg_ha, 0.0) + zuschlaege_kg_ha - abschlaege_kg_ha
    return round(max(bedarf, 0.0), 1)
