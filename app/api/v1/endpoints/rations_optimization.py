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
import math
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import APIRouter, File, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agrar", "rations-optimization"])

RATIONS_TIMEOUT = 30.0

# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def _rations_base_url() -> Optional[str]:
    return getattr(settings, "RATIONS_OPTIMIZATION_URL", None) or None


def _rations_api_key() -> str:
    return getattr(settings, "RATIONS_OPTIMIZATION_API_KEY", "") or "dev-api-key-change-in-production"


def _dlg_json_path() -> Optional[str]:
    configured = getattr(settings, "RATIONS_DLG_DATA_PATH", None)
    if configured:
        return configured
    # Bundled DLG-Futterwerttabellen 2025 (offizieller DLG-JSON-Export)
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in ["DLG_FWT_WK_2025.json", "dlg_feeds_raw.json"]:
        bundled = os.path.normpath(os.path.join(here, "..", "..", "..", "data", candidate))
        if os.path.isfile(bundled):
            return bundled
    return None


def _tenant_from_request(request: Request, x_tenant_id: Optional[str]) -> Optional[str]:
    if x_tenant_id:
        return x_tenant_id
    return (
        request.headers.get("x-tenant-id")
        or request.headers.get("X-Tenant-Id")
        or request.headers.get("X-Tenant-ID")
    )


# ---------------------------------------------------------------------------
# External proxy
# ---------------------------------------------------------------------------

async def _proxy_request(
    method: str,
    path: str,
    tenant_id: Optional[str] = None,
    json_body: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    base_url = _rations_base_url()
    if not base_url:
        raise HTTPException(
            status_code=503,
            detail="Rationsoptimierungs-Service ist nicht konfiguriert (RATIONS_OPTIMIZATION_URL fehlt)",
        )
    url = f"{base_url.rstrip('/')}{path}"
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "X-API-Key": _rations_api_key(),
    }
    if tenant_id:
        headers["X-Tenant-Id"] = tenant_id

    async with httpx.AsyncClient(timeout=RATIONS_TIMEOUT) as client:
        try:
            if method.upper() == "GET":
                resp = await client.get(url, headers=headers, params=params)
            elif method.upper() == "POST":
                resp = await client.post(url, headers=headers, json=json_body or {}, params=params)
            else:
                raise HTTPException(status_code=405, detail="Methode nicht unterstützt")
            try:
                body = resp.json()
            except Exception:
                body = {"detail": resp.text}
            return JSONResponse(status_code=resp.status_code, content=body)
        except httpx.ConnectError as exc:
            logger.warning("Rationsoptimierung nicht erreichbar: %s", exc)
            raise HTTPException(status_code=503, detail="Rationsoptimierungs-Service ist nicht erreichbar")
        except httpx.TimeoutException:
            raise HTTPException(status_code=504, detail="Rationsoptimierungs-Service hat nicht rechtzeitig geantwortet")


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
_PRICE_ESTIMATES: Dict[str, float] = {
    "Maissilage": 0.045,
    "Grassilage": 0.060,
    "Heu": 0.130,
    "Luzerne": 0.080,
    "Melasseschnitzel": 0.195,
    "Rübenblatt": 0.040,
    "Körnermais": 0.210,
    "Weizen": 0.220,
    "Gerste": 0.200,
    "Roggen": 0.190,
    "Triticale": 0.200,
    "Hafer": 0.210,
    "Raps": 0.270,
    "Soja": 0.450,
    "Biertreber": 0.120,
    "Trester": 0.090,
    "Mineralfutter": 1.600,
    "Harnstoff": 0.600,
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
    if "grassilage" in n or ("gras" in n and "siliert" in n):
        return 12.0
    if "ganzpflanzensil" in n or "gps" in n:
        return 8.0
    if "weide" in n or "frischgras" in n or ("gras" in n and "frisch" in n):
        # Fuer Weide-/PMR-Systeme muss deutlich mehr Frischgrasaufnahme moeglich sein.
        # Die TMR-spezifische Deckelung erfolgt spaeter im Solver nur fuer feeding_type=TMR.
        return 14.0

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
]


