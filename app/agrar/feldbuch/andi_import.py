"""
ANDI-Schlagdaten-Import (Welle AS-W8).

ANDI (Agrarfoerderung Niedersachsen Digital) liefert die Schlagdaten des
Agrarfoerderantrags als XML. Dieses Modul parst ein bereits dekodiertes,
vereinfachtes ANDI-Schlag-XML in kanonische Schlag-Dictionaries, die in das
Feldbuch (FeldbuchSchlag) uebernommen werden koennen. Transport/Onboarding und
der amtliche Antrag bleiben ausserhalb; hier erfolgt reine Datenuebernahme.

Erwartetes XML (vereinfacht, robust gegen Namespaces):
  <schlaege jahr="2026">
    <schlag nr="1" name="Am Bach" flaeche="12.5" flik="DENILI..." kultur="Winterweizen"
            gemeinde="Musterdorf" gemarkung="Flur 3"/>
    ...
  </schlaege>
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip().replace(",", ".")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_andi_schlaege(xml_text: str) -> Dict[str, Any]:
    """Parst ANDI-Schlag-XML in kanonische Schlag-Dictionaries.

    Liefert {"jahr": <int|None>, "schlaege": [ {name, flaeche, flik, kultur, ...}, ... ]}.
    Wirft ValueError bei ungueltigem XML oder fehlenden Pflichtfeldern.
    """
    text = (xml_text or "").strip()
    if not text:
        raise ValueError("Leeres ANDI-XML.")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        raise ValueError(f"Ungueltiges ANDI-XML: {exc}") from exc

    jahr = None
    m = re.search(r'jahr="(\d{4})"', text)
    if m:
        jahr = int(m.group(1))
    elif root.attrib.get("jahr"):
        jahr = int(root.attrib["jahr"])

    schlaege: List[Dict[str, Any]] = []
    for el in root.iter():
        if _localname(el.tag) != "schlag":
            continue
        attr = {k.lower(): v for k, v in el.attrib.items()}
        name = (attr.get("name") or attr.get("bezeichnung") or "").strip()
        flaeche = _to_float(attr.get("flaeche") or attr.get("groesse") or attr.get("ha"))
        if not name and attr.get("nr"):
            name = f"Schlag {attr['nr']}"
        if not name or flaeche is None:
            raise ValueError("Jeder ANDI-Schlag braucht name/bezeichnung und flaeche.")
        schlaege.append({
            "schlag_nr": (attr.get("nr") or attr.get("schlagnr") or None),
            "name": name,
            "flaeche": flaeche,
            "flik": attr.get("flik") or attr.get("feldblock") or None,
            "kultur": (attr.get("kultur") or attr.get("frucht") or None),
            "gemeinde": attr.get("gemeinde") or None,
            "gemarkung": attr.get("gemarkung") or attr.get("flur") or None,
        })
    if not schlaege:
        raise ValueError("ANDI-XML enthaelt keine Schlaege.")
    return {"jahr": jahr, "schlaege": schlaege, "anzahl": len(schlaege)}
