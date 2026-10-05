"""Aktuelle Fahrzeugpositionen über WEBFLEET.connect.

Abruf: ``showVehicleReportExtern`` auf ``https://csv.webfleet.com/extern``.
Konto und Schlüssel kommen aus der Umgebung. Das Passwort geht per HTTP Basic
Auth, nicht in der URL (seit Ende Juni 2026 aus dem Handbuch entfernt).
Höchstens ein Abruf pro Minute. Ohne Konfiguration oder ohne gültige Koordinate
bleibt die Tour am Zielort.
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

from app.domains.logistik.strecke import _punkt

BASIS = "https://csv.webfleet.com/extern"
AKTION = "showVehicleReportExtern"
PAUSE_SEKUNDEN = 60.0

_cache: tuple[float, list[dict[str, Any]]] | None = None


def _grad(wert: Any) -> float | None:
    if wert is None or wert == "":
        return None
    try:
        zahl = float(wert)
    except (TypeError, ValueError):
        return None
    return zahl / 1_000_000


def punkt_aus_fahrzeug(zeile: dict[str, Any]) -> tuple[float, float] | None:
    """Mikrograd aus dem Fahrzeugbericht. Ein gesetzter Status gilt nur bei A."""
    status = zeile.get("status")
    if status is not None and str(status) != "A":
        return None
    lat = _grad(zeile.get("latitude"))
    lng = _grad(zeile.get("longitude"))
    if lat is None or lng is None:
        return None
    return _punkt((lat, lng))


def kennzeichen(zeile: dict[str, Any]) -> str:
    for schluessel in ("licenseplatenumber", "objectname", "objectno"):
        wert = str(zeile.get(schluessel) or "").strip()
        if wert:
            return wert
    return ""


def _konfiguration() -> tuple[str, str, str, str] | None:
    account = os.environ.get("WEBFLEET_ACCOUNT", "").strip()
    user = os.environ.get("WEBFLEET_USER", "").strip()
    password = os.environ.get("WEBFLEET_PASSWORD", "").strip()
    apikey = os.environ.get("WEBFLEET_APIKEY", "").strip()
    if not (account and user and password and apikey):
        return None
    return account, user, password, apikey


def _abruf(account: str, user: str, password: str, apikey: str) -> list[dict[str, Any]]:
    query = urllib.parse.urlencode(
        {
            "account": account,
            "apikey": apikey,
            "action": AKTION,
            "outputformat": "json",
            "lang": "de",
            "useUTF8": "true",
            "useISO8601": "true",
        }
    )
    request = urllib.request.Request(f"{BASIS}?{query}")
    token = base64.b64encode(f"{user}:{password}".encode()).decode("ascii")
    request.add_header("Authorization", f"Basic {token}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            roh = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise RuntimeError("Webfleet nicht erreichbar") from exc
    data = json.loads(roh)
    if isinstance(data, dict) and "errorCode" in data:
        raise RuntimeError(str(data.get("errorMsg") or data.get("errorCode")))
    if not isinstance(data, list):
        raise RuntimeError("Webfleet-Antwort ist kein Fahrzeugbericht")
    return [zeile for zeile in data if isinstance(zeile, dict)]


def fahrzeugbericht(
    jetzt: float | None = None,
    transport: Callable[[str, str, str, str], list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """Fahrzeugbericht, höchstens einmal pro Minute. Ohne Konto eine leere Liste."""
    global _cache
    konfig = _konfiguration()
    if konfig is None:
        return []
    moment = time.monotonic() if jetzt is None else jetzt
    if _cache is not None and moment - _cache[0] < PAUSE_SEKUNDEN:
        return _cache[1]
    zeilen = (transport or _abruf)(*konfig)
    _cache = (moment, zeilen)
    return zeilen


def positionen() -> dict[str, tuple[float, float]]:
    """Kennzeichen → WGS84. Fehler und fehlende Fixes liefern nichts."""
    try:
        zeilen = fahrzeugbericht()
    except (RuntimeError, ValueError, OSError):
        # Webfleet ist optional. Ohne Fix bleibt die Position am Zielort.
        return {}
    ergebnis: dict[str, tuple[float, float]] = {}
    for zeile in zeilen:
        name = kennzeichen(zeile)
        punkt = punkt_aus_fahrzeug(zeile)
        if name and punkt is not None:
            ergebnis[name] = punkt
    return ergebnis