def _with_special_supplements(feeds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    existing = {feed["id"] for feed in feeds}
    merged = list(feeds)
    for supplement in _SPECIAL_SUPPLEMENTS:
        if supplement["id"] not in existing:
            merged.append(dict(supplement))
    return merged


def _get_feeds() -> List[Dict[str, Any]]:
    global _FEEDS_CACHE
    if _FEEDS_CACHE is not None:
        return _with_special_supplements(_FEEDS_CACHE)

    json_path = _dlg_json_path()
    if json_path and os.path.isfile(json_path):
        try:
            _FEEDS_CACHE = _load_dlg_feeds_from_json(json_path)
            logger.info("DLG-Futterdatenbank geladen: %d Einträge aus %s", len(_FEEDS_CACHE), json_path)
            return _with_special_supplements(_FEEDS_CACHE)
        except Exception as exc:
            logger.warning("DLG JSON konnte nicht geladen werden: %s – verwende Fallback", exc)

    _FEEDS_CACHE = _FEEDS_FALLBACK
    logger.info("DLG-Futterdatenbank: Fallback mit %d Einträgen", len(_FEEDS_CACHE))
    return _with_special_supplements(_FEEDS_CACHE)


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


def _gfe_requirements(profile: Dict[str, Any]) -> _CowReq:
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
    """
    bw = float(profile.get("body_weight_kg") or 650)
    milk = float(profile.get("milk_kg_day") or 0)
    fat_pct = float(profile.get("milk_fat_pct") or 4.0)
    prot_pct = float(profile.get("milk_protein_pct") or 3.4)

    bw75 = bw ** 0.75

    # --- NEL (für Referenzausgabe) ---
    nel_maint = 0.308 * bw75            # inkl. 5% Aktivitätszuschlag
    nel_milk = (0.38 * fat_pct + 0.21 * prot_pct + 0.95) * milk if milk > 0 else 0.0
    nel_total = nel_maint + nel_milk

    # --- ME (GfE 2023 dreistufig) ---
    me_maint = nel_maint / 0.73         # k_m = 0.73 für laktierende Kühe
    me_milk = nel_milk / 0.62          # k_l = 0.62 für Milch
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

    # --- DMI (Gruber 2004 vereinfacht) ---
    dmi_target = 0.025 * bw + 0.15 * milk if milk > 0 else 0.025 * bw
    dmi_target = max(dmi_target, 8.0)

    # Physiologische Obergrenze nach DLG Information 01|25 Tabelle 14:
    # Absolute Maximale TM-Aufnahme: 28,5 kg/Tag für Elite-Hochleistungskühe (>14.000 kg Herde).
    # Normalkühe 670 kg / 38 kg Milch: Zielwert ~22,5 kg, praktisches Maximum ~25 kg.
    # dmi_max darf NIEMALS durch LP-Relaxation überschritten werden.
    _DMI_ABS_MAX_KG = 28.5  # DLG Tab. 14 – hartes physiologisches Limit
    dmi_max = min(dmi_target * 1.10, _DMI_ABS_MAX_KG)

    # --- aNDFom-Minimum: 300 g/kg TM × DMI (DLG-Empfehlung Pansenstabilität) ---
    ndf_min = 300.0 * dmi_target

    # --- Mengenelemente (GfE 2023 / GfE-Workshop 2023) ---
    ca_min = 0.031 * bw75 + 1.22 * milk
    p_min  = 0.014 * bw75 + 0.90 * milk
    # GfE-Workshop 2023: Mg-Bedarf um 25–40% erhöht gegenüber GfE 2001
    # Erhaltung: 0.048 g/kg LM (hochrechnend aus DLG Tab.12 inkl. +30% Zuschlag)
    # Leistung: 0.10 g/kg Milch (GfE 2023 Workshop Präsentation)
    mg_min = (0.048 * bw + 0.10 * milk) if milk > 0 else 0.048 * bw
    na_min = 1.5 * dmi_target   # ~1.5 g/kg TM
    # K/Mg-Antagonismus (GfE-Workshop 2023): max. K-Versorgung 28 g/kg TM
    k_max  = 28.0 * dmi_target

    return _CowReq(
        me_mj=me_total,
        sidp_g=sidp_total,
        nel_mj=nel_total,
        nxp_g=nxp_total,
        dmi_min_kg=dmi_target * 0.90,
        dmi_max_kg=dmi_max,
        dmi_target_kg=dmi_target,
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
    """Minimale peNDF-Dichte [g/kg TM] aus Lookup-Tabelle (GfE-Workshop 2023)."""
    s_bands = _PENDF_TABLE["staerke_bands"]
    d_bands = _PENDF_TABLE["dmi_bands"]
    matrix  = _PENDF_TABLE["matrix"]
    s_idx = next((i for i, b in enumerate(s_bands) if staerke_density < b), len(s_bands) - 1)
    d_idx = next((i for i, b in enumerate(d_bands) if dmi_kg < b), len(d_bands) - 1)
    return float(matrix[s_idx][d_idx])


def _ph_predict(pendf_density: float, staerke_density: float, dmi_kg: float) -> float:
    """
    Pansen-pH-Vorhersage nach GfE-Workshop 2023 (Zebeli/Schwarz-Formel):
      pH = 6.237 + 0.03332×peNDF - 0.00055×peNDF² - 0.01091×Stärke - 0.0089×TM

    peNDF [g/kg TM], Stärke [g/kg TM], TM-Aufnahme [kg/d].
    Gültig für pH 5.8–6.8, peNDF 60–250 g/kg TM, Stärke 50–350 g/kg TM.
    """
    p = pendf_density
    s = staerke_density
    t = dmi_kg
    ph = 6.237 + 0.03332 * p - 0.00055 * p * p - 0.01091 * s - 0.0089 * t
    return round(max(5.5, min(7.0, ph)), 2)


def _feed_pendf_factor(feed: Dict[str, Any]) -> float:
    pendf_map: Dict[str, float] = {
        "Grundfutter/Grobfutter": 0.90,
        "Grundfutter/Saftfutter": 0.85,
        "Grundfutter/Betrieb": 0.90,
        "Kraftfutter/Trocken": 0.25,
        "Kraftfutter/Feucht": 0.30,
        "Zusatzstoffe": 0.0,
        "Sonstige": 0.30,
    }
    base = pendf_map.get(feed.get("group", "Sonstige"), 0.30)
    name_l = feed.get("name", "").lower()
    if "heu" in name_l or "stroh" in name_l:
        return 1.0
    return base


def _welfare_objective_coeff(feed: Dict[str, Any]) -> float:
    pabkh = float(feed.get("st") or 0.0) + float(feed.get("zu") or 0.0) - float(feed.get("bst") or 0.0)
    pendf_reward = min((float(feed.get("ndf") or 0.0) * _feed_pendf_factor(feed)) / 1000.0, 0.25)
    score = 1.0
    if feed.get("forage"):
        score -= 0.35
    score -= pendf_reward
    score += max(pabkh - 140.0, 0.0) / 400.0
    score += max(float(feed.get("xl") or 0.0) - 30.0, 0.0) / 120.0
    score += max(float(feed.get("cp") or 0.0) - 155.0, 0.0) / 300.0
    score += max(float(feed.get("k") or 0.0) - 25.0, 0.0) / 400.0
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
    for feed in feeds:
        name_l = feed.get("name", "").lower()
        if "weide" in name_l or "frischgras" in name_l or ("gras" in name_l and "frisch" in name_l):
            return True
    return False


def _is_pasture_pmr_system(feeds: List[Dict[str, Any]], profile: Optional[Dict[str, Any]]) -> bool:
    mode = _normalize_feeding_type((profile or {}).get("feeding_type"))
    if mode == "PMR+Weide":
        return True
    if mode != "PMR":
        return False
    return _has_pasture_forage(feeds)


def _run_lp(
    req: _CowReq,
    feeds: List[Dict[str, Any]],
    profile: Optional[Dict[str, Any]] = None,
    runtime_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Minimiere Futterkosten (€/d) via scipy.optimize.linprog (LP, HiGHS-Solver).

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
    from scipy.optimize import linprog  # type: ignore[import]

    n = len(feeds)
    prices = [f["price"] for f in feeds]
    feeding_type = _normalize_feeding_type((profile or {}).get("feeding_type"))
    pasture_pmr = _is_pasture_pmr_system(feeds, profile)
    andfom_gf_min = 180.0 if pasture_pmr else 200.0
    pabkh_max = 225.0 if pasture_pmr else 210.0
    xl_max = 42.0 if pasture_pmr else 40.0
    cp_max = 185.0 if pasture_pmr else 165.0
    k_max = req.k_max_g * (1.15 if pasture_pmr else 1.0)

    A_ub: List[List[float]] = []
    b_ub: List[float] = []

    def _geq(col_vals: List[float], rhs: float) -> None:
        A_ub.append([-v for v in col_vals])
        b_ub.append(-rhs)

    def _leq(col_vals: List[float], rhs: float) -> None:
        A_ub.append(col_vals)
        b_ub.append(rhs)

    ones         = [1.0] * n
    me_per_kg    = [f["me"]   for f in feeds]
    sidp_per_kg  = [f["sidp"] for f in feeds]
    ndf_per_kg   = [f["ndf"]  for f in feeds]
    ca_per_kg    = [f["ca"]   for f in feeds]
    p_per_kg     = [f["p"]    for f in feeds]
    na_per_kg    = [f["na"]   for f in feeds]
    mg_per_kg    = [f["mg"]   for f in feeds]
    xl_per_kg    = [f["xl"]   for f in feeds]

    # Pansenabbaubare KH: pabKH = ST + ZU - bST (g/kg TM)
    pabkh_per_kg = [f["st"] + f["zu"] - f["bst"] for f in feeds]

    # Energie und Protein
    _geq(me_per_kg,   req.me_mj)           # ME ≥ Bedarf
    _geq(sidp_per_kg, req.sidp_g)          # sidP ≥ Bedarf

    # Faserversorgung
    _geq(ndf_per_kg,  req.ndf_min_g)       # aNDFom ≥ Minimum gesamt

    # aNDFomGF-Dichte ≥ 200 g/kg TM (linearisiert):
    #   sum_i(amounts_i × (aNDFom_i × is_forage_i - 200)) ≥ 0
    andfom_gf_density = [
        f["ndf"] - andfom_gf_min if f.get("forage") else -andfom_gf_min
        for f in feeds
    ]
    _geq(andfom_gf_density, 0.0)

    # pabKH-Dichte ≤ 210 g/kg TM (linearisiert):
    #   sum_i(amounts_i × (pabKH_i - 210)) ≤ 0
    pabkh_density = [v - pabkh_max for v in pabkh_per_kg]
    _leq(pabkh_density, 0.0)

    # XL-Dichte ≤ 40 g/kg TM (Fettlimit Milchkuh ohne pansengeschütztes Fett)
    xl_density = [v - xl_max for v in xl_per_kg]
    _leq(xl_density, 0.0)

    # CP-Dichte ≤ 165 g/kg TM (DLG 01|25 Tab. 14 Optimalbereich 135-165 g/kg TM – verhindert überhöhten RNB/RMD)
    cp_per_kg = [f["cp"] for f in feeds]
    cp_density = [v - cp_max for v in cp_per_kg]
    _leq(cp_density, 0.0)

    # RMD-Dichte (DLG 01|25: Ziel -1,5 bis 0 g N/kg TM, Toleranzbereich bis +1,5).
    # In Weidesystemen ist ein strukturell hoeherer N-Ueberschuss real (DLG-Merkblatt 417):
    # Junges Gras/Weide hat laut DLG-Futterwerttabelle RMD-Werte von 7-9 g N/kg TM,
    # Grassilage 1.-3. Schnitt 5-8 g N/kg TM. Das ist biologisch erklaerbar und
    # kein Fuetterungsfehler. Bei hohem Weideanteil ist die LP-Obergrenze daher strukturell
    # nicht erreichbar, wenn man sich an der Stallnorm orientiert. Deshalb wird die
    # Obergrenze je Fuetterungsmodus gestaffelt:
    #   TMR          -> 1.5 g N/kg TM  (unveraendert, Stallfuetterung)
    #   PMR          -> 3.0 g N/kg TM  (moderat weicher, Kraftfutter leistungsabhaengig)
    #   PMR+Weide    -> 8.0 g N/kg TM  (DLG 417: Weidesysteme, Jungweide RMD typ. 7-9)
    # Feeds ohne rmd-Wert werden mit 0 angesetzt (konservativ; zieht LP zu low-rmd-Futtermitteln).
    if feeding_type == "PMR+Weide":
        rmd_max = 8.0
    elif feeding_type == "PMR":
        rmd_max = 3.0
    else:
        rmd_max = 1.5
    rmd_per_kg = [float(f.get("rmd") or 0.0) for f in feeds]
    rmd_density = [v - rmd_max for v in rmd_per_kg]
    _leq(rmd_density, 0.0)

    # ME-Dichte ≤ 12.5 MJ/kg TM (DLG 01|25 Tab. 14 – Energiedichte-Obergrenze Hochleistung)
    me_density_max = [v - 12.5 for v in me_per_kg]
    _leq(me_density_max, 0.0)

    # ME absolut ≤ Bedarf × 1.12 (max. 12% Überversorgung – DLG Toleranz 10%, LP-Spielraum +2%)
    _leq(me_per_kg, req.me_mj * 1.12)

    # aNDFom-Dichte ≤ 420 g/kg TM (DLG 01|25 Tab. 14 – verhindert Überversorgung mit Rohfaser)
    andfom_density_max = [v - 420.0 for v in ndf_per_kg]
    _leq(andfom_density_max, 0.0)

    # Mengenelemente
    _geq(ca_per_kg, req.ca_min_g)
    _geq(p_per_kg,  req.p_min_g)
    _geq(na_per_kg, req.na_min_g)
    _geq(mg_per_kg, req.mg_min_g)

    # K/Mg-Antagonismus: max. Kalium ≤ 28 g/kg TM × DMI (GfE-Workshop 2023)
    k_per_kg = [f.get("k", 0.0) for f in feeds]
    _leq(k_per_kg, k_max)

    # Saftfutter-Gruppengrenze: max. 6 kg TM/d als Nassnebenprodukte (gesamt)
    # Verhindert: Labmagenverlagerung, peNDF-Absturz, übermäßige Feuchtfutter-Dominanz.
    # Grundfutter-Saftfutter (Biertreber, Schlempe, Kartoffelpülpe etc.) ist forage=False
    # bei is_forage=False und group "Grundfutter/Saftfutter" → Saftfutter-Gruppe
    saftfutter_mask = [
        1.0 if (
            "saftfutter" in f.get("group", "").lower() or
            "saftfutter" in f.get("futterart", "").lower()
        ) else 0.0
        for f in feeds
    ]
    _leq(saftfutter_mask, 6.0)

    # Frischgras/Weide nur in TMR strikt begrenzen; PMR/Weidesysteme duerfen das gezielt nutzen.
    if feeding_type == "TMR":
        weide_mask = [
            1.0 if ("weide" in f.get("name", "").lower() or "frischgras" in f.get("name", "").lower()) else 0.0
            for f in feeds
        ]
        _leq(weide_mask, 4.0)

    # PMR+Weide: Weidemineral/Mg-Supplement als fester Sicherheitsbaustein
    # DLG-Merkblatt 417 / 443 / DLG-Information 01|2023 begruenden eine gezielte
    # Mg-/Na-Absicherung bei Frischgras/Weide (K/Mg-Antagonismus, Grastetanie-Risiko).
    if pasture_pmr:
        mg_supplement_mask = [
            1.0 if feed.get("_special") == "pasture_mg" else 0.0
            for feed in feeds
        ]
        if any(mg_supplement_mask):
            # mindestens 0,05 kg TM/d (~ 50 g Frischmasse Mineralfutter) muss in die Ration
            _geq(mg_supplement_mask, 0.05)

    # Mindest-Grobfutter-Anteil: ≥ 40% der DMI als echtes Grobfutter (peNDF-Basis)
    # Verhindert Kraftfutter-Dominanz / NPN-Überschüsse
    grobfutter_neg = [-1.0 if f.get("forage") and "grobfutter" in f.get("group", "").lower() else 0.4 for f in feeds]
    _leq(grobfutter_neg, 0.0)

    # DMI
    _geq(ones, req.dmi_min_kg)
    _leq(ones, req.dmi_max_kg)

    bounds = [(f["min_kg"], f["max_kg"]) for f in feeds]

    def _solve(objective: List[float], A_local: List[List[float]], b_local: List[float]):
        return linprog(
            c=objective,
            A_ub=A_local,
            b_ub=b_local,
            bounds=bounds,
            method="highs",
            options={"disp": False},
        )

    stage1_objective = [_welfare_objective_coeff(feed) for feed in feeds]
    result = _solve(stage1_objective, A_ub, b_ub)

    # Constraint-Index-Karte (entspricht der Reihenfolge der _geq/_leq-Aufrufe):
    #   0: ME ≥ Bedarf
    #   1: sidP ≥ Bedarf
    #   2: aNDFom ≥ Minimum gesamt
    #   3: aNDFomGF-Dichte ≥ 200 g/kg TM
    #   4: pabKH-Dichte ≤ 210 g/kg TM
    #   5: XL-Dichte ≤ 40 g/kg TM        ← weiche Grenze, zuerst relaxieren
    #   6: CP-Dichte ≤ 165 g/kg TM        ← DLG 01|25 Tab.14 Optimal-Obergrenze
    #   7: RMD-Dichte ≤ 1.5 g N/kg TM    ← DLG 01|25 Toleranzbereich
    #   8: ME-Dichte ≤ 12.5 MJ/kg TM     ← DLG 01|25 Tab.14, Energiedichte-Ceiling
    #   9: ME absolut ≤ Bedarf × 1.15    ← max. 15% Überversorgung
    #  10: aNDFom-Dichte ≤ 420 g/kg TM  ← DLG 01|25 Tab.14, Faserdeckel
    #  11..14: Ca, P, Na, Mg
    #  15: DMI ≥ Minimum
    #  16: DMI ≤ Maximum                 ← NIEMALS relaxieren (physiologisches Limit)
    _IDX_XL = 5
    _IDX_ANDFOM_GF = 3
    _IDX_RMD = 7      # RMD-Dichte (weich – relaxierbar wenn zu eng)
    _IDX_ME_ABS = 9   # ME absolut-Obergrenze (weich – nach XL relaxierbar)

    if result.status not in (0, 1):
        # Relaxation 1: XL-Dichte auf 60 g/kg TM lockern (z.B. wenn Biertreber/DDGS im Plan)
        # DMI-Obergrenze bleibt UNVERÄNDERT – physiologisches Limit nach DLG 01|25.
        xl_density_r = [v - (60.0 if not pasture_pmr else 48.0) for v in xl_per_kg]
        A_ub_r_full = list(A_ub)
        A_ub_r_full[_IDX_XL] = xl_density_r
        b_ub_r = b_ub.copy()
        b_ub_r[_IDX_XL] = 0.0          # XL ≤ 60 g/kg TM: linearisiertes RHS bleibt 0
        result = _solve(stage1_objective, A_ub_r_full, b_ub_r)

    if result.status not in (0, 1):
        # Relaxation 2: RMD-Dichte um eine Stufe weicher als die Basis-Grenze (rmd_max).
        # Basis: TMR 1.5 / PMR 3.0 / PMR+Weide 8.0 g N/kg TM.
        # Relax: TMR 3.0 / PMR 5.0 / PMR+Weide 12.0 g N/kg TM
        # (DLG 417: Weidesysteme toleriert strukturell hoehere N-Ueberschuesse bei Weide;
        # ueber Jungweide-Spitze wird ueber den Harnstoff-Indikator kommuniziert).
        rmd_relax = rmd_max + (4.0 if feeding_type == "PMR+Weide" else 1.5)
        b_ub_r2a = b_ub.copy()
        b_ub_r2a[_IDX_RMD] = 0.0
        A_ub_r2a = list(A_ub)
        A_ub_r2a[_IDX_RMD] = [v - rmd_relax for v in rmd_per_kg]
        result = _solve(stage1_objective, A_ub_r2a, b_ub_r2a)

    if result.status not in (0, 1):
        # Relaxation 3: aNDFomGF-Dichte deaktivieren
        A_ub_r = [row for i, row in enumerate(A_ub) if i != _IDX_ANDFOM_GF]
        b_ub_r = [v for i, v in enumerate(b_ub) if i != _IDX_ANDFOM_GF]
        result = _solve(stage1_objective, A_ub_r, b_ub_r)

    if result.status not in (0, 1):
        # Relaxation 4: sidP auf 85% des Bedarfs reduzieren (Proteinverfügbarkeit-Kompromiss)
        # Constraint-Index 1 = sidP (zweite _geq nach ME)
        A_ub_r2 = list(A_ub_r)
        b_ub_r2 = list(b_ub_r)
        for idx, row in enumerate(A_ub_r2):
            if all(abs(row[j] + (feeds[j]["sidp"] or 0)) < 0.01 for j in range(n)):
                b_ub_r2[idx] = -req.sidp_g * 0.85
                break
        result = _solve(stage1_objective, A_ub_r2, b_ub_r2)

    infeasibility_hint = None
    if result.status not in (0, 1):
        infeasibility_hint = _diagnose_infeasibility(req, feeds, profile)
    else:
        stage1_amounts = [_f(v) for v in result.x]
        stage1_total_dmi = sum(stage1_amounts)
        if stage1_total_dmi > 0:
            stage1_forage_pct = (
                sum(stage1_amounts[i] for i in range(n) if feeds[i].get("forage")) / stage1_total_dmi * 100.0
            )
            stage1_pendf_density = sum(
                stage1_amounts[i] * feeds[i]["ndf"] * _feed_pendf_factor(feeds[i])
                for i in range(n)
            ) / stage1_total_dmi
            stage1_starch_density = sum(stage1_amounts[i] * feeds[i]["st"] for i in range(n)) / stage1_total_dmi
            stage1_pabkh_density = sum(stage1_amounts[i] * pabkh_per_kg[i] for i in range(n)) / stage1_total_dmi
            stage1_xl_density = sum(stage1_amounts[i] * xl_per_kg[i] for i in range(n)) / stage1_total_dmi
            stage1_cp_density = sum(stage1_amounts[i] * cp_per_kg[i] for i in range(n)) / stage1_total_dmi

            A_stage2 = list(A_ub)
            b_stage2 = list(b_ub)

            forage_floor = max(60.0 if pasture_pmr else 55.0, stage1_forage_pct - 2.0)
            A_stage2.append([
                forage_floor - 100.0 if feed.get("forage") else forage_floor
                for feed in feeds
            ])
            b_stage2.append(0.0)

            pendf_floor = max(_pendf_minimum(stage1_starch_density, stage1_total_dmi), stage1_pendf_density - 5.0)
            A_stage2.append([
                pendf_floor - (feed["ndf"] * _feed_pendf_factor(feed))
                for feed in feeds
            ])
            b_stage2.append(0.0)

            pabkh_ceiling = min(pabkh_max, stage1_pabkh_density + 10.0)
            A_stage2.append([value - pabkh_ceiling for value in pabkh_per_kg])
            b_stage2.append(0.0)

            xl_ceiling = min(xl_max, stage1_xl_density + 2.0)
            A_stage2.append([value - xl_ceiling for value in xl_per_kg])
            b_stage2.append(0.0)

            cp_ceiling = min(cp_max, stage1_cp_density + 5.0)
            A_stage2.append([value - cp_ceiling for value in cp_per_kg])
            b_stage2.append(0.0)

            cost_result = _solve(prices, A_stage2, b_stage2)
            if cost_result.status == 0:
                result = cost_result

    return {
        "scipy_result": result,
        "feeds": feeds,
        "_relaxed": result.status == 0,
        "_infeasibility_hint": infeasibility_hint,
    }


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

    if not gaps:
        gaps.append("Unbekannte Infeasibility – möglicherweise widersprüchliche Futter-Mengengrenzen.")
        suggestions.append({
            "feed": "Universalausgleich: Laktations-TMR-Konzentrat",
            "action": (
                "Fertig-Laktationsfutter (z.B. 18% XP, 7,2 MJ NEL/kg) in Ration aufnehmen "
                "und Einzelkomponenten-Grenzen prüfen."
            ),
        })

    return {"gaps": gaps, "suggestions": suggestions}


# ---------------------------------------------------------------------------
# Response Builder
# ---------------------------------------------------------------------------

def _f(v: Any) -> float:
    return float(v)


def _milk_requirement_factors(profile: Dict[str, Any]) -> Tuple[float, float, float, float]:
    """Return maintenance ME plus milk coefficients for ME and sidP.

    The milk coefficients follow the same simplified GfE basis that `_gfe_requirements`
    uses for the main requirement calculation, so the display stays consistent with the
    optimizer contract.
    """
    bw = float(profile.get("body_weight_kg") or 650)
    fat_pct = float(profile.get("milk_fat_pct") or 4.0)
    prot_pct = float(profile.get("milk_protein_pct") or 3.4)
    bw75 = bw ** 0.75
    me_maint = (0.308 * bw75) / 0.73
    me_per_kg_milk = (0.38 * fat_pct + 0.21 * prot_pct + 0.95) / 0.62
    sidp_maint = (3.47 * bw75) * 0.95
    sidp_per_kg_milk = 52.0 * 0.95
    return me_maint, me_per_kg_milk, sidp_maint, sidp_per_kg_milk


def _milk_from_supply(
    me_sup: float,
    sidp_sup: float,
    profile: Dict[str, Any],
) -> Dict[str, float]:
    me_maint, me_per_kg_milk, sidp_maint, sidp_per_kg_milk = _milk_requirement_factors(profile)
    milk_from_energy = max(0.0, (me_sup - me_maint) / me_per_kg_milk) if me_per_kg_milk > 0 else 0.0
    milk_from_protein = max(0.0, (sidp_sup - sidp_maint) / sidp_per_kg_milk) if sidp_per_kg_milk > 0 else 0.0
    return {
        "milk_from_energy_kg": round(milk_from_energy, 1),
        "milk_from_protein_kg": round(milk_from_protein, 1),
        "limiting_milk_kg": round(min(milk_from_energy, milk_from_protein), 1),
    }


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
# FAN-MODE-V1: Constraint-Klassifikation (Spec §5.2.2)
# ---------------------------------------------------------------------------

# Mapping: Constraint-Name (wie in _cr() gebildet) -> (Kategorie, Klasse, Normalisierungsbreite)
# Klasse None = hart (nicht relaxierbar); sonst "A" | "B" | "C".
# Normalisierungsbasis richtet sich nach Spec §5.2 und ist als dimensionslose Toleranzbreite zu verstehen.
_CONSTRAINT_CLASSIFICATION: Dict[str, Tuple[str, Optional[str], str, float]] = {
    # name                  -> (hart_or_weich, Klasse, normalisierungs_einheit, halbbreite)
    "ME (MJ/d)":              ("hart",  None, "MJ/d",       0.0),   # hart bei Unterdeckung (>= target ueber _cr)
    "sidP (g/d)":             ("hart",  None, "g/d",        0.0),
    "TM-Aufnahme (kg/d)":     ("hart",  None, "kg/d",       0.0),
    "aNDFom (g/d)":           ("weich", "B",  "g/d",        0.0),   # Struktur
    "aNDFomGF (g/kg TM)":     ("weich", "B",  "g/kg TM",   30.0),
    "pabKH (g/kg TM)":        ("weich", "B",  "g/kg TM",   20.0),
    "XL Rohfett (g/kg TM)":   ("weich", "C",  "g/kg TM",    6.0),
    "peNDF (g/kg TM)":        ("weich", "B",  "g/kg TM",   15.0),
    "Magnesium (g/d)":        ("hart",  None, "g/d",        0.0),
    "Calcium (g/d)":          ("hart",  None, "g/d",        0.0),
    "Phosphor (g/d)":         ("hart",  None, "g/d",        0.0),
    "Grundfutteranteil (%TM)":("weich", "B",  "%TM",        5.0),
}


def _derive_constraint_status_from_report(
    constraint_report: List[Dict[str, Any]],
    relaxation_policy: str,
) -> List[Dict[str, Any]]:
    """Leitet aus dem bestehenden constraint_report einen FAN-V1-konformen Status ab.

    Slice 1: der Solver ist noch nicht dreistufig umgestellt, deshalb ist penalty_cost
    in der Regel 0. Spaetestens in Slice 2/6 werden hier echte Strafkosten befuellt.
    """
    factor = _RELAXATION_FACTORS.get(relaxation_policy, 1.0)
    out: List[Dict[str, Any]] = []
    for item in constraint_report:
        name = item.get("name", "")
        kind, klass, unit, halfwidth = _CONSTRAINT_CLASSIFICATION.get(
            name, ("weich", "C", item.get("unit", ""), 0.0)
        )
        actual = float(item.get("actual") or 0.0)
        target = float(item.get("target") or 0.0)
        deviation_norm = 0.0
        penalty = 0.0
        status = "ok" if item.get("fulfilled") else "violated"
        if halfwidth > 0 and target > 0:
            deviation_norm = abs(actual - target) / halfwidth
        if kind == "weich" and klass:
            klass_w = _PENALTY_CLASS_WEIGHTS.get(klass, 1.0)
            penalty = _PENALTY_BASE_COST * klass_w * factor * deviation_norm
        out.append({
            "name": name,
            "kind": kind,
            "class": klass,
            "unit": unit,
            "target": target,
            "actual": actual,
            "difference": item.get("difference"),
            "fulfilled": bool(item.get("fulfilled")),
            "deviation_norm": round(deviation_norm, 3),
            "penalty_cost": round(penalty, 4),
            "status": status,
            "source": "constraint_report",
        })
    return out


def _build_response(
    lp_out: Dict[str, Any],
    req: _CowReq,
    profile: Dict[str, Any],
) -> Dict[str, Any]:
    result = lp_out["scipy_result"]
    feeds = lp_out["feeds"]
    runtime_options = lp_out.get("_runtime_options") or _resolve_runtime_options(profile)
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
        return {
            "status": "infeasible",
            "ration_items": [],
            "nutrient_supply": {},
            "constraint_report": [],
            "constraint_status": constraint_status_from_lp,
            "dlg_indicators": {},
            "warnings": warnings,
            "feed_suggestions": hint.get("suggestions", []),
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

    amounts = [_f(v) for v in result.x]
    total_cost = sum(amounts[i] * feeds[i]["price"] for i in range(len(feeds)))
    total_dmi = sum(amounts)

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
            # FAN-MODE-V1: Herkunft der FAN-abhaengigen Koeffizienten (Spec §8.2.3).
            # In Slice 1 noch komplett "fallback"; Slice 3 ersetzt dies durch den Katalog.
            "fan_slope_source": feed.get("_fan_slope_source", "fallback"),
        })

    # --- Nährstoffversorgung ---
    def _sum(key: str) -> float:
        return sum(amounts[i] * float(feeds[i].get(key) or 0) for i in range(len(feeds)))

    me_sup    = _sum("me")
    sidp_sup  = _sum("sidp")
    cp_sup    = _sum("cp")
    ndf_sup   = _sum("ndf")
    adf_sup   = _sum("adf")
    st_sup    = _sum("st")
    bst_sup   = _sum("bst")
    zu_sup    = _sum("zu")
    xl_sup    = _sum("xl")
    ca_sup    = _sum("ca")
    p_sup     = _sum("p")
    na_sup    = _sum("na")
    mg_sup    = _sum("mg")
    k_sup     = _sum("k")
    sidlys_sup = _sum("sidlys")
    sidmet_sup = _sum("sidmet")

    pendf_sup = sum(amounts[i] * feeds[i]["ndf"] * _feed_pendf_factor(feeds[i]) for i in range(len(feeds)))
    pendf_density = pendf_sup / total_dmi if total_dmi > 0 else 0.0

    # Stärke-Dichte
    st_density = st_sup / total_dmi if total_dmi > 0 else 0.0
    pendf_min_val = _pendf_minimum(st_density, total_dmi)

    # Pansen-pH-Vorhersage (GfE-Workshop 2023 Zebeli/Schwarz-Formel)
    ph_predicted = _ph_predict(pendf_density, st_density, total_dmi)

    # Grundfutter-Anteile
    forage_kg = sum(amounts[i] for i in range(len(feeds)) if feeds[i].get("forage"))
    concentrate_kg = max(total_dmi - forage_kg, 0.0)
    forage_ndf = sum(amounts[i] * feeds[i]["ndf"] for i in range(len(feeds)) if feeds[i].get("forage"))
    forage_share_pct = forage_kg / total_dmi * 100.0 if total_dmi > 0 else 0.0
    forage_me_sup = sum(amounts[i] * feeds[i]["me"] for i in range(len(feeds)) if feeds[i].get("forage"))
    forage_sidp_sup = sum(amounts[i] * feeds[i]["sidp"] for i in range(len(feeds)) if feeds[i].get("forage"))
    feeding_type = _normalize_feeding_type(profile.get("feeding_type"))
    pasture_pmr = _is_pasture_pmr_system(feeds, profile)
    andfom_gf_target = 180.0 if pasture_pmr else 200.0
    pabkh_target = 225.0 if pasture_pmr else 210.0
    xl_target = 42.0 if pasture_pmr else 40.0
    forage_share_target = 60.0 if pasture_pmr else 55.0
    displacement_factor = _concentrate_displacement_factor(feeding_type, concentrate_kg)
    forage_displacement_dmi = concentrate_kg * displacement_factor
    forage_only_milk = _milk_from_supply(forage_me_sup, forage_sidp_sup, profile)
    supplemented_milk = _milk_from_supply(me_sup, sidp_sup, profile)

    # --- Weide-/Grobfutter-spezifische Leistungs- und Risiko-Auswertung (DLG 417/443) ---
    def _is_pasture_feed(feed: Dict[str, Any]) -> bool:
        name_l = feed.get("name", "").lower()
        return "weide" in name_l or "frischgras" in name_l or ("gras" in name_l and "frisch" in name_l)

    def _is_grass_silage(feed: Dict[str, Any]) -> bool:
        name_l = feed.get("name", "").lower()
        return "grassilage" in name_l or ("gras" in name_l and "siliert" in name_l)

    pasture_kg = sum(amounts[i] for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_me_sup = sum(amounts[i] * feeds[i]["me"] for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_sidp_sup = sum(amounts[i] * feeds[i]["sidp"] for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_k_sup = sum(amounts[i] * float(feeds[i].get("k") or 0.0) for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_mg_sup = sum(amounts[i] * float(feeds[i].get("mg") or 0.0) for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))
    pasture_cp_sup = sum(amounts[i] * feeds[i]["cp"] for i in range(len(feeds)) if _is_pasture_feed(feeds[i]))

    grass_silage_kg = sum(amounts[i] for i in range(len(feeds)) if _is_grass_silage(feeds[i]))
    grass_silage_me_sup = sum(amounts[i] * feeds[i]["me"] for i in range(len(feeds)) if _is_grass_silage(feeds[i]))
    grass_silage_sidp_sup = sum(amounts[i] * feeds[i]["sidp"] for i in range(len(feeds)) if _is_grass_silage(feeds[i]))

    pasture_milk = _milk_from_supply(pasture_me_sup, pasture_sidp_sup, profile) if pasture_kg > 0 else None
    grass_silage_milk = _milk_from_supply(grass_silage_me_sup, grass_silage_sidp_sup, profile) if grass_silage_kg > 0 else None
    pasture_plus_grass_milk = _milk_from_supply(
        pasture_me_sup + grass_silage_me_sup,
        pasture_sidp_sup + grass_silage_sidp_sup,
        profile,
    ) if (pasture_kg + grass_silage_kg) > 0 else None

    pasture_k_mg_ratio = pasture_k_sup / pasture_mg_sup if pasture_mg_sup > 0 else None
    pasture_cp_density = pasture_cp_sup / pasture_kg if pasture_kg > 0 else None
    pasture_mg_supplement_kg = sum(
        amounts[i] for i in range(len(feeds)) if feeds[i].get("_special") == "pasture_mg"
    )

    # aNDFomGF-Dichte [g/kg TM]
    andfom_gf_density = forage_ndf / total_dmi if total_dmi > 0 else 0.0

    # pabKH [g/kg TM]
    pabkh_sup = sum(amounts[i] * (feeds[i]["st"] + feeds[i]["zu"] - feeds[i]["bst"])
                    for i in range(len(feeds)))
    pabkh_density = pabkh_sup / total_dmi if total_dmi > 0 else 0.0

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
    rmd_vals = [feeds[i].get("rmd") for i in range(len(feeds)) if amounts[i] > 0.001]
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
        "k_g": round(k_sup, 1),
        "pendf_kgdm": round(pendf_density, 1),
        "pendf_min_kgdm": round(pendf_min_val, 1),
        "staerke_kgdm": round(st_density, 1),
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
        _cr("aNDFomGF (g/kg TM)",     andfom_gf_density, andfom_gf_target,   unit="g/kg TM"),
        _cr("pabKH (g/kg TM)",        pabkh_target,         pabkh_density, unit="g/kg TM"),  # max-check
        _cr("XL Rohfett (g/kg TM)",   xl_target,          xl_density,   unit="g/kg TM"),   # max-check
        _cr("peNDF (g/kg TM)",        pendf_density, pendf_min_val,                   unit="g/kg TM"),
        _cr("Magnesium (g/d)",        mg_sup,        req.mg_min_g, unit="g/d"),
        _cr("Calcium (g/d)",          ca_sup,        req.ca_min_g, unit="g/d"),
        _cr("Phosphor (g/d)",         p_sup,         req.p_min_g,  unit="g/d"),
        _cr("Grundfutteranteil (%TM)", forage_share_pct, forage_share_target,     unit="%TM"),
    ]

    # --- DLG-Indikatoren (01|2023) ---
    dlg_indicators: Dict[str, Any] = {
        "strukturindex": round(si, 1) if si is not None else None,
        "strukturindex_ziel": ">= 50",
        "strukturindex_erfuellt": bool(si is not None and si >= 50.0),
        "andfom_gf_kgdm": round(andfom_gf_density, 1),
        "andfom_gf_ziel": f">= {andfom_gf_target:.0f} g/kg TM",
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
        "pendf_ziel": f">= {pendf_min_val:.0f} g/kg TM (stärkeabhängig, GfE-Workshop 2023)",
        "pendf_erfuellt": bool(pendf_density >= pendf_min_val),
        "ph_predicted": ph_predicted,
        "ph_ziel": ">= 6.2 (kritisch < 5.9)",
        "ph_ok": bool(ph_predicted >= 6.2),
    }

    # Amino acid ratio (post-check only, not in LP)
    sidlys_sidmet_ratio = (sidlys_sup / sidmet_sup) if sidmet_sup and sidmet_sup > 0 else None

    # --- Warnungen und Erklärungen ---
    warnings: List[str] = []
    if si is not None and si < 50:
        warnings.append(
            f"Strukturindex {si:.1f} < 50 – Pansen-pH < 6,15 wahrscheinlich. "
            f"aNDFomGF erhöhen oder pabKH (Stärke+Zucker) reduzieren."
        )
    if andfom_gf_density < andfom_gf_target:
        warnings.append(
            f"aNDFomGF {andfom_gf_density:.0f} g/kg TM < {andfom_gf_target:.0f} – "
            f"Grundfutter-Faserversorgung unzureichend."
        )
    if pabkh_density > pabkh_target:
        warnings.append(
            f"pabKH {pabkh_density:.0f} g/kg TM > {pabkh_target:.0f} – Pansenazidose-Risiko erhöht."
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

    # peNDF-Versorgung (GfE-Workshop 2023)
    if pendf_density < pendf_min_val:
        warnings.append(
            f"peNDF {pendf_density:.0f} g/kg TM unter Minimum {pendf_min_val:.0f} g/kg TM "
            f"(Stärke {st_density:.0f} g/kg TM, TM-Aufnahme {total_dmi:.1f} kg/d). "
            f"Pufferwirkung unzureichend – langfaseriges Raufutter (Heu, Stroh) ergänzen."
        )

    # Pansen-pH-Simulation (GfE-Workshop 2023)
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
            "milk_from_pasture": pasture_milk,
            "milk_from_grass_silage": grass_silage_milk,
            "milk_from_pasture_plus_grass_silage": pasture_plus_grass_milk,
            "warnings": pasture_warnings,
        }
        warnings.extend(pasture_warnings)

    # FAN-MODE-V1: Constraint-Status aus LP (Slice 2 befuellt penalty_cost; Slice 1 leitet ab).
    constraint_status = constraint_status_from_lp or _derive_constraint_status_from_report(
        constraint_report,
        relaxation_policy,
    )

    return {
        "status": "optimal",
        "objective_value": round(_f(result.fun), 4),
        "total_cost_eur_day": round(total_cost, 4),
        "total_cost_eur_100kg_milk": round(total_cost / (float(profile.get("milk_kg_day") or 1)) * 100, 2),
        "ration_items": ration_items,
        "nutrient_supply": nutrient_supply,
        "constraint_report": constraint_report,
        "constraint_status": constraint_status,
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
        "warnings": warnings,
        "feed_suggestions": [],
        "fan_calibration": fan_calibration,
        "active_policy_profile": policy_profile,
        "policy_overrides": policy_overrides,
        "relaxation_policy": relaxation_policy,
        "objective_strategy": objective_strategy,
        "season_profile": season_profile,
        "metadata": {
            "solver": "scipy-highs-internal",
            # Historischer Schluessel (bleibt stabil fuer alte Clients).
            # Der neue API-steuerbare Wert wird separat als "objective_strategy" ausgewiesen.
            "optimization_strategy": "stage1_balance_then_stage2_cost",
            "objective_strategy": objective_strategy,
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
    nel = float(gfa.get("nel_ts") or 0)
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


_COMPOUND_FEED_MATCHERS: List[Tuple[Tuple[str, ...], str]] = [
    (("mais", "korn"), "dlg_30880030"),
    (("mais",), "dlg_30880030"),
    (("gerste",), "dlg_30820030"),
    (("weizenkleie",), "dlg_31210030"),
    (("weizengriesskleie",), "dlg_31230030"),
    (("weizen",), "dlg_31190030"),
    (("melasseschnitzel",), "dlg_30940030"),
    (("ruebenmelasse",), "dlg_41290030"),
    (("melasse",), "dlg_41290030"),
    (("rapsextraktionsschrot", "thermisch"), "dlg_30980130"),
    (("rapsextraktionsschrot",), "dlg_30970130"),
    (("sojaextraktionsschrot", "geschaelter saat"), "dlg_31060030"),
    (("sojaextraktionsschrot", "geschalter saat"), "dlg_31060030"),
    (("sojaextraktionsschrot",), "dlg_31050130"),
    (("haferschaelkleie",), "dlg_30850030"),
    (("haferschalkleie",), "dlg_30850030"),
    (("hafer",), "dlg_30840030"),
]


def _ascii_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "custom-feed"


def _normalize_feed_label(value: str) -> str:
    replacements = {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss",
        "é": "e",
        "è": "e",
    }
    normalized = value.lower()
    for source, target in replacements.items():
        normalized = normalized.replace(source, target)
    normalized = normalized.replace("&", " und ")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
    return " ".join(normalized.split())


def _parse_localized_float(raw: str) -> Optional[float]:
    candidate = raw.strip().replace(" ", "").replace("%", "").replace("mj", "").replace("kg", "")
    candidate = candidate.replace(",", ".")
    try:
        return float(candidate)
    except (TypeError, ValueError):
        return None


def _extract_value(text: str, pattern: str) -> Optional[float]:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return None
    return _parse_localized_float(match.group(1))


def _extract_labelled_value(text: str, label: str, suffix_pattern: str) -> Optional[float]:
    """Liest einen beschrifteten Deklarationswert aus einem Futtermittel-Etikett.

    Wichtig: das "Label zuerst"-Muster muss vor dem "Wert zuerst"-Muster stehen.
    In Fliesstexten wie
        "Rohprotein 16,50 % Rohfett 2,80 % Rohasche 4,00 %"
    wuerde das inverse Muster (Zahl vor Label) sonst fuer "Rohfett" die 16,5
    aus "Rohprotein" zurueckgeben (Off-by-one-Verschub ueber die Inhaltsstoff-
    Liste). Das hat zuvor zu stark verfaelschten Compound-Feed-Werten gefuehrt
    (Ca = 7,2% statt 0,28%, XL = 165 g/kg statt 31 g/kg usw.).
    """
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    # Zuerst zeilenbasiert mit "Label zuerst" (am robustesten).
    for line in lines:
        if label.lower() not in line.lower():
            continue
        patterns = [
            rf"{label}\s*[:=]?\s*([0-9]+[.,][0-9]+)\s*{suffix_pattern}",
            rf"([0-9]+[.,][0-9]+)\s*{suffix_pattern}\s*{label}",
        ]
        for pattern in patterns:
            value = _extract_value(line, pattern)
            if value is not None:
                return value
    # Fallback auf das gesamte (ggf. flache) Dokument - ebenfalls Label zuerst bevorzugt.
    compact_patterns = [
        rf"{label}\s*[:=]?\s*([0-9]+[.,][0-9]+)\s*{suffix_pattern}",
        rf"([0-9]+[.,][0-9]+)\s*{suffix_pattern}\s*{label}",
    ]
    for pattern in compact_patterns:
        value = _extract_value(text, pattern)
        if value is not None:
            return value
    return None


def _extract_document_text(filename: str, content: bytes) -> Tuple[str, str, List[str]]:
    suffix = Path(filename).suffix.lower()
    warnings: List[str] = []
    if suffix == ".pdf":
        try:
            import io as _io
            import pdfplumber
            with pdfplumber.open(_io.BytesIO(content)) as pdf:
                text = "\n".join((page.extract_text() or "") for page in pdf.pages)
        except ImportError as exc:
            raise HTTPException(503, f"PDF-Parsing nicht verfuegbar: {exc}")
        except Exception as exc:
            raise HTTPException(422, f"PDF konnte nicht gelesen werden: {exc}")
        if not text.strip():
            raise HTTPException(
                422,
                "Das PDF enthaelt keinen Textlayer. Bitte Lieferschein als Foto/JPG/PNG hochladen.",
            )
        return text, "pdf_text", warnings
    if suffix not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
        raise HTTPException(400, "Nur PDF- oder Bilddateien (PNG/JPG/WebP/TIFF) erlaubt")
    try:
        from io import BytesIO
        from PIL import Image
        import pytesseract
        image = Image.open(BytesIO(content))
        text = pytesseract.image_to_string(image, lang="deu+eng")
    except ImportError as exc:
        raise HTTPException(503, f"OCR nicht verfuegbar: {exc}")
    except Exception as exc:
        raise HTTPException(422, f"Bild konnte nicht via OCR gelesen werden: {exc}")
    if not text.strip():
        raise HTTPException(422, "Im Bild wurde kein lesbarer Text erkannt")
    warnings.append("OCR-Erkennung aktiv - Werte vor der Verwendung fachlich pruefen.")
    return text, "image_ocr", warnings


def _match_compound_component(name: str, feeds_by_id: Dict[str, Dict[str, Any]]) -> Tuple[Optional[str], Optional[str]]:
    normalized = _normalize_feed_label(name)
    for tokens, feed_id in _COMPOUND_FEED_MATCHERS:
        if all(token in normalized for token in tokens):
            feed = feeds_by_id.get(feed_id)
            if feed:
                return feed_id, feed["name"]
    return None, None


def _aggregate_compound_components(
    components: List[_CompoundFeedComponent],
    feeds_by_id: Dict[str, Dict[str, Any]],
) -> Tuple[Dict[str, float], float]:
    matched = [c for c in components if c.matched_feed_id and c.inclusion_pct > 0]
    matched_share = sum(c.inclusion_pct for c in matched)
    if matched_share <= 0:
        return {}, 0.0
    numeric_fields = [
        "dm_frac", "price", "me", "sidp", "cp", "ndf", "adf", "st", "bst", "zu", "nfc",
        "xl", "ca", "p", "na", "mg", "k", "rmd", "omdfan1",
    ]
    aggregate = {field: 0.0 for field in numeric_fields}
    for component in matched:
        feed = feeds_by_id[component.matched_feed_id]
        weight = component.inclusion_pct / matched_share
        for field in numeric_fields:
            aggregate[field] += float(feed.get(field) or 0.0) * weight
    return aggregate, matched_share


def _build_compound_estimate(
    product_name: str,
    declared: _CompoundFeedDeclaredAnalysis,
    aggregate: Dict[str, float],
    matched_share: float,
) -> Tuple[_CompoundFeedGfeEstimate, Dict[str, Any]]:
    from modules.agrar.services.naehrwert_service import (
        AnalytikInput,
        FutterTyp,
        QuelleTyp,
        berechne_naehrwerte as _berechne_naehrwerte,
    )

    # Deklaration auf Futtermittel-Etiketten ist in % FM (Frischmasse).
    # Der Optimizer arbeitet in g/kg TM - daher mit 1/dm_frac auf TM-Basis umrechnen.
    dm_frac = float(aggregate.get("dm_frac") or 0.88)
    if dm_frac <= 0.0:
        dm_frac = 0.88
    pct_to_g_per_kg_tm = 10.0 / dm_frac  # %-FM -> g/kg TM

    def _declared_to_tm(pct: Optional[float], fallback: float) -> float:
        if pct is None:
            return fallback
        return float(pct) * pct_to_g_per_kg_tm

    cp_g = _declared_to_tm(declared.crude_protein_pct, float(aggregate.get("cp") or 0.0))
    fat_g = _declared_to_tm(declared.crude_fat_pct, float(aggregate.get("xl") or 0.0))
    ash_g = (
        _declared_to_tm(declared.crude_ash_pct, 0.0)
        if declared.crude_ash_pct is not None
        else max(35.0, 1000.0 - float(aggregate.get("nfc") or 820.0))
    )
    fiber_pct = declared.crude_fiber_pct
    ndf_g = float(aggregate.get("ndf") or max((fiber_pct or 8.0) * 22.0 / dm_frac * 0.1 * 10.0, 130.0))
    adf_g = float(aggregate.get("adf") or max((fiber_pct or 8.0) * 12.0 / dm_frac * 0.1 * 10.0, 75.0))
    starch_g = float(aggregate.get("st") or 220.0)
    sugar_g = float(aggregate.get("zu") or 65.0)

    analytik = AnalytikInput(
        tm=max(float(aggregate.get("dm_frac") or 0.88) * 1000.0, 870.0),
        cp=round(cp_g, 2),
        cl=round(fat_g, 2),
        ca=round(ash_g, 2),
        zucker=round(sugar_g, 2),
        staerke=round(starch_g, 2),
        adfom=round(adf_g, 2),
        andFom=round(ndf_g, 2),
        fan=2.5,
        futtertyp=FutterTyp.MISCHFUTTER,
        quelle=QuelleTyp.USER,
    )
    result = _berechne_naehrwerte(analytik, modus="beratung")

    ca_g = _declared_to_tm(declared.calcium_pct, float(aggregate.get("ca") or 1.5))
    p_g = _declared_to_tm(declared.phosphorus_pct, float(aggregate.get("p") or 4.5))
    na_g = _declared_to_tm(declared.sodium_pct, float(aggregate.get("na") or 1.5))
    mg_g = _declared_to_tm(declared.magnesium_pct, float(aggregate.get("mg") or 2.5))
    nfc_g = max(1000.0 - cp_g - fat_g - ash_g - ndf_g, 0.0)
    product_slug = _ascii_slug(product_name)

    estimate = _CompoundFeedGfeEstimate(
        basis="composition_match" if matched_share >= 60.0 else "declared_analysis_fallback",
        match_coverage_pct=round(matched_share, 1),
        me_fan1_mj_kgdm=round(result.energie.me_fan1_mj_kg_tm, 3),
        me_fani_mj_kgdm=round(result.energie.me_fani_mj_kg_tm, 3),
        nel_mj_kgdm=round(result.nel_mj_kg_tm, 3),
        sidp_g_kgdm=round(result.protein.sidp_gesamt, 1),
        nxp_g_kgdm=round(result.nxp_g_kg_tm, 1),
        cp_g_kgdm=round(cp_g, 1),
        andfom_g_kgdm=round(ndf_g, 1),
        starch_g_kgdm=round(starch_g, 1),
        sugar_g_kgdm=round(sugar_g, 1),
        fat_g_kgdm=round(fat_g, 1),
        omd_method=result.energie.omd_methode,
    )
    optimizer_feed = {
        "id": f"compound_{product_slug}",
        "lid": None,
        "name": product_name,
        "konservierung": "",
        "group": "Kraftfutter/Betrieb",
        "futterart": "Kraftfutter, Mischfutter",
        "forage": False,
        "dm_frac": round(float(aggregate.get("dm_frac") or 0.88), 3),
        "price": round(float(aggregate.get("price") or 0.38), 3),
        "min_kg": 0.0,
        "max_kg": 8.0,
        "me": float(estimate.me_fan1_mj_kgdm or 0.0),
        "sidp": float(estimate.sidp_g_kgdm or 0.0),
        "cp": round(cp_g, 1),
        "ndf": round(ndf_g, 1),
        "adf": round(adf_g, 1),
        "st": round(starch_g, 1),
        "bst": round(starch_g * 0.60, 1),
        "zu": round(sugar_g, 1),
        "nfc": round(nfc_g, 1),
        "xl": round(fat_g, 1),
        "ca": round(ca_g, 2),
        "p": round(p_g, 2),
        "na": round(na_g, 2),
        "mg": round(mg_g, 2),
        "k": round(float(aggregate.get("k") or 8.0), 2),
        "dcab": None,
        "edg": None,
        "rmd": round(float(aggregate.get("rmd") or result.protein.rmd), 2),
        "omdfan1": round(float(aggregate.get("omdfan1") or result.energie.omd_fan1), 2),
        "ndfd": None,
        "ge": None,
        "sidlys": None,
        "sidmet": None,
        "_source": "compound_upload",
        "_match_coverage_pct": round(matched_share, 1),
        "_legacy_nel_mj_kg": declared.nel_mj_kg,
    }
    return estimate, optimizer_feed


def _parse_compound_feed_text(text: str, filename: str, source_type: str) -> _CompoundFeedParsed:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    flat_text = re.sub(r"\s+", " ", text.replace("-\n", "").replace("\n", " "))
    product_name = "Milchleistungsfutter"
    product_match = re.search(r"(Milchleistungsfutter[^\n]+)", text.replace("-\n", ""), flags=re.IGNORECASE)
    if product_match:
        product_name = " ".join(product_match.group(1).split())
    else:
        for idx, line in enumerate(lines):
            if "Inhaltsstoffe" in line:
                for back in range(max(0, idx - 2), idx):
                    candidate = lines[back]
                    if len(candidate) > 12 and not re.search(r"^[0-9./ -]+$", candidate):
                        product_name = candidate
                        break
                break
    analysis_match = re.search(
        r"Inhaltsstoffe:\s*(.+?)(?:\s+Zusatzstoffe:|\s+Zusammensetzung:)",
        flat_text,
        flags=re.IGNORECASE,
    )
    analysis_text = analysis_match.group(1) if analysis_match else flat_text
    declared = _CompoundFeedDeclaredAnalysis(
        crude_protein_pct=_extract_labelled_value(analysis_text, "Rohprotein", "%"),
        crude_fat_pct=_extract_labelled_value(analysis_text, "Rohfett", "%"),
        crude_fiber_pct=_extract_labelled_value(analysis_text, "Rohfaser", "%"),
        crude_ash_pct=_extract_labelled_value(analysis_text, "Rohasche", "%"),
        calcium_pct=_extract_labelled_value(analysis_text, "Calcium", "%"),
        phosphorus_pct=_extract_labelled_value(analysis_text, "Phosphor", "%"),
        sodium_pct=_extract_labelled_value(analysis_text, "Natrium", "%"),
        magnesium_pct=_extract_labelled_value(analysis_text, "Magnesium", "%"),
        nel_mj_kg=(
            _extract_value(analysis_text, r"NEL/?kg\s*([0-9]+[.,][0-9]+)\s*MJ")
            or _extract_value(analysis_text, r"([0-9]+[.,][0-9]+)\s*MJ\s*NEL/?kg")
        ),
    )
    components: List[_CompoundFeedComponent] = []
    composition_match = re.search(
        r"Zusammensetzung:\s*(.+?)(?:\s+(?:Tel\.|Fax|Email:|Ernährungsphysiologische Zusatzstoffe|Ernaehrungsphysiologische Zusatzstoffe|Fütterungshinweis|Fuetterungshinweis|GmbH\s*&|$))",
        flat_text,
        flags=re.IGNORECASE,
    )
    composition_text = composition_match.group(1) if composition_match else ""
    parts = re.findall(
        r"([0-9]+[.,][0-9]+)\s*%\s*([^%]+?)(?=(?:[0-9]+[.,][0-9]+\s*%|$))",
        composition_text,
        flags=re.IGNORECASE,
    )
    feeds_by_id = {feed["id"]: feed for feed in _get_feeds()}
    for pct_raw, name_raw in parts:
        pct = _parse_localized_float(pct_raw)
        if pct is None:
            continue
        cleaned_name = name_raw.strip(" ,.;")
        matched_feed_id, matched_feed_name = _match_compound_component(cleaned_name, feeds_by_id)
        components.append(
            _CompoundFeedComponent(
                name=cleaned_name,
                inclusion_pct=round(pct, 2),
                matched_feed_id=matched_feed_id,
                matched_feed_name=matched_feed_name,
            )
        )
    aggregate, matched_share = _aggregate_compound_components(components, feeds_by_id)
    estimate, optimizer_feed = _build_compound_estimate(product_name, declared, aggregate, matched_share)
    warnings: List[str] = []
    if matched_share < 100.0:
        warnings.append(
            f"Rezeptur-Match deckt {matched_share:.1f}% der Zusammensetzung gegen DLG-Futtermittel ab."
        )
    if declared.nel_mj_kg is not None and estimate.nel_mj_kgdm is not None:
        # Deklarierte NEL auf Futtermitteletiketten steht ueblicherweise in MJ/kg FM.
        # Fuer den Vergleich mit der GfE-Schaetzung (MJ/kg TM) auf TM-Basis umrechnen.
        dm_frac_for_nel = float(optimizer_feed.get("dm_frac") or 0.88)
        declared_nel_tm = declared.nel_mj_kg / dm_frac_for_nel if dm_frac_for_nel > 0 else declared.nel_mj_kg
        delta = abs(declared_nel_tm - estimate.nel_mj_kgdm)
        if delta > 0.4:
            warnings.append(
                "Abweichung zwischen deklarierter NEL "
                f"({declared.nel_mj_kg:.1f} MJ/kg FM ≈ {declared_nel_tm:.2f} MJ/kg TM) und geschaetzter NEL "
                f"({estimate.nel_mj_kgdm:.2f} MJ/kg TM) beachten."
            )
    if not components:
        warnings.append("Keine verwertbare Rezeptur-Zusammensetzung erkannt; GfE-Schaetzung basiert auf Deklarationsanalyse.")
    return _CompoundFeedParsed(
        source_filename=filename,
        source_type=source_type,
        product_name=product_name,
        supplier_name=None,
        declared_analysis=declared,
        composition=components,
        gfe2023_estimate=estimate,
        optimizer_feed=optimizer_feed,
        warnings=warnings,
        raw_text_preview=text[:1200],
    )


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
    if ft == "PMR+Weide" and season in ("spring_young", "spring_mid", "spring_late"):
        return "pmr_pasture_spring"
    return "pmr_standard"


def _resolve_runtime_options(
    profile: Dict[str, Any],
    fan_options: Optional[_FanOptions] = None,
    relaxation_policy: Optional[str] = None,
    objective_strategy: Optional[str] = None,
    season_profile: Optional[str] = None,
    policy_profile: Optional[str] = None,
    policy_overrides: Optional[Dict[str, Any]] = None,
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
    }


def _optimize_internal(
    profile: Dict[str, Any],
    custom_feeds: Optional[List[Dict[str, Any]]] = None,
    feed_ids: Optional[List[str]] = None,
    price_overrides: Optional[Dict[str, float]] = None,
    max_tm_overrides: Optional[Dict[str, float]] = None,
    runtime_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    req = _gfe_requirements(profile)
    feeds = list(_get_feeds())

    # FAN-MODE-V1: alle Laufzeit-Optionen zentral aufloesen
    if runtime_options is None:
        runtime_options = _resolve_runtime_options(profile)

    # Betriebseigene Grundfuttermittel aus GrundfutterAnalysen einmischen
    if custom_feeds:
        for cf in custom_feeds:
            if cf.get("_source") == "gfa":
                feeds.append(cf)
            else:
                feeds.append(cf)

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

    # Filter auf ausgewählte Feed-IDs
    if feed_ids:
        id_set = set(feed_ids)
        feeds = [f for f in feeds if f["id"] in id_set]

    # PMR+Weide: Weidemineral automatisch als Pflichtbaustein fuehren,
    # damit das K/Mg-Antagonismus-Risiko (DLG 417 / DLG 01|2023) sauber abgedeckt ist.
    feeding_type_norm = _normalize_feeding_type(profile.get("feeding_type"))
    if feeding_type_norm == "PMR+Weide" or (
        feeding_type_norm == "PMR" and _has_pasture_forage(feeds)
    ):
        has_mg_supplement = any(feed.get("_special") == "pasture_mg" for feed in feeds)
        if not has_mg_supplement:
            for supplement in _SPECIAL_SUPPLEMENTS:
                if supplement.get("_special") == "pasture_mg":
                    feeds.append(dict(supplement))
                    break

    lp_out = _run_lp(req, feeds, profile, runtime_options=runtime_options)
    lp_out["_runtime_options"] = runtime_options
    return _build_response(lp_out, req, profile)


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
    }


# ---------------------------------------------------------------------------
# Pydantic Models für API
# ---------------------------------------------------------------------------

_FAN_MODES = ("auto_iterative", "reference", "evaluation_only")
_RELAXATION_POLICIES = ("strict", "standard", "soft")
_OBJECTIVE_STRATEGIES = ("balance_then_cost", "balance_only", "cost_only")
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
_POLICY_PROFILES = ("tmr_standard", "pmr_standard", "pmr_pasture_spring")

# FAN-V1 Defaults (Spec §11.1 freigegeben 2026-04-21)
_FAN_DEFAULT_MODE = "auto_iterative"
_FAN_DEFAULT_TOLERANCE = 0.05
_FAN_DEFAULT_TOLERANCE_WARN = 0.10
_FAN_DEFAULT_MAX_ITERATIONS = 5
_FAN_REFERENCE_PRESETS: Tuple[float, ...] = (2.5, 3.0, 3.5)
_FAN_REFERENCE_MIN = 2.0
_FAN_REFERENCE_MAX = 5.0
_RELAXATION_DEFAULT = "standard"
_RELAXATION_FACTORS: Dict[str, float] = {"strict": 3.0, "standard": 1.0, "soft": 0.3}
_PENALTY_BASE_COST = 1.0
_PENALTY_CLASS_WEIGHTS: Dict[str, float] = {"A": 10.0, "B": 3.0, "C": 1.0}


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

    # FAN-MODE-V1 additive Felder (Spec §4 freigegeben 2026-04-21)
    fan_options: Optional[_FanOptions] = None          # GfE-2023 FAN1/FANi-Bewertungsoptionen
    relaxation_policy: Optional[str] = None            # strict | standard | soft (Default: standard)
    objective_strategy: Optional[str] = None           # balance_then_cost | balance_only | cost_only
    season_profile: Optional[str] = None               # spring_young | ...; steuert Policy-Profil (§6)
    policy_profile: Optional[str] = None               # Explicit Override; sonst aus feeding_type+season abgeleitet
    policy_overrides: Optional[Dict[str, Any]] = None  # Expertenmodus: Block-Limit-Overrides


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

@router.get("/health")
async def rations_health():
    base_url = _rations_base_url()
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


@router.get("/feeds")
async def get_feeds(
    request: Request,
    group: Optional[str] = Query(None, description="Filter nach Futtergruppe"),
    forage_only: bool = Query(False, description="Nur Grundfutter"),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not _rations_base_url():
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


@router.get("/feeds/{feed_id}")
async def get_feed(
    feed_id: str,
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not _rations_base_url():
        feeds = _get_feeds()
        feed = next((f for f in feeds if f["id"] == feed_id), None)
        if not feed:
            raise HTTPException(status_code=404, detail="Futtermittel nicht gefunden")
        return JSONResponse(content=feed)
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("GET", f"/api/v1/feeds/{feed_id}", tenant_id=tenant_id)


@router.post("/optimize/from-profile")
async def optimize_from_profile(
    body: _OptimizeFromProfileBody,
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not _rations_base_url():
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
            )
            result = _optimize_internal(
                body.cow_profile,
                custom_feeds=custom,
                feed_ids=body.feeds,
                price_overrides=body.price_overrides,
                max_tm_overrides=body.max_tm_overrides,
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


@router.post("/optimize/demo")
async def optimize_demo(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not _rations_base_url():
        try:
            result = _optimize_internal(_demo_profile())
            return JSONResponse(content=result)
        except Exception as exc:
            logger.exception("Demo-Optimierung fehlgeschlagen: %s", exc)
            raise HTTPException(status_code=500, detail=f"Demo fehlgeschlagen: {exc}")
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("POST", "/api/v1/optimize/demo", tenant_id=tenant_id)


@router.post("/optimize")
async def optimize(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    body = await request.json()
    if not _rations_base_url():
        profile = body.get("cow_profile", body)
        try:
            result = _optimize_internal(profile)
            return JSONResponse(content=result)
        except Exception as exc:
            raise HTTPException(status_code=500, detail=f"Optimierung fehlgeschlagen: {exc}")
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("POST", "/api/v1/optimize", tenant_id=tenant_id, json_body=body)


@router.post("/requirements/calculate")
async def calculate_requirements(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    body = await request.json()
    if not _rations_base_url():
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


@router.post("/requirements/maintenance")
async def maintenance_requirements(
    request: Request,
    body_weight_kg: float = Query(...),
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    if not _rations_base_url():
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


@router.post("/feeds/validate")
async def validate_feeds(
    request: Request,
    x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-Id"),
):
    body = await request.json()
    if not _rations_base_url():
        return JSONResponse(content={"valid": True, "errors": []})
    tenant_id = _tenant_from_request(request, x_tenant_id)
    return await _proxy_request("POST", "/api/v1/feeds/validate", tenant_id=tenant_id, json_body=body)


@router.post("/dlg/strukturindex")
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


@router.get("/dlg/info")
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


@router.post("/dlg/refresh")
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


@router.post("/compound-feed/upload")
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


@router.post("/feeds/from-grundfutter")
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
