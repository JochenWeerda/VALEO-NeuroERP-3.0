"""
Naehrstoffvergleich / Stoffstrombilanz (Welle AS-W3).

Fachliche Grundlage: Duengeverordnung (DueV) Naehrstoffvergleich und
Stoffstrombilanzverordnung (StoffBilV). Gegenuebergestellt werden die
Naehrstoff-Zufuhr (Duengung, aus AS-W1-Reinnaehrstoffen) und die
Naehrstoff-Abfuhr ueber das Erntegut (Ertrag x Naehrstoffentzug je dt).

Der Saldo (Zufuhr - Abfuhr) zeigt Ueber-/Unterversorgung. Die Entzugswerte
sind Standard-/Orientierungswerte und ueber ``ENTZUG`` konfigurierbar
(regionale LWK-Tabellen koennen abweichen).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional

# Naehrstoffentzug je dt Haupterntegut [kg/dt] fuer N und P2O5 (Orientierungswerte).
# Quelle: gaengige DueV-/LWK-Entzugstabellen (Haupt- und Nebenprodukt getrennt
# bilanzierbar; hier Hauptprodukt). Bei Bedarf betriebs-/regionsspezifisch setzen.
ENTZUG: Dict[str, Dict[str, float]] = {
    "winterweizen": {"n": 1.9, "p2o5": 0.8},
    "wintergerste": {"n": 1.7, "p2o5": 0.8},
    "winterroggen": {"n": 1.5, "p2o5": 0.8},
    "triticale": {"n": 1.7, "p2o5": 0.8},
    "koernermais": {"n": 1.4, "p2o5": 0.8},
    "silomais": {"n": 0.42, "p2o5": 0.18},   # je dt Frischmasse
    "winterraps": {"n": 3.3, "p2o5": 1.8},
    "zuckerruebe": {"n": 0.18, "p2o5": 0.10}, # je dt Ruebe
    "kartoffel": {"n": 0.35, "p2o5": 0.14},
}

DEFAULT_ENTZUG = {"n": 1.7, "p2o5": 0.8}


def _kultur_key(kultur: Optional[str]) -> str:
    return (kultur or "").strip().lower().replace(" ", "").replace("-", "")


def naehrstoffabfuhr_kg(
    kultur: Optional[str],
    ertrag_dt_ha: float,
    flaeche_ha: float,
    entzug: Optional[Dict[str, Dict[str, float]]] = None,
) -> Dict[str, float]:
    """Naehrstoffabfuhr ueber das Haupterntegut [kg N/P2O5, gesamt]."""
    table = entzug or ENTZUG
    key = _kultur_key(kultur)
    ez = next((v for k, v in table.items() if k in key or key in k), DEFAULT_ENTZUG) if key else DEFAULT_ENTZUG
    menge = max(ertrag_dt_ha, 0.0) * max(flaeche_ha, 0.0)
    return {"n": round(menge * ez["n"], 2), "p2o5": round(menge * ez["p2o5"], 2)}


@dataclass
class SchlagStrom:
    """Zufuhr (aus Duengung) und Erntedaten eines Schlags fuer die Bilanz."""
    n_zufuhr_kg: float = 0.0
    p2o5_zufuhr_kg: float = 0.0
    kultur: Optional[str] = None
    ertrag_dt_ha: float = 0.0
    flaeche_ha: float = 0.0


def stoffstrombilanz(stroeme: Iterable[SchlagStrom]) -> Dict[str, object]:
    """Aggregiert Zufuhr/Abfuhr/Saldo fuer N und P2O5 ueber mehrere Schlaege."""
    n_zu = n_ab = p_zu = p_ab = 0.0
    for s in stroeme:
        n_zu += s.n_zufuhr_kg
        p_zu += s.p2o5_zufuhr_kg
        ab = naehrstoffabfuhr_kg(s.kultur, s.ertrag_dt_ha, s.flaeche_ha)
        n_ab += ab["n"]
        p_ab += ab["p2o5"]
    return {
        "n": {"zufuhr_kg": round(n_zu, 2), "abfuhr_kg": round(n_ab, 2), "saldo_kg": round(n_zu - n_ab, 2)},
        "p2o5": {"zufuhr_kg": round(p_zu, 2), "abfuhr_kg": round(p_ab, 2), "saldo_kg": round(p_zu - p_ab, 2)},
    }
