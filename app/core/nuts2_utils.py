"""NUTS-2 region utilities — PLZ validation and DE postal-code → NUTS-2 derivation."""

from __future__ import annotations

import re
from typing import Optional


def validate_nuts2_code(nuts2_code: Optional[str]) -> Optional[str]:
    """Validiert NUTS-2-Code Format (2 Buchstaben + 1-2 Ziffern, z.B. DE12)."""
    if not nuts2_code:
        return None
    nuts2_code = nuts2_code.strip().upper()
    if not re.match(r"^[A-Z]{2}[0-9]{1,2}$", nuts2_code):
        raise ValueError(
            f"Invalid NUTS-2 code format: {nuts2_code}. "
            "Expected format: 2 letters + 1-2 digits (e.g., DE12)"
        )
    return nuts2_code


def derive_nuts2_from_postal_code(postal_code: Optional[str], country_code: str = "DE") -> Optional[str]:
    """
    Leitet NUTS-2-Code aus PLZ ab (nur Deutschland).

    Basierend auf Eurostat NUTS 2021 correspondence tables.
    Referenz: https://ec.europa.eu/eurostat/web/nuts/correspondence-tables
    """
    if not postal_code or country_code != "DE":
        return None

    clean = postal_code.strip().replace(" ", "")
    if not clean.isdigit() or len(clean) != 5:
        return None

    p = int(clean)

    # Baden-Württemberg
    if 70100 <= p <= 70699:
        return "DE11"  # Stuttgart
    if 76100 <= p <= 77699:
        return "DE12"  # Karlsruhe
    if 79000 <= p <= 79999:
        return "DE13"  # Freiburg
    if 72000 <= p <= 72999:
        return "DE14"  # Tübingen

    # Bayern
    if 80000 <= p <= 83999:
        return "DE21"  # Oberbayern
    if 90000 <= p <= 90999:
        return "DE21"
    if 84000 <= p <= 84999:
        return "DE22"  # Niederbayern
    if 94000 <= p <= 94499:
        return "DE22"
    if 85000 <= p <= 85999:
        return "DE23"  # Oberpfalz
    if 92000 <= p <= 92999:
        return "DE23"
    if 95000 <= p <= 95499:
        return "DE24"  # Oberfranken
    if 90500 <= p <= 91499:
        return "DE25"  # Mittelfranken
    if 97000 <= p <= 97499:
        return "DE25"
    if 97500 <= p <= 97999:
        return "DE26"  # Unterfranken
    if 86000 <= p <= 87999:
        return "DE27"  # Schwaben

    # Berlin
    if 10000 <= p <= 14199:
        return "DE30"

    # Brandenburg
    if 14400 <= p <= 14999:
        return "DE40"
    if 15000 <= p <= 16999:
        return "DE40"

    # Bremen
    if 28000 <= p <= 28999:
        return "DE50"

    # Hamburg
    if 20000 <= p <= 22999:
        return "DE60"

    # Hessen
    if 64200 <= p <= 65999:
        return "DE70"  # Darmstadt
    if 35000 <= p <= 36999:
        return "DE71"  # Gießen
    if 34000 <= p <= 34999:
        return "DE72"  # Kassel
    if 37000 <= p <= 37999:
        return "DE72"

    # Mecklenburg-Vorpommern
    if 17000 <= p <= 19999:
        return "DE80"

    # Niedersachsen
    if 38100 <= p <= 38999:
        return "DE91"  # Braunschweig
    if 30000 <= p <= 31999:
        return "DE92"  # Hannover
    if 29000 <= p <= 29999:
        return "DE93"  # Lüneburg
    if 26000 <= p <= 28999:
        return "DE94"  # Weser-Ems
    if 49000 <= p <= 49999:
        return "DE94"

    # Nordrhein-Westfalen
    if 40000 <= p <= 41499:
        return "DEA1"  # Düsseldorf
    if 45400 <= p <= 45999:
        return "DEA1"
    if 41500 <= p <= 42999:
        return "DEA2"  # Köln
    if 50000 <= p <= 51999:
        return "DEA2"
    if 57000 <= p <= 57999:
        return "DEA2"
    if 44000 <= p <= 44399:
        return "DEA3"  # Münster
    if 46000 <= p <= 46999:
        return "DEA3"
    if 48000 <= p <= 48999:
        return "DEA3"
    if 32000 <= p <= 33999:
        return "DEA4"  # Detmold
    if 58000 <= p <= 59999:
        return "DEA5"  # Arnsberg

    # Rheinland-Pfalz
    if 55000 <= p <= 56999:
        return "DEB1"  # Koblenz
    if 54200 <= p <= 54999:
        return "DEB2"  # Trier
    if 55100 <= p <= 55299:
        return "DEB3"  # Rheinhessen-Pfalz
    if 67000 <= p <= 67999:
        return "DEB3"

    # Saarland
    if 66000 <= p <= 66999:
        return "DEC0"

    # Sachsen
    if 1000 <= p <= 1999:
        return "DED2"   # Dresden
    if 8000 <= p <= 9999:
        return "DED4"   # Chemnitz
    if 4000 <= p <= 4999:
        return "DED5"   # Leipzig

    # Sachsen-Anhalt
    if 6000 <= p <= 6999:
        return "DEE0"
    if 38000 <= p <= 39999:
        return "DEE0"

    # Schleswig-Holstein
    if 23000 <= p <= 25999:
        return "DEF0"
    if 2000 <= p <= 2999:
        return "DEF0"

    # Thüringen
    if 7000 <= p <= 7999:
        return "DEG0"
    if 98000 <= p <= 99999:
        return "DEG0"

    # Fallback: Bundesland-basiert
    if 68000 <= p <= 69999:
        return "DE12"   # Karlsruhe (BW)
    if 70000 <= p <= 77999:
        return "DE11"   # Stuttgart (BW)
    if 78000 <= p <= 79999:
        return "DE13"   # Freiburg (BW)
    if 80000 <= p <= 86999:
        return "DE21"   # Oberbayern
    if 87000 <= p <= 87999:
        return "DE27"   # Schwaben
    if 90000 <= p <= 92999:
        return "DE25"   # Mittelfranken
    if 93000 <= p <= 93999:
        return "DE23"   # Oberpfalz
    if 94000 <= p <= 96999:
        return "DE22"   # Niederbayern
    if 97000 <= p <= 97999:
        return "DE26"   # Unterfranken
    if 40000 <= p <= 47999:
        return "DEA1"   # Düsseldorf (NRW)
    if 34000 <= p <= 36999:
        return "DE72"   # Kassel (Hessen)
    if 37000 <= p <= 39999:
        return "DE71"   # Gießen (Hessen)
    if 55000 <= p <= 65499:
        return "DE70"   # Darmstadt (Hessen)
    if 27000 <= p <= 31999:
        return "DE94"   # Weser-Ems (Niedersachsen)
    if 37000 <= p <= 38999:
        return "DE94"

    return None
