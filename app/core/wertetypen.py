"""Fachliche Wertetypen der Masken: eine Quelle fuer Backend und Frontend.

Muster und Beispiele stehen in ``config/wertetypen.json``; das Frontend prueft dieselben Regeln in
``components/mask-builder/runtime/text-format.ts``. Beide Testseiten laufen gegen die Beispiele der Datei, damit
eine Maske nichts annimmt, was der Server ablehnt (und umgekehrt).
"""
from __future__ import annotations

import json
import re
from calendar import monthrange
from functools import lru_cache
from pathlib import Path
from typing import Callable

_QUELLE = Path(__file__).resolve().parents[2] / "config" / "wertetypen.json"


@lru_cache(maxsize=1)
def _daten() -> dict:
    return json.loads(_QUELLE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def ust_id_muster() -> dict[str, re.Pattern[str]]:
    return {land: re.compile(muster) for land, muster in _daten()["ustIdMuster"].items()}


def ust_id_normalisiert(roh: str) -> str:
    return roh.replace(" ", "").replace("-", "").strip().upper()


def ust_id_gueltig(roh: str) -> bool:
    wert = ust_id_normalisiert(roh)
    muster = ust_id_muster().get(wert[:2])
    return bool(muster and muster.match(wert))


def gs1_pruefziffer(ziffern: str) -> int:
    """GS1-Mod-10 (GLN, GTIN, SSCC): Gewicht 3 ab der Stelle vor der Pruefziffer."""
    summe = sum(int(z) * (3 if i % 2 == 0 else 1) for i, z in enumerate(reversed(ziffern)))
    return (10 - summe % 10) % 10


def _gs1(laengen: tuple[int, ...]) -> Callable[[str], bool]:
    def pruefe(roh: str) -> bool:
        wert = roh.strip()
        return wert.isdigit() and len(wert) in laengen and gs1_pruefziffer(wert[:-1]) == int(wert[-1])
    return pruefe


def iban_gueltig(roh: str) -> bool:
    wert = re.sub(r"\s+", "", roh).upper()
    if not re.fullmatch(r"[A-Z]{2}[0-9]{2}[A-Z0-9]{11,30}", wert):
        return False
    umgestellt = wert[4:] + wert[:4]
    return int("".join(str(int(z, 36)) for z in umgestellt)) % 97 == 1


def _monat_tag(roh: str) -> bool:
    treffer = re.fullmatch(r"(\d{2})-(\d{2})", roh.strip())
    if not treffer:
        return False
    monat, tag = int(treffer[1]), int(treffer[2])
    return 1 <= monat <= 12 and 1 <= tag <= monthrange(2024, monat)[1]  # Schaltjahr: 29.02. ist ein Stichtag


def _periode(roh: str) -> bool:
    treffer = re.fullmatch(r"(\d{4})-(\d{2})", roh.strip())
    return bool(treffer and 1 <= int(treffer[2]) <= 12)


PRUEFUNGEN: dict[str, Callable[[str], bool]] = {
    "email": lambda w: bool(re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]{2,}", w.strip())),
    "phone": lambda w: bool(re.fullmatch(r"\+?[0-9][0-9 ()/-]{4,}", w.strip())),
    "iban": iban_gueltig,
    "vatId": ust_id_gueltig,
    "gln": _gs1((13,)),
    "gtin": _gs1((8, 12, 13, 14)),
    "sscc": _gs1((18,)),
    "hsCode": lambda w: bool(re.fullmatch(r"\d{8}", w.strip())),
    "currencyCode": lambda w: bool(re.fullmatch(r"[A-Z]{3}", w.strip())),
    "monthDay": _monat_tag,
}

#: Textformate, die eine ScreenDefinition an Textfeldern deklarieren darf.
TEXT_FORMATE = frozenset(PRUEFUNGEN)


def wert_gueltig(format_name: str, roh: str) -> bool:
    """Leer ist gueltig (Pflicht prueft die eigene Regel)."""
    if not str(roh or "").strip():
        return True
    if format_name == "period":
        return _periode(roh)
    return PRUEFUNGEN[format_name](str(roh))


def beispiele() -> dict[str, dict[str, list[str]]]:
    return _daten()["beispiele"]
