"""
Rationsoptimierung API  (GfE 2023 / DLG-Futterwerttabellen Stand Juli 2025)

Primär: Proxy zum externen Rationsoptimierungs-Microservice (RATIONS_OPTIMIZATION_URL).
Fallback: Interner LP-Solver (scipy.optimize.linprog) auf Basis von
  • Energiesystem:  Umsetzbare Energie (ME_FAN1) nach GfE 2023 / dreistufiges Verfahren
  • Proteinsystem:  dünndarmverdauliches Protein (sidP_FAN1) nach GfE 2023
  • Futterwerte:    DLG-Futterwerttabellen Wiederkäuer, Stand Juli 2025
  • Regeln:         DLG-Information 01|2023 (Rationsoptimierung und Fütterungskontrolle)

Architektur:
  1. Futtermittel-Referenzdatenbank: DLG-Tabellen 2025, geladen aus JSON-Export
  2. Bedarfsmodell: GfE 2023 ME+sidP je Tiergruppe / Laktationsstadium / Leistung
  3. LP-Optimierungsmodell: Kostenminimum mit harten Nebenbedingungen
  4. Kontrollschicht: DLG 01|2023 – aNDFomGF, pabKH, XL, RMD, Strukturindex
  5. Erklärschicht: Warnungen und Begründungen im Response
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Literal, Optional, Set, Tuple

from fastapi import APIRouter, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel


logger = logging.getLogger(__name__)

router = APIRouter(tags=["agrar", "rations-optimization"])

# Refactor 2026-04-23: HTTP-Proxy ausgelagert nach app.agrar.rations.http.proxy.
# Re-Exports halten die oeffentliche Schnittstelle stabil (Tests patchen z. T.
# ``rations_optimization.get_rations_base_url``).
from app.agrar.rations.http.proxy import (  # noqa: E402,F401
    RATIONS_TIMEOUT as RATIONS_TIMEOUT,
    get_rations_base_url as get_rations_base_url,
    _rations_api_key as _rations_api_key,
)

# Backwards-compat alias (interne Altaufrufer).
_rations_base_url = get_rations_base_url  # noqa: E305


# Refactor 2026-04-23: DLG-JSON-Pfadaufloesung ausgelagert
from app.agrar.rations.repository.dlg_loader import _dlg_json_path as _dlg_json_path  # noqa: E402

# Refactor 2026-04-23 (Schritt 2): Zentrale Rations-Aggregation
from app.agrar.rations.response import (  # noqa: E402,F401
    RationAggregates,
    aggregate_ration,
)

# Refactor 2026-04-23 (Schritt 3): Constraint-Registry statt Magic-Index
from app.agrar.rations.solver import (  # noqa: E402,F401
    CONSTR_ANDFOM_GF_GEQ as _CONSTR_ANDFOM_GF_GEQ,
    CONSTR_ANDFOM_TOT_GEQ as _CONSTR_ANDFOM_TOT_GEQ,
    CONSTR_ANDFOM_TOT_LEQ as _CONSTR_ANDFOM_TOT_LEQ,
    CONSTR_CA_LEQ as _CONSTR_CA_LEQ,
    CONSTR_CP_DENSITY as _CONSTR_CP_DENSITY,
    CONSTR_DMI_GEQ as _CONSTR_DMI_GEQ,
    CONSTR_DMI_LEQ as _CONSTR_DMI_LEQ,
    CONSTR_ME_ABS_LEQ as _CONSTR_ME_ABS_LEQ,
    CONSTR_ME_DENSITY as _CONSTR_ME_DENSITY,
    CONSTR_ME_GEQ as _CONSTR_ME_GEQ,
    CONSTR_MG_LEQ as _CONSTR_MG_LEQ,
    CONSTR_NA_LEQ as _CONSTR_NA_LEQ,
    CONSTR_P_LEQ as _CONSTR_P_LEQ,
    CONSTR_PABKH_LEQ as _CONSTR_PABKH_LEQ,
    CONSTR_RMD_DENSITY as _CONSTR_RMD_DENSITY,
    CONSTR_SIDP_GEQ as _CONSTR_SIDP_GEQ,
    CONSTR_XL_DENSITY as _CONSTR_XL_DENSITY,
    ConstraintRegistry as _NewConstraintRegistry,
    Feed as _SolverFeed,
)
from app.agrar.rations.solver.lp_constraints import (  # noqa: E402
    build_lp_constraint_matrix as _build_lp_constraint_matrix,
)


from app.agrar.rations.http.proxy import (  # noqa: E402,F401
    _tenant_from_request as _tenant_from_request,
    _proxy_request as _proxy_request,
)


# ---------------------------------------------------------------------------
# DLG 2025 Feed Database
# ---------------------------------------------------------------------------
#
# Jedes Futtermittel-Dict enthält (alle Werte je kg TM sofern nicht anders):
#   id, name, group, futterart, konservierung
#   dm_frac        – Trockenmassegehalt (g/kg → /1000)
#   price          – Preis €/kg TM (Schätzwert, überschreibbar)
#   forage         – True = Grundfutter/Grobfutter (aNDFomGF-relevant)
#   min_kg, max_kg – LP-Grenzen (kg TM/d)
#   me             – ME_FAN1  [MJ/kg TM]  GfE 2023
#   sidp           – sidP_FAN1 [g/kg TM]  dünndarmverdauliches Protein GfE 2023
#   cp             – Rohprotein XP [g/kg TM]
#   ndf            – aNDFom    [g/kg TM]
#   adf            – ADFom     [g/kg TM]
#   st             – Stärke    [g/kg TM]
#   bst            – beständige Stärke [g/kg TM]
#   zu             – Zucker (ZU) [g/kg TM]
#   nfc            – Nicht-Faser-KH [g/kg TM]
#   xl             – Rohfett (CL) [g/kg TM]
#   ca             – Calcium   [g/kg TM]
#   p              – Phosphor  [g/kg TM]
#   na             – Natrium   [g/kg TM]
#   mg             – Magnesium [g/kg TM]
#   k              – Kalium    [g/kg TM]
#   dcab           – Dietary Cation Anion Balance [meq/kg TM]
#   edg            – effektiver Proteinabbau (EDG) [% des CP]  @ FAN1
#   rmd            – ruminale mikrobielle Differenz [g N/kg TM] @ FAN1
#   omdfan1        – Verdaulichkeit OM [% OM] @ FAN1
#   ndfd           – Verdaulichkeit aNDFom [% aNDFom]
#   ge             – Bruttoenergie [MJ/kg TM]
#   sidlys         – sidLys_FAN1 [g/kg TM]
#   sidmet         – sidMet_FAN1 [g/kg TM]

def _v(field: Any) -> Optional[float]:
    """Extrahiere numerischen Wert aus JSON-Objekt {'value': ..., 'unit': ...} oder None."""
    if field is None:
        return None
    if isinstance(field, (int, float)):
        return float(field)
    if isinstance(field, dict):
        raw = field.get("value")
        if raw is None or str(raw).strip() in ("", "-", "n.a.", "n.a"):
            return None
        try:
            return float(raw)
        except (ValueError, TypeError):
            return None
    return None


def _dlg_category(futterart: str) -> Tuple[str, bool]:
    """Gibt (Gruppe, ist_Grundfutter) zurück."""
    fa = futterart.lower()
    if "grobfutter" in fa:
        return ("Grundfutter/Grobfutter", True)
    if "saftfutter" in fa:
        return ("Grundfutter/Saftfutter", True)
    if "feuchtkonzentrat" in fa:
        return ("Kraftfutter/Feucht", False)
    if "trockenkonzentrat" in fa:
        return ("Kraftfutter/Trocken", False)
    if "zusatzstoff" in fa:
        return ("Zusatzstoffe", False)
    return ("Sonstige", False)


# Preis-Schätzwerte €/kg TM nach Futtermittelgruppe/-bezeichnung (Marktpreise 04/2026)
# Marktpreise Stand 24.04.2026 (Paschelke GmbH + Wessel Agentur für Agrarprodukte)
# Einheit: €/kg TM — Umrechnung: Marktpreis €/t FM / (DM% × 1000)
# Frachtkosten bereits eingerechnet: ab Brake +2,50 €/dt; ab Hamburg +3,50 €/dt
_PRICE_ESTIMATES: Dict[str, float] = {
    # --- Grundfutter (Eigenproduktion, Richtwerte) ---
    "Maissilage":       0.045,   # Eigenproduktion TMR-Basis
    "Grassilage":       0.060,
    "Heu":              0.130,
    "Luzerne":          0.085,
    "Rübenblatt":       0.040,
    "Stroh":            0.080,
    # --- Getreide / Körner (Wessel Kurz-Info 24.04.2026, frfr. SO/Emsl./Westf.) ---
    "Körnermais":       0.294,   # europ. Mais Brake/HB/Oldenburg 231+25 Fracht = 256 €/t FM / 870 g DM
    "Weizen":           0.237,   # Futterweizen 20,60 €/dt = 206 €/t FM / 870 g DM
    "Gerste":           0.239,   # Futtergerste 20,80 €/dt = 208 €/t FM / 870 g DM
    "Roggen":           0.220,
    "Triticale":        0.225,
    "Hafer":            0.230,
    "Maisschrot":       0.306,   # Maisschrot Brake QM-Milch 241+25=266 €/t FM / 870 g DM
    # --- Eiweißträger (Paschelke 24.04.2026, fot Hamburg/Norddeutschland) ---
    "Soja":             0.450,   # Sojaschrot 44% LP Hamburg 359+35=394/890 = 0,44 (HP etwas mehr)
    "Raps":             0.375,   # Rapsschrot Rostock 308+35=343/890 = 0,39; Mittel gesamt ~0,38
    "Rapsexpeller":     0.357,   # fot Sternberg Mai 325/910 = 0,36 (weniger aufbereitet)
    "Druckexpeller":    0.357,   # Alias Rapsexpeller
    "Sonnenblume":      0.338,   # Sonne HP 36% Brake 276+25=301/890 = 0,34
    "Sonnenblumenschalen": 0.222, # Sojaschalen-Pellets 173+25=198/890 = 0,22
    "Palmkern":         0.271,   # Palmexpeller Brake 224+25=249/920 = 0,27
    "Palmexpeller":     0.271,
    # --- Sonstige Konzentrate ---
    "Melasse":          0.230,   # Rübenmelasse (Markt Apr 26, Anfrage)
    "Melasseschnitzel": 0.200,
    "Pressschnitzel":   0.085,   # T-Schnitzel ab Station ca. 225-295 €/t TM (Mittel)
    "Trockenschnitzel": 0.200,
    "Biertreber":       0.120,   # Saisonware, regional
    "Trester":          0.090,
    "Weizenkleie":      0.190,   # Weizenkleie frfr. SO/Emsl. 18,20 €/dt Ernte 2026
    "Kleie":            0.190,
    # --- Zusatzstoffe ---
    "Mineralfutter":    1.600,
    "Harnstoff":        0.600,
}


def _estimate_price(name: str, futterart: str) -> float:
    name_lower = name.lower()
    for key, price in _PRICE_ESTIMATES.items():
        if key.lower() in name_lower:
            return price
    fa = futterart.lower()
    if "grobfutter" in fa or "saftfutter" in fa:
        return 0.065
    if "feuchtkonzentrat" in fa:
        return 0.140
    if "trockenkonzentrat" in fa:
        return 0.250
    return 0.200


# Faserreiche Co-Produkte nach DLG 01|2025, Kap. 8.2/8.3. Diese Produkte haben
# zwar eine geringere Partikelgroesse als Grobfutter, aber eine hohe aNDFom und
# sind strukturwirksam genug, um als aNDFomGF+CoP gerechnet zu werden.
_STRUCTURAL_COPRODUCT_KEYWORDS = (
    "biertreber",
    "maltreber",
    "malztreber",
    "treber",
    "schlempe",
    "trester",
    "pressschnitzel",
    "nassschnitzel",
    "trockenschnitzel",
    "rübenschnitzel",
    "ruebenschnitzel",
    "zuckerruebenschnitzel",
    "melasseschnitzel",
    "pülpe",
    "puelpe",
    "pulpe",
    "kartoffelpülpe",
    "rueben",  # generische Zuckerrueben-Koppelprodukte (nicht jedoch "rübenblatt")
)


def _is_structural_coproduct(name: str, futterart: str) -> bool:
    """Faserreiches Co-Produkt nach DLG 01|2025?

    Wird in der Planungsgroesse aNDFomGF+CoP mitgerechnet. Grobfutter selbst
    ist KEIN Co-Produkt und wird ueber ``forage=True`` separat gefuehrt.
    """
    n = (name or "").lower()
    # Rübenblattsilage ist Grobfutter (Blatt/Kopf der Ruebe), kein Co-Produkt
    if "rübenblatt" in n or "ruebenblatt" in n or "blattsilage" in n:
        return False
    if any(kw in n for kw in _STRUCTURAL_COPRODUCT_KEYWORDS):
        return True
    return False


# Nass-Saftfutter / CoP: LP nutzt eine **kg-TM/d-Summenplanke** (weich/hart unten).
# DLG Information 01|2025 Kap. 1.1/8.4/Tab. 14: Zuordnung zu Konzentraten,
# dichtebezogene FIKH/pabKH-Logik; keine tabellierte Tagesmenge „Saftfutter gesamt“.
# Ergaenzende **Quellenkette (HTML)** inkl. komponentenspezifischer %-TM-Studienlagen:
_JUICE_WET_CAP_REFERENCES_HTML = """
<ul>
<li>
<a href="https://www.dlg.org/mediacenter/dlg-merkblaetter/dlg-merkblatt-504-leitfaden-zur-proteinbewertung-und-versorgung-von-milchkuehen" target="_blank">DLG-Merkblatt 504 – Proteinbewertung und Versorgung von Milchkühen</a>.
Wichtig: Saftfuttermittel werden bei der Rationsberechnung den Konzentratfuttermitteln zugerechnet.
</li>
<li>
<a href="https://www.kws.com/de/de/beratung/fuetterung/fuetterungs-ratgeber/bereich-ration.html" target="_blank">KWS Fütterungsratgeber – Futterration Milchkuh</a>:
optimaler TM-Gehalt der TMR am Trog 35–45 % TM; nasse Rationen unter 35 % TM können die TM-Aufnahme senken und die Strukturwirksamkeit verschlechtern.
</li>
<li>
<a href="https://www.sciencedirect.com/science/article/pii/S0022030203738880" target="_blank">Journal of Dairy Science – Wet Brewers’ Grain bei Milchkühen</a>:
Versuch mit 15 % Biertreber in der Rations-TM; Leistung und Futteraufnahme waren vergleichbar.
</li>
<li>
<a href="https://www.ncbi.nlm.nih.gov/books/NBK600591/" target="_blank">NASEM / NCBI Bookshelf – Nutrient Requirements of Dairy Cattle: By-Product Feedstuffs</a>:
Pressschnitzel/Beet pulp wurden in Studien bis 24 % der Rations-TM eingesetzt, ohne Milchleistung negativ zu beeinflussen.
</li>
<li>
<a href="https://www.agproud.com/articles/26871-1808-pd-maximizing-dry-matter-intake-when-using-a-tmr" target="_blank">Ag Proud / Progressive Dairy – TMR moisture and dry matter intake</a>:
günstiger Feuchtebereich 35–50 % Wasser; über 50 % Feuchte aus fermentierten Futtermitteln kann die TM-Aufnahme sinken.
</li>
</ul>
<p><strong>Fazit:</strong> Eine harte pauschale Obergrenze „Saftfutter max. x % TM“ findet man selten.
Belastbar ist: TMR nicht zu nass halten, Struktur sichern, und feuchte Nebenprodukte eher komponentenspezifisch begrenzen —
z. B. Biertreber ca. 15 % TM, Pressschnitzel etwa bis 24 % TM als Studien-/Praxisbereich.</p>
""".strip()

_JUICE_WET_CAP_SOFT_KG_DM = 2.0
_JUICE_WET_CAP_HARD_KG_DM = 3.0


def _feed_counts_toward_saftfutter_wet_cap(feed: Dict[str, Any]) -> bool:
    """Position zaehlt zur Summe Saftfutter/nasse CoP (DLG 01|2025 Kap. 1.1).

    Ausgeschlossen: Weide/Grassilage/Gras-Heu (strukturelles Grobfutter),
    Mineralien/Zusatzstoffe. Literaturlinks: siehe ``_JUICE_WET_CAP_REFERENCES_HTML``.
    """
    name_l = (feed.get("name") or "").lower()
    group_l = (feed.get("group") or "").lower()
    fa_l = (feed.get("futterart") or "").lower()
    if "mineral" in group_l or "mineral" in name_l or "zusatzstoff" in fa_l:
        return False
    gk = _grass_feed_kind(feed)
    if gk in ("pasture", "grass_silage", "grass_hay"):
        return False
    if "saftfutter" in group_l or "saftfutter" in fa_l:
        return True
    if bool(feed.get("structural_coproduct")):
        return True
    keywords = (
        "schlempe", "treber", "trester", "pülpe", "pulpe", "puelpe",
        "pressschnitzel", "pressschlempe", "melasse", "molke",
        "biertreber", "dünnschlempe", "duennschlempe", "blattsilage",
        "rübenklein", "ruebenklein", "kleinteile", "extraktionsschrot",
    )
    return any(k in name_l for k in keywords)


# ---------------------------------------------------------------------------
# Gras-/Silage-/Heu-Klassifikation nach TM-Gehalt (fachlich korrekt).
# ---------------------------------------------------------------------------
# Fachliche Grundlage (Futtermittelkunde / DLG-Futterwerttabellen 2025):
#   Frischgras/Weide:    TM < 30 % (typisch 15-25 %)
#   Grassilage:          TM 30-40 % (anaerobe Milchsaeuregaerung)
#   Anwelksilage:        TM 40-50 %
#   Heulage:             TM 50-80 % (trockene Silage, oft Rundballen-HD)
#   Heu:                 TM >= 85 %
# Die DLG-Label "Gras, frisch o. konserviert" fuehren per "KONSERVIERUNG"
# drei Varianten mit exakt diesen TM-Spruengen (175/350/860 g/kg). Deshalb
# ist der TM-Gehalt das **primaere** Klassifikationskriterium - der Name
# dient nur als Rueckfall, falls dm_frac fehlt.
# ---------------------------------------------------------------------------


def _grass_feed_kind(feed: Dict[str, Any]) -> Optional[str]:
    """Klassifiziert ein Gras-/Grobfutter nach TM-Gehalt und Name.

    Rueckgabe einer von:
        "pasture"       - Frischgras / Weide (TM < 30 %)
        "grass_silage"  - Grassilage inkl. Anwelksilage (30 % <= TM < 80 %)
        "grass_hay"     - Heu / Heulage bei Gras (TM >= 80 %)
        None            - weder gras- noch weidebasiert (Mais, Heu, etc.)
    """
    name_l = (feed.get("name") or "").lower()
    # Konserviertes Gras im Namen liefert bereits eine sehr starke Aussage,
    # die ggf. Namens-Mehrdeutigkeit aufloest ("Gras, frisch o. konserviert, siliert").
    name_has_silage_keyword = (
        "grassilage" in name_l
        or (("siliert" in name_l or "konserviert" in name_l) and "gras" in name_l)
        or "anwelksilage" in name_l
        or "heulage" in name_l
    )
    name_has_hay_keyword = ("heu" in name_l and "heulage" not in name_l) or (
        "gras" in name_l and "trocken" in name_l
    )
    name_has_pasture_keyword = (
        "weide" in name_l
        or "frischgras" in name_l
    )
    name_has_gras = "gras" in name_l

    dm = feed.get("dm_frac")
    try:
        dm_f = float(dm) if dm is not None else None
    except (TypeError, ValueError):
        dm_f = None

    # Name-basierte Fallbacks wenn TM-Gehalt fehlt
    if dm_f is None or dm_f <= 0.0:
        if name_has_hay_keyword:
            return "grass_hay"
        if name_has_silage_keyword:
            return "grass_silage"
        if name_has_pasture_keyword or ("gras" in name_l and "frisch" in name_l):
            return "pasture"
        return None

    # Primaere TM-basierte Klassifikation - nur greifen, wenn der Kontext
    # auf Gras/Weide hinweist. Andernfalls koennten Mais-, Heu- oder
    # Kraftfutterzuordnungen falsch ueberschrieben werden.
    if not (name_has_gras or name_has_pasture_keyword or name_has_silage_keyword or name_has_hay_keyword):
        return None

    if dm_f < 0.30:
        return "pasture"
    if dm_f < 0.80:
        return "grass_silage"
    return "grass_hay"


def _max_kg_for(name: str, futterart: str, dm_frac: float) -> float:
    """
    LP-Obergrenze kg TM/d für Milchkuh (TMR ~22 kg TM/d).

    Wichtig: Saftfutter (Nassnebenprodukte) sind maximal 2–4 kg TM/d je Komponente
    erlaubt – DLG-Information 01|25, Tab. 14, praxisübliche TMR-Grenzen.
    Zu hohe Saftfutter-Anteile verursachen: Labmagenverlagerung, Pansenazidose,
    Mangelversorgung mit effektiver Rohfaser (peNDF).
    """
    n = name.lower()
    fa = futterart.lower()

    # Mineralien / Zusatzstoffe
    if "harnstoff" in n:
        return 0.15
    if "mineralfutter" in n or "zusatz" in fa:
        return 0.30

    # Strukturfutter (Grundfutter/Grobfutter)
    if "heu" in n:
        return 5.0
    if "stroh" in n:
        return 2.5
    if "luzerne" in n and "siliert" not in n:
        return 4.0
    if "maissilage" in n or ("mais" in n and "siliert" in n):
        return 14.0
    # Gras-basierte Klassifikation primaer ueber TM-Gehalt (fachlich korrekt):
    #   TM < 30 %  -> Frischgras/Weide        -> 14 kg TM/d
    #   TM 30-80 % -> Grassilage (inkl. Anwelksilage/Heulage) -> 12 kg TM/d
    #   TM >= 85 % -> Heu (wird oben ueber "heu" im Namen erfasst, 5 kg TM/d)
    # Reihenfolge wichtig: Silage vor Weide pruefen.
    _gk = _grass_feed_kind({"name": name, "dm_frac": dm_frac})
    if _gk == "grass_silage":
        return 12.0
    if "ganzpflanzensil" in n or "gps" in n:
        return 8.0
    if _gk == "pasture":
        # Planungs-RICHTWERT (nicht starre Obergrenze) fuer Weideaufnahme.
        # DLG-Merkblatt 417: Hochleistungs-Standweide praxistypisch ca.
        # 10-12 kg TM/d, Spitzenaufnahme bei 24/7-Kurzrasen bis 13-14 kg.
        # Default 12 kg TM/d als mittlerer Planungswert - die tatsaechliche
        # Weideaufnahme haengt von Jahreszeit, Aufwuchs, Zuteilung, Besatz,
        # Wetter und Ergaenzungsfutter ab. Saisonale Feinsteuerung erfolgt
        # aktuell ueber `season_profile` und policy_overrides; eine dedi-
        # zierte Weideaufnahme-/Substitutions-Logik ist als Folgeslice
        # vorgesehen (User-Review 2026-04-23, §2).
        # Die TMR-spezifische Deckelung (4 kg TM/d) erfolgt spaeter im
        # Solver nur fuer feeding_type=TMR.
        return 12.0
    if _gk == "grass_hay":
        return 5.0

    # Saftfutter – Nassnebenprodukte: einzeln max 3 kg TM/d (DLG Praxisempfehlung)
    # Gefährlich: zu viel → NDF-Dichte sinkt, peNDF unzureichend, Labmagenverlagerung
    if "biertreber" in n:
        return 3.0
    if "trester" in n:
        return 2.5
    if "schlempe" in n:
        return 3.0
    if "kartoffel" in n and ("pülpe" in n or "pulpe" in n or "schlempe" in n):
        return 2.0
    if "rübenblatt" in n or "rübensilage" in n or "blattsilage" in n:
        return 3.0
    if "pressschnitzel" in n or "nassschnitzel" in n:
        return 4.0
    if "melasse" in n:
        return 1.5
    if "molke" in n:
        return 2.0
    if "bierhefe" in n:
        return 1.5

    # Generisches Saftfutter: max 2.5 kg TM (Vorsicht – unbekannte Nebenprodukte)
    if "saftfutter" in fa:
        return 2.5

    # Grobfutter (echtes Raufutter, nicht Nassnebenprodukt)
    if "grobfutter" in fa:
        return 8.0

    # Kraftfutter/Konzentrate: einzeln max 3.5 kg TM, Gesamtbegrenzung durch DMI+Strukturconstraints
    return 3.5


def _load_dlg_feeds_from_json(json_path: str) -> List[Dict[str, Any]]:
    """Lade DLG-Futterwerttabellen 2025 aus JSON-Exportdatei."""
    with open(json_path, encoding="utf-8") as f:
        raw = json.load(f)

    feeds = []
    for entry in raw:
        futterart = entry.get("FUTTERART", "")
        name = entry.get("FUTTERMITTELBEZEICHNUNG") or entry.get("KURZBEZEICHNUNG", "")
        konservierung = entry.get("KONSERVIERUNG", "")
        group, is_forage = _dlg_category(futterart)

        dm_raw = _v(entry.get("TMGEHALT"))
        if dm_raw is None:
            continue
        dm_frac = dm_raw / 1000.0  # g/kg → fraction

        me = _v(entry.get("MEFAN1"))
        if me is None:
            continue  # ohne ME-Wert nicht sinnvoll

        sidp = _v(entry.get("SIDPFAN1"))
        cp = _v(entry.get("CP")) or 0.0
        ndf = _v(entry.get("ANDFOM")) or 0.0
        adf = _v(entry.get("ADFOM")) or 0.0
        st = _v(entry.get("STAERKE")) or 0.0
        bst = _v(entry.get("BESTSTAERKE")) or 0.0
        zu = _v(entry.get("ZUCKER")) or 0.0
        nfc = _v(entry.get("NFC")) or 0.0
        xl = _v(entry.get("CL")) or 0.0
        ca = _v(entry.get("CAMIN")) or _v(entry.get("CA")) or 0.0
        p = _v(entry.get("P")) or 0.0
        na = _v(entry.get("NA")) or 0.0
        mg = _v(entry.get("MG")) or 0.0
        k = _v(entry.get("K")) or 0.0
        dcab = _v(entry.get("DCAB"))
        edg = _v(entry.get("EDGFAN1"))
        rmd = _v(entry.get("RMDFAN1"))
        omdfan1 = _v(entry.get("OMDFAN1"))
        ndfd = _v(entry.get("NDFD"))
        ge = _v(entry.get("GE"))
        sidlys = _v(entry.get("SIDLYSFAN1"))
        sidmet = _v(entry.get("SIDMETFAN1"))

        # sidP Fallback aus MCP + UDP wenn SIDPFAN1 nicht vorhanden
        if sidp is None and edg is not None and omdfan1 is not None:
            # Vereinfachte Berechnung nach GfE 2023
            # MCP = DOM × 150 g/kg, DOM = OM × OMD/100
            ca_pct = (_v(entry.get("CA")) or 0.0) / 10.0  # g/kg TM → %
            om = 1000.0 - ca_pct * 10  # rough OM estimate
            dom = om * (omdfan1 / 100.0)
            mcp = dom / 1000.0 * 150.0  # g/kg TM
            sid_mcp = mcp * 0.78 * 0.85
            udp_frac = (100.0 - edg) / 100.0
            sidudp_pct = _v(entry.get("SIDUDP")) or 85.0
            sid_udp = cp * udp_frac * sidudp_pct / 100.0
            sidp = sid_mcp + sid_udp

        price = _estimate_price(name, futterart)
        lid = str(entry.get("LID", ""))
        primaryid = str(entry.get("PRIMARYID") or "")
        # Eindeutige ID: PRIMARYID bevorzugen, sonst LID + Konservierung-Suffix
        if primaryid:
            feed_id = f"dlg_{primaryid}"
        else:
            konserv_slug = konservierung.replace(" ", "_").replace("/", "_")[:12] if konservierung else ""
            feed_id = f"dlg_{lid}_{konserv_slug}" if konserv_slug else f"dlg_{lid}"

        feeds.append({
            "id": feed_id,
            "lid": lid,
            "name": name,
            "konservierung": konservierung,
            "group": group,
            "futterart": futterart,
            "forage": is_forage,
            # DLG 01|2025: Faserreiche Co-Produkte (Biertreber, Rueben-/Pressschnitzel,
            # Schlempe, Pulpe ...) zaehlen gemeinsam mit dem Grobfutter in die
            # Planungsgroesse aNDFomGF+CoP. Siehe ``_is_structural_coproduct``.
            "structural_coproduct": _is_structural_coproduct(name, futterart),
            "dm_frac": dm_frac,
            "price": price,
            "min_kg": 0.0,
            "max_kg": _max_kg_for(name, futterart, dm_frac),
            "me": me,
            "sidp": sidp or 0.0,
            "cp": cp,
            "ndf": ndf,
            "adf": adf,
            "st": st,
            "bst": bst,
            "zu": zu,
            "nfc": nfc,
            "xl": xl,
            "ca": ca,
            "p": p,
            "na": na,
            "mg": mg,
            "k": k,
            "dcab": dcab,
            "edg": edg,
            "rmd": rmd,
            "omdfan1": omdfan1,
            "ndfd": ndfd,
            "ge": ge,
            "sidlys": sidlys,
            "sidmet": sidmet,
        })

    return feeds


# Kuratierter Fallback-Datensatz (DLG 2025-Werte, GfE 2023 ME+sidP)
# Quellen: DLG-Futterwerttabellen Wiederkäuer Stand Juli 2025, Tabellen A/B
_FEEDS_FALLBACK: List[Dict[str, Any]] = [
    # ── Grundfutter / Grobfutter ──────────────────────────────────────────
    dict(id="maiz_sil_mid",  lid="50", name="Maissilage (OMD mittel)",
         konservierung="siliert", group="Grundfutter/Grobfutter", futterart="Grundfutter, Grobfutter",
         forage=True, dm_frac=0.340, price=0.045, min_kg=0.0, max_kg=14.0,
         me=11.2, sidp=78.0, cp=80.0,  ndf=401.0, adf=230.0, st=309.0, bst=31.0, zu=0.0,
         nfc=280.0, xl=30.0, ca=1.8, p=2.1, na=0.2, mg=1.0, k=11.0, dcab=-20.0,
         edg=65.0, rmd=None, omdfan1=72.0, ndfd=54.0, ge=18.4, sidlys=3.8, sidmet=1.1),
    dict(id="grass_sil_good", lid="32", name="Grassilage (OMD gut)",
         konservierung="siliert", group="Grundfutter/Grobfutter", futterart="Grundfutter, Grobfutter",
         forage=True, dm_frac=0.350, price=0.060, min_kg=0.0, max_kg=12.0,
         me=11.2, sidp=108.0, cp=171.0, ndf=450.0, adf=260.0, st=0.0,  bst=0.0, zu=50.0,
         nfc=200.0, xl=35.0, ca=7.5, p=3.8, na=1.3, mg=2.0, k=29.0, dcab=380.0,
         edg=78.0, rmd=6.0, omdfan1=81.0, ndfd=81.0, ge=18.0, sidlys=7.5, sidmet=2.1),
    dict(id="hay_good",      lid="15", name="Heu (Verdaulichkeit gut)",
         konservierung="getrocknet/Heu", group="Grundfutter/Grobfutter", futterart="Grundfutter, Grobfutter",
         forage=True, dm_frac=0.860, price=0.130, min_kg=0.0, max_kg=5.0,
         me=9.3,  sidp=90.0, cp=189.0, ndf=605.0, adf=336.0, st=0.0,  bst=0.0, zu=89.0,
         nfc=170.0, xl=32.0, ca=7.4, p=3.1, na=1.5, mg=1.5, k=25.0, dcab=400.0,
         edg=65.0, rmd=4.0, omdfan1=65.0, ndfd=67.0, ge=18.4, sidlys=5.5, sidmet=1.5),
    dict(id="luz_sil",       lid="48", name="Luzernegras-Silage",
         konservierung="siliert", group="Grundfutter/Grobfutter", futterart="Grundfutter, Grobfutter",
         forage=True, dm_frac=0.350, price=0.070, min_kg=0.0, max_kg=6.0,
         me=9.9,  sidp=102.0, cp=157.0, ndf=493.0, adf=285.0, st=0.0,  bst=0.0, zu=40.0,
         nfc=180.0, xl=27.0, ca=16.0, p=2.9, na=0.9, mg=2.2, k=27.0, dcab=400.0,
         edg=72.0, rmd=4.0, omdfan1=67.0, ndfd=68.0, ge=18.4, sidlys=5.8, sidmet=1.4),
    dict(id="mel_schnitz",   lid="94", name="Melasseschnitzel (getr.)",
         konservierung="getrocknet", group="Grundfutter/Saftfutter", futterart="Grundfutter, Grobfutter",
         forage=True, dm_frac=0.900, price=0.195, min_kg=0.0, max_kg=3.0,
         me=13.1, sidp=70.0, cp=96.0,  ndf=399.0, adf=200.0, st=0.0,  bst=0.0, zu=200.0,
         nfc=430.0, xl=13.0, ca=11.0, p=0.8, na=2.0, mg=2.5, k=10.0, dcab=250.0,
         edg=80.0, rmd=None, omdfan1=88.0, ndfd=88.0, ge=17.5, sidlys=3.5, sidmet=0.9),
    # ── Kraftfutter – Energie ─────────────────────────────────────────────
    dict(id="corn_grain",    lid="88", name="Körnermais",
         konservierung="", group="Kraftfutter/Trocken", futterart="Konzentratfutter, Trockenkonzentrate, Einzelfutter",
         forage=False, dm_frac=0.880, price=0.210, min_kg=0.0, max_kg=4.0,
         me=13.3, sidp=72.0, cp=93.0,  ndf=115.0, adf=28.0,  st=711.0, bst=71.0, zu=0.0,
         nfc=752.0, xl=52.0, ca=0.3, p=3.2, na=0.1, mg=1.2, k=4.0, dcab=-60.0,
         edg=68.0, rmd=None, omdfan1=90.0, ndfd=66.0, ge=18.4, sidlys=2.4, sidmet=1.6),
    dict(id="wheat",         lid="119", name="Weizen",
         konservierung="", group="Kraftfutter/Trocken", futterart="Konzentratfutter, Trockenkonzentrate, Einzelfutter",
         forage=False, dm_frac=0.880, price=0.220, min_kg=0.0, max_kg=3.0,
         me=13.6, sidp=100.0, cp=134.0, ndf=142.0, adf=33.0,  st=622.0, bst=62.0, zu=0.0,
         nfc=660.0, xl=25.0, ca=0.5, p=3.2, na=0.2, mg=1.2, k=5.0, dcab=-90.0,
         edg=87.0, rmd=None, omdfan1=87.0, ndfd=66.0, ge=18.5, sidlys=2.7, sidmet=1.7),
    dict(id="barley",        lid="82", name="Gerste",
         konservierung="", group="Kraftfutter/Trocken", futterart="Konzentratfutter, Trockenkonzentrate, Einzelfutter",
         forage=False, dm_frac=0.880, price=0.200, min_kg=0.0, max_kg=3.0,
         me=13.4, sidp=88.0, cp=123.0, ndf=243.0, adf=56.0,  st=506.0, bst=51.0, zu=0.0,
         nfc=580.0, xl=33.0, ca=0.7, p=4.0, na=0.2, mg=1.2, k=5.0, dcab=-80.0,
         edg=82.0, rmd=None, omdfan1=87.0, ndfd=66.0, ge=18.3, sidlys=3.2, sidmet=1.6),
    # ── Kraftfutter – Protein ─────────────────────────────────────────────
    dict(id="raps_meal",     lid="97", name="Rapsextraktionsschrot",
         konservierung="", group="Kraftfutter/Trocken", futterart="Konzentratfutter, Trockenkonzentrate, Einzelfutter",
         forage=False, dm_frac=0.890, price=0.270, min_kg=0.0, max_kg=2.5,
         me=11.9, sidp=190.0, cp=385.0, ndf=298.0, adf=185.0, st=72.0,  bst=0.0, zu=0.0,
         nfc=120.0, xl=35.0, ca=8.7, p=11.9, na=1.0, mg=5.0, k=13.0, dcab=-50.0,
         edg=68.0, rmd=None, omdfan1=80.0, ndfd=54.0, ge=19.3, sidlys=14.0, sidmet=5.8),
    dict(id="soy_meal",      lid="105", name="Sojaextraktionsschrot",
         konservierung="", group="Kraftfutter/Trocken", futterart="Konzentratfutter, Trockenkonzentrate, Einzelfutter",
         forage=False, dm_frac=0.890, price=0.450, min_kg=0.0, max_kg=2.0,
         me=13.5, sidp=250.0, cp=500.0, ndf=154.0, adf=88.0,  st=68.0,  bst=0.0, zu=0.0,
         nfc=300.0, xl=18.0, ca=3.1, p=7.0, na=0.4, mg=3.0, k=24.0, dcab=40.0,
         edg=72.0, rmd=None, omdfan1=86.0, ndfd=83.0, ge=19.4, sidlys=23.0, sidmet=5.0),
    # ── Mineralfutter ─────────────────────────────────────────────────────
    dict(id="mineral_hmk",   lid="min1", name="Mineralfutter HMK (25/5)",
         konservierung="", group="Zusatzstoffe", futterart="Konzentratfutter, Trockenkonzentrate, Zusatzstoffe",
         forage=False, dm_frac=0.980, price=1.600, min_kg=0.10, max_kg=0.20,
         me=0.0, sidp=0.0, cp=0.0, ndf=0.0, adf=0.0, st=0.0, bst=0.0, zu=0.0,
         nfc=0.0, xl=0.0, ca=220.0, p=40.0, na=30.0, mg=30.0, k=0.0, dcab=None,
         edg=None, rmd=None, omdfan1=None, ndfd=None, ge=None, sidlys=None, sidmet=None),
    # ── Proteinreiche Nebenprodukte ───────────────────────────────────────
    dict(id="biertreber_nass", lid="bt1", name="Biertreber, naß",
         konservierung="frisch", group="Grundfutter/Saftfutter", futterart="Grundfutter, Saftfutter",
         forage=False, dm_frac=0.240, price=0.090, min_kg=0.0, max_kg=4.0,
         me=11.5, sidp=132.0, cp=240.0, ndf=470.0, adf=185.0, st=0.0, bst=0.0, zu=0.0,
         nfc=130.0, xl=80.0, ca=3.0, p=5.5, na=0.3, mg=2.5, k=0.5, dcab=-30.0,
         edg=58.0, rmd=None, omdfan1=78.0, ndfd=65.0, ge=21.0, sidlys=5.5, sidmet=2.0),
    dict(id="ddgs_mais",      lid="dd1", name="Maisschlempe (DDGS)",
         konservierung="getrocknet", group="Kraftfutter/Trocken", futterart="Konzentratfutter, Trockenkonzentrate, Einzelfutter",
         forage=False, dm_frac=0.890, price=0.230, min_kg=0.0, max_kg=3.0,
         me=12.5, sidp=168.0, cp=285.0, ndf=370.0, adf=140.0, st=0.0, bst=0.0, zu=0.0,
         nfc=180.0, xl=100.0, ca=0.5, p=8.0, na=2.5, mg=3.5, k=12.0, dcab=-100.0,
         edg=52.0, rmd=None, omdfan1=80.0, ndfd=59.0, ge=21.5, sidlys=5.0, sidmet=4.5),
]


# Global feed list – geladen beim ersten Zugriff
_FEEDS_CACHE: Optional[List[Dict[str, Any]]] = None
_SPECIAL_SUPPLEMENTS: List[Dict[str, Any]] = [
    dict(
        id="special_weide_mg_mineral",
        lid="sp1",
        name="Weidemineral Mg/Na Ausgleich",
        konservierung="trocken",
        group="Zusatzstoffe",
        futterart="Konzentratfutter, Trockenkonzentrate, Zusatzstoffe",
        forage=False,
        dm_frac=0.970,
        price=0.780,
        min_kg=0.0,
        max_kg=0.20,
        me=0.5,
        sidp=0.0,
        cp=0.0,
        ndf=0.0,
        adf=0.0,
        st=0.0,
        bst=0.0,
        zu=0.0,
        nfc=0.0,
        xl=0.0,
        ca=140.0,
        p=15.0,
        na=90.0,
        mg=120.0,
        k=0.0,
        dcab=None,
        edg=None,
        rmd=None,
        omdfan1=None,
        ndfd=None,
        ge=None,
        sidlys=None,
        sidmet=None,
        _special="pasture_mg",
    ),
    # Sommer-Pansenpuffer (DLG-Merkblatt 417 / GfE-Workshop 2023):
    # Natriumbicarbonat (NaHCO3) glaettet Pansen-pH-Abfaelle im Sommer, wenn
    # hohe Umgebungstemperaturen zu reduzierter TM-Aufnahme + vermehrtem Hecheln
    # und damit respiratorischer Alkalose fuehren. Wirkt als ruminaler Puffer
    # gegen SARA und deckt gleichzeitig erhoehten Natriumbedarf (Hitzestress)
    # zusammen mit bodenseitigem Elektrolytverlust. Typische Einsatzmenge 150-250 g
    # je Kuh und Tag (entspricht 0,15-0,25 kg TM bei ~99 % TM-Gehalt).
    dict(
        id="special_summer_rumen_buffer",
        lid="sp2",
        name="Pansenpuffer NaHCO3 (Sommerhitze)",
        konservierung="trocken",
        group="Zusatzstoffe",
        futterart="Konzentratfutter, Trockenkonzentrate, Zusatzstoffe",
        forage=False,
        dm_frac=0.990,
        price=0.950,
        min_kg=0.0,
        max_kg=0.25,
        me=0.0,
        sidp=0.0,
        cp=0.0,
        ndf=0.0,
        adf=0.0,
        st=0.0,
        bst=0.0,
        zu=0.0,
        nfc=0.0,
        xl=0.0,
        ca=0.0,
        p=0.0,
        # Natriumgehalt NaHCO3: 22 %; 22 g Na je 100 g Produkt = 220 g/kg TM
        na=220.0,
        mg=0.0,
        k=0.0,
        # DCAB-Effekt (kationenbetonter Puffer)
        dcab=600.0,
        edg=None,
        rmd=None,
        omdfan1=None,
        ndfd=None,
        ge=None,
        sidlys=None,
        sidmet=None,
        _special="summer_buffer",
    ),
    # ---------------------------------------------------------------------------
    # Bypass-Fett / Calcium-Seifen (Typ Megalac®, Bergafat®, Palmit®)
    # ---------------------------------------------------------------------------
    # Pansen-geschütztes Fett: wird nicht im Pansen fermentiert, daher
    # kein Einfluss auf Pansen-pH (SARA-neutral), hohe Energiedichte.
    # Indikation: Frischmelker (NEB), Hochleistung >35 kg Milch,
    # wenn Energiedichte-Grenze durch TM-Kapazität erreicht ist.
    # Quellen: Weiss/Eastridge JDS 2003; DLG-Merkblatt 369 (Fettfütterung).
    # Nährstoffe nach Herstellerangaben Ca-Seifen (Palmöl-Basis):
    #   XL ~830 g/kg TM, ME ~33 MJ/kg TM, Ca ~90 g/kg TM (Ca-Salz-Typ)
    # Preis: Markt 2026 ca. 1.100-1.300 €/t FM (Standard-Bypass-Fett)
    dict(
        id="special_bypass_fat",
        lid="sp3",
        name="Bypass-Fett Ca-Seifen (Pansen-geschützt)",
        konservierung="trocken",
        group="Energieergänzung",
        futterart="Konzentratfutter, Trockenkonzentrate, Fettergänzung",
        forage=False,
        structural_coproduct=False,
        dm_frac=0.970,
        price=1.20,       # €/kg TM; Ca-Seifen-Typ, Markt Apr 2026
        min_kg=0.0,
        max_kg=0.50,      # max 500 g TM/d (DLG-Empfehlung: ≤5% der Rations-TM)
        me=33.0,          # MJ/kg TM — Bypass-Fett, GfE 2023 Koeff. 0,92 × 36 MJ/kg XL
        sidp=0.0,
        cp=0.0,
        ndf=0.0,
        adf=0.0,
        st=0.0,
        bst=0.0,
        zu=0.0,
        nfc=0.0,
        xl=830.0,         # g/kg TM Rohfett (hohe Energiedichte)
        ca=90.0,          # g/kg TM Ca-Seifen-Typ
        p=0.0,
        na=0.0,
        mg=0.0,
        k=0.0,
        dcab=None,
        edg=None,
        rmd=None,
        omdfan1=None,
        ndfd=None,
        ge=None,
        sidlys=0.0,
        sidmet=0.0,
        _special="bypass_fat",
    ),
    # ---------------------------------------------------------------------------
    # Protigrain® (hitzebehandeltes Sojaprotein, hoher Pansen-Bypass-Anteil)
    # ---------------------------------------------------------------------------
    # Herst.: Agrana Stärke GmbH; Behandlung: Feuchthitze + Trocknung →
    # ~85% UDP (undegraded dietary protein), geringer EDG-Wert (~15-18%).
    # Ideal: Deckung des sidP-Bedarfs bei begrenzter Gesamtproteinmenge.
    # Nährstoffe (Herstellerangaben + eigene Analyse-Mittelwerte 2024/25):
    #   CP 430 g/kg TM, sidP 360 g/kg TM, ME 13,4 MJ/kg TM
    # Preise (Paschelke 24.04.2026): Zeitz 240 €/t FM, Drentwede (8-10) 260 €/t FM
    dict(
        id="special_protigrain",
        lid="sp4",
        name="Protigrain® (Bypass-Sojaprotein, hitzebehandelt)",
        konservierung="trocken",
        group="Eiweißergänzung",
        futterart="Konzentratfutter, Trockenkonzentrate, Proteinergänzung",
        forage=False,
        structural_coproduct=False,
        dm_frac=0.900,
        price=0.267,      # €/kg TM; 240 €/t FM / 0,90 DM (Zeitz loko Apr 26)
        min_kg=0.0,
        max_kg=2.0,       # max 2 kg TM/d (Empfehlung: ≤1,5 kg TM für ausgewogenes AA-Profil)
        me=13.4,          # MJ/kg TM
        sidp=360.0,       # g/kg TM — hoher UDP-Anteil (~85%)
        cp=430.0,         # g/kg TM
        ndf=115.0,        # g/kg TM
        adf=55.0,
        st=85.0,
        bst=15.0,
        zu=30.0,
        nfc=260.0,
        xl=28.0,
        ca=3.5,
        p=6.5,
        na=1.5,
        mg=2.5,
        k=22.0,
        dcab=None,
        edg=16.0,         # % EDG (enzymatisch abgebautes Protein im Pansen)
        rmd=None,
        omdfan1=None,
        ndfd=None,
        ge=None,
        sidlys=21.0,      # g/kg TM
        sidmet=5.2,       # g/kg TM
        _special="protigrain",
    ),
]


def _with_special_supplements(feeds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    existing = {feed["id"] for feed in feeds}
    merged = list(feeds)
    for supplement in _SPECIAL_SUPPLEMENTS:
        if supplement["id"] not in existing:
            merged.append(dict(supplement))
    return merged


def _ensure_structural_coproduct_flag(feeds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Setzt ``structural_coproduct`` auf Feeds, die diesen Flag noch nicht tragen.

    Das schliesst den Fallback-Katalog (``_FEEDS_FALLBACK``), die Special-
    Supplemente und alle weiteren Feeds ein, die evtl. aus Testfixtures kommen.
    """
    for feed in feeds:
        if "structural_coproduct" not in feed:
            feed["structural_coproduct"] = _is_structural_coproduct(
                feed.get("name", ""), feed.get("futterart", "")
            )
    return feeds


def _get_feeds() -> List[Dict[str, Any]]:
    global _FEEDS_CACHE
    if _FEEDS_CACHE is not None:
        return _ensure_structural_coproduct_flag(_with_special_supplements(_FEEDS_CACHE))

    json_path = _dlg_json_path()
    if json_path and os.path.isfile(json_path):
        try:
            _FEEDS_CACHE = _load_dlg_feeds_from_json(json_path)
            logger.info("DLG-Futterdatenbank geladen: %d Einträge aus %s", len(_FEEDS_CACHE), json_path)
            return _ensure_structural_coproduct_flag(_with_special_supplements(_FEEDS_CACHE))
        except Exception as exc:
            logger.warning("DLG JSON konnte nicht geladen werden: %s – verwende Fallback", exc)

    _FEEDS_CACHE = _FEEDS_FALLBACK
    logger.info("DLG-Futterdatenbank: Fallback mit %d Einträgen", len(_FEEDS_CACHE))
    return _ensure_structural_coproduct_flag(_with_special_supplements(_FEEDS_CACHE))


# ---------------------------------------------------------------------------
# GfE 2023 Bedarfsberechnung  (ME + sidP, DLG 01|2023 Tabellen 8/11/12)
# ---------------------------------------------------------------------------

class _CowReq(BaseModel):
    """Nährstoffbedarf Milchkuh nach GfE 2023 (ME-Basis, sidP-Protein)."""
    me_mj: float        # Umsetzbare Energie ME_FAN1 [MJ/d]
    sidp_g: float       # dünndarmverdauliches Protein sidP [g/d]  (GfE 2023)
    nel_mj: float       # NEL [MJ/d] – Referenz für Ausgabe
    nxp_g: float        # nXP [g/d]  – Referenz (≈ sidP, GfE 2001)
    dmi_min_kg: float   # Mindest-TM-Aufnahme [kg/d]
    dmi_max_kg: float   # Maximal-TM-Aufnahme [kg/d]
    ndf_min_g: float    # Mindest-aNDFom gesamt [g/d]
    ca_min_g: float     # Mindest-Calcium [g/d]
    p_min_g: float      # Mindest-Phosphor [g/d]
    na_min_g: float     # Mindest-Natrium [g/d]
    mg_min_g: float     # Mindest-Magnesium [g/d]
    k_max_g: float      # Maximum Kalium [g/d] – K/Mg-Antagonismus (GfE-Workshop 2023)
    dmi_target_kg: float  # Ziel-TM-Aufnahme (Mittelpunkt) für peNDF-Lookup


def _gfe_requirements(profile: Dict[str, Any], fani: Optional[float] = None) -> _CowReq:
    """
    GfE 2023 ME + sidP Bedarfsberechnung für Milchkühe.

    Energie (ME-Basis, dreistufiges Verfahren nach GfE 2023):
      ME_Erhaltung = (NEL_maint / k_m) = (0.308 × BW^0.75) / 0.73 = 0.422 × BW^0.75  [MJ/d]
      ME_Milch     = (NEL_milk  / k_l) = (0.38×XL%+ 0.21×XP%+ 0.95) / 0.62 × Milch  [MJ/d]
      Faktor 0.308 = 0.293 × 1.05 (inkl. ~5% Aktivitätszuschlag nach GfE 2001)

    Protein (sidP – dünndarmverdauliches Protein):
      sidP = nXP (GfE 2001 approximation, wird durch GfE 2023 Tab.A3 verfeinert)
      nXP_Erhaltung ≈ 3.47 × BW^0.75 [g/d]  (aus DLG Tab.8 abgeleitet)
      nXP_Milch     ≈ 85 g/kg Milch   [g/d]

    Mineralien (GfE 2001 vereinfacht):
      Ca = 0.031×BW^0.75 + 1.22×Milch;  P = 0.014×BW^0.75 + 0.90×Milch
      Na ≈ 1.5 g/kg TM × DMI;  Mg ≈ 1.5 g/kg TM × DMI

    DMI-Schätzung (Gruber 2004, Deutsche Holstein 675 kg):
      DMI = 0.025×BW + 0.15×Milch  (gilt ab ~60. Laktationstag)
      Optional: ``target_dmi_kg`` überschreibt den Planungsmittelpunkt;
      ``wizard_dmi_min_kg`` / ``wizard_dmi_max_kg`` setzen das TM-Band für den LP.
    """
    bw = float(profile.get("body_weight_kg") or 650)
    milk = float(profile.get("milk_kg_day") or 0)
    fat_pct = float(profile.get("milk_fat_pct") or 4.0)
    prot_pct = float(profile.get("milk_protein_pct") or 3.4)

    bw75 = bw ** 0.75

    # --- Weide-Aktivitaetszuschlag (DLG-Merkblatt 417 / GfE 2001) ---
    # Weidegang erhoeht den Erhaltungsbedarf durch Lauf-, Rupf- und
    # Thermoregulations-Aktivitaet um 10-25 %. Default: +15 % bei echtem
    # Weidegang (feeding_type == "PMR+Weide"). Das ist **zusaetzlich** zu
    # den bereits in 0.308 enthaltenen 5 % Grundaktivitaetszuschlag.
    feeding_type = _normalize_feeding_type(profile.get("feeding_type"))
    pasture_factor = 1.15 if feeding_type == "PMR+Weide" else 1.00

    # --- NEL (für Referenzausgabe) ---
    nel_maint = 0.308 * bw75 * pasture_factor
    nel_milk = (0.38 * fat_pct + 0.21 * prot_pct + 0.95) * milk if milk > 0 else 0.0
    nel_total = nel_maint + nel_milk

    # --- ME (GfE 2023 dreistufig) ---
    me_maint = nel_maint / 0.73         # k_m = 0.73 für laktierende Kühe
    # k_l dichte-abhaengig (GfE 2001, §5): k_l = 0.463 + 0.24·q mit q = ME/GE.
    # Basis: k_l = 0.60 (konservativ, da ME-Dichte beim Planungsaufruf unbekannt).
    # Optional: FANi-Korrektur fuer den FAN-Iterationsloop:
    #   k_l += 0.01 * (FANi - 3.0), begrenzt auf [0.58, 0.64].
    # Bei hoeherem FANi (= mehr Futteraufnahme) steigt die ME-Dichte und damit k_l,
    # was den ME-Bedarf senkt – konsistent mit GfE 2023 Passageraten-Beziehung.
    k_l_planning = 0.60
    if fani is not None and fani > 0:
        k_l_planning = max(0.58, min(0.64, 0.60 + 0.01 * (float(fani) - 3.0)))
    me_milk = nel_milk / k_l_planning if milk > 0 else 0.0
    me_total = me_maint + me_milk

    # --- sidP ≈ nXP (GfE 2001, aus DLG Tab.8 validiert) ---
    # nXP_Milch: DLG Tab.8 (700 kg KM, Laktationstag 100) back-berechnet:
    #   35 kg Milch → 2341 g/d nXP, Erhaltung 468 g/d → 52,8 g/kg Milch für Leistungsanteil
    #   DLG empfiehlt 50-55 g/kg Milch je nach Milchinhaltsstoffen (GfE 2001 Annex).
    nxp_maint = 3.47 * bw75
    nxp_milk = 52.0 * milk     # g/kg Milch (aus DLG Tab.8; früher fälschlich 85 g/kg)
    nxp_total = nxp_maint + nxp_milk

    # sidP-Bedarf: GfE 2023 Tabelle A3 empfiehlt sidP etwas unter nXP (ca. 95%)
    sidp_total = nxp_total * 0.95

    # Physiologische Obergrenze nach DLG Information 01|25 Tabelle 14:
    _DMI_ABS_MAX_KG = 28.5  # DLG Tab. 14 – hartes physiologisches Limit

    # --- DMI (Gruber 2004 vereinfacht), optional durch Wizard-Ziel TM ueberschreibbar ---
    dmi_plan = 0.025 * bw + 0.15 * milk if milk > 0 else 0.025 * bw
    dmi_plan = max(dmi_plan, 8.0)
    td_raw = profile.get("target_dmi_kg")
    if td_raw is not None:
        try:
            td_f = float(td_raw)
            if td_f > 0:
                dmi_plan = max(8.0, min(td_f, _DMI_ABS_MAX_KG))
        except (TypeError, ValueError):
            pass

    dmi_min_kg = dmi_plan * 0.90
    dmi_max_kg = min(dmi_plan * 1.10, _DMI_ABS_MAX_KG)

    wm_raw = profile.get("wizard_dmi_min_kg")
    wx_raw = profile.get("wizard_dmi_max_kg")
    if wm_raw is not None:
        try:
            dmi_min_kg = float(wm_raw)
        except (TypeError, ValueError):
            pass
    if wx_raw is not None:
        try:
            dmi_max_kg = float(wx_raw)
        except (TypeError, ValueError):
            pass

    dmi_min_kg = max(5.0, min(dmi_min_kg, _DMI_ABS_MAX_KG))
    dmi_max_kg = max(dmi_min_kg, min(dmi_max_kg, _DMI_ABS_MAX_KG))
    dmi_target_kg = (dmi_min_kg + dmi_max_kg) / 2.0

    # --- aNDFom-Minimum: 300 g/kg TM × effektive TM-Aufnahme (Bandmittelpunkt) ---
    ndf_min = 300.0 * dmi_target_kg

    # --- Mengenelemente (GfE 2023 / GfE-Workshop 2023) ---
    ca_min = 0.031 * bw75 + 1.22 * milk
    p_min  = 0.014 * bw75 + 0.90 * milk
    # GfE-Workshop 2023: Mg-Bedarf um 25–40% erhöht gegenüber GfE 2001
    # Erhaltung: 0.048 g/kg LM (hochrechnend aus DLG Tab.12 inkl. +30% Zuschlag)
    # Leistung: 0.10 g/kg Milch (GfE 2023 Workshop Präsentation)
    mg_min = (0.048 * bw + 0.10 * milk) if milk > 0 else 0.048 * bw
    na_min = 1.5 * dmi_target_kg   # ~1.5 g/kg TM
    # K/Mg-Antagonismus (GfE-Workshop 2023): max. K-Versorgung 28 g/kg TM
    k_max  = 28.0 * dmi_target_kg

    return _CowReq(
        me_mj=me_total,
        sidp_g=sidp_total,
        nel_mj=nel_total,
        nxp_g=nxp_total,
        dmi_min_kg=dmi_min_kg,
        dmi_max_kg=dmi_max_kg,
        dmi_target_kg=dmi_target_kg,
        ndf_min_g=ndf_min,
        ca_min_g=ca_min,
        p_min_g=p_min,
        na_min_g=na_min,
        mg_min_g=mg_min,
        k_max_g=k_max,
    )


# ---------------------------------------------------------------------------
# LP-Solver  (scipy HiGHS)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# peNDF-Lookup (GfE-Workshop 2023, Schwarz 2022 / Zebeli 2012)
# Minimale peNDF-Dichte [g/kg TM] in Abhängigkeit von Stärke-Dichte und TM-Aufnahme
# Zeilen: Stärke-Dichte-Klassen (g/kg TM), Spalten: TM-Aufnahme-Klassen (kg/d)
# ---------------------------------------------------------------------------
_PENDF_TABLE: Dict[str, Any] = {
    # (staerke_band, dmi_band): peNDF_min_g_kgdm
    # staerke_band: upper bound of starch density class (g/kg TM)
    # dmi_band:     upper bound of TM intake class (kg/d)
    "staerke_bands": [100, 150, 200, 250, 999],   # <100, <150, <200, <250, ≥250
    "dmi_bands":     [16,  20,  24,  999],         # <16, <20, <24, ≥24
    # Matrix[staerke_idx][dmi_idx] = peNDF_min [g/kg TM]
    "matrix": [
        # <100 Stärke  → weniger Säurelast, geringeres peNDF-Minimum
        [155, 145, 140, 135],
        # <150 Stärke
        [165, 158, 150, 145],
        # <200 Stärke
        [175, 168, 160, 155],
        # <250 Stärke
        [185, 178, 170, 165],
        # ≥250 Stärke  → hohe Säurelast, strenge peNDF-Anforderung
        [195, 188, 180, 175],
    ],
}


def _pendf_minimum(staerke_density: float, dmi_kg: float) -> float:
    """Minimale peNDF-Dichte [g/kg TM] aus Lookup-Tabelle (GfE-Workshop 2023).

    Hinweis (DLG 01|2023): peNDF ist fachlich eine Kontroll- und Validierungsgroesse,
    keine praktikable Planungsgroesse fuer die LP-Optimierung. Dieser Wert wird
    deshalb im Ergebnis-Panel als Ampel angezeigt, aber nicht mehr als harte
    Stage-2-Nebenbedingung verwendet. Die eigentliche Planungsgroesse fuer die
    Pansengesundheit ist die aNDFomGF-Dichte (siehe `_andfom_gf_min_target`).
    """
    s_bands = _PENDF_TABLE["staerke_bands"]
    d_bands = _PENDF_TABLE["dmi_bands"]
    matrix  = _PENDF_TABLE["matrix"]
    s_idx = next((i for i, b in enumerate(s_bands) if staerke_density < b), len(s_bands) - 1)
    d_idx = next((i for i, b in enumerate(d_bands) if dmi_kg < b), len(d_bands) - 1)
    return float(matrix[s_idx][d_idx])


# aNDFomGF-Mindestdichte als **primaere Planungsgroesse** (DLG 01|2025, Kap. 8.2).
#
# Neue binaere Kaskade (Tab. 12 / Fussnoten S. 32):
#   pabKH <= 210 g/kg TM  ->  aNDFomGF+CoP >= 200 g/kg TM
#   pabKH  > 210 g/kg TM  ->  aNDFomGF+CoP >= 280 g/kg TM
#   pabKH  > 260 g/kg TM  ->  Warnung "abbaubare Staerke zu hoch" (bST aufstocken)
#
# Dabei ist der Nenner "aNDFomGF+CoP" = aNDFom aus Grobfutter UND faserreichen
# Co-Produkten (Biertreber, Pressschnitzel, Schlempe ...). pabKH = ST+ZU-bST.
#
# Aelteres, staerkeadaptives Modell (DLG 01|2023) bleibt als Fallback erhalten,
# wenn keine pabKH-Dichte uebergeben wird.
# Refactor 2026-04-23: ausgelagert nach app.agrar.rations.constants.dlg2025
from app.agrar.rations.constants.dlg2025 import (
    ANDFOM_GF_BASE_NON_PASTURE as _ANDFOM_GF_BASE_NON_PASTURE,
    ANDFOM_GF_BASE_PASTURE as _ANDFOM_GF_BASE_PASTURE,
    ANDFOM_GF_STARCH_THRESHOLD as _ANDFOM_GF_STARCH_THRESHOLD,
    ANDFOM_GF_STARCH_STEP as _ANDFOM_GF_STARCH_STEP,
    ANDFOM_GF_STARCH_ADD_PER_STEP as _ANDFOM_GF_STARCH_ADD_PER_STEP,
    ANDFOM_GF_STARCH_ADD_CAP as _ANDFOM_GF_STARCH_ADD_CAP,
    PABKH_THRESHOLD_LOW as _DLG2025_PABKH_THRESHOLD_LOW,
    PABKH_WARNING_HIGH as _DLG2025_PABKH_WARNING_HIGH,
    ANDFOMGF_COP_LOW as _DLG2025_ANDFOMGF_COP_LOW,
    ANDFOMGF_COP_HIGH as _DLG2025_ANDFOMGF_COP_HIGH,
    ANDFOMGF_COP_LOW_PASTURE as _DLG2025_ANDFOMGF_COP_LOW_PASTURE,
)


def _andfom_gf_starch_uplift(staerke_density_kgdm: float) -> float:
    """Staerkeadaptiver Aufschlag auf die aNDFomGF-Mindestdichte (g/kg TM).

    DLG 01|2023 (superseded by DLG 01|2025): "bei hoeheren pansenabbaubaren
    Kohlenhydraten entsprechend mehr". Wird nur noch als Fallback verwendet,
    wenn keine pabKH-Dichte vorliegt. Neue Planung: siehe
    ``_andfom_gf_dlg2025_cascade``.
    """
    excess = max(0.0, float(staerke_density_kgdm) - _ANDFOM_GF_STARCH_THRESHOLD)
    steps = excess / _ANDFOM_GF_STARCH_STEP
    uplift = steps * _ANDFOM_GF_STARCH_ADD_PER_STEP
    return float(min(uplift, _ANDFOM_GF_STARCH_ADD_CAP))


def _andfom_gf_dlg2025_cascade(
    pabkh_density_kgdm: float,
    pasture_pmr: bool,
) -> Tuple[float, str]:
    """Binaere DLG-01|2025-Kaskade fuer aNDFomGF+CoP [g/kg TM].

    Returns (target_kgdm, step_label):
      step_label in {"<=210", ">210", ">260_warn"}.
    """
    pabkh = float(pabkh_density_kgdm or 0.0)
    low = _DLG2025_ANDFOMGF_COP_LOW_PASTURE if pasture_pmr else _DLG2025_ANDFOMGF_COP_LOW
    if pabkh <= _DLG2025_PABKH_THRESHOLD_LOW:
        return float(low), "<=210"
    if pabkh > _DLG2025_PABKH_WARNING_HIGH:
        return float(_DLG2025_ANDFOMGF_COP_HIGH), ">260_warn"
    return float(_DLG2025_ANDFOMGF_COP_HIGH), ">210"


def _andfom_gf_min_target(
    staerke_density_kgdm: float,
    pasture_pmr: bool,
    seasonal_boost: float = 0.0,
    sara_boost: float = 0.0,
    pabkh_density_kgdm: Optional[float] = None,
) -> float:
    """Primaere aNDFomGF+CoP-Mindestdichte [g/kg TM].

    Ab DLG 01|2025: binaere pabKH-Kaskade (200 / 280 g/kg TM) hat Vorrang,
    sofern ``pabkh_density_kgdm`` gesetzt ist. Falls nicht (z. B. in Stage-1
    ohne bereits bestimmte pabKH), wird das alte staerkeadaptive Modell
    (DLG 01|2023) als Fallback verwendet. Saisonale und SARA-Boosts werden
    in beiden Faellen additiv aufgeschlagen.
    """
    if pabkh_density_kgdm is not None:
        base, _step = _andfom_gf_dlg2025_cascade(pabkh_density_kgdm, pasture_pmr)
    else:
        base_kgdm = _ANDFOM_GF_BASE_PASTURE if pasture_pmr else _ANDFOM_GF_BASE_NON_PASTURE
        base = base_kgdm + _andfom_gf_starch_uplift(staerke_density_kgdm)
    return float(base + float(seasonal_boost or 0.0) + float(sara_boost or 0.0))


def _pendf_model_calibrated(staerke_density_kgdm: float, dmi_kg: float) -> bool:
    """Liegt die Ration im kalibrierten Bereich des peNDF-Lookup-Modells?

    Kalibrierter Bereich: Staerke 0-250 g/kg TM und TM-Aufnahme 10-25 kg/d.
    Ausserhalb werden die Werte der Lookup-Tabelle extrapoliert (Fallback).
    """
    st_ok = 0.0 <= float(staerke_density_kgdm) <= 250.0
    dmi_ok = 10.0 <= float(dmi_kg) <= 25.0
    return bool(st_ok and dmi_ok)


# pH-Predictor nach Zebeli et al. 2008 J. Dairy Sci. 91:2046-2066, wörtlich
# zitiert in DLG-Information 01|2025, Kap. 8.3 (Strukturindex), S. 34:
#
#   pH = 6,05 + 0,044·peNDF − 0,0006·peNDF² − 0,017·abbauSt − 0,016·TM
#
# Einheiten (DLG 01|2025):
#   peNDF:   % der TM                  (Validitaetsbereich ca. 6 - 25 %)
#   abbauSt: pansenabbaubare Staerke (ST - bST) in % der TM
#                                      (Validitaetsbereich ca. 5 - 35 %)
#   TM:      kg TM/Tag                 (Validitaetsbereich 10 - 25 kg/d)
#
# Wichtig: DLG 01|2025 bezieht den Staerke-Eingang ausdruecklich auf die
# *pansenabbaubare* Staerke (ST - bST), nicht auf Gesamt-ST und NICHT auf
# pabKH = ST + ZU - bST.
#
# Aenderungshistorie:
#   - vor 2026-04-21: Eingaenge in g/kg TM (Unit-Bug) -> false-positive SARA.
#   - 2026-04-21 (SARA-Reopt): Umrechnung g/kg TM -> % TM + Clipping eingefuehrt,
#       aber mit alternativer Koeffizientenvariante (6.237/0.03332/0.00055/
#       0.01091/0.0089) aus dem GfE-Workshop 2023 (Zebeli/Schwarz-Adaption).
#   - 2026-04-21 (DLG2025-PH-FORMEL): Rueckkehr auf die von DLG 01|2025
#       offiziell zitierten Zebeli-2008-Koeffizienten. Staerke-Eingang auf
#       pansenabbaubare Staerke (ST - bST) umgestellt; Zucker gehoert nach
#       DLG NICHT in diese Formel.
# Refactor 2026-04-23: ausgelagert nach app.agrar.rations.constants.gfe2023
from app.agrar.rations.constants.gfe2023 import (
    PH_PEN_DENS_MIN_KGDM as _PH_PEN_DENS_MIN_KGDM,
    PH_PEN_DENS_MAX_KGDM as _PH_PEN_DENS_MAX_KGDM,
    PH_STARCH_MIN_KGDM as _PH_STARCH_MIN_KGDM,
    PH_STARCH_MAX_KGDM as _PH_STARCH_MAX_KGDM,
    PH_DMI_MIN as _PH_DMI_MIN,
    PH_DMI_MAX as _PH_DMI_MAX,
)


def _ph_inputs_in_range(
    pendf_density: float, abbaust_density: float, dmi_kg: float
) -> bool:
    """Alle Eingaenge im Validitaetsbereich der Zebeli-2008-Formel?

    Eingaenge in g/kg TM (peNDF, abbaubare Staerke ST-bST) und kg/d (DMI).
    """
    return (
        _PH_PEN_DENS_MIN_KGDM <= pendf_density <= _PH_PEN_DENS_MAX_KGDM
        and _PH_STARCH_MIN_KGDM <= abbaust_density <= _PH_STARCH_MAX_KGDM
        and _PH_DMI_MIN <= dmi_kg <= _PH_DMI_MAX
    )


def _ph_predict(pendf_density: float, abbaust_density: float, dmi_kg: float) -> float:
    """Pansen-pH-Vorhersage nach Zebeli et al. 2008 (DLG 01|2025, Kap. 8.3).

    Formel:
        pH = 6,05 + 0,044·peNDF − 0,0006·peNDF² − 0,017·abbauSt − 0,016·TM

    Eingaenge:
        pendf_density:    peNDF-Dichte in g/kg TM
        abbaust_density:  pansenabbaubare Staerke (ST - bST) in g/kg TM
        dmi_kg:           TM-Aufnahme in kg/d

    Die DLG/Zebeli-Formel arbeitet intern mit % der TM. Umrechnung g/kg TM x 0.1
    = % TM; Eingaenge werden auf den publizierten Validitaetsbereich geclippt,
    damit die Formel ausserhalb ihres Bereichs keine unphysikalischen Werte
    produziert (Clipping nur defensiv, Anwendbarkeit ueber
    ``_ph_inputs_in_range`` gepruefen).
    """
    p_pct = max(_PH_PEN_DENS_MIN_KGDM, min(_PH_PEN_DENS_MAX_KGDM, float(pendf_density))) / 10.0
    s_pct = max(_PH_STARCH_MIN_KGDM, min(_PH_STARCH_MAX_KGDM, float(abbaust_density))) / 10.0
    t = max(_PH_DMI_MIN, min(_PH_DMI_MAX, float(dmi_kg)))
    ph = 6.05 + 0.044 * p_pct - 0.0006 * p_pct * p_pct - 0.017 * s_pct - 0.016 * t
    return round(max(5.5, min(7.0, ph)), 2)


def _abbaust_density_kgdm(
    feeds: List[Dict[str, Any]],
    amounts: List[float],
    total_dmi_kg: float,
) -> float:
    """Dichte der pansenabbaubaren Staerke (ST - bST) in g/kg TM.

    Zucker wird hier bewusst NICHT eingerechnet: DLG 01|2025 Kap. 8.3 zitiert
    Zebeli 2008 explizit mit "abbaubare Staerke", nicht "pabKH" (ST+ZU-bST).
    """
    if total_dmi_kg <= 0:
        return 0.0
    abbaust_g = 0.0
    for amt, feed in zip(amounts, feeds):
        st = float(feed.get("st") or 0.0)
        bst = float(feed.get("bst") or 0.0)
        abbaust_g += float(amt) * max(0.0, st - bst)
    return abbaust_g / total_dmi_kg


# ---------------------------------------------------------------------------
# DLG 01|2025, Kap. 8.4: Fermentationsindex Kohlenhydrate (FIKH)
#   FIKH [%] = DNDF / (DNDF + pabKH) * 100
# mit
#   DNDF  = aNDFom * NDFD / 100     [g/kg TM]   (verdauliche aNDFom)
#   pabKH = ST + ZU - bST            [g/kg TM]   (pansenabbaubare KH)
# Ziel: >= 50 %. Unter 50 % steht die Fermentation im Pansen einseitig auf
# Staerke/Zucker, was das SARA-Risiko erhoeht (DLG 01|2025 S. 35).
# ---------------------------------------------------------------------------
# Refactor 2026-04-23: ausgelagert nach app.agrar.rations.constants.gfe2023
from app.agrar.rations.constants.gfe2023 import FIKH_TARGET_PCT as _FIKH_TARGET_PCT


def _fikh_percent(
    feeds: List[Dict[str, Any]],
    amounts: List[float],
    total_dmi_kg: float,
) -> Tuple[Optional[float], Dict[str, Any]]:
    """Fermentationsindex Kohlenhydrate (FIKH) in %, DLG 01|2025 Kap. 8.4.

    Returns (fikh_pct, diagnostics). ``fikh_pct`` ist ``None``, wenn fuer keinen
    Feed ein NDFD-Wert vorliegt (dann ist DNDF nicht bestimmbar, der Index ist
    nicht aussagekraeftig).
    """
    if total_dmi_kg <= 0:
        return None, {"reason": "total_dmi_kg <= 0"}

    dndf_g = 0.0
    ndf_with_ndfd_g = 0.0
    ndf_total_g = 0.0
    pabkh_g = 0.0
    missing_ndfd_kg = 0.0
    covered_ndfd_kg = 0.0
    for amt, feed in zip(amounts, feeds):
        amt_f = float(amt or 0.0)
        if amt_f <= 0:
            continue
        ndf = float(feed.get("ndf") or 0.0)
        st = float(feed.get("st") or 0.0)
        zu = float(feed.get("zu") or 0.0)
        bst = float(feed.get("bst") or 0.0)
        pabkh_g += amt_f * max(0.0, st + zu - bst)
        ndf_total_g += amt_f * ndf
        ndfd = feed.get("ndfd")
        if ndfd is None or ndf <= 0:
            missing_ndfd_kg += amt_f
            continue
        dndf_g += amt_f * ndf * float(ndfd) / 100.0
        ndf_with_ndfd_g += amt_f * ndf
        covered_ndfd_kg += amt_f

    if dndf_g + pabkh_g <= 0 or covered_ndfd_kg <= 0:
        return None, {
            "reason": "no_ndfd_data",
            "missing_ndfd_kg": round(missing_ndfd_kg, 2),
        }

    # Falls ein Teil der Ration keinen NDFD-Wert hat, rechnen wir einen konservativen
    # Fallback NDFD = 0.50 (Literaturmittel fuer Grobfutter) auf den Rest, damit der
    # Gesamtindex nicht systematisch zu guenstig dasteht.
    if missing_ndfd_kg > 0:
        dndf_g += max(0.0, ndf_total_g - ndf_with_ndfd_g) * 0.50

    denom = dndf_g + pabkh_g
    if denom <= 0:
        return None, {"reason": "denom_zero"}
    fikh = dndf_g / denom * 100.0
    return round(fikh, 1), {
        "dndf_g": round(dndf_g, 1),
        "pabkh_g": round(pabkh_g, 1),
        "missing_ndfd_kg": round(missing_ndfd_kg, 2),
        "covered_ndfd_kg": round(covered_ndfd_kg, 2),
        "ndfd_coverage_pct": round(
            covered_ndfd_kg / max(covered_ndfd_kg + missing_ndfd_kg, 1e-9) * 100.0, 1
        ),
    }


def _feed_pendf_factor(feed: Dict[str, Any]) -> float:
    """Physikalisch effektiver NDF-Anteil am Gesamt-NDF (peNDF/NDF), fachlich
    kalibriert nach Zebeli 2012 / DLG 01|2023 / DLG-Workshop 2023.

    Typische peNDF/NDF-Quoten:
      Langfaser (Heu, Stroh, >3 cm)        0.95 - 1.00
      Luzernesilage / -heu                 0.65 - 0.75
      Grassilage (Standard-Haecksel)       0.50 - 0.60
      Frischgras / Weide                   0.50 - 0.60
      GPS (Ganzpflanzensilage)             0.45 - 0.55
      Maissilage (Haecksel 0.7-1.2 cm)     0.35 - 0.50
      Ruebenblattsilage                    0.30 - 0.40
      Saftfutter (Biertreber, Schlempe)    0.20 - 0.30
      Ruebenschnitzel (nass)               0.20 - 0.30
      Kraftfutter (Getreide, Schrote)      0.05 - 0.15

    Vor 2026-04-21 waren die Defaults fuer Grobfutter auf 0.90 gesetzt, was
    die peNDF-Dichte systematisch auf ~370 g/kg TM ueberschaetzte und
    false-positive SARA-Alarme (pH-Formel extrapoliert) ausloeste.
    """
    pendf_map: Dict[str, float] = {
        "Grundfutter/Grobfutter": 0.50,
        "Grundfutter/Saftfutter": 0.25,
        "Grundfutter/Betrieb": 0.50,
        "Kraftfutter/Trocken": 0.10,
        "Kraftfutter/Feucht": 0.15,
        "Zusatzstoffe": 0.0,
        "Sonstige": 0.20,
    }
    base = pendf_map.get(feed.get("group", "Sonstige"), 0.20)
    name_l = feed.get("name", "").lower()
    if "stroh" in name_l:
        return 1.00
    if "heu" in name_l:
        return 0.95
    if "luzerne" in name_l:
        return 0.70
    # Gras-basierte Faktoren konsistent ueber TM-klassifizierte Gruppe
    _gk = _grass_feed_kind(feed)
    if _gk == "grass_silage":
        return 0.55
    if "maissilage" in name_l or ("mais" in name_l and "siliert" in name_l):
        return 0.45
    if "ganzpflanzen" in name_l or "gps" in name_l:
        return 0.50
    if _gk == "pasture":
        return 0.55
    if _gk == "grass_hay":
        return 0.95
    if "rübenblatt" in name_l or "ruebenblatt" in name_l or "blattsilage" in name_l:
        return 0.35
    if "treber" in name_l or "schlempe" in name_l or "pülpe" in name_l or "puelpe" in name_l:
        return 0.25
    if "rübenschnitzel" in name_l or "ruebenschnitzel" in name_l:
        return 0.25
    return base


def _feed_is_soya(feed: Dict[str, Any]) -> bool:
    """Heuristik fuer Soja/Soy-Produkte (Etikett + DLG-Gruppe/Futterart)."""
    name = str(feed.get("name") or "").lower()
    group = str(feed.get("group") or "").lower()
    art = str(feed.get("futterart") or "").lower()
    blob = f"{name} {group} {art}"
    return (
        "soja" in blob
        or "soy" in blob
        or "sojaschrot" in blob
        or "sojaextraktionsschrot" in blob.replace(" ", "")
    )


def _welfare_objective_coeff(
    feed: Dict[str, Any],
    wizard_soft_goals: Optional[Dict[str, Any]] = None,
) -> float:
    """
    Qualitäts-Koeffizient für Stage-1-LP (linprog minimiert c·x → niedriger Wert = bevorzugt).

    Prinzip: Strukturanforderungen kommen ausschließlich aus LP-Constraints
    (aNDFomGF ≥ 200, forage_share ≥ 55 %, peNDF-Floor, pabKH-Ceil, CP-Ceil, XL-Ceil).
    Die Zielfunktion belohnt *Nährstoffeffizienz*, nicht pauschal „Grobfutter".

    Dimensionen:
      - ME-Dichte-Reward:  hohe Energiedichte → bevorzugt (Maissilage > Grassilage > Stroh)
      - sidP-Effizienz:    hohes sidP/ME-Verhältnis → bevorzugt (Protein-Effizienz)
      - peNDF-Reward:      hohe effektive Strukturfaser → leichter bevorzugt (Pansen-pH)
      - Penalitäten:       pabKH ↑, XL ↑, CP > Zielkorridor ↑, K ↑ → bestraft
      - Kostenbeitrag:     5 % des normierten Preises als Tiebreaker (nicht dominant)
    """
    me = float(feed.get("me") or 0.0)
    sidp = float(feed.get("sidp") or 0.0)
    ndf = float(feed.get("ndf") or 0.0)
    pabkh = float(feed.get("st") or 0.0) + float(feed.get("zu") or 0.0) - float(feed.get("bst") or 0.0)
    xl = float(feed.get("xl") or 0.0)
    cp = float(feed.get("cp") or 0.0)
    k = float(feed.get("k") or 0.0)
    price = float(feed.get("price") or 0.0)

    score = 1.0

    # ME-Dichte-Reward: Reward pro MJ ME/kg TM (typischer Bereich 7–13 MJ)
    # Maissilage ~12.3 MJ → -0.246; Grassilage ~10.4 → -0.208; Stroh ~7.0 → -0.140
    me_reward = min(me / 50.0, 0.26)
    score -= me_reward

    # sidP-Effizienz-Reward: sidP [g/kg TM] / ME [MJ/kg TM] als Protein-Effizienzkennzahl
    # Rapsschrot: 265/11.8 = 22.5 → reward 0.18; Grassilage: 88/10.4 = 8.5 → reward 0.07
    if me > 0.0:
        sidp_eff = min(sidp / me / 30.0, 0.20)
        score -= sidp_eff

    # peNDF-Reward: NDF × peNDF-Faktor / 1000 (max 0.15)
    pendf_reward = min((ndf * _feed_pendf_factor(feed)) / 1000.0, 0.15)
    score -= pendf_reward

    # Penalitäten: Risikofaktoren nach DLG 01|2023
    score += max(pabkh - 140.0, 0.0) / 400.0    # pabKH-Überschuss (Pansenazidose)
    score += max(xl - 30.0, 0.0) / 120.0          # Rohfett-Überschuss (XL > 40 g/kg)
    score += max(cp - 155.0, 0.0) / 300.0         # CP im Überschuss → NH3-Verluste
    score += max(k - 25.0, 0.0) / 400.0           # K-Überschuss (Grastetanie)

    # Kosten-Tiebreaker: 5 % des normierten Preises (€/kg TM / 3.0 als Normierung)
    # Damit wird bei gleicher Qualität das günstigere Futter leicht bevorzugt,
    # aber Qualitätsunterschiede dominieren.
    score += 0.05 * (price / 3.0)

    # Wizard Step 3 — weiche Ziele (Stage-1-Welfare, keine neuen Hart-Constraints)
    if wizard_soft_goals:
        if wizard_soft_goals.get("minimize_soya") and _feed_is_soya(feed):
            score += 0.32
        if wizard_soft_goals.get("prefer_homegrown"):
            fid = str(feed.get("id") or "")
            src = str(feed.get("_source") or "")
            if fid.startswith("gfa_") or src == "gfa":
                score -= 0.075
        if wizard_soft_goals.get("maximize_n_efficiency_rmd"):
            rmd_val = float(feed.get("rmd") or 0.0)
            if rmd_val > 0.5:
                score += min(rmd_val / 650.0, 0.09)

    return round(score, 6)


def _normalize_feeding_type(raw: Optional[str]) -> str:
    """
    Normalisiert den Fuetterungsmodus:
      TMR          - klassische Totalmischration
      PMR          - partielle Mischration (Grund+Kraftfutter mit separatem Kraftfutter)
      PMR+Weide    - PMR mit nennenswerter Weideaufnahme (Fruehjahr/Sommer)
    """
    value = str(raw or "TMR").strip().upper().replace(" ", "").replace("_", "+")
    if value in {"PMRWEIDE", "PMR+WEIDE", "PASTURE", "WEIDE"}:
        return "PMR+Weide"
    if value == "PMR":
        return "PMR"
    return "TMR"


def _has_pasture_forage(feeds: List[Dict[str, Any]]) -> bool:
    # TM-basierte Klassifikation: echte Weide nur bei TM < 30 %.
    # Grassilage (30-80 % TM) zaehlt hier bewusst nicht als Weide.
    return any(_grass_feed_kind(feed) == "pasture" for feed in feeds)


def _is_pasture_pmr_system(feeds: List[Dict[str, Any]], profile: Optional[Dict[str, Any]]) -> bool:
    mode = _normalize_feeding_type((profile or {}).get("feeding_type"))
    if mode == "PMR+Weide":
        return True
    if mode != "PMR":
        return False
    return _has_pasture_forage(feeds)


# ---------------------------------------------------------------------------
# Fuetterungssystem / Ration-Block-Aufteilung
# ---------------------------------------------------------------------------
#
# Fachliches Modell: eine Ration ist in der Praxis kein homogener Korb, sondern
# ein System gestaffelter Angebote (DLG-Merkblatt 417/443; GfE-Workshop 2023):
#
#   - pasture_block            Weide, freie Aufnahme auf der Flaeche
#   - tmr_block                Misch-/Teilmisch-Wagen (Grundfutter + Mineral
#                              + ggf. Grund-Kraftfutter; homogen vermischt)
#   - concentrate_staged_block Leistungs-Kraftfutter (Transponder / AMS /
#                              Melkstand; gestaffelt nach Milchleistung)
#
# Struktur-/Pansen-Constraints (peNDF, SI, pabKH) wirken physiologisch nur
# im TMR-Block; Weide und gestaffeltes Konzentrat werden getrennt gefressen
# und gehen daher nicht in die Strukturbilanz des Mischwagens ein.


def _feeding_system_defaults(
    system: str,
    distribution: str,
    treat_as_primiparous: bool = False,
    recipe: Optional[ConcentrateRecipeProfile] = None,
) -> Dict[str, float]:
    """Liefert Standardgrenzen fuer die Konzentratzuteilung.

    Abgeleitet aus Praxis-Richtwerten (User-Abstimmung 2026-04-21) plus
    Rezepturklassen-Adjustierung (User-Review 2026-04-23, §5):

    Basiswerte nach Verteilungssystem:
      - Transponder:   2.5 kg/Abruf, Basis 8 kg/Tag
      - AMS (Roboter): 2.0 kg/Melkung, 3 Melkungen, Basis 6 kg/Tag
      - Melkstand:     4.5 kg/Melkzeit Holstein Mehrlakt (9 kg/d Basis),
                       4.0 kg/Melkzeit bei Faersen 1. Lakt. (8 kg/d Basis)
      - TMR/included:  keine zusaetzliche Staffelung

    Rezepturklassen-Adjustierung auf das empfohlene Tagesmaximum
    (Einzelgaben bleiben physiologisch unveraendert bzw. werden beim
    rapid-Pfad sanft abgesenkt):

      recipe.starch_breakdown_class:
        - "slow"   + rumen_buffer_present == True   -> PREMIUM
              Tagesmax +1,0 kg (pansenfreundlich, hohe ME-Nutzung)
              Einzelgabe ggf. erhoeht (nur Melkstand: 4,5->5,0 kg)
        - "slow"   ohne Puffer                      -> LEICHT ERHOEHT
              Tagesmax +0,5 kg (pansenfreundlich, aber kein Premium)
        - "mixed"  (Default)                        -> STANDARD
              Basiswerte unveraendert
        - "rapid"  (Muehlennebenprodukt / schnell)  -> SARA-SCHUTZ
              Tagesmax -1,5 kg (Reduktion gegen Pansenuebersaeuerung)
              Einzelgabe: -0,5 kg bei Melkstand/Transponder
    """
    dist = (distribution or "").strip().lower()
    _sys_norm = (system or "").strip().upper()  # noqa: F841

    starch_class = (
        (recipe.starch_breakdown_class if recipe else "mixed") or "mixed"
    ).lower()
    rumen_buffer = bool(recipe and recipe.rumen_buffer_present)
    is_premium = starch_class == "slow" and rumen_buffer

    if dist == "transponder":
        base = {
            "concentrate_max_per_serving_kg": 2.5,
            "concentrate_servings_per_day": 4.0,
            "concentrate_max_per_day_kg": 8.0,
        }
        if is_premium:
            base["concentrate_max_per_day_kg"] = 9.0
        elif starch_class == "slow":
            base["concentrate_max_per_day_kg"] = 8.5
        elif starch_class == "rapid":
            base["concentrate_max_per_serving_kg"] = 2.0
            base["concentrate_max_per_day_kg"] = 6.5
        return base

    if dist == "ams":
        base = {
            "concentrate_max_per_serving_kg": 2.0,
            "concentrate_servings_per_day": 3.0,
            "concentrate_max_per_day_kg": 6.0,
        }
        if is_premium:
            base["concentrate_max_per_day_kg"] = 7.0
        elif starch_class == "rapid":
            base["concentrate_max_per_serving_kg"] = 1.5
            base["concentrate_max_per_day_kg"] = 4.5
        return base

    if dist == "milkparlor":
        if is_premium:
            # Premium-Konzentrat (slow starch + rumen buffer): erhoehte
            # Einzelgabe und Tagesmax vertretbar.
            return {
                "concentrate_max_per_serving_kg": 5.0,
                "concentrate_servings_per_day": 2.0,
                "concentrate_max_per_day_kg": 10.0,
            }
        if treat_as_primiparous:
            base = {
                "concentrate_max_per_serving_kg": 4.0,
                "concentrate_servings_per_day": 2.0,
                "concentrate_max_per_day_kg": 8.0,
            }
        else:
            base = {
                "concentrate_max_per_serving_kg": 4.5,
                "concentrate_servings_per_day": 2.0,
                "concentrate_max_per_day_kg": 9.0,
            }
        if starch_class == "slow":
            # slow allein (ohne Puffer): vorsichtige +0,5 kg/d
            base["concentrate_max_per_day_kg"] += 0.5
        elif starch_class == "rapid":
            # rapid / Muehlennebenprodukt: Einzelgabe -0,5 kg, Tagesmax -1,5 kg
            base["concentrate_max_per_serving_kg"] = max(
                0.0, base["concentrate_max_per_serving_kg"] - 0.5
            )
            base["concentrate_max_per_day_kg"] = max(
                0.0, base["concentrate_max_per_day_kg"] - 1.5
            )
        return base

    # included_in_tmr / TMR-only: keine zusaetzlichen Staffelgrenzen
    return {
        "concentrate_max_per_serving_kg": 0.0,
        "concentrate_servings_per_day": 0.0,
        "concentrate_max_per_day_kg": 0.0,
    }


def _portfolio_has_pasture(feeds: Optional[List[Dict[str, Any]]]) -> bool:
    """Prueft, ob im Futter-Portfolio mindestens eine Weide-Position mit
    Kapazitaet (max_kg > 0) enthalten ist.

    Dient der Auto-Eskalation des Feeding-Systems: sobald Weide als
    verfuegbares Futtermittel im Portfolio ist, sollte das System nicht
    mehr nominell TMR sein, weil Weide nicht in den Mischwagen gehoert.
    """
    if not feeds:
        return False
    for feed in feeds:
        try:
            max_kg = float(feed.get("max_kg") or 0.0)
        except (TypeError, ValueError):
            max_kg = 0.0
        if max_kg <= 0.0:
            continue
        if _grass_feed_kind(feed) == "pasture":
            return True
    return False


def _feeds_for_fs_resolve_after_solve(
    feeds: List[Dict[str, Any]],
    amounts: List[float],
) -> List[Dict[str, Any]]:
    """Kopiert Feeds mit max_kg = Ist-Menge (kg TM/d) fuer FS-Aufloesung.

    Damit greift die Auto-Eskalation TMR -> PMR_pasture nur, wenn die
    optimale Ration Weide tatsaechlich > 0 kg TM/d enthaelt (nicht nur,
    wenn Weide im Katalog mit Kapazitaet steht).
    """
    if not feeds or len(amounts) != len(feeds):
        return feeds
    out: List[Dict[str, Any]] = []
    for f, a in zip(feeds, amounts):
        amt = max(0.0, float(a or 0.0))
        ff = dict(f)
        ff["max_kg"] = amt if amt > 1e-6 else 0.0
        out.append(ff)
    return out


def _resolve_feeding_system_config(
    raw: Optional[Any],
    profile: Optional[Dict[str, Any]] = None,
    feeds: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Normalisiert einen FeedingSystemConfig-Input (dict/Model/None).

    Fallback-Logik (Abwaertskompatibilitaet):
      - None oder leer            -> aus profile.feeding_type ableiten
      - PMR+Weide im Profil       -> system=PMR_pasture, distribution=milkparlor
      - PMR im Profil             -> system=PMR_stall, distribution=transponder
      - TMR / unbekannt           -> system=TMR, distribution=included_in_tmr

    Auto-Eskalation (fachlicher Fix 2026-04-24):
      Wenn das resultierende System TMR waere, aber das Futter-Portfolio
      Weide mit Kapazitaet enthaelt, wird automatisch auf PMR_pasture +
      milkparlor eskaliert und ``auto_promoted_from_tmr=True`` gesetzt.
      Grund: Weide wird gegrast, nicht gemischt - ein reiner TMR-Modus
      mit Weide im Portfolio fuehrt sonst dazu, dass Weide faelschlich
      ins Mischprotokoll laeuft.

    Grenzen werden ueber `_feeding_system_defaults()` aufgefuellt, falls
    nicht explizit angegeben.
    """
    data: Dict[str, Any] = {}
    if isinstance(raw, FeedingSystemConfig):
        data = raw.model_dump()
    elif isinstance(raw, dict):
        data = dict(raw)

    if not data:
        feeding_type = _normalize_feeding_type((profile or {}).get("feeding_type"))
        if feeding_type == "PMR+Weide":
            data = {"system": "PMR_pasture", "concentrate_distribution": "milkparlor"}
        elif feeding_type == "PMR":
            data = {"system": "PMR_stall", "concentrate_distribution": "transponder"}
        else:
            data = {"system": "TMR", "concentrate_distribution": "included_in_tmr"}

    system = str(data.get("system", "TMR")).strip()
    if system not in {"TMR", "PMR_stall", "PMR_pasture"}:
        system = "TMR"

    distribution = str(data.get("concentrate_distribution", "included_in_tmr")).strip().lower()
    if distribution not in {"included_in_tmr", "transponder", "ams", "milkparlor"}:
        distribution = "included_in_tmr"

    # Auto-Eskalation TMR -> PMR_pasture, falls Weide im Portfolio.
    auto_promoted_from_tmr = False
    if system == "TMR" and _portfolio_has_pasture(feeds):
        system = "PMR_pasture"
        if distribution == "included_in_tmr":
            distribution = "milkparlor"
        auto_promoted_from_tmr = True

    treat_primi = bool(data.get("treat_as_primiparous", False))
    if (profile or {}).get("parity") == 1 or (profile or {}).get("is_primiparous"):
        treat_primi = True

    recipe_raw = data.get("default_concentrate_recipe")
    recipe_model: Optional[ConcentrateRecipeProfile] = None
    if isinstance(recipe_raw, ConcentrateRecipeProfile):
        recipe_model = recipe_raw
    elif isinstance(recipe_raw, dict):
        try:
            recipe_model = ConcentrateRecipeProfile(**recipe_raw)
        except Exception:
            recipe_model = None

    defaults = _feeding_system_defaults(system, distribution, treat_primi, recipe_model)
    resolved: Dict[str, Any] = {
        "system": system,
        "concentrate_distribution": distribution,
        "treat_as_primiparous": treat_primi,
        "concentrate_max_per_serving_kg": float(
            data.get("concentrate_max_per_serving_kg") or defaults["concentrate_max_per_serving_kg"]
        ),
        "concentrate_servings_per_day": float(
            data.get("concentrate_servings_per_day") or defaults["concentrate_servings_per_day"]
        ),
        "concentrate_max_per_day_kg": float(
            data.get("concentrate_max_per_day_kg") or defaults["concentrate_max_per_day_kg"]
        ),
        "default_concentrate_recipe": (
            recipe_model.model_dump() if recipe_model is not None else None
        ),
        "auto_promoted_from_tmr": auto_promoted_from_tmr,
    }
    return resolved


def _auto_assign_block(feed: Dict[str, Any], system: str) -> str:
    """Ordnet ein Feed automatisch einem Rationsblock zu.

    Regeln (konservativ, gut vorhersehbar):
      - Weide (Gras, TM < 30 %)                -> IMMER pasture_block
        (auch wenn das System TMR ist - fachlich wird Weide nie in den
        Mischwagen gefuellt; sie wird direkt auf dem Gruenland gefressen.
        Das TMR-System eskaliert in diesem Fall ueber
        ``_resolve_feeding_system_config`` automatisch auf PMR_pasture.)
      - andere Grobfutter (Silage, Heu, Stroh) -> tmr_block
      - Mineral                                -> tmr_block
      - Kraftfutter / Konzentrat               -> bei TMR: tmr_block
                                                  bei PMR: concentrate_staged_block
    Grobe Heuristik ueber Feed-Group + _grass_feed_kind.
    """
    sys_norm = (system or "TMR").strip().upper()

    group = str(feed.get("group", "") or "").strip().lower()
    name = str(feed.get("name", "") or "").strip().lower()
    futterart = str(feed.get("futterart", "") or "").strip().lower()

    # Mineral-Check zuerst: "Weidemineral" darf nicht faelschlich wegen
    # dem Wortteil "weide" im _grass_feed_kind-Fallback als Weide gelten.
    is_mineral = (
        "mineral" in group
        or "mineral" in name
        or "mineral" in futterart
    )
    if is_mineral:
        return "tmr_block"

    grass_kind = _grass_feed_kind(feed)
    if grass_kind == "pasture":
        # Fachlicher Fix 2026-04-24 (User-Review Mischprotokoll): Weide
        # darf unter keinen Umstaenden in den TMR-/Mischwagen-Block
        # landen. Selbst wenn das System nominell TMR ist, wird Weide
        # gegrast, nicht gemischt. Die automatische Systemeskalation
        # erfolgt in ``_resolve_feeding_system_config`` (TMR+Weide-Feed
        # im Portfolio => PMR_pasture).
        return "pasture_block"

    is_forage = bool(feed.get("forage"))
    if is_forage:
        return "tmr_block"

    is_concentrate = (
        "kraftfutter" in group
        or "konzentrat" in group
        or "kraftfutter" in futterart
        or "milchleistungsfutter" in name
        or "milchleistungsfutter" in futterart
        or group.startswith("mlf")
    )
    if is_concentrate:
        if sys_norm in {"PMR_STALL", "PMR_PASTURE"}:
            return "concentrate_staged_block"
        return "tmr_block"

    # Fallback: TMR
    return "tmr_block"


def _split_feeds_by_block(
    feeds: List[Dict[str, Any]],
    system_config: Dict[str, Any],
    overrides: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """Zerlegt die Feed-Liste in pasture/tmr/concentrate_staged.

    `overrides` ist eine Liste von {"feed_id": ..., "block": ...} und gewinnt
    gegenueber der Automatik.
    """
    override_map: Dict[str, str] = {}
    if overrides:
        for entry in overrides:
            if not isinstance(entry, dict):
                continue
            fid = str(entry.get("feed_id") or "").strip()
            blk = str(entry.get("block") or "").strip().lower()
            if fid and blk in {"pasture", "tmr", "concentrate_staged"}:
                override_map[fid] = f"{blk}_block"

    system = system_config.get("system", "TMR")

    buckets: Dict[str, List[Dict[str, Any]]] = {
        "pasture_block": [],
        "tmr_block": [],
        "concentrate_staged_block": [],
    }

    for feed in feeds:
        fid = str(feed.get("id") or "").strip()
        target = override_map.get(fid) or _auto_assign_block(feed, system)
        if target not in buckets:
            target = "tmr_block"
        buckets[target].append(feed)

    return buckets


# ---------------------------------------------------------------------------
# Slice 2 (2026-04-23): Futterabruf-Staffel Konstanten (Modul-Scope)
# ---------------------------------------------------------------------------
# Umrechnungs-Praxisfaktor: kg Konzentrat (FM) je kg Zusatzmilch oberhalb
# der Basisleistung aus Grobfutter/Weide. Unteres Band = 0,45 (Hochleistungs-
# Kraftfutter, hohe Energiedichte), oberes Band = 0,50 (Standard).
# Refactor 2026-04-23: ausgelagert nach app.agrar.rations.constants.feeding_system
from app.agrar.rations.constants.feeding_system import (
    CONC_PER_ADDITIONAL_MILK_LOW as _CONC_PER_ADDITIONAL_MILK_LOW,
    CONC_PER_ADDITIONAL_MILK_HIGH as _CONC_PER_ADDITIONAL_MILK_HIGH,
    CONC_DEFAULT_DM_FRAC as _CONC_DEFAULT_DM_FRAC,
    CONC_HARD_SAFETY_FACTOR as _CONC_HARD_SAFETY_FACTOR,
)


# Wizard Step 3: L1-Abstand zu Referenzration (kg TM je feed_id).
# Hilfsvariablen t_i mit min sum(t_i) ≡ sum |x_i-b_i|; Gewicht in Stage 1/2 gekoppelt.
_WIZARD_BASELINE_L1_WEIGHT = 0.088


def _run_lp(
    req: _CowReq,
    feeds: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
    runtime_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    LP-Rationsoptimierung (scipy.optimize.linprog, HiGHS).

    Endstufe bei Laktation: Minimierung der **Futterkosten je kg ECM** (fraktionales
    LP / Charnes–Cooper), sonst klassisch **EUR pro Tag**.

    Ablauf bei gesetztem Milchleistungsziel im Profil (milk_kg_day > 0):
      (1) Stage Milch: limitierende Milch maximieren bis max. Ist-Leistung + 5 %
          (Hilfsvariable z, gleiche ME/sidP-Linearisierung wie _milk_from_supply).
      (2) Stage Welfare: Welfare-Ziel bei hoechstens MILK_TRADEOFF_% Einbusse ggue.
          Stage (1), ausser disable_milk_tradeoff_between_stages.
      (3) Stage Kosten: bei Laktation min. **EUR je kg ECM** (Charnes–Cooper/
          fraktionales LP: min Feedkosten / limitierende Milch; ECM linear aus
          Profil-Fett/-Protein-%). Optional `stage2_minimize_feed_eur_per_day`:
          klassisches min. EUR/Tag (Fallback bei Infeasible des fraktionalen LP).
    Ohne Milchleistungsziel: wie zuvor Welfare-Stage-1, dann Kosten-Stage-2.
    Konzentrat-Tagesmax-Slack und Policy-Slacks wie bisher.

    Optional Wizard ``policy_overrides.wizard_baseline_kg_dm`` (feed_id -> kg TM)
    bei ``minimize_deviation_from_baseline``: L1-Abstand ||x-b||_1 ueber Hilfs-
    variablen in Stage 1 und gekoppeltes Gewicht in Stage 2.

    Nebenbedingungen nach GfE 2023 / DLG 01|2023 / GfE-Workshop 2023:
      ME   ≥ Bedarf                           [GfE 2023]
      sidP ≥ Bedarf                           [GfE 2023]
      aNDFom gesamt ≥ Minimum (Pansenstab.)   [DLG 01|23]
      aNDFomGF-Dichte ≥ 200 g/kg TM          [DLG 01|23 – linearisiert]
      pabKH-Dichte ≤ 210 g/kg TM             [DLG 01|23 – Pansenazidose]
      XL-Dichte ≤ 40 g/kg TM                 [DLG 01|23 – Fettlimit]
      K-Menge ≤ k_max_g (K/Mg-Antagonismus)  [GfE-Workshop 2023]
      Ca, P, Na, Mg ≥ Minimum
      DMI ≥ Minimum, DMI ≤ Maximum
    """
    conc_max_lp_slack_kg_out: Optional[float] = None
    conc_max_lp_slack_penalty_out: Optional[float] = None
    stage2_lp_mode_out: Optional[str] = None
    stage2_relaxation_summary_out: List[Dict[str, Any]] = []
    stage2_fallback_used_out = False
    stage2_ecm_failure_class_out: Optional[str] = None
    from scipy.optimize import linprog  # type: ignore[import]

    n = len(feeds)
    prices = [f["price"] for f in feeds]
    _raw_os = str((runtime_options or {}).get("objective_strategy") or "balance_then_cost").strip().lower()
    _obj_strat = _raw_os if _raw_os in _OBJECTIVE_STRATEGIES else "balance_then_cost"
    feeding_type = _normalize_feeding_type((profile or {}).get("feeding_type"))
    pasture_pmr = _is_pasture_pmr_system(feeds, profile)
    _wizard_sg = ((runtime_options or {}).get("policy_overrides") or {}).get("wizard_soft_goals") or {}
    _wizard_baseline_raw = (
        ((runtime_options or {}).get("policy_overrides") or {}).get("wizard_baseline_kg_dm") or {}
    )
    _wizard_baseline_kgdm: Dict[str, float] = {}
    if isinstance(_wizard_baseline_raw, dict):
        for _bk, _bv in _wizard_baseline_raw.items():
            try:
                _wizard_baseline_kgdm[str(_bk)] = max(0.0, float(_bv))
            except (TypeError, ValueError):
                continue
    andfom_gf_min = 180.0 if pasture_pmr else 200.0
    pabkh_max = 225.0 if pasture_pmr else 210.0
    xl_max = 42.0 if pasture_pmr else 40.0
    cp_max = 185.0 if pasture_pmr else 165.0
    k_max = req.k_max_g * (1.15 if pasture_pmr else 1.0)

    # --- Feeding-System / Block-Scoping (Slice 1c/1e) -----------------------
    # Abgeleitet aus runtime_options["feeding_system_config"] (oder Fallback
    # aus profile.feeding_type). Block-Scoping wirkt nur, wenn das System
    # gestaffelt ist (PMR_stall / PMR_pasture) - bei reinem TMR bleiben alle
    # Feeds im TMR-Block und das Verhalten ist unveraendert (Abwaerts-
    # kompatibel mit bestehender Nutzung ohne feeding_system_config).
    #
    # Fachlicher Scope der Scoping-Regel (User-Review 2026-04-23, §1):
    #   Die Struktur-/Kohlenhydrat-/Fett-/CP-Dichte-Limits gelten fuer die
    #   Mischmasse des TMR-Blocks (homogene Ration im Mischwagen). Weide
    #   und gestaffeltes Lockfutter werden daraus ausgenommen, weil sie
    #   nicht Bestandteil der Mischung sind. Das bedeutet NICHT, dass Weide
    #   strukturphysiologisch irrelevant waere - lange Partikel, Kaudauer,
    #   Speichelbildung wirken strukturell weiter. Fuer die Weide gelten
    #   eigene Bewertungs- und Risikologiken (pasture_block, K/Mg-Ratio,
    #   Saisonprofile), die tages- und aufnahmebezogen ausgewertet werden.
    _fs_cfg = _resolve_feeding_system_config(
        (runtime_options or {}).get("feeding_system_config"), profile, feeds=feeds
    )
    _fs_overrides = (runtime_options or {}).get("feed_block_overrides") or []
    _fs_buckets = _split_feeds_by_block(feeds, _fs_cfg, _fs_overrides)
    _block_by_id: Dict[str, str] = {}
    for blk_name, blk_feeds in _fs_buckets.items():
        for f in blk_feeds:
            _block_by_id[str(f.get("id") or id(f))] = blk_name
    block_labels = [_block_by_id.get(str(f.get("id") or id(f)), "tmr_block") for f in feeds]
    _is_staged_system = _fs_cfg.get("system") in {"PMR_stall", "PMR_pasture"}
    _has_pasture_block = any(lab == "pasture_block" for lab in block_labels)
    _has_staged_concentrate = any(lab == "concentrate_staged_block" for lab in block_labels)
    # Mischmasse-Scoping nur, wenn PMR-System mit tatsaechlich befuelltem
    # Nicht-TMR-Block vorliegt (sonst keine Staffelung = keine Trennung).
    _block_scoping_struct = _is_staged_system and (_has_pasture_block or _has_staged_concentrate)

    def _tmr_only(col_vals: List[float]) -> List[float]:
        """Beschraenkt Mischmasse-Struktur-Koeffizienten auf TMR-Block-Feeds.

        Hintergrund: Struktur-Dichten (aNDFomGF, pabKH, XL, CP) wirken
        auf die homogene Mischung des Mischwagens. Weide und gestaffeltes
        Lockfutter werden getrennt gefressen und gehen deshalb nicht in
        die Mischmasse-Bilanz ein. Das ist nicht zu verwechseln mit der
        tagesbezogenen Strukturversorgung der Kuh - die wird separat ueber
        Weide-Logik / pasture_block abgedeckt.

        Bei TMR (keine Staffelung) ist _block_scoping_struct=False und
        die Funktion gibt die Liste unveraendert zurueck (alle Feeds
        zaehlen zur TMR-Mischmasse, weil es nur einen TMR-Block gibt).
        """
        if not _block_scoping_struct:
            return list(col_vals)
        return [
            v if block_labels[i] == "tmr_block" else 0.0
            for i, v in enumerate(col_vals)
        ]

    # Saisonale Feinsteuerung (Spec §12):
    #   autumn              -> haertere CP-Dichte-Obergrenze (Harnstoffschutz)
    #   autumn/summer_late  -> aNDFomGF-Boost zur Strukturstuetzung
    #   autumn              -> kontrolliertes RMD-Relax um Weidecharakteristik
    _season = (runtime_options or {}).get("season_profile") if runtime_options else None
    _seasonal = _seasonal_adjustments(_season)
    if "cp_density_max_override" in _seasonal:
        cp_max = min(cp_max, float(_seasonal["cp_density_max_override"]))
    if "andfom_gf_min_boost" in _seasonal:
        andfom_gf_min = andfom_gf_min + float(_seasonal["andfom_gf_min_boost"])

    # SARA-Safety-Reopt-Overrides (§13 Pansenazidose-Reopt, 2026-04-21):
    # Wenn der erste Solve ph_predicted < 5.9 oder peNDF unter Minimum liefert,
    # wird _optimize_internal _run_lp mit verschaerften Constraints aufrufen.
    _sara = (runtime_options or {}).get("sara_overrides") or {}
    if _sara.get("pabkh_max") is not None:
        pabkh_max = min(pabkh_max, float(_sara["pabkh_max"]))
    if _sara.get("andfom_gf_min_boost"):
        andfom_gf_min = andfom_gf_min + float(_sara["andfom_gf_min_boost"])
    if _sara.get("xl_max") is not None:
        xl_max = min(xl_max, float(_sara["xl_max"]))
    if _sara.get("cp_density_max_override") is not None:
        cp_max = min(cp_max, float(_sara["cp_density_max_override"]))
    _sara_pendf_floor_boost = float(_sara.get("pendf_floor_boost") or 0.0)

    # Wizard Step 3: minimale aNDFomGF+CoP-Dichte (Nutzer-% TM vs. DLG-Kaskade).
    _wizard_hb_early = (
        ((runtime_options or {}).get("policy_overrides") or {}).get("wizard_hard_bounds") or {}
    )
    _gf_pct_user = _wizard_hb_early.get("andfom_gf_min_pct_tm")
    if _gf_pct_user is not None:
        try:
            _gf_floor_g_kgdm = float(_gf_pct_user) * 10.0
            if _gf_floor_g_kgdm > 0:
                andfom_gf_min = max(andfom_gf_min, _gf_floor_g_kgdm)
        except (TypeError, ValueError):
            pass

    _cm = _build_lp_constraint_matrix(
        feeds=feeds,
        req=req,
        feeding_type=feeding_type,
        pasture_pmr=pasture_pmr,
        block_labels=block_labels,
        block_scoping_struct=_block_scoping_struct,
        andfom_gf_min=andfom_gf_min,
        pabkh_max=pabkh_max,
        xl_max=xl_max,
        cp_max=cp_max,
        k_max=k_max,
        seasonal=_seasonal,
        runtime_options=runtime_options,
        juice_wet_cap_fn=_feed_counts_toward_saftfutter_wet_cap,
        grass_feed_kind_fn=_grass_feed_kind,
    )
    A_ub                 = _cm.A_ub
    b_ub                 = _cm.b_ub
    bounds               = _cm.bounds
    _constraint_registry = _cm.registry
    me_per_kg            = _cm.me_per_kg
    sidp_per_kg          = _cm.sidp_per_kg
    _ndf_per_kg = _cm.ndf_per_kg  # noqa: F841
    xl_per_kg            = _cm.xl_per_kg
    rmd_per_kg           = _cm.rmd_per_kg
    pabkh_per_kg         = _cm.pabkh_per_kg
    _k_per_kg = _cm.k_per_kg  # noqa: F841
    cp_per_kg            = _cm.cp_per_kg
    rmd_max              = _cm.rmd_max
    k_lp_extra           = _cm.k_lp_extra
    _baseline_positions  = _cm.baseline_positions  # noqa: F841

    n_tot = n + k_lp_extra
    A_ub_snap = [list(row) for row in A_ub]
    b_ub_snap = list(b_ub)
    bounds_snap = list(bounds)

    _prof_lp = profile or {}
    herd_milk_kg = float(_prof_lp.get("milk_kg_day") or 0.0)
    _disable_milk_tradeoff = bool((runtime_options or {}).get("disable_milk_tradeoff_between_stages"))
    _trade_frac_eff: Optional[float]
    if _disable_milk_tradeoff:
        _trade_frac_eff = None
    else:
        _tr_raw = (runtime_options or {}).get("milk_tradeoff_max_pct_per_stage")
        if _tr_raw is None:
            _trade_frac_eff = _MILK_TRADEOFF_MAX_PCT_PER_STAGE_DEFAULT / 100.0
        else:
            try:
                tv = float(_tr_raw)
                _trade_frac_eff = tv / 100.0 if tv > 1.0 else tv
            except (TypeError, ValueError):
                _trade_frac_eff = _MILK_TRADEOFF_MAX_PCT_PER_STAGE_DEFAULT / 100.0
            _trade_frac_eff = max(0.0, min(0.5, float(_trade_frac_eff)))

    _fs_sys_for_kl = str((_fs_cfg or {}).get("system") or "TMR")
    _conc_max_per_day = float((_fs_cfg or {}).get("concentrate_max_per_day_kg") or 0.0)
    _me_maint_milk, _me_pkm, _sidp_maint_milk, _sidp_pkm = _milk_requirement_factors(
        _prof_lp,
        None,
        feeding_system=_fs_sys_for_kl,
    )
    _use_milk_stage = herd_milk_kg > 1e-6
    z_cap_milk = herd_milk_kg * (1.0 + float(_MILK_TARGET_HEADROOM_FRAC))
    z_star: Optional[float] = None

    _zero_wiz = [0.0] * k_lp_extra

    def _feed_row_pad(vec: List[float]) -> List[float]:
        return list(vec) + [0.0] * k_lp_extra

    def _feed_row_pad_z(vec: List[float]) -> List[float]:
        return _feed_row_pad(vec) + [0.0]

    def _lin_prog(
        objective: List[float],
        A_loc: List[List[float]],
        b_loc: List[float],
        bounds_loc: List[Tuple[Any, Any]],
    ):
        return linprog(
            c=objective,
            A_ub=A_loc,
            b_ub=b_loc,
            bounds=bounds_loc,
            method="highs",
            options={"disp": False},
        )

    def _solve_simple(objective: List[float], A_loc: List[List[float]], b_loc: List[float]):
        return _lin_prog(objective, A_loc, b_loc, bounds_snap)

    _IDX_XL = _constraint_registry.index_of(_CONSTR_XL_DENSITY)
    _IDX_ANDFOM_GF = _constraint_registry.index_of(_CONSTR_ANDFOM_GF_GEQ)
    _IDX_RMD = _constraint_registry.index_of(_CONSTR_RMD_DENSITY)
    _IDX_ME_ABS = _constraint_registry.index_of(_CONSTR_ME_ABS_LEQ)
    assert _IDX_XL == 5, f"XL-Index erwartet 5, ist {_IDX_XL}"
    assert _IDX_ANDFOM_GF == 3, f"aNDFomGF-Index erwartet 3, ist {_IDX_ANDFOM_GF}"
    assert _IDX_RMD == 7, f"RMD-Index erwartet 7, ist {_IDX_RMD}"
    assert _IDX_ME_ABS == 9, f"ME-abs-Index erwartet 9, ist {_IDX_ME_ABS}"

    def _relax_primary_cascade(cur_result, objective, A_constraints_base, b_constraints_base, bounds_loc, row_extend_fn):
        r = cur_result
        if r.status not in (0, 1):
            xl_density_r = [v - (60.0 if not pasture_pmr else 48.0) for v in xl_per_kg]
            A_loc = list(A_constraints_base)
            A_loc[_IDX_XL] = row_extend_fn(xl_density_r)
            b_loc = list(b_constraints_base)
            b_loc[_IDX_XL] = 0.0
            r = _lin_prog(objective, A_loc, b_loc, bounds_loc)
        if r.status not in (0, 1):
            rmd_relax = rmd_max + (4.0 if feeding_type == "PMR+Weide" else 1.5)
            b_loc = list(b_constraints_base)
            b_loc[_IDX_RMD] = 0.0
            A_loc = list(A_constraints_base)
            A_loc[_IDX_RMD] = row_extend_fn([v - rmd_relax for v in rmd_per_kg])
            r = _lin_prog(objective, A_loc, b_loc, bounds_loc)
        A_r3 = list(A_constraints_base)
        b_r3 = list(b_constraints_base)
        if r.status not in (0, 1):
            A_r3 = [row for i, row in enumerate(A_constraints_base) if i != _IDX_ANDFOM_GF]
            b_r3 = [v for i, v in enumerate(b_constraints_base) if i != _IDX_ANDFOM_GF]
            r = _lin_prog(objective, A_r3, b_r3, bounds_loc)
        if r.status not in (0, 1):
            A_r4 = list(A_r3)
            b_r4 = list(b_r3)
            for idx, row in enumerate(A_r4):
                if all(abs(row[j] + (feeds[j]["sidp"] or 0)) < 0.01 for j in range(n)):
                    b_r4[idx] = -req.sidp_g * 0.85
                    break
            r = _lin_prog(objective, A_r4, b_r4, bounds_loc)
        return r

    _sg_kw = _wizard_sg if _wizard_sg else None
    _welfare_coeffs = [_welfare_objective_coeff(feed, wizard_soft_goals=_sg_kw) for feed in feeds]
    stage1_obj_base = list(_welfare_coeffs)
    if _obj_strat == "cost_only":
        stage1_obj_base = [float(prices[i]) for i in range(n)]
    stage1_objective = stage1_obj_base + [_WIZARD_BASELINE_L1_WEIGHT] * k_lp_extra

    result: Any

    if _use_milk_stage:
        A_milk = [list(row) + [0.0] for row in A_ub_snap]
        b_milk = list(b_ub_snap)
        coupling_me = [-float(me_per_kg[i]) for i in range(n)] + _zero_wiz + [float(_me_pkm)]
        coupling_sidp = [-float(sidp_per_kg[i]) for i in range(n)] + _zero_wiz + [float(_sidp_pkm)]
        A_milk.append(coupling_me)
        b_milk.append(-float(_me_maint_milk))
        A_milk.append(coupling_sidp)
        b_milk.append(-float(_sidp_maint_milk))
        bounds_milk = list(bounds_snap) + [(0.0, max(z_cap_milk, 0.0))]
        c_milk = [0.0] * n_tot + [-1.0]
        res_milk = _lin_prog(c_milk, A_milk, b_milk, bounds_milk)
        res_milk = _relax_primary_cascade(res_milk, c_milk, A_milk, b_milk, bounds_milk, _feed_row_pad_z)
        if res_milk.status not in (0, 1):
            result = res_milk
        elif _obj_strat == "cost_only":
            z_star = float(res_milk.x[n_tot])
            result = res_milk
        else:
            z_star = float(res_milk.x[n_tot])
            A_welfare = [list(row) for row in A_ub_snap]
            b_welfare = list(b_ub_snap)
            if _trade_frac_eff is not None and z_star is not None:
                mf_w = max(0.0, z_star * (1.0 - _trade_frac_eff))
                me_rhs_w = float(_me_maint_milk) + float(_me_pkm) * mf_w
                sidp_rhs_w = float(_sidp_maint_milk) + float(_sidp_pkm) * mf_w
                A_welfare.append(_feed_row_pad([-float(me_per_kg[i]) for i in range(n)]))
                b_welfare.append(-me_rhs_w)
                A_welfare.append(_feed_row_pad([-float(sidp_per_kg[i]) for i in range(n)]))
                b_welfare.append(-sidp_rhs_w)
            res_w = _solve_simple(stage1_objective, A_welfare, b_welfare)
            res_w = _relax_primary_cascade(res_w, stage1_objective, A_welfare, b_welfare, bounds_snap, _feed_row_pad)
            if res_w.status not in (0, 1) and len(A_welfare) > len(A_ub_snap):
                res_w = _solve_simple(stage1_objective, A_ub_snap, b_ub_snap)
                res_w = _relax_primary_cascade(res_w, stage1_objective, A_ub_snap, b_ub_snap, bounds_snap, _feed_row_pad)
            result = res_w
    else:
        result = _solve_simple(stage1_objective, A_ub_snap, b_ub_snap)
        result = _relax_primary_cascade(result, stage1_objective, A_ub_snap, b_ub_snap, bounds_snap, _feed_row_pad)

    infeasibility_hint = None
    if result.status not in (0, 1):
        infeasibility_hint = _diagnose_infeasibility(req, feeds, profile)
    else:
        stage1_amounts = [_f(v) for v in result.x[:n]]
        stage1_total_dmi = sum(stage1_amounts)
        if stage1_total_dmi > 0:
            stage1_forage_pct = (
                sum(stage1_amounts[i] for i in range(n) if feeds[i].get("forage")) / stage1_total_dmi * 100.0
            )
            _stage1_pendf_density = sum(  # noqa: F841
                stage1_amounts[i] * feeds[i]["ndf"] * _feed_pendf_factor(feeds[i])
                for i in range(n)
            ) / stage1_total_dmi
            stage1_starch_density = sum(stage1_amounts[i] * feeds[i]["st"] for i in range(n)) / stage1_total_dmi
            stage1_pabkh_density = sum(stage1_amounts[i] * pabkh_per_kg[i] for i in range(n)) / stage1_total_dmi
            stage1_xl_density = sum(stage1_amounts[i] * xl_per_kg[i] for i in range(n)) / stage1_total_dmi
            stage1_cp_density = sum(stage1_amounts[i] * cp_per_kg[i] for i in range(n)) / stage1_total_dmi

            milk_floor_cost: Optional[float] = None
            if _use_milk_stage and _trade_frac_eff is not None:
                if _obj_strat == "cost_only" and z_star is not None:
                    milk_floor_cost = max(0.0, float(z_star) * (1.0 - float(_trade_frac_eff)))
                elif _obj_strat != "cost_only":
                    me_sup_w = sum(me_per_kg[i] * stage1_amounts[i] for i in range(n))
                    sidp_sup_w = sum(sidp_per_kg[i] * stage1_amounts[i] for i in range(n))
                    milk_e = (
                        max(0.0, (me_sup_w - float(_me_maint_milk)) / float(_me_pkm))
                        if float(_me_pkm) > 1e-9
                        else 0.0
                    )
                    milk_p = (
                        max(0.0, (sidp_sup_w - float(_sidp_maint_milk)) / float(_sidp_pkm))
                        if float(_sidp_pkm) > 1e-9
                        else 0.0
                    )
                    milk_lim_w = min(milk_e, milk_p)
                    milk_floor_cost = max(0.0, milk_lim_w * (1.0 - float(_trade_frac_eff)))

            _orig_pabkh_base = float(min(pabkh_max, stage1_pabkh_density + 10.0))
            _orig_cp_base = float(min(cp_max, stage1_cp_density + 5.0))
            _orig_forage_floor_base = float(max(60.0 if pasture_pmr else 55.0, stage1_forage_pct - 2.0))

            # Stage-2: Konzentrat-Slack-Kosten und Zielfunktion (von Relax-Snapshots unabhaengig).
            policy_relax = str((runtime_options or {}).get("relaxation_policy", "standard"))
            _conc_slack_halfwidth = 1.5
            _conc_relax_f = _RELAXATION_FACTORS.get(policy_relax, 1.0)
            w_conc_slack = (
                _PENALTY_BASE_COST
                * _PENALTY_CLASS_WEIGHTS.get("B", 3.0)
                * _conc_relax_f
                / _conc_slack_halfwidth
            )
            conc_slack_needed = _conc_max_per_day > 0 and _has_staged_concentrate
            conc_mask = [1.0 if block_labels[i] == "concentrate_staged_block" else 0.0 for i in range(n)]

            def _is_forage_or_cop(f: Dict[str, Any]) -> bool:
                return bool(f.get("forage")) or bool(f.get("structural_coproduct"))
            n_cs = 1 if conc_slack_needed else 0
            _prices_stage2 = list(prices)
            if _wizard_sg.get("minimize_soya"):
                _prices_stage2 = [
                    float(prices[i]) + (0.095 if _feed_is_soya(feeds[i]) else 0.0)
                    for i in range(n)
                ]
            _feed_c2 = [
                float(_prices_stage2[i])
                + (
                    _STAGE2_WELFARE_WEIGHT_BALANCE_ONLY * float(_welfare_coeffs[i])
                    if _obj_strat == "balance_only"
                    else 0.0
                )
                for i in range(n)
            ]
            c_s2 = (
                _feed_c2
                + [_WIZARD_BASELINE_L1_WEIGHT] * k_lp_extra
                + ([w_conc_slack] if conc_slack_needed else [])
            )
            ncol_s2 = len(c_s2)

            _try_frac = (
                _use_milk_stage
                and herd_milk_kg > 1e-6
                and not bool((runtime_options or {}).get("stage2_minimize_feed_eur_per_day"))
            )
            m_hi_ecm = max(float(z_cap_milk), herd_milk_kg * 4.0, 90.0)
            m_lo_ecm = max(
                0.5,
                (float(milk_floor_cost) * 0.75) if milk_floor_cost else (herd_milk_kg * 0.12),
            )
            m_lo_ecm = float(min(m_lo_ecm, m_hi_ecm * 0.48))
            v_lo_ecm = 1.0 / m_hi_ecm
            v_hi_ecm = 1.0 / max(m_lo_ecm, 0.15)

            _relax_snaps: Tuple[Tuple[float, float, float, float], ...] = (
                (
                    (0.0, 0.0, 0.0, 1.0),
                    (2.0, 0.0, 0.0, 1.0),
                    (4.0, 0.0, 0.0, 1.0),
                    (6.0, 0.0, 0.0, 1.0),
                    (6.0, 4.0, 0.0, 1.0),
                    (6.0, 8.0, 0.0, 1.0),
                    (6.0, 8.0, 1.0, 1.0),
                    (6.0, 8.0, 2.0, 1.0),
                    (6.0, 8.0, 2.0, 1.02),
                    (6.0, 8.0, 2.0, 1.04),
                )
                if _try_frac
                else ((0.0, 0.0, 0.0, 1.0),)
            )

            cost_result: Any = None
            _stage2_lp_mode_local = "feed_eur_per_day"
            A_s2: List[List[float]] = []
            b_s2: List[float] = []
            bounds_s2: List[Tuple[Any, Any]] = []
            last_feasible_bundle: Optional[
                Tuple[
                    List[List[float]],
                    List[float],
                    List[Tuple[Any, Any]],
                    List[float],
                    Tuple[float, float, float, float],
                ]
            ] = None

            for snap_idx, (_pe, _cpe, _fs, _fm) in enumerate(_relax_snaps):
                cost_result = None
                A_stage2 = list(A_ub_snap)
                b_stage2 = list(b_ub_snap)

                if milk_floor_cost is not None and milk_floor_cost > 1e-6:
                    mf_c = float(milk_floor_cost)
                    A_stage2.append(_feed_row_pad([-float(me_per_kg[i]) for i in range(n)]))
                    b_stage2.append(-(float(_me_maint_milk) + float(_me_pkm) * mf_c))
                    A_stage2.append(_feed_row_pad([-float(sidp_per_kg[i]) for i in range(n)]))
                    b_stage2.append(-(float(_sidp_maint_milk) + float(_sidp_pkm) * mf_c))

                forage_floor = _orig_forage_floor_base - _fs
                A_stage2.append(_feed_row_pad([
                    forage_floor - 100.0 if feed.get("forage") else forage_floor
                    for feed in feeds
                ]))
                b_stage2.append(0.0)

                stage2_andfom_gf_min = _andfom_gf_min_target(
                    staerke_density_kgdm=stage1_starch_density,
                    pabkh_density_kgdm=stage1_pabkh_density,
                    pasture_pmr=pasture_pmr,
                    seasonal_boost=float(_seasonal.get("andfom_gf_min_boost") or 0.0),
                    sara_boost=float(_sara.get("andfom_gf_min_boost") or 0.0)
                    + _sara_pendf_floor_boost,
                )
                if stage2_andfom_gf_min > andfom_gf_min:
                    stage2_andfom_gf_cop_density = [
                        f["ndf"] - stage2_andfom_gf_min if _is_forage_or_cop(f) else -stage2_andfom_gf_min
                        for f in feeds
                    ]
                    A_stage2.append(_feed_row_pad([-v for v in _tmr_only(stage2_andfom_gf_cop_density)]))
                    b_stage2.append(0.0)

                _PENDF_SAFETY_FLOOR = 120.0
                pendf_floor_coeffs = [
                    _PENDF_SAFETY_FLOOR - (feed["ndf"] * _feed_pendf_factor(feed))
                    for feed in feeds
                ]
                A_stage2.append(_feed_row_pad(_tmr_only(pendf_floor_coeffs)))
                b_stage2.append(0.0)

                pabkh_ceiling = _orig_pabkh_base + _pe
                pabkh_ceil_coeffs = [value - pabkh_ceiling for value in pabkh_per_kg]
                A_stage2.append(_feed_row_pad(_tmr_only(pabkh_ceil_coeffs)))
                b_stage2.append(0.0)

                xl_ceiling = min(xl_max, stage1_xl_density + 2.0)
                xl_ceil_coeffs = [value - xl_ceiling for value in xl_per_kg]
                A_stage2.append(_feed_row_pad(_tmr_only(xl_ceil_coeffs)))
                b_stage2.append(0.0)

                cp_ceiling = _orig_cp_base + _cpe
                cp_ceil_coeffs = [value - cp_ceiling for value in cp_per_kg]
                A_stage2.append(_feed_row_pad(_tmr_only(cp_ceil_coeffs)))
                b_stage2.append(0.0)

                A_s2 = [list(row) + [0.0] * n_cs for row in A_stage2]
                b_s2 = list(b_stage2)
                if conc_slack_needed:
                    A_s2.append(_feed_row_pad(list(conc_mask)) + [-1.0])
                    b_s2.append(_conc_max_per_day)

                bounds_s2_base: List[Tuple[Any, Any]] = []
                for _bi in range(len(bounds_snap)):
                    _lo, _hi = bounds_snap[_bi]
                    if _bi < n and _hi is not None and not feeds[_bi].get("forage"):
                        _hi = float(_hi) * _fm
                    bounds_s2_base.append((_lo, _hi))
                bounds_s2 = bounds_s2_base + ([(0.0, None)] if conc_slack_needed else [])

                feas_r = _stage2_feasibility_probe(A_s2, b_s2, bounds_s2)
                if feas_r.status != 0:
                    if snap_idx == 0 and _try_frac:
                        stage2_ecm_failure_class_out = (
                            "infeasible"
                            if feas_r.status == 2
                            else "unbounded"
                            if feas_r.status == 3
                            else "feasibility_error"
                        )
                    continue

                last_feasible_bundle = (A_s2, b_s2, bounds_s2, c_s2, (_pe, _cpe, _fs, _fm))

                frac_ok = False
                frac_failed_raw: Any = None
                if _try_frac:
                    try:
                        A_fr, b_fr, c_fr, bnd_fr = _charnes_cooper_min_cost_per_milk_transform(
                            A_s2, b_s2, c_s2, bounds_s2, v_lo=v_lo_ecm, v_hi=v_hi_ecm
                        )
                        frac_failed_raw = linprog(
                            c=c_fr,
                            A_ub=A_fr,
                            b_ub=b_fr,
                            bounds=bnd_fr,
                            method="highs",
                            options={"disp": False},
                        )
                        x_frac = _recover_x_from_charnes_cooper(frac_failed_raw, ncol_s2)
                        if x_frac is not None:
                            class _FracTrim:
                                pass

                            _fr = _FracTrim()
                            _fr.status = 0
                            _fr.x = x_frac
                            _fr.message = "stage2_frac_min_eur_per_kg_ecm"
                            cost_result = _fr
                            _stage2_lp_mode_local = (
                                "feed_cost_eur_per_kg_ecm_relaxed"
                                if snap_idx > 0
                                else "min_eur_per_kg_ecm"
                            )
                            frac_ok = True
                        else:
                            cost_result = None
                    except Exception:  # pragma: no cover
                        frac_failed_raw = None
                        cost_result = None

                    if snap_idx == 0 and not frac_ok:
                        stage2_ecm_failure_class_out = _classify_stage2_frac_failure(
                            frac_failed_raw, m_lo_ecm, m_hi_ecm
                        )

                    if frac_ok:
                        if snap_idx > 0:
                            if stage2_ecm_failure_class_out == "infeasible":
                                stage2_ecm_failure_class_out = "recovered_via_relaxation"
                            stage2_relaxation_summary_out = _summarize_stage2_relaxations(
                                _orig_pabkh_base,
                                _orig_cp_base,
                                _orig_forage_floor_base,
                                _pe,
                                _cpe,
                                _fs,
                                _fm,
                            )
                        break

                if not _try_frac:
                    try:
                        cost_result = linprog(
                            c=c_s2,
                            A_ub=A_s2,
                            b_ub=b_s2,
                            bounds=bounds_s2,
                            method="highs",
                            options={"disp": False},
                        )
                    except Exception:  # pragma: no cover
                        cost_result = None
                    _stage2_lp_mode_local = "feed_eur_per_day"
                    break
            else:
                if _try_frac and last_feasible_bundle is not None:
                    _A2, _b2, _bd2, _c2, (_lpe, _lcpe, _lfs, _lfm) = last_feasible_bundle
                    A_s2, b_s2, bounds_s2, c_s2 = _A2, _b2, _bd2, _c2
                    try:
                        cost_result = linprog(
                            c=c_s2,
                            A_ub=A_s2,
                            b_ub=b_s2,
                            bounds=bounds_s2,
                            method="highs",
                            options={"disp": False},
                        )
                    except Exception:  # pragma: no cover
                        cost_result = None
                    if cost_result is not None and cost_result.status == 0:
                        stage2_fallback_used_out = True
                        _stage2_lp_mode_local = "feed_eur_per_day_fallback"
                        if stage2_ecm_failure_class_out == "infeasible":
                            stage2_ecm_failure_class_out = "recovered_via_relaxation"
                        if (_lpe + _lcpe + _lfs > 1e-12) or (_lfm > 1.0 + 1e-9):
                            stage2_relaxation_summary_out = _summarize_stage2_relaxations(
                                _orig_pabkh_base,
                                _orig_cp_base,
                                _orig_forage_floor_base,
                                _lpe,
                                _lcpe,
                                _lfs,
                                _lfm,
                            )

            if cost_result is not None and cost_result.status == 0:
                class _Stage2Trim:
                    pass
                _s2r = _Stage2Trim()
                _s2r.x = list(cost_result.x[:n])
                _s2r.fun = float(sum(prices[i] * cost_result.x[i] for i in range(n)))
                _s2r.status = 0
                _s2r.message = getattr(cost_result, "message", "")
                result = _s2r
                if conc_slack_needed:
                    c_sl = max(0.0, float(cost_result.x[n + k_lp_extra]))
                    if c_sl > 1e-6:
                        conc_max_lp_slack_kg_out = round(c_sl, 4)
                        conc_max_lp_slack_penalty_out = round(w_conc_slack * c_sl, 4)
                stage2_lp_mode_out = _stage2_lp_mode_local

            # DLG-01|2025-Slack-Erweiterung (nur wenn Policy-Profil Targets liefert).
            # Ziel: Policy-Baender werden nicht nur post-solve bewertet, sondern
            # sind im LP als weiche Constraints gebunden (Klasse B, relaxation-
            # policy-skaliert). Falls der erweiterte Solve scheitert, bleibt
            # cost_result aus dem Standard-Solve bestehen.
            policy_profile_key = (runtime_options or {}).get("policy_profile")
            policy_targets = _policy_profile_targets(policy_profile_key)
            if policy_targets:
                dmi_typ = 0.5 * (float(req.dmi_min_kg) + float(req.dmi_max_kg))
                ext = _build_policy_band_lp_extension(
                    targets=policy_targets,
                    feeds=feeds,
                    relaxation_policy=policy_relax,
                    dmi_typ_kg=dmi_typ,
                )
                n_pol = int(ext.get("n_slacks") or 0)
                if n_pol > 0:
                    A_ext = [list(row) + [0.0] * n_pol for row in A_s2]
                    for prow in ext["rows"]:
                        feed_part = prow[:n]
                        pol_part = prow[n:]
                        A_ext.append(
                            list(feed_part)
                            + [0.0] * k_lp_extra
                            + [0.0] * n_cs
                            + list(pol_part)
                        )
                    b_ext = list(b_s2) + list(ext["rhs"])
                    c_ext = list(c_s2) + list(ext["slack_costs"])
                    bounds_ext = list(bounds_s2) + list(ext["slack_bounds"])
                    ncol_ext = len(c_ext)
                    ext_result: Any = None
                    if _try_frac:
                        try:
                            A_efr, b_efr, c_efr, bnd_efr = _charnes_cooper_min_cost_per_milk_transform(
                                A_ext, b_ext, c_ext, bounds_ext, v_lo=v_lo_ecm, v_hi=v_hi_ecm
                            )
                            ext_result = linprog(
                                c=c_efr,
                                A_ub=A_efr,
                                b_ub=b_efr,
                                bounds=bnd_efr,
                                method="highs",
                                options={"disp": False},
                            )
                            x_ef = _recover_x_from_charnes_cooper(ext_result, ncol_ext)
                            if x_ef is not None:
                                class _PolFrac:
                                    pass
                                _pf = _PolFrac()
                                _pf.status = 0
                                _pf.x = x_ef
                                _pf.message = "stage2_policy_frac_min_eur_per_kg_ecm"
                                ext_result = _pf
                            else:
                                ext_result = None
                        except Exception:  # pragma: no cover
                            ext_result = None
                    if ext_result is None:
                        try:
                            ext_result = linprog(
                                c=c_ext,
                                A_ub=A_ext,
                                b_ub=b_ext,
                                bounds=bounds_ext,
                                method="highs",
                                options={"disp": False},
                            )
                        except Exception:  # pragma: no cover - Solver-Fehler fallback
                            ext_result = None
                    if ext_result is not None and ext_result.status == 0:
                        slack_values = [float(v) for v in ext_result.x[-n_pol:]]
                        policy_lp_slacks: List[Dict[str, Any]] = []
                        total_slack_penalty = 0.0
                        if n_cs > 0:
                            c_sl = max(0.0, float(ext_result.x[n + k_lp_extra]))
                            c_pen = w_conc_slack * c_sl
                            total_slack_penalty += c_pen
                            if c_sl > 1e-6:
                                policy_lp_slacks.append({
                                    "name": "Konzentrat-Tagesmax (empfohlen, LP-Slack)",
                                    "unit": "kg TM/d",
                                    "direction": "max",
                                    "band_min": None,
                                    "band_max": round(float(_conc_max_per_day), 3),
                                    "halfwidth": round(_conc_slack_halfwidth, 3),
                                    "weight": round(float(w_conc_slack), 6),
                                    "slack_value": round(c_sl, 4),
                                    "penalty_cost": round(c_pen, 4),
                                    "active": True,
                                    "source": "stage2_concentrate_slack",
                                })
                                conc_max_lp_slack_kg_out = round(c_sl, 4)
                                conc_max_lp_slack_penalty_out = round(c_pen, 4)
                        for meta, val in zip(ext["slack_meta"], slack_values):
                            val = max(0.0, val)
                            penalty = float(meta["weight"]) * val
                            total_slack_penalty += penalty
                            policy_lp_slacks.append({
                                "name": meta["name"],
                                "unit": meta["unit"],
                                "direction": meta["direction"],
                                "band_min": meta["band_min"],
                                "band_max": meta["band_max"],
                                "halfwidth": round(float(meta["halfwidth"]), 3),
                                "weight": round(float(meta["weight"]), 6),
                                "slack_value": round(val, 4),
                                "penalty_cost": round(penalty, 4),
                                "active": val > 1e-6,
                            })
                        feed_x = list(ext_result.x[:n])
                        class _ExtResult:
                            pass
                        _r = _ExtResult()
                        _r.x = feed_x
                        _r.fun = float(sum(prices[i] * feed_x[i] for i in range(n)))
                        _r.status = 0
                        _r.message = "stage2_policy_slack"
                        result = _r
                        stage2_lp_mode_out = (
                            "min_eur_per_kg_ecm_policy"
                            if getattr(ext_result, "message", "") == "stage2_policy_frac_min_eur_per_kg_ecm"
                            else "feed_eur_per_day_policy"
                        )
                        return {
                            "scipy_result": result,
                            "feeds": feeds,
                            "_relaxed": True,
                            "_infeasibility_hint": infeasibility_hint,
                            "_policy_lp_slacks": policy_lp_slacks,
                            "_policy_lp_slack_total_penalty": round(total_slack_penalty, 4),
                            "_policy_lp_slack_objective_mode": "stage2_cost_plus_policy_slack",
                            "_feeding_system_config": _fs_cfg,
                            "_block_labels": list(block_labels),
                            "_concentrate_max_lp_slack_kg": conc_max_lp_slack_kg_out,
                            "_concentrate_max_lp_slack_penalty": conc_max_lp_slack_penalty_out,
                            "_stage2_lp_mode": stage2_lp_mode_out,
                            "_stage2_relaxation_summary": stage2_relaxation_summary_out,
                            "_stage2_fallback_used": stage2_fallback_used_out,
                            "_stage2_ecm_failure_class": stage2_ecm_failure_class_out,
                        }

    return {
        "scipy_result": result,
        "feeds": feeds,
        "_relaxed": result.status == 0,
        "_infeasibility_hint": infeasibility_hint,
        "_feeding_system_config": _fs_cfg,
        "_block_labels": list(block_labels),
        "_concentrate_max_lp_slack_kg": conc_max_lp_slack_kg_out,
        "_concentrate_max_lp_slack_penalty": conc_max_lp_slack_penalty_out,
        "_stage2_lp_mode": stage2_lp_mode_out,
        "_stage2_relaxation_summary": stage2_relaxation_summary_out,
        "_stage2_fallback_used": stage2_fallback_used_out,
        "_stage2_ecm_failure_class": stage2_ecm_failure_class_out,
    }


def _suggestions_already_cover_hay_straw(suggestions: List[Dict[str, Any]]) -> bool:
    """True, wenn bereits ein Vorschlag Heu/Stroh/Raufutter implizit abdeckt."""
    for s in suggestions:
        blob = f"{s.get('feed', '')} {s.get('action', '')}".lower()
        if any(k in blob for k in ("stroh", "heu", "raufutter", "grasheu")):
            return True
    return False


_MAX_OPTIMAL_FEED_SUGGESTIONS = 3


def _build_optimal_feed_suggestions(
    req: _CowReq,
    feeds: List[Dict[str, Any]],
    *,
    warnings: List[str],
    stage2_relaxation_summary: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Bis zu drei konkrete Futtermittel-Richtungen zur Korb-Erweiterung bei optimaler Loesung.

    Nutzt dieselbe Kapazitaetslogik wie die Infeasibility-Diagnose sowie Warnungen /
    dokumentierte Relaxationen zu Struktur und fermentierbaren KH.
    """
    out: List[Dict[str, Any]] = []

    def push(item: Dict[str, Any]) -> None:
        if len(out) >= _MAX_OPTIMAL_FEED_SUGGESTIONS:
            return
        blob_new = f"{item.get('feed', '')} {item.get('action', '')}".lower()
        for x in out:
            blob_x = f"{x.get('feed', '')} {x.get('action', '')}".lower()
            if blob_new.strip() == blob_x.strip():
                return
        out.append(item)

    max_me = sum(f["me"] * f["max_kg"] for f in feeds)
    max_sidp = sum(f["sidp"] * f["max_kg"] for f in feeds)
    max_ndf = sum(f["ndf"] * f["max_kg"] for f in feeds)

    if max_ndf + 1e-6 < req.ndf_min_g:
        if not _suggestions_already_cover_hay_straw(out):
            push({
                "feed": "Wiesenheu / Raufutter",
                "dlg_id": "10150030",
                "ndf": "Heu typ. 450–650 g/kg TM (DLG-Tabellen)",
                "action": (
                    "Futtermittelliste um strukturreiches Grobfutter erweitern oder Max-FM bei Heu "
                    "erhoehen; orientierungsweise 0,5–3 kg TM/d. Energie-/Proteinbilanz mitpruefen."
                ),
                "rationale": "portfolio_ndf_capacity_below_req",
            })
        if len(out) < _MAX_OPTIMAL_FEED_SUGGESTIONS:
            if not any("stroh" in str(x.get("feed", "")).lower() for x in out):
                push({
                    "feed": "Weizen- oder Gerstenstroh",
                    "dlg_id": "10610000",
                    "ndf": "Stroh oft >750 g/kg TM aNDFom-aequivalent",
                    "action": (
                        "Struktur und peNDF-Puffer; langsam einarbeiten (verduennt ME/Protein – "
                        "Gesamtration neu bewerten)."
                    ),
                    "rationale": "portfolio_ndf_capacity_straw_option",
                })

    warn_blob = " ".join(warnings).lower()
    fiber_hit = any(
        k in warn_blob
        for k in (
            "strukturindex",
            "andfomgf",
            "struktur-faser",
            "rohfaser",
            "pendf",
            "langfaser",
            "grundfutteranteil",
        )
    )
    rel_fiber = False
    for row in stage2_relaxation_summary or []:
        ck = str(row.get("constraint") or "").lower()
        if "forage" in ck or "pabkh" in ck:
            rel_fiber = True
            break

    if (fiber_hit or rel_fiber) and not _suggestions_already_cover_hay_straw(out):
        push({
            "feed": "Heu (gute OMD) oder kompatibles Stroh",
            "dlg_id": "10150030 / 10610000",
            "action": (
                "Warnungen oder dokumentierte Relaxationen deuten auf strukturelle bzw. "
                "KH-Grenzkonflikte: langfaseriges Grobfutter erhoehen oder Staerkeanteile im Korb "
                "mischen, erneut optimieren."
            ),
            "rationale": "warnings_or_relaxation_structure_signal",
        })

    if len(out) >= _MAX_OPTIMAL_FEED_SUGGESTIONS:
        return out

    if max_me + 1e-6 < req.me_mj:
        push({
            "feed": "Koernermais oder Gerste",
            "dlg_id": "88 / 82",
            "me": "13.3 / 13.4 MJ/kg TM",
            "action": "Energiekonzentrat in die Auswahl aufnehmen oder Max-FM erhoehen (TMR-Band beachten).",
            "rationale": "portfolio_me_capacity_below_req",
        })

    if len(out) >= _MAX_OPTIMAL_FEED_SUGGESTIONS:
        return out

    if max_sidp + 1e-6 < req.sidp_g:
        push({
            "feed": "Rapsextraktionsschrot oder Sojaextraktionsschrot",
            "dlg_id": "97 / 105",
            "sidp": "190 / 250 g/kg TM",
            "action": "sidP-tragendes Kraftfutter ergaenzen oder Obergrenzen pruefen.",
            "rationale": "portfolio_sidp_capacity_below_req",
        })

    return out


def _diagnose_infeasibility(
    req: _CowReq,
    feeds: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Analysiert warum der LP keine Lösung findet und schlägt Korrekturfutter vor.

    Strategie: Schätze für jede Anforderung, ob die aktuellen Futtermittel sie
    prinzipiell erfüllen können (Summe der max_kg × Nährstoff ≥ Bedarf).
    """
    max_me   = sum(f["me"]   * f["max_kg"] for f in feeds)
    max_sidp = sum(f["sidp"] * f["max_kg"] for f in feeds)
    max_dmi  = sum(f["max_kg"] for f in feeds)
    max_ndf  = sum(f["ndf"]  * f["max_kg"] for f in feeds)
    max_ca   = sum((f.get("ca") or 0.0) * f["max_kg"] for f in feeds)
    max_p    = sum((f.get("p") or 0.0) * f["max_kg"] for f in feeds)
    max_na   = sum((f.get("na") or 0.0) * f["max_kg"] for f in feeds)
    max_mg   = sum((f.get("mg") or 0.0) * f["max_kg"] for f in feeds)
    pasture_pmr = _is_pasture_pmr_system(feeds, profile)

    gaps: List[str] = []
    suggestions: List[Dict[str, Any]] = []

    if max_me < req.me_mj:
        gaps.append(f"ME-Kapazität {max_me:.0f} MJ < Bedarf {req.me_mj:.0f} MJ")
        suggestions.append({
            "feed": "Körnermais oder Gerste",
            "dlg_id": "88 / 82",
            "me": "13.3 / 13.4 MJ/kg TM",
            "action": "Energiekonzentrat (max. 3–4 kg TM/d) in Ration aufnehmen.",
        })

    if max_sidp < req.sidp_g:
        gaps.append(f"sidP-Kapazität {max_sidp:.0f} g < Bedarf {req.sidp_g:.0f} g")
        suggestions.append({
            "feed": "Rapsextraktionsschrot (RES) oder Sojaextraktionsschrot (SES)",
            "dlg_id": "97 / 105",
            "sidp": "190 / 250 g/kg TM",
            "action": "Proteinergänzer bis 2,5 kg TM/d zufüttern.",
        })

    # Rohfaser-Deckel: gewählte max_kg reichen selbst bei voller Auslastung nicht
    # für das aNDFom-Minimum (harte LP-Nebenbedingung) -> Heu/Stroh als
    # nachvollziehbare Portfolio-Erweiterung / Argumentationshilfe.
    if max_ndf + 1e-6 < req.ndf_min_g:
        gaps.append(
            f"aNDFom-Kapazität {max_ndf:.0f} g/d < Mindestbedarf {req.ndf_min_g:.0f} g/d"
        )
        if not _suggestions_already_cover_hay_straw(suggestions):
            suggestions.append({
                "feed": "Wiesenheu / Raufutter oder Weizenstroh",
                "ndf": "Heu typ. 450–650 g/kg TM; Stroh oft >750 g/kg TM (DLG-Tabellen)",
                "action": (
                    "Futtermittelliste um strukturreiches Grobfutter erweitern, z. B. "
                    "0,5–3 kg TM/d Heu oder 0,3–1,5 kg TM/d Stroh. Stroh verdünnt stark "
                    "Energie und Protein – ME/sidP der Gesamtration neu bewerten. "
                    "Hinweis: Nur sinnvoll, wenn die Infeasibility mit zu geringer "
                    "Rohfaser-/Strukturdeckung im gewählten Portfolio zusammenhängt."
                ),
                "rationale": "infeasible_ndf_capacity",
            })

    cp_density_current = (
        sum(f["cp"] * f["max_kg"] for f in feeds) / max_dmi if max_dmi > 0 else 0
    )
    cp_limit = 185 if pasture_pmr else 160
    if cp_density_current > cp_limit and not any("cp" in g.lower() for g in gaps):
        gaps.append(f"CP-Dichte bei maximaler Auslastung {cp_density_current:.0f} g/kg TM > {cp_limit}")
        suggestions.append({
            "feed": "Maissilage (OMD mittel) oder Weizenstroh",
            "dlg_id": "50 / 12",
            "cp": "80 / 35 g/kg TM",
            "action": (
                "CP-armes Grundfutter/Stroh als Verdünner einsetzen "
                "(0,5–1,5 kg TM Stroh oder +2 kg TM Maissilage). "
                "Achtung: Stroh senkt auch ME – Energiebedarf neu prüfen."
            ),
        })

    xl_dense_feeds = [f["name"] for f in feeds if f["xl"] > 40 and f["max_kg"] > 0]
    if xl_dense_feeds:
        gaps.append(f"XL-Dichte-Konflikt durch: {', '.join(xl_dense_feeds)}")
        suggestions.append({
            "feed": "Anteile XL-reicher Futtermittel reduzieren",
            "action": (
                f"Maximalmenge von {', '.join(xl_dense_feeds)} verringern "
                f"(DLG-Limit 40 g XL/kg TM). "
                f"Alternativ: pansengeschütztes Fett (By-pass-Fett) einsetzen, "
                f"welches nicht zur XL-Fettlimitierung zählt."
            ),
        })

    mineral_checks = [
        ("Calcium", max_ca, req.ca_min_g, "calciumreicher Mineraltraeger oder Mineralfutter fuer Weide/PMR"),
        ("Phosphor", max_p, req.p_min_g, "P-ausgeglichenes Mineralfutter oder leistungsbezogenes Kraftfutter"),
        ("Natrium", max_na, req.na_min_g, "Viehsalz bzw. natriumhaltiges Weidemineral"),
        ("Magnesium", max_mg, req.mg_min_g, "Mg-betontes Weidemineral / Magnesiumoxid bei Weiderationen"),
    ]
    for label, actual, target, feed_hint in mineral_checks:
        if actual < target:
            gaps.append(f"{label}-Kapazitaet {actual:.1f} < Bedarf {target:.1f}")
            suggestions.append({
                "feed": feed_hint,
                "action": f"{label}-Versorgung ueber spezielles Mineralfutter absichern.",
            })

    max_me_supply = req.me_mj * 1.12 if req.me_mj > 0 else None
    if max_me_supply and req.mg_min_g / max_me_supply > max(
        (float(f.get("mg") or 0.0) / float(f.get("me") or 1.0)) for f in feeds if float(f.get("me") or 0.0) > 0
    ):
        gaps.append("Magnesiumdichte der ausgewaehlten Futtermittel reicht innerhalb der zulaessigen Energieversorgung nicht aus")
        suggestions.append({
            "feed": "Mg-betontes Weidemineral / Magnesiumoxid",
            "action": "Die aktuelle Weide-/PMR-Auswahl liefert je MJ Energie zu wenig Magnesium; Mg gezielt separat ergaenzen.",
        })

    n_forage_pos = sum(
        1 for f in feeds if f.get("forage") and float(f.get("max_kg") or 0.0) > 0.0
    )
    fiber_density_cap_g_kg = (max_ndf / max_dmi) if max_dmi > 1e-6 else 0.0

    if not gaps:
        gaps.append("Unbekannte Infeasibility – möglicherweise widersprüchliche Futter-Mengengrenzen.")
        suggestions.append({
            "feed": "Universalausgleich: Laktations-TMR-Konzentrat",
            "action": (
                "Fertig-Laktationsfutter (z.B. 18% XP, 7,2 MJ NEL/kg) in Ration aufnehmen "
                "und Einzelkomponenten-Grenzen prüfen."
            ),
        })
        # Argumentationshilfe nur bei plausibel grobfutter-/strukturarmem Set:
        # wenig echtes Grobfutter im Portfolio oder geringe maximale Faserdichte.
        if (
            not _suggestions_already_cover_hay_straw(suggestions)
            and (n_forage_pos <= 1 or fiber_density_cap_g_kg < 300.0)
        ):
            suggestions.append({
                "feed": "Heu oder Stroh (Struktur/Rohfaser, nur bei passendem Kontext)",
                "action": (
                    "Wenn die Nicht-Lösbarkeit mit knapper Struktur, zu wenig "
                    "wählbarem Grobfutter oder mit Rohfaser-/TMR-Dichtezielen zusammenhängen "
                    "könnte: zusätzlich 0,5–2 kg TM/d Heu bzw. 0,3–1 kg TM/d Stroh ins "
                    "Portfolio aufnehmen und Grenzen prüfen (Verdünnung von Energie/Protein)."
                ),
                "rationale": "infeasible_generic_structure_argument",
            })

    # FAN-MODE-002: Infeasibility-Reason kategorisieren, damit Bruder-Regression (§10.1)
    # keine pauschalen infeasibles mehr toleriert, sondern einen expliziten Grund erwartet.
    reason: Optional[str] = None
    text = " ".join(gaps).lower()
    if "magnesiumdichte" in text or "magnesium" in text and "mg" in text:
        reason = "mg_deficit"
    elif "kalium" in text or "k/mg" in text or "k:mg" in text:
        reason = "k_mg_antagonism"
    elif "me-kapaz" in text or "energie" in text:
        reason = "energy_deficit"
    elif "sidp" in text or "protein" in text:
        reason = "protein_deficit"
    elif "xl" in text:
        reason = "fat_density"
    elif "andfom-kapaz" in text:
        reason = "ndf_capacity"
    elif "cp" in text:
        reason = "cp_density"
    elif "calcium" in text:
        reason = "ca_deficit"
    elif "phosphor" in text:
        reason = "p_deficit"
    elif "natrium" in text:
        reason = "na_deficit"
    else:
        reason = "generic"

    return {"reason": reason, "gaps": gaps, "suggestions": suggestions}


# ---------------------------------------------------------------------------
# Response Builder
# ---------------------------------------------------------------------------

def _f(v: Any) -> float:
    return float(v)


def _kl_milk_from_me_density(
    me_density_mj_per_kg_tm: Optional[float],
    feeding_system: Optional[str] = None,
    *,
    tmr_me_density_mj_per_kg_tm: Optional[float] = None,
    fani: Optional[float] = None,
) -> float:
    """GfE 2001 §5: k_l (ME->NEL-Verwertung fuer Laktation) = 0,463 + 0,24*q.

    q = ME/GE mit GE ~ 18,4 MJ/kg TM (grobe Annahme fuer Wiederkaeuer-
    Mischrationen). Das Resultat wird auf den Arbeitsbereich 0,58-0,64
    begrenzt.

    PMR+Weide / PMR_pasture:
        Die Weide wird nicht im Mischwagen gefressen; die **physikalische**
        Mischration ist der **TMR-Block** (Mischwagen). Wenn
        ``tmr_me_density_mj_per_kg_tm`` aus der optimalen Loesung bekannt
        ist, wird k_l daraus wie bei TMR berechnet (nicht aus Weide-ME-
        Dichte). Ohne TMR-Anteil (>0 kg TM) bleibt der konservative
        Fallback 0,60.

        Optional: ``fani`` (Futteraufnahmeintensitaet) verschiebt k_l um
        0,01 je Einheit Abweichung von FANi=3,0 (GfE 2023: Nutzbarkeit/
        Passage grob), erneut auf 0,58-0,64 begrenzt.

    Ohne gueltige ME-Dichte (und ohne PMR-Weide-TMR-Fall) -> 0,60.
    """
    sys_norm = (feeding_system or "").strip().upper()
    is_pmr_pasture = sys_norm in {"PMR_PASTURE", "PMRPASTURE", "PMR+WEIDE"}

    if is_pmr_pasture:
        tmr_d = tmr_me_density_mj_per_kg_tm
        if tmr_d is not None and tmr_d > 0:
            q = tmr_d / 18.4
            kl = 0.463 + 0.24 * q
            kl = max(0.58, min(0.64, kl))
            if fani is not None and fani > 0:
                kl = max(0.58, min(0.64, kl + 0.01 * (float(fani) - 3.0)))
            return kl
        return 0.60

    if me_density_mj_per_kg_tm is None or me_density_mj_per_kg_tm <= 0:
        return 0.60
    q = me_density_mj_per_kg_tm / 18.4
    kl = 0.463 + 0.24 * q
    return max(0.58, min(0.64, kl))


def _milk_requirement_factors(
    profile: Dict[str, Any],
    me_density_mj_per_kg_tm: Optional[float] = None,
    feeding_system: Optional[str] = None,
    *,
    tmr_me_density_mj_per_kg_tm: Optional[float] = None,
    fani: Optional[float] = None,
) -> Tuple[float, float, float, float]:
    """Return maintenance ME plus milk coefficients for ME and sidP.

    Die Milch-Koeffizienten folgen der gleichen GfE-Basis wie
    `_gfe_requirements`, damit die Anzeige "Milch aus Grundfutter" mit dem
    Solver-Kontrakt konsistent bleibt.

    Weide-Aktivitaetszuschlag: bei feeding_type == "PMR+Weide" wird der
    ME-Erhaltungsbedarf um +15 % erhoeht (DLG-Merkblatt 417 / GfE 2001).

    k_l: bei TMR/PMR_stall aus ``me_density_mj_per_kg_tm``; bei PMR+Weide/
    PMR_pasture aus TMR-Block-Dichte (``tmr_me_density_mj_per_kg_tm``) und
    optional ``fani`` (siehe ``_kl_milk_from_me_density``).
    """
    bw = float(profile.get("body_weight_kg") or 650)
    fat_pct = float(profile.get("milk_fat_pct") or 4.0)
    prot_pct = float(profile.get("milk_protein_pct") or 3.4)
    bw75 = bw ** 0.75

    feeding_type = _normalize_feeding_type(profile.get("feeding_type"))
    pasture_factor = 1.15 if feeding_type == "PMR+Weide" else 1.00

    # Fallback: wenn kein feeding_system explizit gegeben ist, das
    # vorhandene feeding_type als Signalquelle nehmen.
    fs_for_kl = feeding_system
    if fs_for_kl is None and feeding_type == "PMR+Weide":
        fs_for_kl = "PMR_pasture"

    k_l = _kl_milk_from_me_density(
        me_density_mj_per_kg_tm,
        fs_for_kl,
        tmr_me_density_mj_per_kg_tm=tmr_me_density_mj_per_kg_tm,
        fani=fani,
    )

    me_maint = (0.308 * bw75 * pasture_factor) / 0.73
    nel_per_kg_milk = 0.38 * fat_pct + 0.21 * prot_pct + 0.95
    me_per_kg_milk = nel_per_kg_milk / k_l
    sidp_maint = (3.47 * bw75) * 0.95
    sidp_per_kg_milk = 52.0 * 0.95
    return me_maint, me_per_kg_milk, sidp_maint, sidp_per_kg_milk


def _maintenance_allocation_fraction(subset_me_sup: float, total_me_sup: float) -> float:
    """Anteil der Rations-ME [0..1] fuer anteilige Erhaltungsbuchung bei Teilmengen.

    Erhaltungs-ME und -sidP werden mit diesem Faktor gewichtet. Verwendung:
    ``forage_only_milk`` (GF-ME / Gesamt-ME), Weide-/Grassilage-Kennziffern im
    Pasture-Risk-Panel. Entspricht der ueblichen Buchhaltung bei Effizienz-
    Kennzahlen (Aufschluesselung nach Futtergruppen ueber ME-Anteile).
    Vergleiche zur energetischen Partitionierung bei Laktation:
    u.a. *Journal of Dairy Science* (ME-Nutzung, Erhaltung vs. Milch).
    """
    if total_me_sup <= 1e-9:
        return 0.0
    return max(0.0, min(1.0, subset_me_sup / total_me_sup))


def _milk_from_supply(
    me_sup: float,
    sidp_sup: float,
    profile: Dict[str, Any],
    me_density_mj_per_kg_tm: Optional[float] = None,
    feeding_system: Optional[str] = None,
    *,
    tmr_me_density_mj_per_kg_tm: Optional[float] = None,
    fani: Optional[float] = None,
    maintenance_allocation: Optional[float] = None,
) -> Dict[str, float]:
    me_maint, me_per_kg_milk, sidp_maint, sidp_per_kg_milk = _milk_requirement_factors(
        profile,
        me_density_mj_per_kg_tm,
        feeding_system,
        tmr_me_density_mj_per_kg_tm=tmr_me_density_mj_per_kg_tm,
        fani=fani,
    )
    # Anteilige Erhaltung (0..1): fuer Teilmengen (z.B. nur Weide-MJ) wird der
    # Erhaltungsbedarf wie in Effizienz-Bilanzen ueblich nach ME-Anteil an der
    # Gesamtration gewichtet. Vollbedarf (1,0) = bisheriges Verhalten.
    # Hintergrund: Partitionierung von ME bei Laktation (u.a. JDS); fuer
    # Marginalbeitraege einzelner Futtergruppen ist die pauschale Voll-Erhaltung
    # auf Teillieferanten fachlich irrefuehrend.
    _alloc = 1.0 if maintenance_allocation is None else float(maintenance_allocation)
    _alloc = max(0.0, min(1.0, _alloc))
    me_maint *= _alloc
    sidp_maint *= _alloc
    milk_from_energy = max(0.0, (me_sup - me_maint) / me_per_kg_milk) if me_per_kg_milk > 0 else 0.0
    milk_from_protein = max(0.0, (sidp_sup - sidp_maint) / sidp_per_kg_milk) if sidp_per_kg_milk > 0 else 0.0
    return {
        "milk_from_energy_kg": round(milk_from_energy, 1),
        "milk_from_protein_kg": round(milk_from_protein, 1),
        "limiting_milk_kg": round(min(milk_from_energy, milk_from_protein), 1),
    }


def _ecm_kg_per_kg_milk_factor(profile: Dict[str, Any]) -> float:
    """kg ECM je kg Milch bei festem Fett-/Proteingehalt der Milch [%].

    Gaengige Linearisierung (NRC-Ansatz):
      ECM [kg/d] = 0.327*M + 12.95*Fett_kg/d + 7.2*Protein_kg/d
    mit Fett_kg/d = M * fat%/100, Protein analog.
    """
    fat = float(profile.get("milk_fat_pct") or 4.0)
    prot = float(profile.get("milk_protein_pct") or 3.4)
    return 0.327 + 0.1295 * fat + 0.072 * prot


def _charnes_cooper_min_cost_per_milk_transform(
    A_ub: List[List[float]],
    b_ub: List[float],
    c_obj: List[float],
    bounds_x: List[Tuple[Any, Any]],
    *,
    v_lo: float,
    v_hi: float,
) -> Tuple[List[List[float]], List[float], List[float], List[Tuple[Any, Any]]]:
    """Charnes–Cooper: min c^T x / m mit x = y/v, Nebenbedingungen A x <= b => A y - b v <= 0.

    Bei konstantem ECM je kg Milch (Fett/Protein-% aus Profil) minimiert dasselbe
    LP die Futterkosten je kg ECM wie je kg physische Milch.
    """
    ncol = len(c_obj)
    if len(bounds_x) != ncol:
        raise ValueError("bounds_x und c_obj Laenge stimmen nicht ueberein")
    if not all(len(row) == ncol for row in A_ub):
        raise ValueError("A_ub-Zeilenbreite passt nicht zu c_obj")
    A_out: List[List[float]] = []
    b_out: List[float] = []
    for row, rhs in zip(A_ub, b_ub):
        A_out.append(list(row) + [-float(rhs)])
        b_out.append(0.0)
    for i in range(ncol):
        lb, ub = bounds_x[i]
        lb_eff = 0.0 if lb is None else float(lb)
        if lb_eff > 1e-12:
            zrow = [0.0] * (ncol + 1)
            zrow[i] = -1.0
            zrow[-1] = lb_eff
            A_out.append(zrow)
            b_out.append(0.0)
        else:
            zrow = [0.0] * (ncol + 1)
            zrow[i] = -1.0
            A_out.append(zrow)
            b_out.append(0.0)
        if ub is not None:
            ub_f = float(ub)
            z2 = [0.0] * (ncol + 1)
            z2[i] = 1.0
            z2[-1] = -ub_f
            A_out.append(z2)
            b_out.append(0.0)
    c_frac = list(c_obj) + [0.0]
    bounds_frac: List[Tuple[Any, Any]] = [(None, None)] * ncol + [(float(v_lo), float(v_hi))]
    return A_out, b_out, c_frac, bounds_frac


def _recover_x_from_charnes_cooper(res: Any, ncol: int) -> Optional[List[float]]:
    """Mappt Optimum (y, v) zurueck auf x = y/v."""
    if res is None or getattr(res, "status", None) not in (0, 1) or res.x is None:
        return None
    v_sol = float(res.x[ncol])
    if v_sol <= 1e-14:
        return None
    return [float(res.x[i]) / v_sol for i in range(ncol)]


def _stage2_feasibility_probe(
    A_ub: List[List[float]],
    b_ub: List[float],
    bounds: List[Tuple[Any, Any]],
) -> Any:
    """Trivial-Zielfunktion: prueft Zulaessigkeit von A_ub x <= b_ub unter bounds."""
    from scipy.optimize import linprog  # type: ignore[import]

    ncol = len(bounds)
    c_triv = [1e-9] * ncol
    try:
        return linprog(
            c=c_triv,
            A_ub=A_ub,
            b_ub=b_ub,
            bounds=bounds,
            method="highs",
            options={"disp": False},
        )
    except Exception:
        class _Bad:
            status = 4
            message = "feasibility_probe_exception"

        return _Bad()


def _classify_stage2_frac_failure(frac_res: Any, m_lo_ecm: float, m_hi_ecm: float) -> str:
    """Klassifikation wenn fraktionales ECM-LP nach Zulaessigkeit dennoch scheitert."""
    st = getattr(frac_res, "status", None)
    if st == 3:
        return "unbounded"
    if m_hi_ecm <= max(m_lo_ecm * 1.001, 1e-6) or m_lo_ecm < 0.05:
        return "zero_or_near_zero_ecm_denominator"
    return "numerical_fractional"


def _summarize_stage2_relaxations(
    orig_pabkh: float,
    orig_cp: float,
    orig_forage_floor: float,
    pe: float,
    cpe: float,
    fs: float,
    fm: float,
) -> List[Dict[str, Any]]:
    """Menschenlesbare Liste dokumentierter Stage-2-Relaxationen fuer API/UI."""
    out: List[Dict[str, Any]] = []
    if pe > 1e-9:
        out.append({
            "constraint": "pabkh_density_ceiling_g_kg_tm",
            "original": round(orig_pabkh, 2),
            "relaxed_to": round(orig_pabkh + pe, 2),
            "unit": "g/kg TM",
            "reason": (
                "begrenzte Aufweitung fermentierbarer KH (Komfortband) fuer ECM-Zielgang "
                "oder Charnes-Cooper-Stabilitaet"
            ),
        })
    if cpe > 1e-9:
        out.append({
            "constraint": "cp_density_ceiling_g_kg_tm",
            "original": round(orig_cp, 2),
            "relaxed_to": round(orig_cp + cpe, 2),
            "unit": "g/kg TM",
            "reason": (
                "moderate Aufweitung der CP-Obergrenze (Komfortband); ME-/sidP-Untergrenzen "
                "unveraendert"
            ),
        })
    if fs > 1e-9:
        out.append({
            "constraint": "stage2_forage_share_floor",
            "original": round(orig_forage_floor, 2),
            "relaxed_to": round(orig_forage_floor - fs, 2),
            "unit": "% TM (Modellgroesse Grundfutteranteil)",
            "reason": "leichte Absenkung der GF-Untergrenze nur nach weniger kritischen Schritten",
        })
    if fm > 1.0 + 1e-9:
        out.append({
            "constraint": "feed_max_kg_dm_non_forage",
            "original": 1.0,
            "relaxed_to": round(fm, 4),
            "unit": "Faktor auf max_kg TM",
            "reason": "kleiner Spielraum bei Kraftfutter-Obergrenzen (Profil-Feed-Caps)",
        })
    return out


# Abgleich UI „Milch aus Protein“ vs. „Milch aus Energie“ (kg Milch ~ l).
_ADJUST_EP_MAX_PROTEIN_EXCESS_KG = 2.0


def _build_ration_adjustment_suggestions(
    *,
    status: str,
    warnings: List[str],
    relaxation_policy: str,
    milk_p_excess_forage: Optional[float] = None,
    milk_p_excess_total: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """UI/API: maschinenlesbare Vorschlaege zur Rationsanpassung (Patch fuer Re-Optimierung).

    Prioritaet bleibt bei harten fachlichen Grenzen; Patches lockern hoechstens
    weiche Solver-Relaxation oder erweitern die Feed-Auswahl.
    """
    out: List[Dict[str, Any]] = []
    seen: Set[str] = set()

    def add(sid: str, title: str, detail: str, apply_patch: Dict[str, Any]) -> None:
        if sid in seen:
            return
        seen.add(sid)
        out.append({
            "id": sid,
            "title": title,
            "detail": detail,
            "apply_patch": apply_patch,
        })

    blob = " ".join(warnings).lower()
    ep_f = float(milk_p_excess_forage or 0.0)
    ep_t = float(milk_p_excess_total or 0.0)
    show_ep_f = ep_f > _ADJUST_EP_MAX_PROTEIN_EXCESS_KG + 1e-6
    show_ep_t = ep_t > _ADJUST_EP_MAX_PROTEIN_EXCESS_KG + 1e-6
    need_intervention = bool(warnings) or status != "optimal" or show_ep_f or show_ep_t

    if need_intervention:
        if relaxation_policy == "strict":
            add(
                "relax_standard",
                "Relaxation auf „standard“",
                "Lockert ausgewaehlte weiche Nebenbedingungen moderat; kann die Loesbarkeit verbessern.",
                {"relaxation_policy": "standard"},
            )
        if relaxation_policy in ("strict", "standard"):
            add(
                "relax_soft",
                "Relaxation auf „soft“",
                "Maximale Lockerung weicher Constraints im Solver (Kosten koennen steigen; harte Grenzen bleiben).",
                {"relaxation_policy": "soft"},
            )

    if status == "infeasible":
        if "cp-dichte" in blob or "xl-dichte" in blob or "xl-konflikt" in blob:
            add(
                "widen_basket_cp_xl",
                "Futtermittelkorb erweitern (CP/XL)",
                "Weitere Grobfutterpositionen mit moderatem Rohprotein/Rohfett waehlen oder stark fetthaltige "
                "Konzentrate begrenzen; dann erneut optimieren.",
                {},
            )
        if (
            "me-kapazit" in blob
            or "me-kapazität" in blob
            or ("energie" in blob and "kapaz" in blob)
        ):
            add(
                "widen_basket_me",
                "Energiebasis vergroessern",
                "Energiereichere Silage/Getreide zulassen oder Ziel-Leistung pruefen; Max-FM-Grenzen lockern.",
                {},
            )

    if "saftfutter" in blob or "nasse cop" in blob:
        add(
            "reduce_wet_cop",
            "Saftfutter / nasse CoP begrenzen",
            "Max-FM bei Rueben, Trebern, Kleinteilen senken oder Trockenkomponenten ergaenzen.",
            {},
        )

    if "k:mg" in blob or "tetanie" in blob or "grastetanie" in blob:
        add(
            "mg_mineral_pasture",
            "Weidemineral Mg/Na pruefen",
            "Mg-betontes Mineral sicherstellen; Weideanteil oder K-Zufuhr bewerten.",
            {},
        )

    if show_ep_f:
        add(
            "ep_balance_forage",
            "E/P auf Grundfutter ausgleichen",
            "Protein-Milchaequivalent liegt ueber dem Energie-Aequivalent (>"
            f" {_ADJUST_EP_MAX_PROTEIN_EXCESS_KG:g} kg): energiereicheres Grobfutter oder Getreide/Mais "
            "ergaenzen, stark proteinreiche Grobfutteranteile begrenzen.",
            {},
        )
    if show_ep_t and (not show_ep_f or ep_t > ep_f + 0.05):
        add(
            "ep_balance_after_concentrate",
            "E/P nach Kraftfutter pruefen",
            "Nach Modell-Konzentrat bleibt ein grosser Protein-Ueberhang: eher energielastiges Kraftfutter "
            "oder weniger proteinreiches Konzentrat.",
            {},
        )

    if need_intervention:
        add(
            "wizard_manual",
            "Eigene Anpassung im Assistenten",
            "Futtermittel-Auswahl, Max-FM je Position, FAN/Relaxation oder Saisonprofil anpassen, "
            "dann erneut „Optimieren“.",
            {},
        )

    return out


def _concentrate_displacement_factor(feeding_type: str, concentrate_dmi_kg: float) -> float:
    """
    Heuristic forage-displacement factor for concentrate supplements.

    DLG 01|2023 clearly requires forage displacement by concentrates to be considered,
    especially for PMR systems. The document does not provide one single universal
    formula for all farms, so the UI/API exposes a conservative engineering heuristic:
    - TMR: lower displacement because concentrate is embedded in the mixed ration
    - PMR: higher displacement because extra concentrate is fed performance-dependently
    The factor increases slightly with higher concentrate levels.
    """
    mode = _normalize_feeding_type(feeding_type)
    if mode == "TMR":
        base = 0.18
    elif mode == "PMR+Weide":
        # Weide verdraengt Grundfutter etwas staerker (DLG-Merkblatt 443: Konzentrat-
        # gabe waehrend Weide erhoeht die Konkurrenz um Aufnahmezeit am Bestand).
        base = 0.38
    else:
        base = 0.32
    step = min(max(concentrate_dmi_kg - 4.0, 0.0) * 0.015, 0.12)
    return min(base + step, 0.48)


# ---------------------------------------------------------------------------
# FAN-MODE-V1 / FAN-MODE-002: Hart/Weich-Klassifikation und Penalty-Score (Spec §5.2)
# ---------------------------------------------------------------------------

# Signatur eines klassifizierten Constraints:
#   kind       -> "hart" | "weich"    (Slice 2: weich hat immer eine Klasse)
#   klass      -> "A" | "B" | "C" | None
#   unit       -> Anzeige-Einheit
#   halfwidth  -> dimensionslose Toleranzbreite des Zielkorridors (Spec §5.2.1)
#   direction  -> "min" (actual muss >= target sein) | "max" (actual <= target) | "target" (bilateral)
_CONSTRAINT_CLASSIFICATION: Dict[str, Tuple[str, Optional[str], str, float, str]] = {
    # name                        -> (kind,   class, unit,      halfwidth, direction)
    "ME (MJ/d)":                    ("hart",  None,  "MJ/d",     0.0,     "min"),
    "sidP (g/d)":                   ("hart",  None,  "g/d",      0.0,     "min"),
    "TM-Aufnahme (kg/d)":           ("hart",  None,  "kg/d",     0.0,     "target"),
    "aNDFom (g/d)":                 ("weich", "B",   "g/d",    400.0,     "min"),
    "aNDFomGF (g/kg TM)":           ("weich", "B",   "g/kg TM", 30.0,     "min"),
    "pabKH (g/kg TM)":              ("weich", "B",   "g/kg TM", 20.0,     "max"),
    "XL Rohfett (g/kg TM)":         ("weich", "C",   "g/kg TM",  6.0,     "max"),
    "peNDF (g/kg TM)":              ("weich", "B",   "g/kg TM", 15.0,     "min"),
    "Magnesium (g/d)":              ("hart",  None,  "g/d",      0.0,     "min"),
    "Calcium (g/d)":                ("hart",  None,  "g/d",      0.0,     "min"),
    "Phosphor (g/d)":               ("hart",  None,  "g/d",      0.0,     "min"),
    "Grundfutteranteil (%TM)":      ("weich", "B",   "%TM",      5.0,     "min"),
    # Zusatz-Constraints, die im LP aktiv sind und ueber _build_constraint_status_v2
    # direkt aus supply/density Werten gespeist werden:
    "RMD (g N/kg TM)":              ("weich", "A",   "g N/kg TM", 1.5,    "target"),
    "Kalium (g/d)":                 ("weich", "A",   "g/d",     30.0,     "max"),
    "ME-Dichte (MJ/kg TM)":         ("weich", "A",   "MJ/kg TM", 0.5,     "max"),
    "sidP-Zielkorridor (g/d)":      ("weich", "A",   "g/d",    100.0,     "target"),
    "CP-Dichte (g/kg TM)":          ("weich", "C",   "g/kg TM", 20.0,     "max"),
    "K:Mg-Ratio":                   ("weich", "A",   "",         2.0,     "max"),
    # Konzentrat-Tagesmaximum nach FeedingSystemConfig (Slice 1e-Nachschaerfung
    # 2026-04-23, §4): Einzelgabe-Limits sind physiologisch hart (SARA-Schutz,
    # im LP als 1,5x-Sicherheitsnetz aktiv), das empfohlene Tagesmaximum
    # selbst wird weich bewertet. Klasse B (Struktur-/Komfort-nahe), Halb-
    # breite 1,5 kg TM/d, Richtung "max" (Ueberschreitung = Verletzung).
    "Konzentrat-Tagesmax (kg TM/d)": ("weich", "B",   "kg TM/d",  1.5,     "max"),
    # Saftfutter / nasse CoP: weiche Leitplanke (Ziel), vgl. Konstanten
    # _JUICE_WET_CAP_SOFT_KG_DM / LP-harte Deckelung separat.
    "Saftfutter/nasse CoP (kg TM/d)": ("weich", "B", "kg TM/d", 0.5, "max"),
}


def _classify_constraint(name: str) -> Tuple[str, Optional[str], str, float, str]:
    """Liefert Klassifikationstupel; unbekannte Namen fallen auf weich/C/keine Normierung."""
    return _CONSTRAINT_CLASSIFICATION.get(name, ("weich", "C", "", 0.0, "target"))


def _compute_penalty(
    name: str,
    actual: float,
    target: float,
    halfwidth: float,
    direction: str,
    relaxation_policy: str,
    kind: str,
    klass: Optional[str],
) -> Tuple[float, float, str]:
    """Berechnet (deviation_norm, penalty_cost, status_string) gemaess Spec §5.2.1.

    Verletzungen werden nur in Richtung der Constraint-Bedingung gewertet:
      - direction=min:  actual < target   => violation (target - actual)
      - direction=max:  actual > target   => violation (actual - target)
      - direction=target: beide Richtungen => |actual - target|
    """
    if halfwidth <= 0 or kind == "hart":
        # Harte Constraints: keine Penalty im weichen Sinn; Verletzung => hard_violated
        if direction == "min" and actual < target:
            return 0.0, 0.0, "hard_violated"
        if direction == "max" and actual > target:
            return 0.0, 0.0, "hard_violated"
        return 0.0, 0.0, "ok"

    if direction == "min":
        violation = max(0.0, target - actual)
    elif direction == "max":
        violation = max(0.0, actual - target)
    else:
        violation = abs(actual - target)

    deviation_norm = violation / halfwidth if halfwidth > 0 else 0.0
    factor = _RELAXATION_FACTORS.get(relaxation_policy, 1.0)
    klass_weight = _PENALTY_CLASS_WEIGHTS.get(klass or "C", 1.0)
    penalty = _PENALTY_BASE_COST * klass_weight * factor * deviation_norm
    status = "ok" if deviation_norm < 1e-6 else "violated"
    return deviation_norm, penalty, status


def _build_constraint_status_v2(
    constraint_report: List[Dict[str, Any]],
    relaxation_policy: str,
    extras: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """FAN-MODE-002 Constraint-Status: echte Penalty-Kosten je Constraint (Spec §5.2).

    Aufbau:
      1. Jeder Eintrag aus constraint_report wird klassifiziert.
      2. Zusaetzliche, im Report nicht aufgefuehrte weiche Kennzahlen (RMD, K:Mg, etc.)
         koennen ueber 'extras' nachgereicht werden.
      3. Fuer jede weiche Nebenbedingung wird penalty_cost nach der Formel aus §5.2.1
         berechnet: penalty = base × class_weight × relaxation_factor × deviation_norm.
    """
    out: List[Dict[str, Any]] = []
    seen_names: Set[str] = set()

    for item in constraint_report:
        name = item.get("name", "")
        seen_names.add(name)
        kind, klass, unit, halfwidth, direction = _classify_constraint(name)
        actual = float(item.get("actual") or 0.0)
        target = float(item.get("target") or 0.0)
        dev, pen, status = _compute_penalty(
            name, actual, target, halfwidth, direction, relaxation_policy, kind, klass,
        )
        # Hard-check via bestehendes fulfilled-Flag
        if kind == "hart" and not item.get("fulfilled", True):
            status = "hard_violated"
        out.append({
            "name": name,
            "kind": kind,
            "class": klass,
            "unit": unit or item.get("unit", ""),
            "target": round(target, 3),
            "actual": round(actual, 3),
            "difference": item.get("difference"),
            "fulfilled": bool(item.get("fulfilled", True)),
            "deviation_norm": round(dev, 3),
            "penalty_cost": round(pen, 4),
            "status": status,
            "source": "constraint_report",
        })

    for extra in extras or []:
        name = extra.get("name", "")
        if name in seen_names:
            continue
        kind, klass, unit, halfwidth, direction = _classify_constraint(name)
        actual = float(extra.get("actual") or 0.0)
        target = float(extra.get("target") or 0.0)
        dev, pen, status = _compute_penalty(
            name, actual, target, halfwidth, direction, relaxation_policy, kind, klass,
        )
        out.append({
            "name": name,
            "kind": kind,
            "class": klass,
            "unit": extra.get("unit", unit),
            "target": round(target, 3),
            "actual": round(actual, 3),
            "difference": round(actual - target, 3),
            "fulfilled": dev < 1e-6,
            "deviation_norm": round(dev, 3),
            "penalty_cost": round(pen, 4),
            "status": status,
            "source": extra.get("source", "supply_metric"),
        })

    return out


def _summarize_penalty(status: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregiert die Strafkosten pro Klasse und insgesamt."""
    totals = {"A": 0.0, "B": 0.0, "C": 0.0}
    hard_violations = 0
    soft_violations = 0
    for row in status:
        if row["kind"] == "hart":
            if row["status"] == "hard_violated":
                hard_violations += 1
            continue
        klass = row.get("class") or "C"
        totals[klass] = totals.get(klass, 0.0) + float(row.get("penalty_cost") or 0.0)
        if row["status"] == "violated":
            soft_violations += 1
    total = sum(totals.values())
    return {
        "total": round(total, 4),
        "by_class": {k: round(v, 4) for k, v in totals.items()},
        "soft_violations": soft_violations,
        "hard_violations": hard_violations,
    }


# Backwards-compat Alias (Slice 1 hat diese Funktion bereits aufgerufen)
def _derive_constraint_status_from_report(
    constraint_report: List[Dict[str, Any]],
    relaxation_policy: str,
) -> List[Dict[str, Any]]:
    return _build_constraint_status_v2(constraint_report, relaxation_policy)


# ---------------------------------------------------------------------------
# Slice 2 (2026-04-23): Futterabruf-Staffel (Concentrate Call-Up Table)
# ---------------------------------------------------------------------------
#
# Fachliche Grundlage (User-Review 2026-04-23, §4 "Futterabruf"):
#   - Staffel linear bzw. stueckweise linear OBERHALB Basisleistung.
#   - Basisleistung = Milch aus Grundfutter/Weide (limiting_milk_kg aus
#     forage_only_milk bei PMR, bzw. aus supplemented_milk bei TMR ohne
#     gestaffeltem Block). Erhaltungs-ME/-sidP fuer forage_only anteilig
#     nach GF-ME-Anteil an Gesamt-ME (_maintenance_allocation_fraction).
#   - Umrechnungsfaktor: 0,45-0,50 kg Konzentrat (FM) je kg Zusatzmilch
#     (Praxisrichtwert, entspricht ~1 l Konzentrat / 2 l Milch bei
#     Dichte ~0,5 kg/l). Dies ist als BAND angegeben (low/high).
#   - Einzelgabe-Limit (Pansenphysiologie) je Verteilungssystem wird
#     strikt geprueft und markiert.
#   - Tagesmaximum aus FeedingSystemConfig wird als Soft-Warnung
#     markiert (Kombination mit _CONC_HARD_SAFETY_FACTOR als harte
#     Obergrenze).
#
# Die Staffel ersetzt das frueher diskutierte "KI-Bildwerte" -Nachbauen.
# Konstanten siehe oben (direkt vor _run_lp): _CONC_PER_ADDITIONAL_MILK_LOW,
# _CONC_PER_ADDITIONAL_MILK_HIGH, _CONC_DEFAULT_DM_FRAC, _CONC_HARD_SAFETY_FACTOR.


def _build_concentrate_call_up_table(
    profile: Dict[str, Any],
    feeding_system_config: Dict[str, Any],
    base_milk_from_forage_kg: float,
    milk_kg_steps: Optional[List[float]] = None,
) -> Optional[Dict[str, Any]]:
    """Erzeugt eine Konzentrat-Futterabruf-Staffel (linear, stueckweise).

    Parameter:
        profile                 : Profil der Kuh (u.a. milk_kg_day als Ziel).
        feeding_system_config   : aufgeloeste FeedingSystemConfig-Werte.
        base_milk_from_forage_kg: kg Milch aus Grundfutter/Weide (Basis).
        milk_kg_steps           : optional explizite Leistungsstufen; sonst
                                  25/30/35/40/45 kg + Ziel aus Profil.

    Rueckgabe:
        None, wenn das System keine gestaffelte Konzentratgabe kennt
        (TMR / included_in_tmr) oder wenn feeding_system_config leer ist.
        Sonst Dict mit 'basis', 'rows' (je Leistungsstufe) und 'warnings'.
    """
    if not feeding_system_config:
        return None

    system = (feeding_system_config.get("system") or "").strip().upper()
    distribution = (feeding_system_config.get("concentrate_distribution") or "").strip().lower()
    # Nur gestaffelte Systeme (Transponder, AMS, Melkstand) liefern eine Staffel.
    if distribution not in {"transponder", "ams", "milkparlor"}:
        return None

    per_serving_max = float(feeding_system_config.get("concentrate_max_per_serving_kg") or 0.0)
    servings_per_day = float(feeding_system_config.get("concentrate_servings_per_day") or 0.0)
    per_day_max = float(feeding_system_config.get("concentrate_max_per_day_kg") or 0.0)

    target_milk = float(profile.get("milk_kg_day") or 0.0)
    basis_milk = max(0.0, float(base_milk_from_forage_kg or 0.0))

    # Stufen: 25/30/35/40/45 kg + Zielleistung (falls ausserhalb), sortiert & dedup.
    raw_steps: List[float] = list(milk_kg_steps) if milk_kg_steps else [25.0, 30.0, 35.0, 40.0, 45.0]
    if target_milk > 0 and target_milk not in raw_steps:
        raw_steps.append(round(target_milk, 1))
    # Duplikate entfernen, sortieren, auf positive Werte beschraenken
    steps = sorted({float(round(s, 1)) for s in raw_steps if s > 0})

    rows: List[Dict[str, Any]] = []
    warnings_list: List[str] = []

    for milk_kg in steps:
        # Stueckweise linear: unter Basis wird kein Konzentrat ergaenzt.
        additional_milk = max(0.0, milk_kg - basis_milk)
        conc_fm_low = additional_milk * _CONC_PER_ADDITIONAL_MILK_LOW
        conc_fm_high = additional_milk * _CONC_PER_ADDITIONAL_MILK_HIGH
        conc_fm_mid = 0.5 * (conc_fm_low + conc_fm_high)

        # Einzelgabe = Tagesmenge / Servings (wenn Servings > 0).
        per_serving_mid = (
            conc_fm_mid / servings_per_day if servings_per_day > 0 else conc_fm_mid
        )

        exceeds_serving = per_serving_max > 0 and per_serving_mid > per_serving_max + 1e-6
        exceeds_daily = per_day_max > 0 and conc_fm_mid > per_day_max + 1e-6
        hard_daily_cap = _CONC_HARD_SAFETY_FACTOR * per_day_max if per_day_max > 0 else 0.0
        exceeds_hard = hard_daily_cap > 0 and conc_fm_mid > hard_daily_cap + 1e-6

        row = {
            "milk_kg_day": round(milk_kg, 1),
            "additional_milk_kg": round(additional_milk, 1),
            # Band: low/high je kg FM (Praxisband 0,45-0,50 kg Konzentrat je kg Zusatzmilch)
            "concentrate_kg_fm_day_low": round(conc_fm_low, 2),
            "concentrate_kg_fm_day_high": round(conc_fm_high, 2),
            "concentrate_kg_fm_day_mid": round(conc_fm_mid, 2),
            # TM-Umrechnung (Richtwert 88 % TM-Gehalt Praxis-Konzentrat)
            "concentrate_kg_tm_day_mid": round(conc_fm_mid * _CONC_DEFAULT_DM_FRAC, 2),
            # Einzelgabe je Abruf/Melkung (kg FM) auf Basis mid
            "per_serving_kg_fm": round(per_serving_mid, 2),
            # Limit-Checks
            "exceeds_per_serving_limit": bool(exceeds_serving),
            "exceeds_recommended_daily_limit": bool(exceeds_daily),
            "exceeds_hard_safety_limit": bool(exceeds_hard),
        }
        rows.append(row)

        if exceeds_hard:
            warnings_list.append(
                f"{milk_kg:.0f} kg Milch: errechnete Konzentratmenge "
                f"({conc_fm_mid:.1f} kg FM/Tag) ueberschreitet die physiologische "
                f"Obergrenze ({hard_daily_cap:.1f} kg FM/Tag; 1,5x Tagesmax). "
                "Bei dieser Leistung sollte die Grundration energie-/proteindichter werden."
            )
        elif exceeds_serving:
            warnings_list.append(
                f"{milk_kg:.0f} kg Milch: Einzelgabe {per_serving_mid:.2f} kg FM "
                f"ueberschreitet Einzelgaben-Limit {per_serving_max:.1f} kg FM "
                f"({distribution}). Verteilung auf mehr Abrufe empfohlen."
            )

    return {
        "basis": {
            "feeding_system": system,
            "concentrate_distribution": distribution,
            "milk_from_forage_kg": round(basis_milk, 1),
            "target_milk_kg": round(target_milk, 1),
            "concentrate_max_per_serving_kg_fm": round(per_serving_max, 2) if per_serving_max > 0 else None,
            "concentrate_servings_per_day": servings_per_day if servings_per_day > 0 else None,
            "concentrate_max_per_day_kg_fm": round(per_day_max, 2) if per_day_max > 0 else None,
            "hard_safety_daily_cap_kg_fm": round(_CONC_HARD_SAFETY_FACTOR * per_day_max, 2) if per_day_max > 0 else None,
            "kg_conc_per_additional_milk_low": _CONC_PER_ADDITIONAL_MILK_LOW,
            "kg_conc_per_additional_milk_high": _CONC_PER_ADDITIONAL_MILK_HIGH,
            "assumed_concentrate_dm_frac": _CONC_DEFAULT_DM_FRAC,
        },
        "rows": rows,
        "warnings": warnings_list,
    }


# ---------------------------------------------------------------------------
# Slice 3 (2026-04-23): Mischprotokoll / Fuetterungsprotokoll
# ---------------------------------------------------------------------------
#
# Fachliche Grundlage (User-Review 2026-04-23, §5):
#   - Nur sinnvoll, wenn ein TMR-Block im Futtergang vorliegt (TMR oder
#     PMR_stall). Bei reinem PMR+Weide ohne TMR liefert das Protokoll
#     None (kein Mischwagen im Einsatz).
#   - Reihenfolge Vertikalmischer (Praxis):
#     1. Strukturfutter (Heu, Stroh)
#     2. Silagen (Grassilage, Maissilage)
#     3. Saftfutter / Co-Produkte (Ruebenschnitzel, Treber, Melasse)
#     4. Sonstiges
#     5. Kraftfutter + Mineralien
#   - Wasser zur Homogenitaet auf Ziel-TM 38-42 % (Default 40 %).
#   - Uebermenge: Praxisfaktor 5 % (Mischverluste / Futterreste).
#
# Abwaertskompatibel: None, wenn keine TMR-Komponenten im Ergebnis liegen.
# Refactor 2026-04-23: ausgelagert nach app.agrar.rations.constants.feeding_system
from app.agrar.rations.constants.feeding_system import (
    MIX_TARGET_DM_FRAC_DEFAULT as _MIX_TARGET_DM_FRAC_DEFAULT,
    MIX_OVERFILL_PCT_DEFAULT as _MIX_OVERFILL_PCT_DEFAULT,
)


def _mix_group_order(name: str) -> int:
    """Heuristische Mischreihenfolge anhand Futtername (Praxis-Regeln)."""
    n = (name or "").lower()
    if any(k in n for k in ("stroh", "heu")):
        return 1
    if any(k in n for k in ("silage", "gras", "mais")):
        return 2
    if any(k in n for k in ("ruebe", "rübe", "biertreber", "melasse", "schnitzel", "cop")):
        return 3
    if any(k in n for k in ("mineral", "kraftfutter", "konzentrat", "milchleistung")):
        return 5
    return 4


# Refactor 2026-04-23: ausgelagert nach app.agrar.rations.constants.feeding_system
from app.agrar.rations.constants.feeding_system import MIX_GROUP_LABELS as _MIX_GROUP_LABELS


def _build_mixing_protocol(
    ration_items: List[Dict[str, Any]],
    block_labels: List[str],
    feeds: List[Dict[str, Any]],
    amounts: List[float],
    feeding_system_config: Dict[str, Any],
    target_dm_frac: float = _MIX_TARGET_DM_FRAC_DEFAULT,
    overfill_pct: float = _MIX_OVERFILL_PCT_DEFAULT,
) -> Optional[Dict[str, Any]]:
    """Erzeugt das Misch- und Fuetterungsprotokoll fuer den TMR-Block.

    Rueckgabe None, wenn kein TMR-Block existiert oder das System rein
    weidebasiert ohne Mischwagen ist. Sonst Dict mit basis, steps,
    totals und warnings.
    """
    if not feeds or not amounts:
        return None

    system = (feeding_system_config.get("system") or "").strip().upper() if feeding_system_config else ""
    distribution = (feeding_system_config.get("concentrate_distribution") or "").strip().lower() if feeding_system_config else ""

    # TMR-Block-Positionen extrahieren. Wenn keine Block-Labels, behandeln
    # wir alle Feeds als TMR-Block (klassischer TMR).
    #
    # Sicherheitsnetz (User-Review 2026-04-24): Weide (TM < 30 %) wird
    # grundsaetzlich NIE in die Mischung aufgenommen, auch wenn das
    # Block-Label faelschlich "tmr_block" waere. Weide wird auf dem
    # Gruenland gefressen, nicht im Mischwagen gemischt. Die Block-
    # Zuordnung wird in ``_auto_assign_block`` bereits korrigiert -
    # dieser Filter ist bewusst redundant (Guertel und Hosentraeger).
    tmr_rows: List[Dict[str, Any]] = []
    excluded_pasture_kgdm = 0.0
    excluded_pasture_items: List[Dict[str, Any]] = []
    for idx, feed in enumerate(feeds):
        feed_view = _SolverFeed.from_dict(feed)
        kg_dm = amounts[idx] if idx < len(amounts) else 0.0
        if kg_dm < 0.001:
            continue
        label = block_labels[idx] if idx < len(block_labels) else "tmr_block"
        # Harter fachlicher Ausschluss: Weide niemals in Mischung.
        if _grass_feed_kind(feed) == "pasture":
            excluded_pasture_kgdm += kg_dm
            excluded_pasture_items.append({
                "feed_id": feed_view.id,
                "name": feed_view.name or "?",
                "kgdm": round(kg_dm, 3),
                "reason": "pasture_not_mixed",
            })
            continue
        if label != "tmr_block":
            continue
        dm_frac = feed_view.dm_frac
        kg_fm = kg_dm / dm_frac if dm_frac > 0 else kg_dm
        tmr_rows.append({
            "feed_id": feed_view.id,
            "name": feed_view.name or "?",
            "group_idx": _mix_group_order(feed_view.name),
            "kgdm": round(kg_dm, 3),
            "kgfm": round(kg_fm, 3),
            "dm_frac": dm_frac,
        })

    if not tmr_rows:
        return None

    tmr_rows.sort(key=lambda r: (r["group_idx"], -r["kgdm"]))
    for step, row in enumerate(tmr_rows, start=1):
        row["step"] = step
        row["group_label"] = _MIX_GROUP_LABELS.get(row["group_idx"], "Sonstiges")
        anteil = 0.0  # wird nachher berechnet
        row["share_fm_pct"] = anteil

    total_tmr_kgdm = sum(r["kgdm"] for r in tmr_rows)
    total_tmr_kgfm = sum(r["kgfm"] for r in tmr_rows)
    target_dm_frac = max(0.20, min(0.60, float(target_dm_frac)))
    target_total_fm = total_tmr_kgdm / target_dm_frac if target_dm_frac > 0 else total_tmr_kgfm
    water_kg = max(0.0, target_total_fm - total_tmr_kgfm)
    overfill_kg_fm = total_tmr_kgfm * (max(0.0, float(overfill_pct)) / 100.0)
    if total_tmr_kgfm > 0:
        for row in tmr_rows:
            row["share_fm_pct"] = round(row["kgfm"] / total_tmr_kgfm * 100.0, 1)

    warnings_list: List[str] = []
    actual_dm_frac = total_tmr_kgdm / total_tmr_kgfm if total_tmr_kgfm > 0 else 0.0
    if actual_dm_frac > target_dm_frac + 0.05:
        warnings_list.append(
            f"Mischung sehr trocken ({actual_dm_frac * 100:.0f} % TM). "
            f"Wasserzugabe {water_kg:.1f} kg empfohlen zur Homogenitaet auf "
            f"Ziel-TM {target_dm_frac * 100:.0f} %."
        )
    if actual_dm_frac < target_dm_frac - 0.08:
        warnings_list.append(
            f"Mischung sehr nass ({actual_dm_frac * 100:.0f} % TM). "
            "Wasserzugabe nicht noetig; ggf. trockene Komponenten (Heu/Stroh) erhoehen."
        )

    if excluded_pasture_kgdm > 0.001:
        warnings_list.append(
            f"Weide ({excluded_pasture_kgdm:.2f} kg TM) ist NICHT Teil der "
            "Mischung - wird separat auf dem Gruenland gefressen "
            "(DLG-Merkblatt 417: Weide/Gruenland-Nutzung). Ration wird "
            "als PMR (Partial Mixed Ration) gefuehrt."
        )

    return {
        "basis": {
            "feeding_system": system or "TMR",
            "concentrate_distribution": distribution or None,
            "target_dm_frac": round(target_dm_frac, 3),
            "actual_dm_frac_before_water": round(actual_dm_frac, 3),
            "overfill_pct": round(float(overfill_pct), 1),
        },
        "steps": tmr_rows,
        "water_addition_kg_fm": round(water_kg, 2),
        "overfill_kg_fm": round(overfill_kg_fm, 2),
        "totals": {
            "tmr_kgdm": round(total_tmr_kgdm, 2),
            "tmr_kgfm_without_water": round(total_tmr_kgfm, 2),
            "tmr_kgfm_with_water": round(total_tmr_kgfm + water_kg, 2),
            "tmr_kgfm_with_water_and_overfill": round(
                total_tmr_kgfm + water_kg + overfill_kg_fm, 2
            ),
        },
        "excluded_pasture": {
            "kgdm": round(excluded_pasture_kgdm, 3),
            "items": excluded_pasture_items,
        },
        "warnings": warnings_list,
    }


def _build_response(
    lp_out: Dict[str, Any],
    req: _CowReq,
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    result = lp_out["scipy_result"]
    feeds = lp_out["feeds"]
    runtime_options = lp_out.get("_runtime_options") or _resolve_runtime_options(profile)
    _stage2_rx: List[Dict[str, Any]] = list(lp_out.get("_stage2_relaxation_summary") or [])
    fan_opts = runtime_options.get("fan", {})
    fan_mode = fan_opts.get("mode", _FAN_DEFAULT_MODE)
    fan_reference = fan_opts.get("reference")
    fan_tolerance = fan_opts.get("tolerance", _FAN_DEFAULT_TOLERANCE)
    fan_tolerance_warn = fan_opts.get("tolerance_warn", _FAN_DEFAULT_TOLERANCE_WARN)
    fan_max_iterations = fan_opts.get("max_iterations", _FAN_DEFAULT_MAX_ITERATIONS)
    relaxation_policy = runtime_options.get("relaxation_policy", _RELAXATION_DEFAULT)
    objective_strategy = runtime_options.get("objective_strategy", "balance_then_cost")
    season_profile = runtime_options.get("season_profile")
    policy_profile = runtime_options.get("policy_profile", "pmr_standard")
    policy_overrides = runtime_options.get("policy_overrides", {}) or {}
    _wsg_meta = policy_overrides.get("wizard_soft_goals") or {}
    _wizard_soft_lp_meta: Optional[Dict[str, bool]] = None
    if _wsg_meta:
        _wizard_soft_lp_meta = {
            k: bool(_wsg_meta[k])
            for k in (
                "minimize_soya",
                "prefer_homegrown",
                "maximize_n_efficiency_rmd",
                "minimize_deviation_from_baseline",
            )
            if _wsg_meta.get(k)
        }
        if not _wizard_soft_lp_meta:
            _wizard_soft_lp_meta = None

    # FAN-Kalibrierung: Platzhalter-Payload (Slice 1) – FAN-Iteration folgt in Slice 3.
    fan_iterations = lp_out.get("_fan_iterations") or []
    fan_converged = lp_out.get("_fan_converged")
    fan_final = lp_out.get("_fan_final")
    fan_catalog_info = lp_out.get("_fan_catalog_info") or {}
    fan_calibration: Dict[str, Any] = {
        "mode": fan_mode,
        "reference": fan_reference,
        "tolerance": fan_tolerance,
        "tolerance_warn": fan_tolerance_warn,
        "max_iterations": fan_max_iterations,
        "iterations": fan_iterations,
        "iteration_count": len(fan_iterations),
        "converged": fan_converged,
        "fani_final": fan_final,
        "catalog_version": fan_catalog_info.get("version"),
        "feeds_exact": fan_catalog_info.get("feeds_exact", 0),
        "feeds_mapped": fan_catalog_info.get("feeds_mapped", 0),
        "feeds_fallback": fan_catalog_info.get("feeds_fallback", 0),
        "fallback_warning": fan_catalog_info.get("fallback_warning"),
    }
    constraint_status_from_lp: List[Dict[str, Any]] = lp_out.get("_constraint_status") or []

    if result.status != 0:
        hint = lp_out.get("_infeasibility_hint") or {}
        warnings = ["Keine optimale Lösung gefunden – Eingaben prüfen."]
        if hint.get("gaps"):
            warnings += [f"Ursache: {g}" for g in hint["gaps"]]
        _adj_inf = _build_ration_adjustment_suggestions(
            status="infeasible",
            warnings=warnings,
            relaxation_policy=str(relaxation_policy or _RELAXATION_DEFAULT),
        )
        return {
            "status": "infeasible",
            "ration_items": [],
            "nutrient_supply": {},
            "constraint_report": [],
            "constraint_status": constraint_status_from_lp,
            "penalty_summary": {"total": 0.0, "by_class": {"A": 0.0, "B": 0.0, "C": 0.0}, "soft_violations": 0, "hard_violations": 0},
            "dlg_indicators": {},
            "warnings": warnings,
            "feed_suggestions": hint.get("suggestions", []),
            "ration_adjustment_suggestions": _adj_inf,
            "total_cost_eur_day": None,
            "fan_calibration": fan_calibration,
            "active_policy_profile": policy_profile,
            "policy_overrides": policy_overrides,
            "relaxation_policy": relaxation_policy,
            "objective_strategy": objective_strategy,
            "season_profile": season_profile,
            "diagnosis": {
                "reason": hint.get("reason"),
                "gaps": hint.get("gaps", []),
                "suggestions": hint.get("suggestions", []),
            } if hint else None,
        }

    n_feeds = len(feeds)
    amounts = [_f(v) for v in result.x[:n_feeds]]
    total_cost = sum(amounts[i] * feeds[i]["price"] for i in range(len(feeds)))
    total_dmi = sum(amounts)

    # Slice 1f: Block-Zuordnung je Feed - abgeleitet aus lp_out oder
    # (Fallback) neu berechnet, damit ration_items["block"] und die
    # aggregierte ration_blocks-Sektion stets verfuegbar sind.
    _fs_cfg_resp = lp_out.get("_feeding_system_config") or _resolve_feeding_system_config(None, profile, feeds=feeds)
    _block_labels_resp = lp_out.get("_block_labels")
    if not _block_labels_resp or len(_block_labels_resp) != len(feeds):
        _fs_buckets_resp = _split_feeds_by_block(feeds, _fs_cfg_resp, [])
        _block_by_id_resp: Dict[str, str] = {}
        for _blk_name, _blk_feeds in _fs_buckets_resp.items():
            for _f_item in _blk_feeds:
                _block_by_id_resp[str(_f_item.get("id") or id(_f_item))] = _blk_name
        _block_labels_resp = [
            _block_by_id_resp.get(str(f.get("id") or id(f)), "tmr_block") for f in feeds
        ]

    # --- Rationsposten ---
    ration_items = []
    for i, feed in enumerate(feeds):
        kg_dm = amounts[i]
        if kg_dm < 0.001:
            continue
        kg_fm = kg_dm / feed["dm_frac"] if feed["dm_frac"] > 0 else kg_dm
        ration_items.append({
            "feed_id": feed["id"],
            "lid": feed.get("lid"),
            "name": feed["name"],
            "group": feed["group"],
            "forage": feed.get("forage", False),
            "kgdm": round(kg_dm, 3),
            "kgfm": round(kg_fm, 3),
            "dm_pct": round(feed["dm_frac"] * 100, 1),
            "unit_cost": round(float(feed["price"]), 4),
            "total_cost": round(kg_dm * float(feed["price"]), 4),
            "me_mj": round(kg_dm * feed["me"], 2),
            "sidp_g": round(kg_dm * feed["sidp"], 1),
            "cp_g": round(kg_dm * feed["cp"], 1),
            # Slice 1f: Block-Zuordnung (tmr_block / pasture_block /
            # concentrate_staged_block). Bei reinem TMR immer "tmr_block".
            "block": _block_labels_resp[i] if i < len(_block_labels_resp) else "tmr_block",
            # FAN-MODE-V1: Herkunft der FAN-abhaengigen Koeffizienten (Spec §8.2.3).
            # In Slice 1 noch komplett "fallback"; Slice 3 ersetzt dies durch den Katalog.
            "fan_slope_source": feed.get("_fan_slope_source", "fallback"),
        })

    # --- Nährstoffversorgung (Refactor Schritt 2, 2026-04-23) -------------
    # Alle Tagesaggregate werden in einem einzigen Pass berechnet;
    # Legacy-Variablennamen bleiben als Aliase erhalten, damit der Rest
    # von ``_build_response`` unveraendert bleibt.
    _agg = aggregate_ration(
        feeds,
        amounts,
        block_labels=_block_labels_resp,
        pendf_factor_fn=_feed_pendf_factor,
    )
    me_sup = _agg.me
    sidp_sup = _agg.sidp
    cp_sup = _agg.cp
    ndf_sup = _agg.ndf
    adf_sup = _agg.adf
    st_sup = _agg.st
    _bst_sup = _agg.bst  # noqa: F841
    zu_sup = _agg.zu
    xl_sup = _agg.xl
    ca_sup = _agg.ca
    p_sup = _agg.p
    na_sup = _agg.na
    mg_sup = _agg.mg
    k_sup = _agg.k
    sidlys_sup = _agg.sidlys
    sidmet_sup = _agg.sidmet

    _pendf_sup = _agg.pendf  # noqa: F841
    pendf_density = _agg.pendf_density

    # Stärke-Dichten
    st_density = _agg.st_density
    # Pansenabbaubare Staerke (ST - bST) als Input der Zebeli-2008-Formel (DLG 01|2025)
    abbaust_density = _abbaust_density_kgdm(feeds, amounts, total_dmi)
    pendf_min_val = _pendf_minimum(st_density, total_dmi)
    pendf_model_calibrated = _pendf_model_calibrated(st_density, total_dmi)

    # Pansen-pH-Vorhersage nach Zebeli 2008 (DLG 01|2025, Kap. 8.3)
    ph_predicted = _ph_predict(pendf_density, abbaust_density, total_dmi)
    ph_formula_applicable = _ph_inputs_in_range(pendf_density, abbaust_density, total_dmi)

    # Grundfutter-Anteile
    forage_kg = _agg.forage_kg
    concentrate_kg = max(total_dmi - forage_kg, 0.0)
    forage_ndf = _agg.forage_ndf
    forage_share_pct = _agg.forage_share_pct
    forage_me_sup = _agg.forage_me
    forage_sidp_sup = _agg.forage_sidp
    # DLG 01|2025: aNDFomGF+CoP - faserreiche Co-Produkte (Biertreber, Press-
    # schnitzel, Schlempe) werden gemeinsam mit Grobfutter als strukturelle
    # Faserbasis gewertet.
    _cop_kg = _agg.cop_kg  # noqa: F841
    _cop_ndf_sup = _agg.cop_ndf  # noqa: F841
    forage_plus_cop_ndf = _agg.forage_plus_cop_ndf
    feeding_type = _normalize_feeding_type(profile.get("feeding_type"))
    pasture_pmr = _is_pasture_pmr_system(feeds, profile)
    # pabKH [g/kg TM] fuer die aNDFomGF+CoP-Kaskade (DLG 01|2025, Kap. 8.2).
    _pre_pabkh_sup = _agg.pabkh
    _pre_pabkh_density = _agg.pabkh_density
    # Primaere Planungsgroesse (DLG 01|2025, Kap. 8.2): binaere pabKH-Kaskade
    # fuer aNDFomGF+CoP-Mindestdichte.
    andfom_gf_cop_target, _andfom_gf_cop_step = _andfom_gf_dlg2025_cascade(
        pabkh_density_kgdm=_pre_pabkh_density, pasture_pmr=pasture_pmr
    )
    andfom_gf_base = andfom_gf_cop_target          # fuer UI-Aufriss
    andfom_gf_starch_uplift = 0.0                  # Legacy-Aufschlag nicht mehr aktiv
    andfom_gf_target = andfom_gf_cop_target
    pabkh_target = 225.0 if pasture_pmr else 210.0
    xl_target = 42.0 if pasture_pmr else 40.0
    forage_share_target = 60.0 if pasture_pmr else 55.0
    displacement_factor = _concentrate_displacement_factor(feeding_type, concentrate_kg)
    forage_displacement_dmi = concentrate_kg * displacement_factor
    # ME-Dichte [MJ ME/kg TM] je Analyseebene fuer dichte-abhaengige k_l-Wahl
    # (GfE 2001 §5: k_l = 0,463 + 0,24*q). PMR+Weide: k_l aus TMR-Block-Dichte
    # + optional FANi (siehe _kl_milk_from_me_density).
    forage_me_density = forage_me_sup / forage_kg if forage_kg > 0 else None
    total_me_density = me_sup / total_dmi if total_dmi > 0 else None
    _fs_sys_for_kl = str(_fs_cfg_resp.get("system") or "").strip().upper()
    _pmr_pasture_kl = _fs_sys_for_kl in {"PMR_PASTURE", "PMRPASTURE"} or (
        feeding_type == "PMR+Weide" and pasture_pmr
    )
    tmr_me_density_for_kl: Optional[float] = None
    if _block_labels_resp and len(_block_labels_resp) == len(feeds) and _pmr_pasture_kl:
        _tmr_kg_sum = sum(
            amounts[i] for i in range(len(feeds)) if _block_labels_resp[i] == "tmr_block"
        )
        if _tmr_kg_sum > 1e-6:
            _tmr_me_sum = sum(
                amounts[i] * feeds[i]["me"]
                for i in range(len(feeds))
                if _block_labels_resp[i] == "tmr_block"
            )
            tmr_me_density_for_kl = _tmr_me_sum / _tmr_kg_sum
    _fani_for_kl: Optional[float] = None
    if fan_final is not None and _pmr_pasture_kl:
        try:
            _fani_for_kl = float(fan_final)
        except (TypeError, ValueError):
            _fani_for_kl = None
    _milk_kl_kw: Dict[str, Any] = {}
    if _pmr_pasture_kl:
        _milk_kl_kw["tmr_me_density_mj_per_kg_tm"] = tmr_me_density_for_kl
        if _fani_for_kl is not None:
            _milk_kl_kw["fani"] = _fani_for_kl
    _forage_maint_alloc = _maintenance_allocation_fraction(forage_me_sup, me_sup)
    forage_only_milk = _milk_from_supply(
        forage_me_sup,
        forage_sidp_sup,
        profile,
        forage_me_density,
        **{**_milk_kl_kw, "maintenance_allocation": _forage_maint_alloc},
    )
    supplemented_milk = _milk_from_supply(
        me_sup, sidp_sup, profile, total_me_density, **_milk_kl_kw
    )

    # --- Weide-/Grobfutter-spezifische Leistungs- und Risiko-Auswertung (DLG 417/443) ---
    # Wichtig: DLG-Futterwerttabellen fuehren Futterwerte unter Namen wie
    # "Gras, frisch o. konserviert, 2. Aufwuchs". In der Praxis ist die
    # "konservierte" Variante grundsaetzlich **Grassilage** (konserviertes
    # Gras = siliertes Gras). Wir werten deshalb jeden Namen mit dem
    # Stichwort "konserviert" als Grassilage und NICHT als Weide - auch
    # wenn gleichzeitig "frisch" im Namen steht. Entscheidend ist dabei
    # der explizite Hinweis auf Lagerung/Konservierung.
    def _is_grass_silage(feed: Dict[str, Any]) -> bool:
        # TM-basierte Klassifikation (siehe _grass_feed_kind):
        #   Grassilage = TM 30-80 % (inkl. Anwelksilage / Heulage)
        return _grass_feed_kind(feed) == "grass_silage"

    def _is_pasture_feed(feed: Dict[str, Any]) -> bool:
        # Weide/Frischgras = TM < 30 %. Grassilage (>= 30 % TM) hat Vorrang.
        return _grass_feed_kind(feed) == "pasture"

    pasture_kg = sum(amounts[i] for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_me_sup = sum(amounts[i] * feeds[i]["me"] for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_sidp_sup = sum(amounts[i] * feeds[i]["sidp"] for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_k_sup = sum(amounts[i] * float(feeds[i].get("k") or 0.0) for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_mg_sup = sum(amounts[i] * float(feeds[i].get("mg") or 0.0) for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_cp_sup = sum(amounts[i] * feeds[i]["cp"] for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))

    grass_silage_kg = sum(amounts[i] for i in range(len(feeds)) if _is_grass_silage(feeds[i]))
    grass_silage_me_sup = sum(amounts[i] * feeds[i]["me"] for i in range(len(feeds)) if _is_grass_silage(feeds[i]))
    grass_silage_sidp_sup = sum(amounts[i] * feeds[i]["sidp"] for i in range(len(feeds)) if _is_grass_silage(feeds[i]))

    # Dichte-spezifisches k_l je Teilfutter (GfE 2001 §5)
    pasture_me_density = pasture_me_sup / pasture_kg if pasture_kg > 0 else None
    grass_silage_me_density = grass_silage_me_sup / grass_silage_kg if grass_silage_kg > 0 else None
    pasture_plus_grass_kg = pasture_kg + grass_silage_kg
    pasture_plus_grass_me_density = (
        (pasture_me_sup + grass_silage_me_sup) / pasture_plus_grass_kg
        if pasture_plus_grass_kg > 0 else None
    )

    _pasture_maint_alloc = _maintenance_allocation_fraction(pasture_me_sup, me_sup)
    _grass_silage_maint_alloc = _maintenance_allocation_fraction(grass_silage_me_sup, me_sup)
    _pasture_plus_grass_maint_alloc = _maintenance_allocation_fraction(
        pasture_me_sup + grass_silage_me_sup, me_sup
    )

    pasture_milk = (
        _milk_from_supply(
            pasture_me_sup,
            pasture_sidp_sup,
            profile,
            pasture_me_density,
            **{**_milk_kl_kw, "maintenance_allocation": _pasture_maint_alloc},
        )
        if pasture_kg > 0 else None
    )
    grass_silage_milk = (
        _milk_from_supply(
            grass_silage_me_sup,
            grass_silage_sidp_sup,
            profile,
            grass_silage_me_density,
            **{**_milk_kl_kw, "maintenance_allocation": _grass_silage_maint_alloc},
        )
        if grass_silage_kg > 0 else None
    )
    pasture_plus_grass_milk = (
        _milk_from_supply(
            pasture_me_sup + grass_silage_me_sup,
            pasture_sidp_sup + grass_silage_sidp_sup,
            profile,
            pasture_plus_grass_me_density,
            **{**_milk_kl_kw, "maintenance_allocation": _pasture_plus_grass_maint_alloc},
        )
        if pasture_plus_grass_kg > 0 else None
    )

    pasture_k_mg_ratio = pasture_k_sup / pasture_mg_sup if pasture_mg_sup > 0 else None
    pasture_cp_density = pasture_cp_sup / pasture_kg if pasture_kg > 0 else None
    pasture_mg_supplement_kg = sum(
        amounts[i] for i in range(len(feeds)) if feeds[i].get("_special") == "pasture_mg"
    )

    # aNDFomGF-Dichte [g/kg TM] (nur Grobfutter, Legacy-Anzeige)
    andfom_gf_density = forage_ndf / total_dmi if total_dmi > 0 else 0.0
    # DLG 01|2025: aNDFomGF+CoP-Dichte [g/kg TM] (Grobfutter + faserreiche Co-Produkte)
    andfom_gf_cop_density = forage_plus_cop_ndf / total_dmi if total_dmi > 0 else 0.0

    # pabKH [g/kg TM]
    pabkh_sup = _pre_pabkh_sup
    pabkh_density = _pre_pabkh_density

    # Fermentationsindex Kohlenhydrate (DLG 01|2025 Kap. 8.4)
    fikh_pct, fikh_diag = _fikh_percent(feeds, amounts, total_dmi)

    # XL-Dichte [g/kg TM]
    xl_density = xl_sup / total_dmi if total_dmi > 0 else 0.0

    # --- Strukturindex (DLG 01|2023, Rutzmoser et al. 2011) ---
    # SI = NDFomGF_kg / (NDFomGF_kg + (pabKH_kg - 2.8)/0.36) × 100
    # NDFomGF_kg = forage_ndf/1000 per Tier und Tag; pabKH_kg = pabkh_sup/1000
    ndfom_gf_kg = forage_ndf / 1000.0
    pabkh_kg = pabkh_sup / 1000.0
    if ndfom_gf_kg > 0 and (ndfom_gf_kg + (pabkh_kg - 2.8) / 0.36) > 0:
        si = ndfom_gf_kg / (ndfom_gf_kg + (pabkh_kg - 2.8) / 0.36) * 100.0
    else:
        si = None

    # --- RMD (Ruminale Mikrobielle Differenz) – Ration gesamt ---
    _rmd_vals = [feeds[i].get("rmd") for i in range(len(feeds)) if amounts[i] > 0.001]  # noqa: F841
    has_rmd = any(v is not None for v in [feeds[i].get("rmd") for i in range(len(feeds))])
    rmd_ration = None
    if has_rmd and total_dmi > 0:
        rmd_ration = sum(
            amounts[i] * (feeds[i].get("rmd") or 0)
            for i in range(len(feeds))
        ) / total_dmi

    nutrient_supply = {
        "dmi_kg": round(total_dmi, 2),
        "me_mj": round(me_sup, 1),
        "me_kgdm": round(me_sup / total_dmi, 2) if total_dmi > 0 else None,
        "nel_ref_mj": round(req.nel_mj, 1),
        "sidp_g": round(sidp_sup, 0),
        "sidp_kgdm": round(sidp_sup / total_dmi, 1) if total_dmi > 0 else None,
        "cp_g": round(cp_sup, 0),
        "cp_kgdm": round(cp_sup / total_dmi, 1) if total_dmi > 0 else None,
        "andfom_g": round(ndf_sup, 0),
        "andfom_kgdm": round(ndf_sup / total_dmi, 1) if total_dmi > 0 else None,
        "andfom_gf_kgdm": round(andfom_gf_density, 1),
        # DLG 01|2025: aNDFomGF+CoP (Grobfutter + faserreiche Co-Produkte)
        "andfom_gf_cop_kgdm": round(andfom_gf_cop_density, 1),
        "adfom_g": round(adf_sup, 0),
        "staerke_g": round(st_sup, 0),
        "pabkh_kgdm": round(pabkh_density, 1),
        "zucker_g": round(zu_sup, 0),
        "xl_g": round(xl_sup, 0),
        "xl_kgdm": round(xl_density, 1),
        "ca_g": round(ca_sup, 1),
        "p_g": round(p_sup, 1),
        "na_g": round(na_sup, 1),
        "mg_g": round(mg_sup, 1),
        "k_g": round(k_sup, 1),
        "sidlys_g": round(sidlys_sup, 1) if sidlys_sup else None,
        "sidmet_g": round(sidmet_sup, 1) if sidmet_sup else None,
        "sidlys_sidmet_ratio": round(sidlys_sup / sidmet_sup, 2) if sidmet_sup and sidmet_sup > 0 else None,
        "forage_share_pct": round(forage_share_pct, 1),
        "rmd_gn_kgdm": round(rmd_ration, 2) if rmd_ration is not None else None,
        "pendf_kgdm": round(pendf_density, 1),
        "pendf_min_kgdm": round(pendf_min_val, 1),
        "staerke_kgdm": round(st_density, 1),
        "abbaust_kgdm": round(abbaust_density, 1),
        "ph_predicted": ph_predicted,
    }

    # --- Constraint-Report (DLG 01|2023 Ampel) ---
    def _cr(
        name: str,
        actual: float,
        target: float,
        max_val: Optional[float] = None,
        unit: str = "",
    ) -> Dict[str, Any]:
        actual = float(actual)
        target = float(target)
        diff = actual - target
        fulfilled = actual >= target * 0.98
        if max_val is not None and actual > float(max_val):
            status = "MAX_EXCEEDED"
            fulfilled = False
        elif fulfilled:
            status = "OK"
        else:
            status = "MIN_DEFICIENT"
        return {
            "name": name,
            "unit": unit,
            "target": round(target, 1),
            "actual": round(actual, 1),
            "difference": round(diff, 1),
            "fulfilled": bool(fulfilled),
            "status": status,
        }

    constraint_report = [
        _cr("ME (MJ/d)",              me_sup,        req.me_mj,    unit="MJ/d"),
        _cr("sidP (g/d)",             sidp_sup,      req.sidp_g,   unit="g/d"),
        _cr("TM-Aufnahme (kg/d)",     total_dmi,     req.dmi_min_kg, req.dmi_max_kg, unit="kg/d"),
        _cr("aNDFom (g/d)",           ndf_sup,       req.ndf_min_g, unit="g/d"),
        _cr("aNDFomGF+CoP (g/kg TM)", andfom_gf_cop_density, andfom_gf_target, unit="g/kg TM"),
        _cr("pabKH (g/kg TM)",        pabkh_target,         pabkh_density, unit="g/kg TM"),  # max-check
        _cr("XL Rohfett (g/kg TM)",   xl_target,          xl_density,   unit="g/kg TM"),   # max-check
        _cr("peNDF (g/kg TM)",        pendf_density, pendf_min_val,                   unit="g/kg TM"),
        _cr("Magnesium (g/d)",        mg_sup,        req.mg_min_g, unit="g/d"),
        _cr("Calcium (g/d)",          ca_sup,        req.ca_min_g, unit="g/d"),
        _cr("Phosphor (g/d)",         p_sup,         req.p_min_g,  unit="g/d"),
        _cr("Grundfutteranteil (%TM)", forage_share_pct, forage_share_target,     unit="%TM"),
    ]

    # --- DLG-Indikatoren (01|2025) ---
    dlg_indicators: Dict[str, Any] = {
        "strukturindex": round(si, 1) if si is not None else None,
        "strukturindex_ziel": ">= 50",
        "strukturindex_erfuellt": bool(si is not None and si >= 50.0),
        "andfom_gf_kgdm": round(andfom_gf_density, 1),
        "andfom_gf_cop_kgdm": round(andfom_gf_cop_density, 1),
        "andfom_gf_ziel": (
            f">= {andfom_gf_target:.0f} g/kg TM aNDFomGF+CoP "
            f"(DLG 01|2025 Kap. 8.2, pabKH={pabkh_density:.0f} -> "
            f"Stufe {_andfom_gf_cop_step}, Ziel {andfom_gf_cop_target:.0f})"
        ),
        "andfom_gf_base": round(andfom_gf_base, 1),
        "andfom_gf_starch_uplift": round(andfom_gf_starch_uplift, 1),
        "andfom_gf_cop_step": _andfom_gf_cop_step,
        "andfom_gf_cop_target_kgdm": round(andfom_gf_cop_target, 1),
        "andfom_gf_cop_erfuellt": bool(andfom_gf_cop_density >= andfom_gf_cop_target * 0.98),
        "pabkh_kgdm": round(pabkh_density, 1),
        "pabkh_ziel": f"<= {pabkh_target:.0f} g/kg TM",
        "xl_kgdm": round(xl_density, 1),
        "xl_ziel": f"<= {xl_target:.0f} g/kg TM",
        "rmd_gn_kgdm": round(rmd_ration, 2) if rmd_ration is not None else None,
        "rmd_ziel": "-1 bis 0 g N/kg TM",
        "forage_share_pct": round(forage_share_pct, 1),
        "forage_share_ziel": f">= {forage_share_target:.0f}% TM",
        "pendf_kgdm": round(pendf_density, 1),
        "pendf_min_kgdm": round(pendf_min_val, 1),
        # DLG 01|2023: peNDF dient in der Rationsplanung nur als Kontroll- und
        # Validierungsgroesse, nicht als primaerer Steuerhebel. Die Planung laeuft
        # ueber aNDFomGF. Deshalb wird das peNDF-Ziel explizit als "Kontrolle"
        # gekennzeichnet; die eigentliche Steuergroesse steht unter andfom_gf_ziel.
        "pendf_ziel": (
            f"Kontrolle: >= {pendf_min_val:.0f} g/kg TM (staerkeabhaengig, GfE-Workshop 2023). "
            f"Primaer-Planung: aNDFomGF."
        ),
        "pendf_erfuellt": bool(pendf_density >= pendf_min_val),
        "pendf_model_calibrated": pendf_model_calibrated,
        "pendf_model_status": (
            "peNDF-Modell im kalibrierten Bereich"
            if pendf_model_calibrated
            else "peNDF ausserhalb Modellbereich; Fallback-Regeln verwendet"
        ),
        "pendf_role": "Kontrolle/Validierung (DLG 01|2023)",
        "ph_predicted": ph_predicted,
        "ph_ziel": ">= 6.2 (kritisch < 5.9)",
        "ph_ok": bool(ph_predicted >= 6.2),
        "ph_formula_applicable": ph_formula_applicable,
        "ph_formula_source": "Zebeli et al. 2008; DLG 01|2025 Kap. 8.3",
        "abbaust_kgdm": round(abbaust_density, 1),
        # DLG 01|2025, Kap. 8.4: Fermentationsindex Kohlenhydrate
        "fikh_pct": fikh_pct,
        "fikh_ziel": f">= {_FIKH_TARGET_PCT:.0f} %",
        "fikh_erfuellt": bool(fikh_pct is not None and fikh_pct >= _FIKH_TARGET_PCT),
        "fikh_diagnose": fikh_diag,
        "fikh_quelle": "DLG 01|2025 Kap. 8.4",
    }

    # Amino acid ratio (post-check only, not in LP)
    sidlys_sidmet_ratio = (sidlys_sup / sidmet_sup) if sidmet_sup and sidmet_sup > 0 else None

    # --- Warnungen und Erklärungen ---
    warnings: List[str] = []
    if _stage2_rx:
        warnings.append(
            "Die EUR/kg-ECM-Optimierung war zunaechst nicht mit dem Ausgangs-Nebenbedingungssatz "
            "loesbar. Es wurden kleine, dokumentierte Relaxationen an fachlich weniger kritischen "
            "Grenzen geprueft bzw. angewendet (siehe relaxation_summary). Bitte Relaxationen "
            "fachlich kontrollieren, bevor die Ration uebernommen wird."
        )
    if lp_out.get("_stage2_lp_mode") == "feed_eur_per_day_fallback":
        warnings.append(
            "Stage 2: Das Ziel EUR/kg ECM war fuer das fraktionale LP nicht erreichbar "
            "(keine gueltige Loesung oder Recovery fehlgeschlagen); es wurde auf "
            "Minimierung EUR/Tag zurueckgeschaltet. Die harten Nebenbedingungen "
            "(ME, sidP, Mindest-TM usw.) sind dieselben wie bei ECM; bei positivem "
            "Bedarf ist 'nichts fuettern' weiterhin ausgeschlossen. Bei wiederholbarem "
            "Fallback Futtermittelkorb oder Relaxation pruefen."
        )
    if si is not None and si < 50:
        warnings.append(
            f"Strukturindex {si:.1f} < 50 – Pansen-pH < 6,15 wahrscheinlich. "
            f"aNDFomGF erhöhen oder pabKH (Stärke+Zucker) reduzieren."
        )
    if andfom_gf_cop_density < andfom_gf_target:
        warnings.append(
            f"aNDFomGF+CoP {andfom_gf_cop_density:.0f} g/kg TM < {andfom_gf_target:.0f} – "
            f"Struktur-Faserversorgung (Grobfutter + faserreiche Co-Produkte) unzureichend "
            f"(DLG 01|2025 Kap. 8.2)."
        )
    if pabkh_density > pabkh_target:
        warnings.append(
            f"pabKH {pabkh_density:.0f} g/kg TM > {pabkh_target:.0f} – Pansenazidose-Risiko erhöht."
        )
    if _andfom_gf_cop_step == ">260_warn":
        warnings.append(
            f"pabKH {pabkh_density:.0f} g/kg TM > 260 g/kg TM – abbaubare Staerke zu hoch. "
            f"DLG 01|2025 empfiehlt Umstellung auf Sorten/Konservate mit hoeherem bST-Anteil "
            f"(resistenter Staerke) oder CCM statt Mais-/Getreideflocken."
        )
    if fikh_pct is not None and fikh_pct < _FIKH_TARGET_PCT:
        warnings.append(
            f"FIKH {fikh_pct:.0f} % < {_FIKH_TARGET_PCT:.0f} % – Fermentation im Pansen einseitig "
            f"auf Staerke/Zucker. DLG 01|2025 Kap. 8.4 empfiehlt Anhebung der verdaulichen "
            f"aNDFom (DNDF) z. B. durch juengere Grassilage, Biertreber oder Pressschnitzel."
        )
    # XL: Weide/PMR-Systeme etwas toleranter, aber weiter tierwohlbegrenzt.
    if xl_density > (xl_target + 4.0):
        warnings.append(
            f"Rohfett (XL) {xl_density:.0f} g/kg TM > {xl_target + 4.0:.0f} – zellulolytische Pansenmikroben stark gehemmt. "
            f"Grenzwert {xl_target:.0f} g/kg TM deutlich überschritten."
        )
    elif xl_density > xl_target:
        warnings.append(
            f"Rohfett (XL) {xl_density:.1f} g/kg TM leicht über Richtwert {xl_target:.0f} – Pansen beobachten."
        )
    if forage_share_pct < forage_share_target:
        warnings.append(
            f"Grundfutteranteil {forage_share_pct:.0f}% TM < {forage_share_target:.0f}% – "
            f"Wiederkäuergerechtigkeit prüfen."
        )
    # RMD: Ziel -1,5 bis 0 g N/kg TM (DLG 01|25); LP-Toleranz bis +1,5; Alarm ab +2,0
    if rmd_ration is not None and rmd_ration > 2.0:
        warnings.append(
            f"RMD {rmd_ration:.2f} g N/kg TM > 2,0 – N-Effizienz sehr gering, "
            f"Harnstoffbelastung wahrscheinlich. CP-Anteil reduzieren oder UDP-Futter einsetzen."
        )
    elif rmd_ration is not None and rmd_ration > 1.5:
        warnings.append(
            f"RMD {rmd_ration:.2f} g N/kg TM – Toleranzbereich (Ziel 0, DLG-Toleranz bis +1,5) leicht überschritten."
        )
    elif rmd_ration is not None and 0.0 < rmd_ration <= 1.5:
        warnings.append(
            f"RMD {rmd_ration:.2f} g N/kg TM – im DLG-Toleranzbereich (Ziel ≤ 0, Toleranz bis +1,5). "
            f"Pansen-N-Bilanz beobachten."
        )
    if rmd_ration is not None and rmd_ration < -1.5:
        warnings.append(
            f"RMD {rmd_ration:.2f} g N/kg TM – Pansen-N-Mangel möglich; "
            f"MXP-Synthese eingeschränkt."
        )
    _juice_wet_sum = sum(
        amounts[i]
        for i in range(len(feeds))
        if _feed_counts_toward_saftfutter_wet_cap(feeds[i])
    )
    if _juice_wet_sum > _JUICE_WET_CAP_SOFT_KG_DM + 1e-6:
        warnings.append(
            f"Saftfutter und nasse CoP summiert {_juice_wet_sum:.2f} kg TM/d – über "
            f"der konservativen Leitplanke {_JUICE_WET_CAP_SOFT_KG_DM:.1f} kg TM/d "
            f"(DLG 01|2025 Kap. 1.1/8.4; LP-hart bis {_JUICE_WET_CAP_HARD_KG_DM:.1f} kg TM/d). "
            f"SARA-/Klauenrisiko beobachten."
        )
    # ME: Toleranz bis +10%; +10–12% gelb (LP-Ceiling bei +12%); > +12% blockiert vom LP
    me_overshoot_pct = (me_sup / req.me_mj - 1.0) * 100 if req.me_mj > 0 else 0.0
    if me_overshoot_pct > 12:
        warnings.append(
            f"ME-Versorgung {me_sup:.0f} MJ/d – {me_overshoot_pct:.0f}% über Bedarf {req.me_mj:.0f} MJ/d. "
            f"Energiebilanz / Verfettungsrisiko prüfen (DLG: Toleranz ≤ 10%)."
        )
    elif me_overshoot_pct > 10:
        warnings.append(
            f"ME-Versorgung {me_sup:.0f} MJ/d – {me_overshoot_pct:.1f}% über Bedarf {req.me_mj:.0f} MJ/d "
            f"(DLG-Toleranzbereich bis +10%; knapp überschritten – Energiebilanz beobachten)."
        )
    if sidp_sup < req.sidp_g * 0.95:
        warnings.append(
            f"sidP-Versorgung {sidp_sup:.0f} g/d unter Bedarf {req.sidp_g:.0f} g/d – "
            f"Proteinversorgung kritisch."
        )

    # peNDF-Versorgung (GfE-Workshop 2023). Gem. DLG 01|2023 ist peNDF hier eine
    # Kontroll-/Validierungsgroesse; die eigentliche Planung laeuft ueber
    # aNDFomGF (s. andfom_gf_ziel). Warnung nur, wenn peNDF-Modell kalibriert.
    if not pendf_model_calibrated:
        warnings.append(
            f"peNDF ausserhalb Modellbereich (Staerke {st_density:.0f} g/kg TM, "
            f"TM-Aufnahme {total_dmi:.1f} kg/d). Fallback-Regeln verwendet - "
            f"peNDF-Ampel nur eingeschraenkt belastbar."
        )
    elif pendf_density < pendf_min_val:
        warnings.append(
            f"peNDF {pendf_density:.0f} g/kg TM unter Modell-Minimum {pendf_min_val:.0f} g/kg TM "
            f"(Stärke {st_density:.0f} g/kg TM, TM-Aufnahme {total_dmi:.1f} kg/d). "
            f"Kontrollgroesse im Warnbereich - aNDFomGF und pabKH pruefen, ggf. "
            f"langfaseriges Raufutter (Heu, Stroh) ergaenzen."
        )

    # Pansen-pH-Simulation (Zebeli 2008, DLG 01|2025 Kap. 8.3).
    # Nur warnen, wenn die Eingaenge auch im Validitaetsbereich der Formel
    # liegen (peNDF 60-250 g/kg TM, abbaubare Staerke 50-350 g/kg TM,
    # TM 10-25 kg/d). Sehr hohe peNDF-Dichten (>250 g/kg TM) sind strukturell
    # ueberversorgt und azidotisch NICHT gefaehrdet - hier wuerde die Formel
    # sonst falsch-positive SARA-Alarme ausloesen.
    if ph_formula_applicable:
        if ph_predicted < 5.9:
            warnings.append(
                f"Simulierter Pansen-pH {ph_predicted:.2f} < 5,9 – SARA (subakute Pansenazidose) wahrscheinlich! "
                f"peNDF erhöhen, Stärke reduzieren, gepufferte Kraftfuttergabe prüfen."
            )
        elif ph_predicted < 6.2:
            warnings.append(
                f"Simulierter Pansen-pH {ph_predicted:.2f} – Grenzbereich (Ziel ≥ 6,2). "
                f"peNDF-Versorgung und Fütterungsmanagement (TMR-Qualität, Kraftfuttergaben) prüfen."
            )

    # sidLys:sidMet-Verhältnis (GfE-Workshop 2023 – Ziel 3:1)
    if sidlys_sidmet_ratio is not None:
        if sidlys_sidmet_ratio > 3.5:
            warnings.append(
                f"sidLys:sidMet-Verhältnis {sidlys_sidmet_ratio:.1f}:1 > 3,5 – "
                f"Methionin-Unterversorgung möglich. Methionin-geschütztes Supplement prüfen."
            )
        elif sidlys_sidmet_ratio < 2.5:
            warnings.append(
                f"sidLys:sidMet-Verhältnis {sidlys_sidmet_ratio:.1f}:1 < 2,5 – "
                f"Lysin-Unterversorgung möglich. Lysin-Versorgung aus UDP-Quellen prüfen."
            )

    # K/Mg-Antagonismus (GfE-Workshop 2023)
    if k_sup > req.k_max_g:
        warnings.append(
            f"Kalium {k_sup:.0f} g/d ({k_sup/total_dmi:.0f} g/kg TM) > Richtwert {req.k_max_g:.0f} g/d "
            f"– K/Mg-Antagonismus: Mg-Absorption kann beeinträchtigt sein (Grastetanie-Risiko). "
            f"Kaliumreiche Grundfutter begrenzen, Mg-Versorgung erhöhen."
        )

    # --- Weide-Risikoauswertung (nur bei PMR+Weide-Szenarien aktiv) ---
    pasture_warnings: List[str] = []
    if pasture_kg > 0:
        if pasture_cp_density is not None and pasture_cp_density > 230.0:
            pasture_warnings.append(
                f"Jungweide: Rohprotein {pasture_cp_density:.0f} g/kg TM > 230 – "
                f"erhoehter N-Abfluss/Harnstoff wahrscheinlich (DLG 417)."
            )
        if pasture_k_mg_ratio is not None and pasture_k_mg_ratio > 6.0:
            pasture_warnings.append(
                f"Weide K:Mg {pasture_k_mg_ratio:.1f} > 6 – Grastetanie-Risiko durch K/Mg-Antagonismus. "
                f"Mg-betontes Weidemineral gezielt einsetzen (GfE-Workshop 2023 / DLG 417)."
            )
        if pasture_mg_supplement_kg < 0.04 and pasture_k_mg_ratio is not None and pasture_k_mg_ratio > 4.0:
            pasture_warnings.append(
                "Weide liefert relativ zu Kalium wenig Magnesium; Weidemineral Mg/Na aktuell kaum eingesetzt."
            )

    pasture_risk_payload: Optional[Dict[str, Any]] = None
    # Panel nur bei explizitem PMR+Weide-Modus oder nennenswerter Weideaufnahme (> 1 kg TM/d).
    pasture_risk_active = feeding_type == "PMR+Weide" or pasture_kg > 1.0
    if pasture_risk_active:
        pasture_risk_payload = {
            "active": True,
            "feeding_type": feeding_type,
            "pasture_dmi_kg": round(pasture_kg, 2),
            "grass_silage_dmi_kg": round(grass_silage_kg, 2),
            "pasture_cp_g_kgdm": round(pasture_cp_density, 1) if pasture_cp_density is not None else None,
            "pasture_k_mg_ratio": round(pasture_k_mg_ratio, 2) if pasture_k_mg_ratio is not None else None,
            "pasture_k_mg_ratio_ziel": "<= 4 (Grastetanie-Risiko ab > 6)",
            "mg_supplement_dmi_kg": round(pasture_mg_supplement_kg, 3),
            "mg_supplement_ziel": ">= 0.05 kg TM/d bei PMR+Weide",
            # Milch aus Teilmengen: ME-Erhaltungsanteil = Teilmengen-ME / Gesamt-ME;
            # gleicher Faktor fuer sidP-Erhaltung (konsequent zur bilanziellen Aufschluesselung).
            "milk_from_pasture": pasture_milk,
            "milk_from_grass_silage": grass_silage_milk,
            "milk_from_pasture_plus_grass_silage": pasture_plus_grass_milk,
            "warnings": pasture_warnings,
        }
        warnings.extend(pasture_warnings)

    # FAN-MODE-002: Constraint-Status mit echter Penalty-Berechnung je weichem Constraint.
    # Neben den constraint_report-Eintraegen werden weitere weiche Metriken (RMD, Kalium,
    # K:Mg-Ratio, ME-Dichte, sidP-Oberkorridor, CP-Dichte) aus der Versorgung abgeleitet.
    k_mg_ratio = (k_sup / mg_sup) if mg_sup > 0 else 0.0
    me_density_actual = (me_sup / total_dmi) if total_dmi > 0 else 0.0
    constraint_status_extras: List[Dict[str, Any]] = [
        {
            "name": "RMD (g N/kg TM)",
            "actual": rmd_ration if rmd_ration is not None else 0.0,
            "target": 0.0,  # DLG-Ziel -1.5..0, Halbbreite 1.5 (bilateral)
            "unit": "g N/kg TM",
        },
        {
            "name": "Kalium (g/d)",
            "actual": k_sup,
            "target": req.k_max_g,
            "unit": "g/d",
        },
        {
            "name": "ME-Dichte (MJ/kg TM)",
            "actual": me_density_actual,
            "target": 12.5,
            "unit": "MJ/kg TM",
        },
        {
            "name": "sidP-Zielkorridor (g/d)",
            "actual": sidp_sup,
            "target": req.sidp_g,
            "unit": "g/d",
        },
        {
            "name": "CP-Dichte (g/kg TM)",
            "actual": (cp_sup / total_dmi) if total_dmi > 0 else 0.0,
            "target": 165.0 if not pasture_pmr else 185.0,
            "unit": "g/kg TM",
        },
        {
            "name": "K:Mg-Ratio",
            "actual": k_mg_ratio,
            "target": 4.0,  # Zielobergrenze; ab > 6 Grastetanie-Risiko
            "unit": "",
        },
        {
            "name": "Saftfutter/nasse CoP (kg TM/d)",
            "actual": round(
                sum(
                    amounts[i]
                    for i in range(len(feeds))
                    if _feed_counts_toward_saftfutter_wet_cap(feeds[i])
                ),
                3,
            ),
            "target": _JUICE_WET_CAP_SOFT_KG_DM,
            "unit": "kg TM/d",
            "source": "dlg_01_2025_juice_wet_cap",
        },
    ]

    # Slice 1e-Nachschaerfung §4: Konzentrat-Tagesmax als weicher Constraint.
    # Einzelgabe-Limit bleibt physiologisch hart ueber 1,5x-Sicherheitsnetz
    # im LP (siehe _run_lp), das empfohlene Tagesmax selbst wird weich
    # bewertet - Ueberschreitung fuehrt zu Penalty, nicht zu Infeasible.
    _fs_cfg_resp = lp_out.get("_feeding_system_config") or {}
    _block_labels_resp = lp_out.get("_block_labels") or []
    _conc_max_per_day_resp = float(_fs_cfg_resp.get("concentrate_max_per_day_kg") or 0.0)
    if _conc_max_per_day_resp > 0 and _block_labels_resp and len(_block_labels_resp) == len(feeds):
        _conc_staged_total = sum(
            amounts[i]
            for i in range(len(feeds))
            if _block_labels_resp[i] == "concentrate_staged_block"
        )
        if _conc_staged_total > 0:
            constraint_status_extras.append({
                "name": "Konzentrat-Tagesmax (kg TM/d)",
                "actual": round(_conc_staged_total, 2),
                "target": round(_conc_max_per_day_resp, 2),
                "unit": "kg TM/d",
                "source": "feeding_system_config",
            })

    constraint_status = constraint_status_from_lp or _build_constraint_status_v2(
        constraint_report,
        relaxation_policy,
        extras=constraint_status_extras,
    )

    # DLG-01|2025-Policy-Profil: Post-Solve-Band-Auswertung (weiche Bindung).
    # Die Bandchecks werden als zusaetzliche Eintraege in constraint_status
    # mit source="policy_profile" gefuehrt und fliessen in penalty_summary ein.
    policy_profile_targets_dict = _policy_profile_targets(policy_profile)
    policy_profile_bands = _policy_profile_band_evaluate(
        policy_profile_targets_dict,
        nutrient_supply,
        relaxation_policy,
    )
    if policy_profile_bands:
        constraint_status = list(constraint_status) + policy_profile_bands
    policy_profile_evaluation = _build_policy_profile_evaluation(
        policy_profile,
        policy_profile_targets_dict,
        policy_profile_bands,
    )

    penalty_summary = _summarize_penalty(constraint_status)

    # Slice 1f: Block-Aggregate (TMR-Mischmasse / Weide / gestaffeltes
    # Konzentrat). Enthaelt je Block Summen und Anteile (Gesamt-TM, Kosten,
    # Energie, Protein, Item-Liste). Abwaertskompatibel: bei reinem TMR
    # sind pasture_block / concentrate_staged_block leer (0-Kennzahlen).
    def _block_summary(block_name: str) -> Dict[str, Any]:
        block_indices = [i for i, lab in enumerate(_block_labels_resp) if lab == block_name]
        block_dmi = sum(amounts[i] for i in block_indices)
        block_cost = sum(amounts[i] * feeds[i]["price"] for i in block_indices)
        block_me = sum(amounts[i] * feeds[i]["me"] for i in block_indices)
        block_sidp = sum(amounts[i] * feeds[i]["sidp"] for i in block_indices)
        block_cp = sum(amounts[i] * feeds[i]["cp"] for i in block_indices)
        block_items = [
            {
                "feed_id": feeds[i]["id"],
                "name": feeds[i]["name"],
                "kgdm": round(amounts[i], 3),
                "kgfm": round(
                    amounts[i] / feeds[i]["dm_frac"] if feeds[i]["dm_frac"] > 0 else amounts[i], 3
                ),
            }
            for i in block_indices
            if amounts[i] >= 0.001
        ]
        return {
            "dmi_kg": round(block_dmi, 3),
            "dmi_share_pct": round(block_dmi / total_dmi * 100, 1) if total_dmi > 0 else 0.0,
            "cost_eur_day": round(block_cost, 4),
            "me_mj": round(block_me, 2),
            "sidp_g": round(block_sidp, 1),
            "cp_g": round(block_cp, 1),
            "items": block_items,
        }

    ration_blocks = {
        "feeding_system": {
            "system": _fs_cfg_resp.get("system"),
            "concentrate_distribution": _fs_cfg_resp.get("concentrate_distribution"),
            "concentrate_max_per_serving_kg": _fs_cfg_resp.get("concentrate_max_per_serving_kg"),
            "concentrate_servings_per_day": _fs_cfg_resp.get("concentrate_servings_per_day"),
            "concentrate_max_per_day_kg": _fs_cfg_resp.get("concentrate_max_per_day_kg"),
            "treat_as_primiparous": _fs_cfg_resp.get("treat_as_primiparous", False),
            "default_concentrate_recipe": _fs_cfg_resp.get("default_concentrate_recipe"),
            "auto_promoted_from_tmr": bool(_fs_cfg_resp.get("auto_promoted_from_tmr")),
        },
        "tmr_block": _block_summary("tmr_block"),
        "pasture_block": _block_summary("pasture_block"),
        "concentrate_staged_block": _block_summary("concentrate_staged_block"),
    }

    # Slice 2: Konzentrat-Futterabruf-Staffel (nur fuer gestaffelte Systeme).
    # Basis = Milch aus Grundfutter (forage_only_milk.limiting_milk_kg); dort
    # anteilige Erhaltung wie beim Weide-/Silage-Panel (GF-ME / Gesamt-ME).
    concentrate_call_up = _build_concentrate_call_up_table(
        profile=profile,
        feeding_system_config=_fs_cfg_resp,
        base_milk_from_forage_kg=float(forage_only_milk.get("limiting_milk_kg") or 0.0),
    )

    # Slice 3: Misch- und Fuetterungsprotokoll (nur bei TMR-Block).
    mixing_protocol = _build_mixing_protocol(
        ration_items=ration_items,
        block_labels=_block_labels_resp,
        feeds=feeds,
        amounts=amounts,
        feeding_system_config=_fs_cfg_resp,
    )

    _ex_pf = max(
        0.0,
        float(forage_only_milk.get("milk_from_protein_kg") or 0.0)
        - float(forage_only_milk.get("milk_from_energy_kg") or 0.0),
    )
    _ex_sup = max(
        0.0,
        float(supplemented_milk.get("milk_from_protein_kg") or 0.0)
        - float(supplemented_milk.get("milk_from_energy_kg") or 0.0),
    )
    ration_adjustment_suggestions = _build_ration_adjustment_suggestions(
        status="optimal",
        warnings=warnings,
        relaxation_policy=str(relaxation_policy or _RELAXATION_DEFAULT),
        milk_p_excess_forage=_ex_pf,
        milk_p_excess_total=_ex_sup,
    )
    feed_suggestions_opt = _build_optimal_feed_suggestions(
        req,
        feeds,
        warnings=warnings,
        stage2_relaxation_summary=_stage2_rx,
    )

    _lim_mk = float(supplemented_milk.get("limiting_milk_kg") or 0.0)
    _ecm_day_kg = _lim_mk * _ecm_kg_per_kg_milk_factor(profile) if _lim_mk > 1e-9 else 0.0
    feed_cost_eur_per_kg_ecm = round(total_cost / max(_ecm_day_kg, 1e-9), 5)

    return {
        "status": "optimal",
        "objective_value": round(_f(result.fun), 4),
        "total_cost_eur_day": round(total_cost, 4),
        "total_cost_eur_100kg_milk": round(total_cost / (float(profile.get("milk_kg_day") or 1)) * 100, 2),
        "feed_cost_eur_per_kg_ecm": feed_cost_eur_per_kg_ecm,
        "ecm_supply_kg_day": round(_ecm_day_kg, 4),
        "ration_items": ration_items,
        # Slice 1f: Block-Aggregate je Fuetterungssystem (leer/0 bei reinem TMR).
        "ration_blocks": ration_blocks,
        # Slice 2: Konzentrat-Abruf-Staffel (nur bei gestaffelter Gabe; sonst None).
        "concentrate_call_up": concentrate_call_up,
        # Slice 3: Mischprotokoll TMR-Block (nur wenn TMR-Block existiert; sonst None).
        "mixing_protocol": mixing_protocol,
        "nutrient_supply": nutrient_supply,
        "constraint_report": constraint_report,
        "constraint_status": constraint_status,
        "penalty_summary": penalty_summary,
        "dlg_indicators": dlg_indicators,
        "forage_performance": {
            "feeding_type": feeding_type,
            "target_milk_kg": round(float(profile.get("milk_kg_day") or 0.0), 1),
            "forage_only": {
                "forage_dmi_kg": round(forage_kg, 2),
                **forage_only_milk,
            },
            "supplemented": {
                "total_dmi_kg": round(total_dmi, 2),
                "concentrate_dmi_kg": round(concentrate_kg, 2),
                "forage_displacement_dmi_kg": round(forage_displacement_dmi, 2),
                "forage_displacement_factor": round(displacement_factor, 2),
                **supplemented_milk,
            },
        },
        "pasture_risk": pasture_risk_payload,
        "sara_safety_reopt": lp_out.get("_sara_reopt") or {"triggered": False},
        "warnings": warnings,
        "feed_suggestions": feed_suggestions_opt,
        "ration_adjustment_suggestions": ration_adjustment_suggestions,
        "fan_calibration": fan_calibration,
        "active_policy_profile": policy_profile,
        "policy_profile_targets": policy_profile_targets_dict,
        "policy_profile_evaluation": policy_profile_evaluation,
        # DLG 01|2025 native LP-Slacks (Stage-2-Cost-Solve mit Policy-Penalty):
        # vorhanden, wenn der erweiterte LP-Solve erfolgreich war. Sonst None -
        # dann liegt nur die Post-Solve-Auswertung vor.
        "policy_profile_lp_slacks": lp_out.get("_policy_lp_slacks"),
        "policy_profile_lp_total_penalty": lp_out.get("_policy_lp_slack_total_penalty"),
        "policy_profile_lp_mode": lp_out.get("_policy_lp_slack_objective_mode"),
        "concentrate_max_lp_slack_kg": lp_out.get("_concentrate_max_lp_slack_kg"),
        "concentrate_max_lp_slack_penalty": lp_out.get("_concentrate_max_lp_slack_penalty"),
        "policy_overrides": policy_overrides,
        "relaxation_policy": relaxation_policy,
        "objective_strategy": objective_strategy,
        "solver_stage2_lp_mode": lp_out.get("_stage2_lp_mode"),
        "relaxation_applied": bool(_stage2_rx),
        "relaxation_summary": list(_stage2_rx),
        "fallback_used": bool(lp_out.get("_stage2_fallback_used")),
        "stage2_ecm_failure_class": lp_out.get("_stage2_ecm_failure_class"),
        "season_profile": season_profile,
        "metadata": {
            "solver": "scipy-highs-internal",
            # Historischer Schluessel (Spec §10.2): stabiler Kurzstring fuer Legacy-Clients.
            "optimization_strategy": "stage1_balance_then_stage2_cost",
            # Zwei-Stufen-Pipeline mit optionalen Slack-/Penalty-Erweiterungen (Detail).
            "optimization_strategy_pipeline": (
                "stage1_balance_then_stage2_cost_plus_policy_slack"
                if lp_out.get("_policy_lp_slack_objective_mode")
                else (
                    "stage1_balance_then_stage2_cost_plus_concentrate_slack"
                    if lp_out.get("_concentrate_max_lp_slack_kg")
                    else None
                )
            ),
            "wizard_soft_goals_lp": _wizard_soft_lp_meta,
            "objective_strategy": objective_strategy,
            "solver_stage2_lp_mode": lp_out.get("_stage2_lp_mode"),
            "relaxation_applied": bool(_stage2_rx),
            "relaxation_summary": list(_stage2_rx),
            "fallback_used": bool(lp_out.get("_stage2_fallback_used")),
            "stage2_ecm_failure_class": lp_out.get("_stage2_ecm_failure_class"),
            "pasture_pmr_mode": pasture_pmr,
            "energy_system": "ME-FAN1-GfE2023",
            "protein_system": "sidP-GfE2023",
            "feed_data": "DLG-Futterwerttabellen-2025",
            "dlg_rules": "DLG-Information-01|2023",
            "gfe_workshop": "GfE-Workshop-2023 (pH-Vorhersage, peNDF, Mg, K/Mg, sidLys:sidMet)",
            "me_requirement_mj": round(req.me_mj, 1),
            "nel_ref_mj": round(req.nel_mj, 1),
            "sidp_requirement_g": round(req.sidp_g, 1),
            "nxp_ref_g": round(req.nxp_g, 1),
            "dmi_target_kg": round((req.dmi_min_kg + req.dmi_max_kg) / 2, 1),
            "feeding_type": feeding_type,
            "fan_mode": fan_mode,
            "fan_reference": fan_reference,
            "active_policy_profile": policy_profile,
            "relaxation_policy": relaxation_policy,
            "forage_displacement_note": (
                "DLG 01|2023 fordert die Beruecksichtigung der Grundfutterverdrängung "
                "durch Konzentratfutter; der ausgewiesene Faktor ist eine dokumentierte "
                "TMR/PMR-Heuristik fuer die operative Schaetzung."
            ),
        },
    }


def _gfa_to_feed(gfa: Dict[str, Any]) -> Dict[str, Any]:
    """
    Konvertiert eine GrundfutterAnalyse (aus der DB/API) in ein LP-kompatibles Feed-Dict.

    Einheiten GrundfutterAnalyse: organische Parameter in % TS (×10 = g/kg TM),
    Energie in MJ/kg TM, Mineralstoffe in % TS (×10 = g/kg TM).
    """
    def pct(v: Optional[float]) -> float:
        """% TS → g/kg TM"""
        return float(v or 0) * 10.0

    dm_os = float(gfa.get("trockensubstanz_os") or 86.0)  # % OS
    dm_frac = dm_os / 100.0

    # Energie
    me = float(gfa.get("me_gfe2023_ts") or gfa.get("me_rind_gfe2008_ts") or 9.5)

    # Protein
    cp = pct(gfa.get("rohprotein_ts"))
    sidp_raw = gfa.get("sidp_ts")
    nxp_raw = gfa.get("nxp_ts")
    if sidp_raw is not None:
        sidp = float(sidp_raw)
    elif nxp_raw is not None:
        sidp = float(nxp_raw) * 0.95
    else:
        sidp = cp * 0.60  # Schätzung: 60% sidP wenn keine Daten

    # Faser
    ndf = pct(gfa.get("andfom_ts"))
    adf = pct(gfa.get("adfom_ts"))

    # Weitere
    xl = pct(gfa.get("rohfett_ts"))
    zu = pct(gfa.get("gesamtzucker_ts"))
    nfc = pct(gfa.get("nfc_ts"))

    # Mineralstoffe (% TS → g/kg TM)
    ca = pct(gfa.get("calcium_ts"))
    p  = pct(gfa.get("phosphor_ts"))
    na = pct(gfa.get("natrium_ts"))
    mg = pct(gfa.get("magnesium_ts"))
    k  = pct(gfa.get("kalium_ts"))

    # RMD / RNB
    rmd = float(gfa.get("rmd_ts") or gfa.get("rnb_ts") or 0)

    # NEL / OMD
    _nel = float(gfa.get("nel_ts") or 0)  # noqa: F841
    omd = float(gfa.get("omd_ts") or 65.0)

    name = gfa.get("bezeichnung") or gfa.get("name") or "Betriebseigenes Grundfutter"
    analyse_id = gfa.get("id") or gfa.get("analyse_id") or "custom"

    return {
        "id": f"gfa_{analyse_id}",
        "lid": None,
        "name": name,
        "konservierung": gfa.get("konservierung", ""),
        "group": "Grundfutter/Betrieb",
        "futterart": "Grundfutter, Grobfutter",
        "forage": True,
        "dm_frac": dm_frac,
        "price": float(gfa.get("price_eur_kgdm") or 0.065),
        "min_kg": float(gfa.get("min_kg") or 0.0),
        "max_kg": float(gfa.get("max_kg") or 12.0),
        "me": me,
        "sidp": sidp,
        "cp": cp,
        "ndf": ndf,
        "adf": adf,
        "st": 0.0,
        "bst": 0.0,
        "zu": zu,
        "nfc": nfc,
        "xl": xl,
        "ca": ca,
        "p": p,
        "na": na,
        "mg": mg,
        "k": k,
        "dcab": None,
        "edg": None,
        "rmd": rmd,
        "omdfan1": omd,
        "ndfd": None,
        "ge": None,
        "sidlys": None,
        "sidmet": None,
        "_source": "gfa",
        "_probe_nr": gfa.get("probe_nr"),
        "_labor": gfa.get("labor"),
    }


# Refactor 2026-04-23 (Schritt 1e): Compound-Feed-Parser ausgelagert nach
# app.agrar.rations.compound_feed.parser. Re-Exports unter den alten Namen
# erhalten die oeffentliche Schnittstelle (Tests + Endpoint).
from app.agrar.rations.compound_feed.parser import (  # noqa: E402,F401
    COMPOUND_FEED_MATCHERS as _COMPOUND_FEED_MATCHERS,
    ascii_slug as _ascii_slug,
    normalize_feed_label as _normalize_feed_label,
    parse_localized_float as _parse_localized_float,
    extract_value as _extract_value,
    extract_labelled_value as _extract_labelled_value,
    extract_document_text as _extract_document_text,
    match_compound_component as _match_compound_component,
    aggregate_compound_components as _aggregate_compound_components,
    build_compound_estimate as _build_compound_estimate,
    parse_compound_feed_text as _parse_compound_feed_text_impl,
)


def _parse_compound_feed_text(text: str, filename: str, source_type: str):
    """Backwards-kompatibler Wrapper: nutzt ``_get_feeds`` als Feeds-Provider.

    Siehe ``app.agrar.rations.compound_feed.parser.parse_compound_feed_text``
    fuer die ausgelagerte Implementation.
    """
    return _parse_compound_feed_text_impl(
        text, filename, source_type, feeds_provider=_get_feeds
    )


# ---------------------------------------------------------------------------
# FAN-MODE-003: Katalog mit Herkunftsflag (Spec §8.2) und FAN-Iteration (§8.4)
# ---------------------------------------------------------------------------

import json as _json_fan

_FAN_CATALOG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "config", "fan_slope_catalog.json")
_fan_catalog_cache: Optional[Dict[str, Any]] = None


def _load_fan_catalog() -> Dict[str, Any]:
    """Laedt den FAN-Slope-Katalog (Spec §8.2.2) inkl. Herkunftsflag exact/mapped/fallback."""
    global _fan_catalog_cache
    if _fan_catalog_cache is not None:
        return _fan_catalog_cache
    try:
        path = os.path.abspath(_FAN_CATALOG_PATH)
        with open(path, "r", encoding="utf-8") as f:
            data = _json_fan.load(f)
        _fan_catalog_cache = data
        return data
    except Exception as exc:  # pragma: no cover
        logger.warning("FAN-Katalog konnte nicht geladen werden (%s) – Fallback aktiv.", exc)
        _fan_catalog_cache = {
            "_meta": {"version": "fallback"},
            "base_fan": 1.0,
            "groups": {
                "default": {"label": "Fallback", "slope_me": -0.05, "k_fan1": 0.025, "source": "fallback"},
            },
        }
        return _fan_catalog_cache


def _classify_feed_to_fan_group(feed: Dict[str, Any], season_profile: Optional[str] = None) -> str:
    """Mappt ein Feed-Dict auf die passende FAN-Katalog-Gruppe (Spec §8.2.1).

    Praeferenz:
      1. _fan_group Override (explizit)
      2. Spezialfutter (z. B. Weidemineral) -> mineral_supplement
      3. futterart + Name-Keywords + season_profile
      4. Fallback -> default
    """
    override = feed.get("_fan_group")
    if override:
        return str(override)
    if feed.get("_special") == "pasture_mg":
        return "mineral_supplement"
    name_l = (feed.get("name") or "").lower()
    fart_l = (feed.get("futterart") or "").lower()
    group_l = (feed.get("group") or "").lower()
    # Gras-basierte Klassifikation zentral ueber TM-Gehalt (siehe _grass_feed_kind).
    # Die DLG-Daten fuehren "Gras, frisch o. konserviert" mit drei TM-Varianten
    # (175 / 350 / 860 g/kg) - nur der TM-Gehalt loest sauber zwischen Weide,
    # Silage und Heu auf. Der Name dient nur als Fallback.
    _gk = _grass_feed_kind(feed)
    is_grass_silage = _gk == "grass_silage"
    is_pasture = _gk == "pasture"
    is_grass_hay = _gk == "grass_hay"
    is_maize_silage = ("maissilage" in name_l or "mais" in name_l and "silage" in name_l)
    is_hay = "heu" in name_l or is_grass_hay
    is_straw = "stroh" in name_l
    is_juice = "saftfutter" in fart_l or "saftfutter" in group_l or "biertreber" in name_l or "schlempe" in name_l
    is_cereal = any(k in name_l for k in ("mais", "maiskorn", "weizen", "gerste", "hafer", "roggen", "triticale", "maismehl", "gerstenmehl"))
    is_protein = any(k in name_l for k in ("soja", "raps", "sonnenblumen", "ackerbohnen", "leinsamen", "proteinschrot", "extraktionsschrot"))
    is_mineral = "mineral" in name_l or "mineralf" in group_l or "kalk" in name_l or "magnesiumoxid" in name_l
    is_compound = any(k in name_l for k in ("milchleistungsfutter", "kraftfutter", "laktations", "mischfutter"))

    if is_pasture:
        if season_profile == "spring_young":
            return "roughage_pasture_spring_young"
        if season_profile == "spring_mid":
            return "roughage_pasture_spring_mid"
        if season_profile in ("summer_young", "summer_mid", "summer_late", "autumn"):
            return "roughage_pasture_other"
        return "roughage_pasture_other"
    if is_grass_silage:
        return "roughage_grass_silage"
    if is_maize_silage:
        return "roughage_maize_silage"
    if is_hay:
        return "roughage_hay"
    if is_straw:
        return "roughage_straw"
    if is_juice:
        return "roughage_juice_feed"
    if is_compound:
        return "concentrate_mix"
    if is_protein:
        return "concentrate_protein"
    if is_cereal:
        return "concentrate_cereal"
    if is_mineral:
        return "mineral_supplement"
    return "default"


def _annotate_feeds_with_fan_catalog(
    feeds: List[Dict[str, Any]],
    season_profile: Optional[str] = None,
) -> Dict[str, Any]:
    """Markiert jede Futterposition mit FAN-Gruppe, slope_me, k_fan1 und Herkunftsflag.

    Gibt ein Info-Dict zurueck mit catalog_version + Zaehler (exact/mapped/fallback).
    """
    catalog = _load_fan_catalog()
    groups = catalog.get("groups", {})
    info = {
        "version": catalog.get("_meta", {}).get("version"),
        "feeds_exact": 0,
        "feeds_mapped": 0,
        "feeds_fallback": 0,
    }
    for feed in feeds:
        grp_id = _classify_feed_to_fan_group(feed, season_profile)
        grp_def = groups.get(grp_id) or groups.get("default") or {
            "label": "default", "slope_me": -0.05, "k_fan1": 0.025, "source": "fallback",
        }
        source = grp_def.get("source", "fallback")
        feed["_fan_group"] = grp_id
        feed["_fan_group_label"] = grp_def.get("label", grp_id)
        feed["_fan_slope_me"] = float(grp_def.get("slope_me", 0.0))
        feed["_fan_k_fan1"] = float(grp_def.get("k_fan1", 0.0))
        feed["_fan_slope_source"] = source
        if source == "exact":
            info["feeds_exact"] += 1
        elif source == "mapped":
            info["feeds_mapped"] += 1
        else:
            info["feeds_fallback"] += 1
    if info["feeds_fallback"] > 0:
        info["fallback_warning"] = (
            f"{info['feeds_fallback']} Futterposition(en) verwenden einen konservativen "
            f"Fallback-Slope; Ergebnis ist plausibel, aber nicht exakt DLG-tabellarisch belegt."
        )
    else:
        info["fallback_warning"] = None
    return info


def _fan1_reference_kg(profile: Dict[str, Any]) -> float:
    """FAN1 [kg TM/d] Referenzwert: 50 g TM je kg^0.75 LM (DLG 503).

    Konservative Wahl mit 50 (statt 55) entspricht der DLG-503-Definition fuer die
    FAN1-Tabellenwerte. Ergibt bei 650 kg LM etwa 6.4 kg TM/d.
    """
    bw = float(profile.get("body_weight_kg") or 650.0)
    return max(0.001, 0.050 * (bw ** 0.75))


def _apply_fan_effect(feeds: List[Dict[str, Any]], fani: float) -> List[Dict[str, Any]]:
    """Passt ME und sidP-Koeffizienten jedes Feeds an das gewaehlte FAN-Niveau an.

    Spec §8.2: ME(FANi) = ME_FAN1 + slope_me * (FANi - 1)
    Der Proteinwert (sidP) wird entsprechend der Passage-k-Steigerung um
    (1 + k_fan1 * (FANi - 1)) multipliziert, was eine konservative Annaeherung an das
    in DLG 504 beschriebene lineare Passageraten-Modell ist.
    """
    out: List[Dict[str, Any]] = []
    delta = fani - 1.0
    for feed in feeds:
        base = feed.get("_me_fan1")
        if base is None:
            base = float(feed.get("me") or 0.0)
            feed["_me_fan1"] = base
        sidp_base = feed.get("_sidp_fan1")
        if sidp_base is None:
            sidp_base = float(feed.get("sidp") or 0.0)
            feed["_sidp_fan1"] = sidp_base
        slope_me = float(feed.get("_fan_slope_me") or 0.0)
        k_fan1 = float(feed.get("_fan_k_fan1") or 0.0)
        new_me = max(0.0, base + slope_me * delta)
        sidp_factor = max(0.0, 1.0 + k_fan1 * delta)
        new_sidp = sidp_base * sidp_factor
        adjusted = dict(feed)
        adjusted["me"] = new_me
        adjusted["sidp"] = new_sidp
        out.append(adjusted)
    return out


def _fani_from_result(amounts: List[float], profile: Dict[str, Any]) -> float:
    """Berechnet FANi aus einer LP-Loesung: FANi = DMI [kg TM/d] / FAN1 [kg TM/d]."""
    dmi = float(sum(amounts))
    fan1 = _fan1_reference_kg(profile)
    return dmi / fan1 if fan1 > 0 else 1.0


# ---------------------------------------------------------------------------
# FAN-MODE-V1 Runtime-Options (Spec §4, §6, §8 freigegeben 2026-04-21)
# ---------------------------------------------------------------------------

def _resolve_policy_profile(
    feeding_type: str,
    season_profile: Optional[str],
    explicit: Optional[str] = None,
) -> str:
    """Policy-Profil-Auswahl nach Spec §6.2.

    Reihenfolge:
      1. explicit (nur im Expertenmodus)
      2. feeding_type + season_profile → versionertes Profil
      3. Fallback pmr_standard
    """
    if explicit and explicit in _POLICY_PROFILES:
        return explicit
    ft = _normalize_feeding_type(feeding_type)
    season = (season_profile or "").lower()
    if ft == "TMR":
        return "tmr_standard"
    if ft == "PMR+Weide":
        if season in ("spring_young", "spring_mid", "spring_late"):
            return "pmr_pasture_spring"
        if season in ("summer_young", "summer_mid", "summer_late"):
            return "pmr_pasture_summer"
        if season == "autumn":
            return "pmr_pasture_autumn"
    return "pmr_standard"


def _resolve_runtime_options(
    profile: Dict[str, Any],
    fan_options: Optional[_FanOptions] = None,
    relaxation_policy: Optional[str] = None,
    objective_strategy: Optional[str] = None,
    season_profile: Optional[str] = None,
    policy_profile: Optional[str] = None,
    policy_overrides: Optional[Dict[str, Any]] = None,
    feeding_system_config: Optional[Any] = None,
    feed_block_overrides: Optional[List[Any]] = None,
    disable_milk_tradeoff_between_stages: Optional[bool] = None,
    milk_tradeoff_max_pct_per_stage: Optional[float] = None,
    stage2_minimize_feed_eur_per_day: Optional[bool] = None,
) -> Dict[str, Any]:
    """Vereinheitlicht FAN-/Policy-/Relaxation-Optionen und setzt V1-Defaults.

    Validiert Enum-Werte und klemmt Zahlen ins erlaubte Fenster.
    """
    fan = fan_options or _FanOptions()

    fan_mode = (fan.mode or "").strip().lower() or _FAN_DEFAULT_MODE
    if fan_mode not in _FAN_MODES:
        fan_mode = _FAN_DEFAULT_MODE

    fan_ref = fan.reference
    if fan_ref is not None:
        try:
            fan_ref = float(fan_ref)
        except (TypeError, ValueError):
            fan_ref = None
        if fan_ref is not None:
            fan_ref = max(_FAN_REFERENCE_MIN, min(_FAN_REFERENCE_MAX, float(fan_ref)))
    if fan_mode == "reference" and fan_ref is None:
        fan_ref = 3.0  # Standard-Preset

    fan_tol = float(fan.tolerance) if fan.tolerance is not None else _FAN_DEFAULT_TOLERANCE
    fan_tol = max(0.01, min(0.5, fan_tol))
    fan_tol_warn = float(fan.tolerance_warn) if fan.tolerance_warn is not None else _FAN_DEFAULT_TOLERANCE_WARN
    fan_tol_warn = max(fan_tol, min(1.0, fan_tol_warn))
    fan_max_iter = int(fan.max_iterations) if fan.max_iterations is not None else _FAN_DEFAULT_MAX_ITERATIONS
    fan_max_iter = max(1, min(20, fan_max_iter))

    rp = (relaxation_policy or "").strip().lower() or _RELAXATION_DEFAULT
    if rp not in _RELAXATION_POLICIES:
        rp = _RELAXATION_DEFAULT

    obj = (objective_strategy or "").strip().lower() or "balance_then_cost"
    if obj not in _OBJECTIVE_STRATEGIES:
        obj = "balance_then_cost"

    season = (season_profile or profile.get("season_profile") or "").strip().lower()
    if season and season not in _SEASON_PROFILES:
        season = ""

    profile_name = _resolve_policy_profile(
        profile.get("feeding_type") or "",
        season or None,
        policy_profile,
    )

    overrides = dict(policy_overrides or {})

    _s2eur = stage2_minimize_feed_eur_per_day
    if _s2eur is None:
        _s2eur = profile.get("stage2_minimize_feed_eur_per_day")
    stage2_min_feed_eur_day_bool = bool(_s2eur)

    _dmilk_disable = disable_milk_tradeoff_between_stages
    if _dmilk_disable is None:
        _dmilk_disable = profile.get("disable_milk_tradeoff_between_stages")
    disable_milk_tradeoff_bool = bool(_dmilk_disable)

    _mtp_override = milk_tradeoff_max_pct_per_stage
    if _mtp_override is None:
        _mtp_override = profile.get("milk_tradeoff_max_pct_per_stage")
    _mtp_clean: Optional[float]
    if _mtp_override is None:
        _mtp_clean = None
    else:
        try:
            _mtp_clean = float(_mtp_override)
        except (TypeError, ValueError):
            _mtp_clean = None

    # Slice 1h: FeedingSystemConfig + Block-Overrides normalisieren.
    # Eingabe kann FeedingSystemConfig-Instanz, dict oder None sein.
    # Wir normieren ueber _resolve_feeding_system_config(), damit die
    # Defaults (Konzentratgrenzen je Verteilungssystem) gleich gesetzt
    # werden. Die Overrides werden als Liste normalisiert.
    fs_cfg = _resolve_feeding_system_config(feeding_system_config, profile)
    block_overrides_norm: List[Dict[str, Any]] = []
    for ovr in feed_block_overrides or []:
        if isinstance(ovr, FeedBlockAssignment):
            block_overrides_norm.append(ovr.model_dump())
        elif isinstance(ovr, dict):
            block_overrides_norm.append(dict(ovr))

    return {
        "fan": {
            "mode": fan_mode,
            "reference": fan_ref,
            "tolerance": fan_tol,
            "tolerance_warn": fan_tol_warn,
            "max_iterations": fan_max_iter,
        },
        "relaxation_policy": rp,
        "objective_strategy": obj,
        "season_profile": season or None,
        "policy_profile": profile_name,
        "policy_overrides": overrides,
        # Slice 1h: Fuetterungssystem + Block-Overrides
        "feeding_system_config": fs_cfg,
        "feed_block_overrides": block_overrides_norm,
        "disable_milk_tradeoff_between_stages": disable_milk_tradeoff_bool,
        "milk_tradeoff_max_pct_per_stage": _mtp_clean,
        "stage2_minimize_feed_eur_per_day": stage2_min_feed_eur_day_bool,
    }


def _optimize_internal(
    profile: Dict[str, Any],
    custom_feeds: Optional[List[Dict[str, Any]]] = None,
    feed_ids: Optional[List[str]] = None,
    price_overrides: Optional[Dict[str, float]] = None,
    max_tm_overrides: Optional[Dict[str, float]] = None,
    min_tm_overrides: Optional[Dict[str, float]] = None,
    runtime_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    req = _gfe_requirements(profile)
    feeds = list(_get_feeds())

    # FAN-MODE-V1: alle Laufzeit-Optionen zentral aufloesen
    if runtime_options is None:
        runtime_options = _resolve_runtime_options(profile)

    # Preisüberschreibungen anwenden
    if price_overrides:
        feeds = [
            {**f, "price": float(price_overrides[f["id"]])} if f["id"] in price_overrides else f
            for f in feeds
        ]

    # Saisonale Mengenlimits überschreiben max_kg je Feed
    if max_tm_overrides:
        feeds = [
            {**f, "max_kg": float(max_tm_overrides[f["id"]])} if f["id"] in max_tm_overrides else f
            for f in feeds
        ]

    # Mindestmengen (kg TM/Tag) z. B. aus Min-FM-Grenzen der UI
    if min_tm_overrides:
        feeds = [
            {**f, "min_kg": float(min_tm_overrides[f["id"]])} if f["id"] in min_tm_overrides else f
            for f in feeds
        ]

    # Filter auf ausgewählte Feed-IDs
    if feed_ids:
        id_set = set(feed_ids)
        feeds = [f for f in feeds if f["id"] in id_set]

    # Betriebseigene Grundfuttermittel / Custom Feeds NACH dem Feed-ID-Filter einmischen.
    # Wichtig: custom_feeds werden immer hinzugefügt, unabhängig von feed_ids,
    # da sie betriebsspezifisch sind und nicht in der DLG-Datenbank stehen.
    if custom_feeds:
        for cf in custom_feeds:
            feeds.append(cf)

    feeding_type_norm = _normalize_feeding_type(profile.get("feeding_type"))
    # Reines TMR: Weidemineral-Supplement nicht als optionaler LP-Kandidat fuehren
    # (liegt sonst via _with_special_supplements in jedem Feed-Pool und kann fuer
    # Mineral-Klemmen gewaehlt werden; Pflicht gilt nur PMR+Weide / PMR mit Weide).
    if feeding_type_norm == "TMR":
        feeds = [f for f in feeds if f.get("_special") != "pasture_mg"]

    # PMR+Weide: Weidemineral automatisch als Pflichtbaustein fuehren,
    # damit das K/Mg-Antagonismus-Risiko (DLG 417 / DLG 01|2023) sauber abgedeckt ist.
    if feeding_type_norm == "PMR+Weide" or (
        feeding_type_norm == "PMR" and _has_pasture_forage(feeds)
    ):
        has_mg_supplement = any(feed.get("_special") == "pasture_mg" for feed in feeds)
        if not has_mg_supplement:
            for supplement in _SPECIAL_SUPPLEMENTS:
                if supplement.get("_special") == "pasture_mg":
                    feeds.append(dict(supplement))
                    break

    # Saisonale Anpassungen (Spec §12 Sommer/Herbst):
    #  - Hitzestress-Saisonprofile reduzieren DMI (Gruber korrigiert um dmi_factor)
    #  - Na-Bedarf wird um Schwitzverlust-Faktor angehoben
    #  - NaHCO3-Pansenpuffer wird bei Sommerprofilen automatisch als
    #    Pflichtbaustein mit Mindestmenge eingefuehrt
    season = runtime_options.get("season_profile")
    seasonal = _seasonal_adjustments(season)
    dmi_factor = float(seasonal.get("dmi_factor", 1.0))
    na_boost = float(seasonal.get("na_boost_factor", 1.0))
    inject_buffer = bool(seasonal.get("inject_buffer", 0.0))
    buffer_min_kg = float(seasonal.get("buffer_min_kg", 0.0))

    if dmi_factor != 1.0:
        req = _CowReq(
            me_mj=req.me_mj,
            sidp_g=req.sidp_g,
            nel_mj=req.nel_mj,
            nxp_g=req.nxp_g,
            dmi_min_kg=req.dmi_min_kg * dmi_factor,
            dmi_max_kg=req.dmi_max_kg * dmi_factor,
            dmi_target_kg=req.dmi_target_kg * dmi_factor,
            ndf_min_g=req.ndf_min_g * dmi_factor,
            ca_min_g=req.ca_min_g,
            p_min_g=req.p_min_g,
            na_min_g=req.na_min_g * na_boost,
            mg_min_g=req.mg_min_g,
            k_max_g=req.k_max_g * dmi_factor,
        )
    elif na_boost != 1.0:
        req = _CowReq(**{**req.model_dump(), "na_min_g": req.na_min_g * na_boost})

    if inject_buffer:
        buffer_idx = next(
            (i for i, feed in enumerate(feeds) if feed.get("_special") == "summer_buffer"),
            None,
        )
        if buffer_idx is None:
            for supplement in _SPECIAL_SUPPLEMENTS:
                if supplement.get("_special") == "summer_buffer":
                    buf = dict(supplement)
                    if buffer_min_kg > 0.0:
                        buf["min_kg"] = max(float(buf.get("min_kg", 0.0)), buffer_min_kg)
                    feeds.append(buf)
                    break
        elif buffer_min_kg > 0.0:
            # Bereits vorhanden (z. B. aus _with_special_supplements): Mindestmenge
            # saisonal hochziehen, damit der LP-Solver ihn als Pflichtbaustein fuehrt.
            existing = dict(feeds[buffer_idx])
            existing["min_kg"] = max(float(existing.get("min_kg", 0.0)), buffer_min_kg)
            feeds[buffer_idx] = existing

    # FAN-MODE-003: FAN-Katalog auf Feeds anwenden (exact/mapped/fallback) + Iteration starten.
    catalog_info = _annotate_feeds_with_fan_catalog(feeds, season_profile=season)

    fan_opts = runtime_options.get("fan", {}) or {}
    fan_mode = fan_opts.get("mode", _FAN_DEFAULT_MODE)
    fan_tol = float(fan_opts.get("tolerance") or _FAN_DEFAULT_TOLERANCE)
    fan_tol_warn = float(fan_opts.get("tolerance_warn") or _FAN_DEFAULT_TOLERANCE_WARN)
    fan_max_iter = int(fan_opts.get("max_iterations") or _FAN_DEFAULT_MAX_ITERATIONS)
    fan_reference = fan_opts.get("reference")

    iterations: List[Dict[str, Any]] = []
    converged: Optional[bool] = None
    fani_final: Optional[float] = None

    if fan_mode == "evaluation_only":
        # Keine FAN-Korrektur – reine Bewertung mit FAN1-Tabellenwerten.
        lp_out = _run_lp(req, feeds, profile, runtime_options=runtime_options)
        if lp_out["scipy_result"].status == 0:
            fani_final = _fani_from_result(
                [_f(v) for v in lp_out["scipy_result"].x[: len(feeds)]], profile
            )
        converged = True
        iterations.append({
            "i": 0, "fan_in": 1.0, "fan_out": fani_final or 1.0,
            "delta": None, "mode": "evaluation_only",
        })
    elif fan_mode == "reference":
        # Einmalige Rechnung bei festgeklemmtem FANi = fan_reference.
        target_fani = float(fan_reference or 3.0)
        adjusted = _apply_fan_effect(feeds, target_fani)
        req_ref = _gfe_requirements(profile, fani=target_fani)
        lp_out = _run_lp(req_ref, adjusted, profile, runtime_options=runtime_options)
        fani_out = (
            _fani_from_result(
                [_f(v) for v in lp_out["scipy_result"].x[: len(feeds)]], profile
            )
            if lp_out["scipy_result"].status == 0 else target_fani
        )
        fani_final = target_fani  # bei reference ist das der ausgewiesene Wert
        converged = True
        iterations.append({
            "i": 0, "fan_in": target_fani, "fan_out": fani_out,
            "delta": round(fani_out - target_fani, 4),
            "mode": "reference",
        })
    else:
        # auto_iterative: Fixpunktiteration bis |fani_out - fani_in| <= tolerance.
        # Startwert aus geschaetzter DMI (Gruber 2004): ~0.025*BW + 0.15*Milch. Das verkuerzt
        # die Konvergenz gegenueber einem naiven Start bei FANi=1 drastisch, weil laktierende
        # Kuehe tatsaechlich im Bereich FANi 2.5..4.0 operieren.
        bw_init = float(profile.get("body_weight_kg") or 650.0)
        milk_init = float(profile.get("milk_kg_day") or 0.0)
        est_dmi = max(8.0, 0.025 * bw_init + 0.15 * milk_init if milk_init > 0 else 0.025 * bw_init)
        fan1_init = _fan1_reference_kg(profile)
        fani_in = max(1.0, est_dmi / fan1_init) if fan1_init > 0 else 2.5
        lp_out = None
        for i in range(fan_max_iter):
            adjusted = _apply_fan_effect(feeds, fani_in)
            req_iter = _gfe_requirements(profile, fani=fani_in)
            lp_out = _run_lp(req_iter, adjusted, profile, runtime_options=runtime_options)
            if lp_out["scipy_result"].status != 0:
                iterations.append({
                    "i": i, "fan_in": round(fani_in, 4), "fan_out": None,
                    "delta": None, "status": "infeasible",
                })
                converged = False
                break
            amounts_i = [_f(v) for v in lp_out["scipy_result"].x[: len(feeds)]]
            fani_out = _fani_from_result(amounts_i, profile)
            delta = fani_out - fani_in
            iterations.append({
                "i": i, "fan_in": round(fani_in, 4), "fan_out": round(fani_out, 4),
                "delta": round(delta, 4),
            })
            if abs(delta) <= fan_tol:
                converged = True
                fani_final = fani_out
                break
            # Leichte Unterrelaxation fuer monotones Einschwingen
            fani_in = 0.3 * fani_in + 0.7 * fani_out
        else:
            converged = False
            fani_final = iterations[-1].get("fan_out") if iterations else None
        if lp_out is None:  # pragma: no cover
            lp_out = _run_lp(req, feeds, profile, runtime_options=runtime_options)

    if fani_final is not None and not converged and abs(iterations[-1].get("delta") or 0.0) > fan_tol_warn:
        catalog_info = dict(catalog_info)
        fw = catalog_info.get("fallback_warning")
        hint = (
            f"FAN-Iteration nicht konvergiert (|Delta|={abs(iterations[-1].get('delta') or 0):.3f} "
            f"> Warnschwelle {fan_tol_warn})."
        )
        catalog_info["fallback_warning"] = f"{fw} {hint}" if fw else hint

    lp_out["_runtime_options"] = runtime_options
    lp_out["_fan_iterations"] = iterations
    lp_out["_fan_converged"] = converged
    lp_out["_fan_final"] = round(fani_final, 4) if fani_final is not None else None
    lp_out["_fan_catalog_info"] = catalog_info

    # SARA-Safety-Reopt-Loop (Pansenazidose-Schutz, 2026-04-21):
    # Wenn der erste Solve fachlich rot ist (pH < 5.9 ODER peNDF < Minimum ODER
    # pabKH am Limit), wird mit verschaerften Constraints erneut optimiert.
    # Die Prevention ist sonst nur implizit ueber LP-Constraints; dieser Loop
    # macht den Feedback-Zyklus explizit und sichtbar (DLG 01|23 Regelkreis).
    if lp_out["scipy_result"].status == 0 and not runtime_options.get("sara_overrides"):
        lp_out = _maybe_run_sara_safety_reopt(
            lp_out=lp_out,
            req=req,
            feeds=feeds,
            profile=profile,
            runtime_options=runtime_options,
            fan_mode=fan_mode,
            fan_reference=fan_reference,
            fan_tol=fan_tol,
            fan_max_iter=fan_max_iter,
            seasonal=seasonal,
            buffer_min_kg=buffer_min_kg,
        )

    # Feeding-System nach optimaler Ration neu aufloesen (Weide-Istmenge > 0
    # kann TMR -> PMR_pasture ausloesen; Block-Labels folgen dem System).
    if lp_out["scipy_result"].status == 0:
        amounts_post = [_f(v) for v in lp_out["scipy_result"].x[: len(feeds)]]
        raw_fs = (runtime_options or {}).get("feeding_system_config")
        feeds_eff = _feeds_for_fs_resolve_after_solve(feeds, amounts_post)
        fs_post = _resolve_feeding_system_config(raw_fs, profile, feeds=feeds_eff)
        lp_out["_feeding_system_config"] = fs_post
        _blk_ov = (runtime_options or {}).get("feed_block_overrides") or []
        _post_buckets = _split_feeds_by_block(feeds, fs_post, _blk_ov)
        _post_by_id: Dict[str, str] = {}
        for blk_nm, blk_fd in _post_buckets.items():
            for f in blk_fd:
                _post_by_id[str(f.get("id") or id(f))] = blk_nm
        lp_out["_block_labels"] = [
            _post_by_id.get(str(f.get("id") or id(f)), "tmr_block") for f in feeds
        ]

    return _build_response(lp_out, req, profile)


# ---------------------------------------------------------------------------
# SARA-Safety-Reopt-Loop
# ---------------------------------------------------------------------------
# Fachliche Logik (GfE-Workshop 2023 / DLG 01|2023 / DLG-Merkblatt 417):
#   Der erste Solve wird auf pH_predicted, peNDF-Deckung und pabKH geprueft.
#   Wenn fachlich rot, wird mit verschaerften Constraints erneut gerechnet:
#     - pabKH-Deckel um 20 g/kg TM senken
#     - peNDF-Floor (Stage-2) um 10 g/kg TM heben
#     - aNDFomGF-Mindestdichte um 10 g/kg TM heben
#     - NaHCO3-Pansenpuffer als Pflichtbaustein (min_kg >= 0.15 kg TM/d)
#   Wenn der zweite Solve infeasible ist oder keine Verbesserung bringt,
#   behalten wir das erste Ergebnis und flaggen es als "reopt_attempted".
def _detect_sara_risk(lp_out: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Bewerte den ersten Solver-Output auf Pansenazidose-Risiko.

    Liefert `{"triggered": bool, "reason": str | None, "metrics": dict}`.
    """
    result = lp_out.get("scipy_result")
    feeds_res = lp_out.get("feeds") or []
    if result is None or result.status != 0 or not feeds_res:
        return {"triggered": False, "reason": None, "metrics": {}}

    n_lp_feeds = len(feeds_res)
    amounts = [_f(v) for v in result.x[:n_lp_feeds]]
    total_dmi = sum(amounts)
    if total_dmi <= 0:
        return {"triggered": False, "reason": None, "metrics": {}}

    pendf_sup = sum(
        amounts[i] * float(feeds_res[i].get("ndf") or 0.0) * _feed_pendf_factor(feeds_res[i])
        for i in range(len(feeds_res))
    )
    pendf_density = pendf_sup / total_dmi
    pabkh_sup = sum(
        amounts[i] * (
            float(feeds_res[i].get("st") or 0.0)
            + float(feeds_res[i].get("zu") or 0.0)
            - float(feeds_res[i].get("bst") or 0.0)
        )
        for i in range(len(feeds_res))
    )
    pabkh_density = pabkh_sup / total_dmi
    st_density = sum(
        amounts[i] * float(feeds_res[i].get("st") or 0.0) for i in range(len(feeds_res))
    ) / total_dmi
    # Pansenabbaubare Staerke (DLG 01|2025 -> Input der Zebeli-2008-pH-Formel)
    abbaust_density = _abbaust_density_kgdm(feeds_res, amounts, total_dmi)
    pendf_min_val = _pendf_minimum(st_density, total_dmi)
    pendf_model_ok = _pendf_model_calibrated(st_density, total_dmi)
    ph = _ph_predict(pendf_density, abbaust_density, total_dmi)
    ph_valid = _ph_inputs_in_range(pendf_density, abbaust_density, total_dmi)

    pasture_pmr = _is_pasture_pmr_system(feeds_res, profile)
    pabkh_limit = 225.0 if pasture_pmr else 210.0
    # Primaere Planungsgroesse (DLG 01|2025 Kap. 8.2): aNDFomGF+CoP-Mindestdichte
    # als binaere pabKH-Kaskade. Co-Produkte (Biertreber, Pressschnitzel, ...)
    # zaehlen hier mit zu den strukturwirksamen Fasertraegern.
    forage_ndf_sup = sum(
        amounts[i] * float(feeds_res[i].get("ndf") or 0.0)
        for i in range(len(feeds_res))
        if feeds_res[i].get("forage")
    )
    cop_ndf_sup = sum(
        amounts[i] * float(feeds_res[i].get("ndf") or 0.0)
        for i in range(len(feeds_res))
        if feeds_res[i].get("structural_coproduct") and not feeds_res[i].get("forage")
    )
    andfom_gf_cop_density = (forage_ndf_sup + cop_ndf_sup) / total_dmi if total_dmi > 0 else 0.0
    andfom_gf_target = _andfom_gf_min_target(
        staerke_density_kgdm=st_density,
        pabkh_density_kgdm=pabkh_density,
        pasture_pmr=pasture_pmr,
    )

    triggers: List[str] = []
    if ph_valid and ph < 5.9:
        triggers.append(f"pH_predicted={ph:.2f} < 5.9 (SARA-Schwelle)")
    # peNDF ist laut DLG 01|2023 eine Kontrollgroesse; als SARA-Trigger nur, wenn
    # das peNDF-Modell im kalibrierten Bereich ist (ausserhalb extrapolieren wir
    # nur Fallback-Werte, die keinen Reopt rechtfertigen).
    if pendf_model_ok and pendf_density < pendf_min_val:
        triggers.append(
            f"peNDF={pendf_density:.0f} < Minimum {pendf_min_val:.0f} g/kg TM (Kontrollgroesse)"
        )
    # aNDFomGF+CoP ist die primaere Planungsgroesse (DLG 01|2025) - hier
    # deutlich unter Ziel ist ein valider SARA-Trigger unabhaengig vom
    # peNDF-Modellstatus.
    if andfom_gf_cop_density < andfom_gf_target - 10.0:
        triggers.append(
            f"aNDFomGF+CoP={andfom_gf_cop_density:.0f} < Ziel {andfom_gf_target:.0f} g/kg TM"
        )
    if pabkh_density > pabkh_limit - 3.0:
        triggers.append(
            f"pabKH={pabkh_density:.0f} g/kg TM am Limit {pabkh_limit:.0f} (Puffer <= 3)"
        )

    metrics = {
        "ph_predicted": ph,
        "ph_formula_applicable": ph_valid,
        "pendf_kgdm": round(pendf_density, 1),
        "pendf_min_kgdm": round(pendf_min_val, 1),
        "pendf_model_calibrated": pendf_model_ok,
        "andfom_gf_cop_kgdm": round(andfom_gf_cop_density, 1),
        "andfom_gf_target_kgdm": round(andfom_gf_target, 1),
        "pabkh_kgdm": round(pabkh_density, 1),
        "pabkh_limit_kgdm": pabkh_limit,
        "starch_kgdm": round(st_density, 1),
        "abbaust_kgdm": round(abbaust_density, 1),
        "total_dmi_kg": round(total_dmi, 2),
    }
    return {
        "triggered": bool(triggers),
        "reason": "; ".join(triggers) if triggers else None,
        "metrics": metrics,
    }


def _maybe_run_sara_safety_reopt(
    *,
    lp_out: Dict[str, Any],
    req: "_CowReq",
    feeds: List[Dict[str, Any]],
    profile: Dict[str, Any],
    runtime_options: Dict[str, Any],
    fan_mode: str,
    fan_reference: Optional[float],
    fan_tol: float,
    fan_max_iter: int,
    seasonal: Dict[str, Any],
    buffer_min_kg: float,
) -> Dict[str, Any]:
    """Loese Rationsoptimierung bei SARA-Risiko mit verschaerften Constraints erneut.

    Immer return: entweder `lp_out` (unveraendert, ggf. mit `_sara_reopt` Block)
    oder neuer `lp_out_tight` mit `_sara_reopt = {triggered, actions, before, after}`.
    """
    risk = _detect_sara_risk(lp_out, profile)
    if not risk["triggered"]:
        lp_out["_sara_reopt"] = {
            "triggered": False,
            "reason": None,
            "metrics_before": risk["metrics"],
        }
        return lp_out

    # Verschaerfte Constraints fuer Reopt-Versuch.
    tight_overrides = {
        "pabkh_max": max(160.0, (225.0 if _is_pasture_pmr_system(feeds, profile) else 210.0) - 20.0),
        "pendf_floor_boost": 15.0,
        "andfom_gf_min_boost": 10.0,
    }

    # Pansenpuffer als Pflichtbaustein mit erhoehter Mindestmenge.
    feeds_tight: List[Dict[str, Any]] = [dict(f) for f in feeds]
    buffer_target_min = max(buffer_min_kg, 0.15)
    buffer_idx = next(
        (i for i, f in enumerate(feeds_tight) if f.get("_special") == "summer_buffer"),
        None,
    )
    if buffer_idx is None:
        for supplement in _SPECIAL_SUPPLEMENTS:
            if supplement.get("_special") == "summer_buffer":
                buf = dict(supplement)
                buf["min_kg"] = buffer_target_min
                feeds_tight.append(buf)
                break
    else:
        feeds_tight[buffer_idx]["min_kg"] = max(
            float(feeds_tight[buffer_idx].get("min_kg", 0.0)), buffer_target_min
        )

    runtime_tight = dict(runtime_options)
    runtime_tight["sara_overrides"] = tight_overrides

    # FAN-Modus exakt nachbilden (einfache Umsetzung: ein Solve mit aktueller FAN-Ref).
    # Fuer die Reopt-Runde reicht ein einmaliger Solve; Iteration wuerde nur bei
    # starker Mengenaenderung helfen, die verschaerften Constraints dominieren hier.
    fani_ref = lp_out.get("_fan_final") or fan_reference or 3.0
    adjusted = _apply_fan_effect(feeds_tight, float(fani_ref))
    lp_tight = _run_lp(req, adjusted, profile, runtime_options=runtime_tight)

    actions = [
        f"pabKH-Deckel -20 -> {tight_overrides['pabkh_max']:.0f} g/kg TM",
        "peNDF-Floor +15 g/kg TM (Stage-2)",
        "aNDFomGF-Mindestdichte +10 g/kg TM",
        f"NaHCO3-Pansenpuffer Pflichtmenge >= {buffer_target_min:.2f} kg TM/d",
    ]

    if lp_tight["scipy_result"].status != 0:
        # Reopt infeasible -> wir behalten das urspruengliche Ergebnis,
        # markieren aber, dass der Safety-Loop versucht wurde und hart wurde.
        lp_out["_sara_reopt"] = {
            "triggered": True,
            "reason": risk["reason"],
            "actions": actions,
            "resolved": False,
            "resolution_note": (
                "Reoptimierung mit verschaerften Constraints infeasible – bestehende Ration "
                "beibehalten, aber fachlich rot. Grobfutterangebot ueberpruefen (peNDF-Quellen, "
                "langfaseriges Heu/Stroh, Luzerne) oder Zielmilchleistung reduzieren."
            ),
            "metrics_before": risk["metrics"],
        }
        return lp_out

    # Zweitmessung der Metriken nach Reopt.
    lp_tight["_runtime_options"] = runtime_tight
    lp_tight["_fan_iterations"] = lp_out.get("_fan_iterations", []) + [
        {"i": "sara_reopt", "mode": "safety_reopt", "delta": 0.0}
    ]
    lp_tight["_fan_converged"] = lp_out.get("_fan_converged")
    lp_tight["_fan_final"] = lp_out.get("_fan_final")
    lp_tight["_fan_catalog_info"] = lp_out.get("_fan_catalog_info")
    post = _detect_sara_risk(lp_tight, profile)
    lp_tight["_sara_reopt"] = {
        "triggered": True,
        "reason": risk["reason"],
        "actions": actions,
        "resolved": not post["triggered"],
        "resolution_note": (
            "Reoptimierung mit verschaerften Azidose-Constraints erfolgreich." if not post["triggered"]
            else "Reoptimierung hat Risiko reduziert, aber Indikatoren bleiben grenzwertig."
        ),
        "metrics_before": risk["metrics"],
        "metrics_after": post["metrics"],
    }
    return lp_tight


def _demo_profile() -> Dict[str, Any]:
    return {
        "breed": "Deutsche Holstein",
        "body_weight_kg": 675,
        "milk_kg_day": 35,
        "milk_fat_pct": 4.0,
        "milk_protein_pct": 3.4,
        "lactation_stage_days": 100,
        "parity": 2,
        "production_group": "Hochleistung",
        # Kuratierte Feed-Auswahl für Demo — praxisübliche TMR norddeutscher Milchviehbetriebe.
        # Verhindert, dass der LP-Solver zu günstige Nassnebenprodukte dominieren lässt.
        # Kuratierter Feed-Set: typische Norddeutsche Milchvieh-TMR ohne
        # Nassnebenprodukt-Dominanz. Mais Korn entfernt (XL-Konflikt bei vollem
        # Stärkeportfolio). Grassilage-Anteil durch Max-Overrides begrenzt.
        "_demo_feed_ids": [
            "dlg_10490020",  # Mais, Ganzpflanze, hohe OMD (siliert) — TMR-Backbone
            "dlg_10500020",  # Mais, Ganzpflanze, mittlere OMD (siliert)
            "dlg_10320020",  # Gras, gute OMD (siliert)
            "dlg_10150030",  # Gras, gute OMD (Heu)
            "dlg_10610000",  # Stroh, Gerste — Struktursicherung / peNDF
            "dlg_30970130",  # Raps, Extraktionsschrot — Proteinträger
            "dlg_31050130",  # Soja, Extraktionsschrot — sidLys
            "dlg_30820030",  # Gerste, Samen — Stärke/Energie
            "dlg_20750012",  # Rübenpressschnitzel — faserhaltiger Saftfutter-Beitrag
            "dlg_41290030",  # Zuckerrüben-Melasse — Schmackhaftigkeit/DCAB
        ],
    }


# ---------------------------------------------------------------------------
# Pydantic Models für API
# ---------------------------------------------------------------------------

# Refactor 2026-04-23: ausgelagert nach app.agrar.rations.constants
from app.agrar.rations.constants.gfe2023 import FAN_MODES as _FAN_MODES
from app.agrar.rations.constants.solver_defaults import (
    MILK_TARGET_HEADROOM_FRAC as _MILK_TARGET_HEADROOM_FRAC,
    MILK_TRADEOFF_MAX_PCT_PER_STAGE_DEFAULT as _MILK_TRADEOFF_MAX_PCT_PER_STAGE_DEFAULT,
    OBJECTIVE_STRATEGIES as _OBJECTIVE_STRATEGIES,
    RELAXATION_POLICIES as _RELAXATION_POLICIES,
)
_SEASON_PROFILES = (
    "spring_young",
    "spring_mid",
    "spring_late",
    "summer_young",
    "summer_mid",
    "summer_late",
    "autumn",
    "winter",
)
_POLICY_PROFILES = (
    # Generische Profile (Abwaerts-Kompatibilitaet)
    "tmr_standard",
    "pmr_standard",
    "pmr_pasture_spring",
    "pmr_pasture_summer",
    "pmr_pasture_autumn",
    # DLG 01|2025 Tab. 13-15: Leistungs- und Physiologiestufen.
    # Namen halten wir bewusst kurz und eindeutig fuer API-Kompatibilitaet.
    "tmr_fresh_lactation",   # Frischmelker 0-60 LT
    "tmr_high_yield",        # Hochleistung (>=35 kg Milch/d)
    "tmr_mid_yield",         # Mittellaktation (25-34 kg Milch/d)
    "tmr_late_lactation",    # Altmelker (<25 kg Milch/d)
    "tmr_dry_cow",           # Trockensteher (frueh/Standard)
    "tmr_transit",           # Transit/Anfuetterung (~-3 LT bis Abkalbung)
)


# ---------------------------------------------------------------------------
# DLG 01|2025 Tab. 13-15: Referenzkorridore je Leistungs-/Physiologiestufe.
#
# Alle Angaben in Rations-TM-Bezug (g/kg TM), sofern nicht anders vermerkt.
# Die Werte dienen als Zielkorridore (UI / Soft-Konfiguration) und greifen
# nicht in die harten LP-Constraints ein. Quellen:
#   - DLG-Information 01|2025, Tab. 13 (Fresh Cow / High Yield)
#   - DLG-Information 01|2025, Tab. 14 (Mid + Late Lactation)
#   - DLG-Information 01|2025, Tab. 15 (Dry Cow / Transit)
#
# Spalten:
#   me_kgdm_min/max:    Energiedichte  (MJ ME/kg TM)
#   cp_kgdm_min/max:    Rohprotein     (g/kg TM)
#   sidp_kgdm_min:      sidP           (g/kg TM)   (sofern DLG angibt)
#   pabkh_max:          pabKH-Obergrenze [g/kg TM]
#   xl_kgdm_max:        Rohfett [g/kg TM]
#   forage_share_min_pct: Grundfutter-Mindestanteil [% TM]
#   andfom_gf_cop_min:  aNDFomGF+CoP-Mindestdichte [g/kg TM] (bei niedrigem pabKH)
#   ndf_kgdm_min:       Gesamt-aNDFom-Mindestdichte [g/kg TM]
# ---------------------------------------------------------------------------
_POLICY_PROFILE_TARGETS: Dict[str, Dict[str, Any]] = {
    # ME-Dichte-Korridore in MJ ME/kg TM (GfE-System).
    # Umrechnung aus DLG 01|2025 NEL-Werten: ME = NEL / k_l (k_l ≈ 0,62 Laktation / 0,57 TS).
    # Beispiel Mittellaktation: NEL 6,8 MJ → ME ≈ 11,0 MJ/kg TM.
    "tmr_standard": {
        "me_kgdm_min": 10.50, "me_kgdm_max": 11.50,
        "cp_kgdm_min": 140.0, "cp_kgdm_max": 165.0,
        "sidp_kgdm_min": 90.0,
        "pabkh_max": 200.0, "xl_kgdm_max": 38.0,
        "forage_share_min_pct": 55.0,
        "andfom_gf_cop_min": 220.0, "ndf_kgdm_min": 320.0,
        "label": "TMR Standard (entspricht Tab. 14 Mittellaktation, DLG 01|2025)",
    },
    "pmr_standard": {
        "me_kgdm_min": 10.50, "me_kgdm_max": 11.50,
        "cp_kgdm_min": 140.0, "cp_kgdm_max": 165.0,
        "sidp_kgdm_min": 90.0,
        "pabkh_max": 200.0, "xl_kgdm_max": 38.0,
        "forage_share_min_pct": 55.0,
        "andfom_gf_cop_min": 220.0, "ndf_kgdm_min": 320.0,
        "label": "PMR Standard (Stall; Referenz wie Tab. 14 Mittellaktation)",
    },
    "pmr_pasture_spring": {
        "me_kgdm_min": 10.50, "me_kgdm_max": 11.80,
        "cp_kgdm_min": 140.0, "cp_kgdm_max": 170.0,
        "sidp_kgdm_min": 90.0,
        "pabkh_max": 195.0, "xl_kgdm_max": 38.0,
        "forage_share_min_pct": 58.0,
        "andfom_gf_cop_min": 200.0, "ndf_kgdm_min": 300.0,
        "label": "PMR+Weide Fruehjahr (junges Grün, Tab. 14 angepasst, konserv. pabKH)",
    },
    "pmr_pasture_summer": {
        "me_kgdm_min": 10.50, "me_kgdm_max": 11.80,
        "cp_kgdm_min": 140.0, "cp_kgdm_max": 165.0,
        "sidp_kgdm_min": 90.0,
        "pabkh_max": 200.0, "xl_kgdm_max": 38.0,
        "forage_share_min_pct": 58.0,
        "andfom_gf_cop_min": 200.0, "ndf_kgdm_min": 300.0,
        "label": "PMR+Weide Sommer (Tab. 14 Mittellaktation, Weideanteil im PMR)",
    },
    "pmr_pasture_autumn": {
        "me_kgdm_min": 10.00, "me_kgdm_max": 11.20,
        "cp_kgdm_min": 135.0, "cp_kgdm_max": 160.0,
        "sidp_kgdm_min": 85.0,
        "pabkh_max": 185.0, "xl_kgdm_max": 36.0,
        "forage_share_min_pct": 60.0,
        "andfom_gf_cop_min": 225.0, "ndf_kgdm_min": 330.0,
        "label": "PMR+Weide Herbst (nach Tab. 14 Altmelker verschoben, hoehere Faserziele)",
    },
    "tmr_fresh_lactation": {
        "me_kgdm_min": 11.50, "me_kgdm_max": 12.50,
        "cp_kgdm_min": 160.0, "cp_kgdm_max": 185.0,
        "sidp_kgdm_min": 105.0,
        "pabkh_max": 210.0, "xl_kgdm_max": 42.0,
        "forage_share_min_pct": 50.0,
        "andfom_gf_cop_min": 200.0, "ndf_kgdm_min": 300.0,
        "label": "Frischmelker (0-60 LT, DLG 01|2025 Tab. 13)",
    },
    "tmr_high_yield": {
        "me_kgdm_min": 11.00, "me_kgdm_max": 12.00,
        "cp_kgdm_min": 155.0, "cp_kgdm_max": 180.0,
        "sidp_kgdm_min": 100.0,
        "pabkh_max": 210.0, "xl_kgdm_max": 40.0,
        "forage_share_min_pct": 55.0,
        "andfom_gf_cop_min": 200.0, "ndf_kgdm_min": 310.0,
        "label": "Hochleistung (>=35 kg Milch, DLG 01|2025 Tab. 13)",
    },
    "tmr_mid_yield": {
        "me_kgdm_min": 10.50, "me_kgdm_max": 11.50,
        "cp_kgdm_min": 140.0, "cp_kgdm_max": 165.0,
        "sidp_kgdm_min": 90.0,
        "pabkh_max": 200.0, "xl_kgdm_max": 38.0,
        "forage_share_min_pct": 58.0,
        "andfom_gf_cop_min": 220.0, "ndf_kgdm_min": 320.0,
        "label": "Mittellaktation (25-34 kg Milch, DLG 01|2025 Tab. 14)",
    },
    "tmr_late_lactation": {
        "me_kgdm_min": 10.00, "me_kgdm_max": 11.00,
        "cp_kgdm_min": 130.0, "cp_kgdm_max": 155.0,
        "sidp_kgdm_min": 80.0,
        "pabkh_max": 180.0, "xl_kgdm_max": 35.0,
        "forage_share_min_pct": 62.0,
        "andfom_gf_cop_min": 230.0, "ndf_kgdm_min": 340.0,
        "label": "Altmelker (<25 kg Milch, DLG 01|2025 Tab. 14)",
    },
    "tmr_dry_cow": {
        "me_kgdm_min": 9.00, "me_kgdm_max": 10.00,
        "cp_kgdm_min": 115.0, "cp_kgdm_max": 135.0,
        "sidp_kgdm_min": 60.0,
        "pabkh_max": 140.0, "xl_kgdm_max": 30.0,
        "forage_share_min_pct": 75.0,
        "andfom_gf_cop_min": 300.0, "ndf_kgdm_min": 380.0,
        "label": "Trockensteher (DLG 01|2025 Tab. 15)",
    },
    "tmr_transit": {
        "me_kgdm_min": 10.00, "me_kgdm_max": 11.00,
        "cp_kgdm_min": 135.0, "cp_kgdm_max": 160.0,
        "sidp_kgdm_min": 80.0,
        "pabkh_max": 170.0, "xl_kgdm_max": 35.0,
        "forage_share_min_pct": 62.0,
        "andfom_gf_cop_min": 260.0, "ndf_kgdm_min": 350.0,
        "label": "Transit / Anfuetterung (DLG 01|2025 Tab. 15)",
    },
}


def _policy_profile_targets(profile_key: Optional[str]) -> Optional[Dict[str, Any]]:
    """Gibt die DLG-01|2025-Referenzkorridore fuer ein Policy-Profil zurueck."""
    if not profile_key:
        return None
    return _POLICY_PROFILE_TARGETS.get(profile_key)


# ---------------------------------------------------------------------------
# DLG-01|2025-Policy-Profil-Auswertung — Re-Export aus lp_stage2.py
# (RATIONS-LP-SPLIT-001: extrahiert nach app/agrar/rations/solver/lp_stage2.py)
# ---------------------------------------------------------------------------
from app.agrar.rations.solver.lp_stage2 import (  # noqa: E402,F401
    POLICY_BAND_SPECS as _POLICY_BAND_SPECS,
    policy_band_coeffs as _policy_band_coeffs,
    policy_profile_band_evaluate as _policy_profile_band_evaluate,
    build_policy_band_lp_extension as _build_policy_band_lp_extension,
    build_policy_profile_evaluation as _build_policy_profile_evaluation,
)


# ---------------------------------------------------------------------------
# Saisonprofile – fachliche Anpassungen (Spec §12 Sommer/Herbst)
# ---------------------------------------------------------------------------
# Quellen:
#   - DLG-Merkblatt 417 (Weidehaltung, Sommer-/Herbstweide)
#   - DLG-Information 01|2023 (Strukturversorgung, RNB/RMD)
#   - GfE-Workshop 2023 (K/Mg-Antagonismus, Hitzestress, NaHCO3)
#
# dmi_factor:           Multiplikator auf dmi_target/min/max (Hitzestress).
# na_boost_factor:      Multiplikator auf Na-Mindestbedarf (Schweissverlust).
# inject_buffer:        Bool – automatischer Pansenpuffer (NaHCO3).
# buffer_min_kg:        Untergrenze fuer NaHCO3 (Pflichtmenge bei Hitzestress).
# cp_density_max:       Harte Obergrenze CP-Dichte [g/kg TM] (Harnstoffschutz Herbst).
# ndf_density_min_boost: Additiver Aufschlag auf aNDFom-Mindestdichte [g/kg TM].
# rmd_max_override:     Obergrenze RMD [g N/kg TM] (wird gegen Fuetterungstyp minimiert).
# andfom_gf_min_boost:  Aufschlag auf aNDFomGF-Dichteminimum [g/kg TM] (Strukturverstaerkung).

_SEASONAL_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "spring_young": {
        "dmi_factor": 1.00,
        "na_boost_factor": 1.00,
        "inject_buffer": 0.0,
        "buffer_min_kg": 0.0,
    },
    "spring_mid": {
        "dmi_factor": 1.00,
        "na_boost_factor": 1.00,
        "inject_buffer": 0.0,
        "buffer_min_kg": 0.0,
    },
    "spring_late": {
        "dmi_factor": 1.00,
        "na_boost_factor": 1.00,
        "inject_buffer": 0.0,
        "buffer_min_kg": 0.0,
    },
    # Sommer: Hitzestress fuehrt zu reduzierter TM-Aufnahme (GfE-Workshop 2023 /
    # DLG-Merkblatt 417). Typische Reduktion: -5 % bei moderaten Temperaturen
    # (summer_young/mid) bis -12 % bei Hochsommer/Abend (summer_late). Na-Bedarf
    # steigt durch Schwitzen um 20-30 %. NaHCO3 als Pansenpuffer wirkt der
    # subakuten Azidose entgegen.
    "summer_young": {
        "dmi_factor": 0.97,
        "na_boost_factor": 1.15,
        "inject_buffer": 1.0,
        "buffer_min_kg": 0.05,
    },
    "summer_mid": {
        "dmi_factor": 0.93,
        "na_boost_factor": 1.25,
        "inject_buffer": 1.0,
        "buffer_min_kg": 0.10,
    },
    "summer_late": {
        "dmi_factor": 0.88,
        "na_boost_factor": 1.30,
        "inject_buffer": 1.0,
        "buffer_min_kg": 0.12,
        # Zusaetzliche Strukturstuetze fuer reduzierte Aufnahme
        "andfom_gf_min_boost": 10.0,
    },
    # Herbst: Stickstoffreicher Grasaufwuchs mit hohem RNB. Schutz der Tiere vor
    # Harnstoffbelastung ueber harte CP-Dichte-Obergrenze (140 g/kg TM fuer Stall-
    # orientierung, 175 g/kg TM als Grundfutterkorridor bei Weide) und zusaetzliche
    # Stuetzung ueber Strukturfutter.
    "autumn": {
        "dmi_factor": 0.98,
        "na_boost_factor": 1.05,
        "inject_buffer": 0.0,
        "buffer_min_kg": 0.0,
        # Harnstoffschutz: CP-Obergrenze staerker limitieren
        "cp_density_max_override": 175.0,
        # Strukturverstaerkung gegen N-Ueberschuss
        "andfom_gf_min_boost": 15.0,
        # Leichte RMD-Entspannung (weidetypisch), aber nicht beliebig
        "rmd_max_boost": 1.0,
    },
    "winter": {
        "dmi_factor": 1.00,
        "na_boost_factor": 1.00,
        "inject_buffer": 0.0,
        "buffer_min_kg": 0.0,
    },
}


def _seasonal_adjustments(season_profile: Optional[str]) -> Dict[str, float]:
    """Gibt die fachliche Saisonanpassung (Spec §12) zurueck oder neutralen Default."""
    if not season_profile:
        return {
            "dmi_factor": 1.0,
            "na_boost_factor": 1.0,
            "inject_buffer": 0.0,
            "buffer_min_kg": 0.0,
        }
    return dict(_SEASONAL_ADJUSTMENTS.get(season_profile, {
        "dmi_factor": 1.0,
        "na_boost_factor": 1.0,
        "inject_buffer": 0.0,
        "buffer_min_kg": 0.0,
    }))

# FAN-V1 Defaults (Spec §11.1 freigegeben 2026-04-21)
# Refactor 2026-04-23: ausgelagert nach app.agrar.rations.constants
from app.agrar.rations.constants.gfe2023 import (  # noqa: F401
    FAN_DEFAULT_MODE as _FAN_DEFAULT_MODE,
    FAN_DEFAULT_TOLERANCE as _FAN_DEFAULT_TOLERANCE,
    FAN_DEFAULT_TOLERANCE_WARN as _FAN_DEFAULT_TOLERANCE_WARN,
    FAN_DEFAULT_MAX_ITERATIONS as _FAN_DEFAULT_MAX_ITERATIONS,
    FAN_REFERENCE_PRESETS as _FAN_REFERENCE_PRESETS,
    FAN_REFERENCE_MIN as _FAN_REFERENCE_MIN,
    FAN_REFERENCE_MAX as _FAN_REFERENCE_MAX,
)
from app.agrar.rations.constants.solver_defaults import (
    RELAXATION_DEFAULT as _RELAXATION_DEFAULT,
    RELAXATION_FACTORS as _RELAXATION_FACTORS,
    PENALTY_BASE_COST as _PENALTY_BASE_COST,
    PENALTY_CLASS_WEIGHTS as _PENALTY_CLASS_WEIGHTS,
    STAGE2_WELFARE_WEIGHT_BALANCE_ONLY as _STAGE2_WELFARE_WEIGHT_BALANCE_ONLY,
)


class ConcentrateRecipeProfile(BaseModel):
    """Rezeptur-/Pansen-Charakteristik eines Konzentratfutters.

    Entscheidet (zusammen mit `FeedingSystemConfig`) ueber die zulaessigen
    Einzelgaben im Melkstand/Transponder/AMS.

    - starch_breakdown_class: 'slow' (Trockenschnitzel+Maismehl dominant),
      'rapid' (Muehlennebenprodukte dominant), 'mixed' (Default).
    - rumen_buffer_present: NaHCO3 oder MgO als Zusatz in der Rezeptur.
    - Quelle kennzeichnet, ob Werte deklariert, per OCR gescannt, manuell
      geschaetzt oder Default sind (UI zeigt Badge an).
    """
    starch_breakdown_class: Literal["slow", "mixed", "rapid"] = "mixed"
    mill_byproduct_share: Optional[float] = None        # 0..1, optional
    slow_starch_share: Optional[float] = None           # 0..1 (Trockenschnitzel + Maismehl)
    rumen_buffer_present: bool = False
    source: Literal["declared", "scanned_ocr", "manual_estimate", "default"] = "default"


class FeedingSystemConfig(BaseModel):
    """Fuetterungssystem-Konfiguration (steuert Block-Aufteilung + Limits).

    - system: TMR (alles im Mischwagen), PMR_stall (Stall + Kraftfutter-
      Staffelung), PMR_pasture (Weide + ergaenzende Stallfuetterung).
    - concentrate_distribution: wie Kraftfutter zugeteilt wird.
    - Praxisgrenzen werden aus System + Verteilung + Parity + Rezeptur abgeleitet.
    """
    system: Literal["TMR", "PMR_stall", "PMR_pasture"] = "TMR"
    concentrate_distribution: Literal[
        "included_in_tmr", "transponder", "ams", "milkparlor"
    ] = "included_in_tmr"

    # Optionale Praxiseinstellungen (werden sonst aus Defaults abgeleitet)
    concentrate_max_per_serving_kg: Optional[float] = None
    concentrate_max_per_day_kg: Optional[float] = None
    concentrate_servings_per_day: Optional[float] = None

    # Bei Milchvieh: 1. Laktation bekommt tendenziell kleinere Einzelgaben
    treat_as_primiparous: bool = False

    # Default-Konzentrat-Rezepturprofil (kann pro Feed ueberschrieben werden)
    default_concentrate_recipe: Optional[ConcentrateRecipeProfile] = None


class FeedBlockAssignment(BaseModel):
    """Manuelles Override: explizite Block-Zuordnung fuer ein Feed."""
    feed_id: str
    block: Literal["pasture", "tmr", "concentrate_staged"]
    # optionale Rezepturdaten, falls Feed als Konzentrat-Staged klassifiziert ist
    concentrate_recipe: Optional[ConcentrateRecipeProfile] = None


class _FanOptions(BaseModel):
    """GfE-2023 / FAN1 ⇄ FANi Bewertungsoptionen.

    Spec §4 + §8. Alle Felder optional; Defaults werden in `_resolve_fan_options()` gesetzt.
    """
    mode: Optional[str] = None                # auto_iterative | reference | evaluation_only
    reference: Optional[float] = None         # FANi bei mode=reference, Presets 2.5/3.0/3.5 + Freiwert
    tolerance: Optional[float] = None         # |FANi_out - FANi_in| Abbruchkriterium
    tolerance_warn: Optional[float] = None    # Warnschwelle fuer UI-Hinweis
    max_iterations: Optional[int] = None      # Iterationsdeckel


class _OptimizeFromProfileBody(BaseModel):
    cow_profile: Dict[str, Any]
    feeds: Optional[List[str]] = None          # Filter auf bestimmte Feed-IDs
    custom_feeds: Optional[List[Dict[str, Any]]] = None  # Betriebseigene Werte
    price_overrides: Optional[Dict[str, float]] = None   # Preisüberschreibung
    max_tm_overrides: Optional[Dict[str, float]] = None  # Max kg TM/Tag je Feed (saisonale Limits)
    min_tm_overrides: Optional[Dict[str, float]] = None  # Min kg TM/Tag je Feed (UI Min-FM)

    # FAN-MODE-V1 additive Felder (Spec §4 freigegeben 2026-04-21)
    fan_options: Optional[_FanOptions] = None          # GfE-2023 FAN1/FANi-Bewertungsoptionen
    relaxation_policy: Optional[str] = None            # strict | standard | soft (Default: standard)
    objective_strategy: Optional[str] = None           # balance_then_cost | balance_only | cost_only
    season_profile: Optional[str] = None               # spring_young | ...; steuert Policy-Profil (§6)
    policy_profile: Optional[str] = None               # Explicit Override; sonst aus feeding_type+season abgeleitet
    policy_overrides: Optional[Dict[str, Any]] = None  # Expertenmodus: Block-Limit-Overrides

    # Lexikografische Milch-Pipeline: Zwischen-Stufen-Einbusse begrenzen oder abschalten.
    disable_milk_tradeoff_between_stages: Optional[bool] = None
    milk_tradeoff_max_pct_per_stage: Optional[float] = None   # Prozentpunkte je Stufenwechsel (Default Backend)
    stage2_minimize_feed_eur_per_day: Optional[bool] = None   # True: Stage 2 klassisch EUR/d statt EUR/kg ECM

    # Slice 1h (2026-04-23): Fuetterungssystem-Architektur
    # - feeding_system_config: TMR / PMR_stall / PMR_pasture + Verteilungssystem
    #   (transponder/ams/milkparlor/included_in_tmr) + optionale Rezeptur-Profile
    # - feed_block_overrides: optionale manuelle Zuordnung Feed -> Block,
    #   falls die Heuristik (_auto_assign_block) nicht passt
    # Abwaertskompatibel: Wenn beide None sind, wird aus profile.feeding_type
    # automatisch ein FeedingSystemConfig abgeleitet (PMR+Weide -> PMR_pasture
    # mit milkparlor; PMR -> PMR_stall mit transponder; sonst TMR/included).
    feeding_system_config: Optional[FeedingSystemConfig] = None
    feed_block_overrides: Optional[List[FeedBlockAssignment]] = None


class _RequirementsBody(BaseModel):
    body_weight_kg: float = 675.0
    milk_kg_day: float = 30.0
    milk_fat_pct: float = 4.0
    milk_protein_pct: float = 3.4
    lactation_stage_days: Optional[int] = None
    parity: Optional[int] = None


class _CompoundFeedComponent(BaseModel):
    name: str
    inclusion_pct: float
    matched_feed_id: Optional[str] = None
    matched_feed_name: Optional[str] = None


class _CompoundFeedDeclaredAnalysis(BaseModel):
    crude_protein_pct: Optional[float] = None
    crude_fat_pct: Optional[float] = None
    crude_fiber_pct: Optional[float] = None
    crude_ash_pct: Optional[float] = None
    calcium_pct: Optional[float] = None
    phosphorus_pct: Optional[float] = None
    sodium_pct: Optional[float] = None
    magnesium_pct: Optional[float] = None
    nel_mj_kg: Optional[float] = None


class _CompoundFeedGfeEstimate(BaseModel):
    basis: str
    match_coverage_pct: float
    me_fan1_mj_kgdm: Optional[float] = None
    me_fani_mj_kgdm: Optional[float] = None
    nel_mj_kgdm: Optional[float] = None
    sidp_g_kgdm: Optional[float] = None
    nxp_g_kgdm: Optional[float] = None
    cp_g_kgdm: Optional[float] = None
    andfom_g_kgdm: Optional[float] = None
    starch_g_kgdm: Optional[float] = None
    sugar_g_kgdm: Optional[float] = None
    fat_g_kgdm: Optional[float] = None
    omd_method: Optional[str] = None


class _CompoundFeedParsed(BaseModel):
    source_filename: str
    source_type: str
    product_name: str
    supplier_name: Optional[str] = None
    declared_analysis: _CompoundFeedDeclaredAnalysis
    composition: List[_CompoundFeedComponent]
    gfe2023_estimate: _CompoundFeedGfeEstimate
    optimizer_feed: Dict[str, Any]
    warnings: List[str]
    raw_text_preview: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/health", summary="Health rations")
async def rations_health():
    base_url = get_rations_base_url()
    feeds = _get_feeds()
    json_path = _dlg_json_path()
    if not base_url:
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "configured": True,
                "solver": "internal-gfe2023",
                "energy_system": "ME-FAN1",
                "protein_system": "sidP",
                "feed_database": "DLG-FWT-2025" if (json_path and len(feeds) > 20) else "fallback",
                "feed_count": len(feeds),
                "dlg_data_path": json_path,
                "message": f"Interner GfE-2023 LP-Solver aktiv – {len(feeds)} Futtermittel geladen",
            },
        )
    return await _proxy_request("GET", "/health")


@router.get("/feeds", summary="Feeds abrufen")
async def get_feeds(
    request: Request,
    group: Optional[str] = Query(None, description="Filter nach Futtergruppe"),
    forage_only: bool = Query(False, description="Nur Grundfutter"),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not get_rations_base_url():
        feeds = _get_feeds()
        if group:
            feeds = [f for f in feeds if group.lower() in f.get("group", "").lower()]
        if forage_only:
            feeds = [f for f in feeds if f.get("forage")]
        feed_list = [
            {
                # Pflichtfelder gemäß Frontend FeedIngredient-Interface
                "id": f["id"],
                "name": f["name"],
                "group": f["group"],
                "dm_frac": round(f["dm_frac"], 4),
                "price_eur_kgdm": f["price"],
                "me_mj_kgdm": f["me"],
                "sidp_g_kgdm": f["sidp"],
                "andfom_g_kgdm": f["ndf"],
                "starch_g_kgdm": f["st"],
                "sugar_g_kgdm": f["zu"],
                "fat_g_kgdm": f["xl"],
                "ca_g_kgdm": f["ca"],
                "p_g_kgdm": f["p"],
                "na_g_kgdm": f.get("na", 0.0),
                "min_kgdm": f.get("min_kg", 0.0),
                "max_kgdm": f.get("max_kg", 15.0),
                "active": True,
                # Zusatzfelder für erweiterte Anzeige
                "forage": f.get("forage", False),
                "konservierung": f.get("konservierung"),
                "futterart": f.get("futterart"),
                "cp_g_kgdm": f.get("cp", 0.0),
                "rmd_gn_kgdm": f.get("rmd"),
                "omdfan1_pct": f.get("omdfan1"),
                "dcab_meq_kgdm": f.get("dcab"),
                "edg_pct": f.get("edg"),
                "ge_mj_kgdm": f.get("ge"),
                "sidlys_g_kgdm": f.get("sidlys"),
                "sidmet_g_kgdm": f.get("sidmet"),
                "dlg_lid": f.get("lid"),
                "dlg_primaryid": f.get("dlg_primaryid"),
                "nomenklatur": f.get("nomenklatur"),
            }
            for f in feeds
        ]
        return JSONResponse(content=feed_list)
    params = dict(request.query_params)
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("GET", "/api/v1/feeds", tenant_id=tenant_id, params=params)


@router.get("/feeds/{feed_id}", summary="Feed abrufen")
async def get_feed(
    feed_id: str,
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not get_rations_base_url():
        feeds = _get_feeds()
        feed = next((f for f in feeds if f["id"] == feed_id), None)
        if not feed:
            raise HTTPException(status_code=404, detail="Futtermittel nicht gefunden")
        return JSONResponse(content=feed)
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("GET", f"/api/v1/feeds/{feed_id}", tenant_id=tenant_id)


@router.post("/optimize/from-profile", summary="From profile optimize")
async def optimize_from_profile(
    body: _OptimizeFromProfileBody,
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not get_rations_base_url():
        try:
            custom = None
            if body.custom_feeds:
                custom = [
                    _gfa_to_feed(cf) if cf.get("_source") == "gfa" or "rohprotein_ts" in cf else cf
                    for cf in body.custom_feeds
                ]
            runtime_options = _resolve_runtime_options(
                body.cow_profile,
                fan_options=body.fan_options,
                relaxation_policy=body.relaxation_policy,
                objective_strategy=body.objective_strategy,
                season_profile=body.season_profile,
                policy_profile=body.policy_profile,
                policy_overrides=body.policy_overrides,
                feeding_system_config=body.feeding_system_config,
                feed_block_overrides=body.feed_block_overrides,
                disable_milk_tradeoff_between_stages=body.disable_milk_tradeoff_between_stages,
                milk_tradeoff_max_pct_per_stage=body.milk_tradeoff_max_pct_per_stage,
                stage2_minimize_feed_eur_per_day=body.stage2_minimize_feed_eur_per_day,
            )
            result = _optimize_internal(
                body.cow_profile,
                custom_feeds=custom,
                feed_ids=body.feeds,
                price_overrides=body.price_overrides,
                max_tm_overrides=body.max_tm_overrides,
                min_tm_overrides=body.min_tm_overrides,
                runtime_options=runtime_options,
            )
            return JSONResponse(content=result)
        except Exception as exc:
            logger.exception("Interner LP-Solver fehlgeschlagen: %s", exc)
            raise HTTPException(status_code=500, detail=f"Optimierung fehlgeschlagen: {exc}")
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request(
        "POST", "/api/v1/optimize/from-profile",
        tenant_id=tenant_id,
        json_body=body.model_dump(),
    )


@router.post("/optimize/demo", summary="Demo optimize")
async def optimize_demo(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not get_rations_base_url():
        try:
            demo = _demo_profile()
            demo_feed_ids = demo.pop("_demo_feed_ids", None)
            # Praxistypische Mindest-/Höchstmengen für TMR Hochleistung (Musterbetrieb).
            # Ziel: Maissilage als TMR-Rückgrat, Grassilage als Ergänzung.
            demo_min = {
                "dlg_10490020": 5.0,   # Maissilage hohe OMD ≥ 5 kg TM (TMR-Backbone)
                "dlg_30970130": 2.0,   # Raps-Extraktionsschrot ≥ 2 kg TM (Protein/CP)
                "dlg_31050130": 0.8,   # Sojaschrot ≥ 0.8 kg TM (sidP, Lys)
                "dlg_30820030": 2.5,   # Gerste ≥ 2.5 kg TM (Stärke-Quelle)
            }
            demo_max = {
                "dlg_10490020": 9.0,   # Maissilage hohe OMD ≤ 9 kg TM
                "dlg_10500020": 3.0,   # Maissilage mittlere OMD ≤ 3 kg TM
                "dlg_10320020": 3.5,   # Grassilage gute OMD ≤ 3.5 kg TM
                "dlg_10150030": 1.5,   # Heu gute OMD ≤ 1.5 kg TM
                "dlg_10610000": 2.0,   # Stroh Gerste ≤ 2 kg TM (peNDF-Puffer)
                "dlg_20750012": 2.0,   # Rübenpressschnitzel ≤ 2 kg TM
                "dlg_41290030": 0.5,   # Melasse ≤ 0.5 kg TM
            }
            # Mineralfutter Milchvieh: Nicht im DLG-FWT enthalten → als Custom-Feed.
            # Typische Zusammensetzung für Laktation (Ca:Mg 2:1 Typ, 250g/d Gabe).
            demo_custom: List[Dict[str, Any]] = [{
                "id": "demo_mineralfutter",
                "name": "Mineralfutter Milchvieh (Demo)",
                "group": "Mineralfutter",
                "futterart": "Mineralien/Zusatzstoffe",
                "forage": False,
                "structural_coproduct": False,
                "dm_frac": 0.970,
                "price": 1.80,     # EUR/kg TM
                "min_kg": 0.05,    # min. 50 g TM/d als Pflichtbaustein
                "max_kg": 0.25,    # max 250 g TM/d
                "me": 0.0, "sidp": 0.0, "cp": 0.0,
                "ndf": 0.0, "adf": 0.0, "st": 0.0,
                "bst": 0.0, "zu": 0.0, "nfc": 0.0,
                "xl": 0.0,
                "ca": 150.0,   # g/kg TM — typisches Laktations-Mineralfutter
                "p": 50.0,
                "na": 80.0,
                "mg": 180.0,   # g/kg TM — Mg-reich für Grastetanie-Prophylaxe
                "k": 0.0,
                "sidlys": 0.0, "sidmet": 0.0,
            }]
            result = _optimize_internal(
                demo, feed_ids=demo_feed_ids,
                custom_feeds=demo_custom,
                min_tm_overrides=demo_min,
                max_tm_overrides=demo_max,
            )
            return JSONResponse(content=result)
        except Exception as exc:
            logger.exception("Demo-Optimierung fehlgeschlagen: %s", exc)
            raise HTTPException(status_code=500, detail=f"Demo fehlgeschlagen: {exc}")
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("POST", "/api/v1/optimize/demo", tenant_id=tenant_id)


@router.post("/optimize", summary="Optimize")
async def optimize(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    body = await request.json()
    if not get_rations_base_url():
        profile = body.get("cow_profile", body)
        try:
            result = _optimize_internal(profile)
            return JSONResponse(content=result)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Optimierung fehlgeschlagen: {exc}")
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("POST", "/api/v1/optimize", tenant_id=tenant_id, json_body=body)


@router.post("/requirements/calculate", summary="Requirements berechnen")
async def calculate_requirements(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    body = await request.json()
    if not get_rations_base_url():
        try:
            req = _gfe_requirements(body)
            return JSONResponse(content={
                "me_mj_day": round(req.me_mj, 1),
                "nel_ref_mj_day": round(req.nel_mj, 1),
                "sidp_g_day": round(req.sidp_g, 1),
                "nxp_ref_g_day": round(req.nxp_g, 1),
                "dmi_min_kg": round(req.dmi_min_kg, 2),
                "dmi_max_kg": round(req.dmi_max_kg, 2),
                "ndf_min_g": round(req.ndf_min_g, 0),
                "ca_min_g": round(req.ca_min_g, 1),
                "p_min_g": round(req.p_min_g, 1),
                "na_min_g": round(req.na_min_g, 1),
                "mg_min_g": round(req.mg_min_g, 1),
                "energy_system": "ME-FAN1-GfE2023",
                "protein_system": "sidP-GfE2023",
            })
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc))
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("POST", "/api/v1/requirements/calculate", tenant_id=tenant_id, json_body=body)


@router.post("/requirements/maintenance", summary="Requirements maintenance")
async def maintenance_requirements(
    request: Request,
    body_weight_kg: float = Query(...),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not get_rations_base_url():
        bw75 = body_weight_kg ** 0.75
        nel_maint = 0.308 * bw75
        me_maint = nel_maint / 0.73
        return JSONResponse(content={
            "me_mj_day": round(me_maint, 1),
            "nel_mj_day": round(nel_maint, 1),
            "body_weight_kg": body_weight_kg,
            "bw075": round(bw75, 1),
        })
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request(
        "POST", "/api/v1/requirements/maintenance",
        tenant_id=tenant_id,
        params={"body_weight_kg": body_weight_kg},
    )


@router.post("/feeds/validate", summary="Feeds validieren")
async def validate_feeds(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    body = await request.json()
    if not get_rations_base_url():
        return JSONResponse(content={"valid": True, "errors": []})
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("POST", "/api/v1/feeds/validate", tenant_id=tenant_id, json_body=body)


@router.post("/dlg/strukturindex", summary="Strukturindex berechnen")
async def calculate_strukturindex(request: Request):
    """
    Berechne Strukturindex nach DLG 01|2023 (Rutzmoser et al. 2011).

    Body: { "andfom_gf_kg_day": float, "pabkh_kg_day": float }
    SI = NDFomGF_kg / (NDFomGF_kg + (pabKH_kg - 2.8)/0.36) × 100
    SI ≥ 50 → Pansen-pH ≥ 6.15 erwartet
    """
    body = await request.json()
    ndfom_gf = float(body.get("andfom_gf_kg_day", 0))
    pabkh = float(body.get("pabkh_kg_day", 0))
    denom = ndfom_gf + (pabkh - 2.8) / 0.36
    si = ndfom_gf / denom * 100.0 if denom > 0 else None
    return JSONResponse(content={
        "strukturindex": round(si, 1) if si is not None else None,
        "ziel": ">= 50",
        "bewertung": (
            "OK – Pansen-pH >= 6.15 erwartet" if si is not None and si >= 50
            else ("KRITISCH – Pansen-pH < 6.15 erwartet" if si is not None else "nicht berechenbar")
        ),
        "formeln": {
            "SI": "NDFomGF_kg / (NDFomGF_kg + (pabKH_kg - 2.8)/0.36) × 100",
            "pabKH": "Stärke_kg + Zucker_kg - beständige_Stärke_kg",
            "quelle": "DLG-Information 01|2023, Rutzmoser et al. 2011",
        },
    })


@router.get("/dlg/info", summary="Info dlg")
async def dlg_info():
    """DLG-Futterdatenbank-Status: Anzahl Einträge, Quelle, Aktualität."""
    from datetime import datetime, timezone
    feeds = _get_feeds()
    json_path = _dlg_json_path()
    last_update: Optional[str] = None
    days_since_update: Optional[int] = None
    needs_update = False

    if json_path and os.path.isfile(json_path):
        mtime = os.path.getmtime(json_path)
        last_update = datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d")
        days_since_update = (datetime.now(tz=timezone.utc) - datetime.fromtimestamp(mtime, tz=timezone.utc)).days
        needs_update = days_since_update > 90

    is_fallback = len(feeds) <= 20
    return JSONResponse(content={
        "feed_count": len(feeds),
        "source": "fallback-13" if is_fallback else "DLG-FWT-2025-JSON",
        "is_fallback": is_fallback,
        "last_update": last_update,
        "days_since_update": days_since_update,
        "needs_update": needs_update,
        "update_interval_days": 90,
        "dlg_info_url": "https://www.dlg-ev.de/services/futterwerttabellen",
        "hint": (
            "Fallback-Datensatz aktiv (13 Einträge). Vollständige DLG-Futterwerttabelle "
            "(>160 Einträge) als JSON-Export in DLG_JSON_PATH ablegen."
            if is_fallback else
            (f"Datenbank aktuell – {days_since_update} Tage alt." if not needs_update else
             f"Datenbank {days_since_update} Tage alt – Aktualisierung empfohlen (alle 90 Tage).")
        ),
    })


@router.post("/dlg/refresh", summary="Refresh dlg")
async def dlg_refresh():
    """
    Leert den Feed-Cache und prüft ob neue DLG-Daten vorliegen.
    Der eigentliche Download erfolgt manuell: DLG-Futterwerttabellen als JSON in DLG_JSON_PATH ablegen.
    """
    global _FEEDS_CACHE
    _FEEDS_CACHE = None  # Cache invalidieren
    feeds = _get_feeds()   # Neu laden
    return JSONResponse(content={
        "refreshed": True,
        "feed_count": len(feeds),
        "source": "DLG-FWT-2025-JSON" if len(feeds) > 20 else "fallback-13",
        "message": f"Feed-Cache geleert. {len(feeds)} Futtermittel neu geladen.",
    })


@router.post("/compound-feed/upload", summary="Compound feed document hochladen")
async def upload_compound_feed_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "Dateiname fehlt")
    content = await file.read()
    text, source_type, extract_warnings = _extract_document_text(file.filename, content)
    parsed = _parse_compound_feed_text(text, file.filename, source_type)
    warnings = [*extract_warnings, *parsed.warnings]
    return JSONResponse(
        content={
            "parsed": {
                **parsed.model_dump(),
                "warnings": warnings,
            },
            "warnings": warnings,
        }
    )


@router.post("/feeds/from-grundfutter", summary="From grundfutter feed")
async def feed_from_grundfutter(request: Request):
    """
    Konvertiert eine GrundfutterAnalyse in ein LP-kompatibles Futtermittel-Dict.
    Body: GrundfutterAnalyse-Objekt (oder Array davon).
    Response: Feed-Dict-Array für die Optimizer-API (custom_feeds).
    """
    body = await request.json()
    if isinstance(body, list):
        analysen = body
    else:
        analysen = [body]

    result = []
    for gfa in analysen:
        feed = _gfa_to_feed(gfa)
        result.append({
            "id": feed["id"],
            "name": feed["name"],
            "group": feed["group"],
            "forage": feed["forage"],
            "dm_pct": round(feed["dm_frac"] * 100, 1),
            "price_eur_kgdm": feed["price"],
            "me_mj_kgdm": feed["me"],
            "sidp_g_kgdm": round(feed["sidp"], 1),
            "cp_g_kgdm": round(feed["cp"], 1),
            "andfom_g_kgdm": round(feed["ndf"], 1),
            "xl_g_kgdm": round(feed["xl"], 1),
            "rmd_gn_kgdm": feed["rmd"],
            "ca_g_kgdm": round(feed["ca"], 2),
            "p_g_kgdm": round(feed["p"], 2),
            # Vollständiges Feed-Dict für Optimizer-Übergabe
            "_optimizer_feed": feed,
        })
    return JSONResponse(content=result)
