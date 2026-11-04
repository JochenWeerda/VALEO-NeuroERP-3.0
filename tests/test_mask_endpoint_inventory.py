"""Jede Maskenquelle muss auf eine Route zeigen, die es wirklich gibt.

Warum dieses Gate existiert
---------------------------

Eine ScreenDefinition darf einen Endpunkt nennen, den niemand gebaut hat — das
faellt **nicht** auf. Die Maskenlaufzeit holt die Daten, bekommt einen 404 und
zeigt „Vorgang konnte nicht geladen werden". Sechs native Masken haben genau
das getan: Ihr `entity`-Endpunkt hatte ein `masks/`-Praefix, unter dem keine
Route liegt (`/api/v1/masks/einkauf/bestellungen/{id}`), waehrend der echte
Endpunkt daneben lag (`/api/v1/einkauf/bestellungen/{id}`).

Dasselbe Muster wie bei der Faktura-Liste, die monatelang leer aussah, weil
`GET /sales/invoices` nicht existierte und ein `catch` den 404 verschluckte.

Der Test prueft die **Adresse**, nicht die Antwort: Ob die Felder der Maske zu
den Schluesseln der Antwort passen, kann er nicht wissen. Aber eine Maske, die
auf eine nicht vorhandene Route zeigt, ist immer ein Fehler.
"""

from __future__ import annotations

import re

import pytest

from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition

pytestmark = pytest.mark.unit


def _route_muster() -> list[re.Pattern[str]]:
    from app.main import app

    muster: list[re.Pattern[str]] = []
    for route in app.routes:
        pfad = getattr(route, "path", None)
        if not pfad:
            continue
        # "/crm/contacts/" und "/crm/contacts" sind derselbe Weg (FastAPI leitet um).
        ausdruck = re.escape(pfad.rstrip("/") or "/")
        # {param:path} frisst mehrere Segmente, {param} genau eines.
        ausdruck = re.sub(r"\\\{[^}]*:path\\\}", ".+", ausdruck)
        ausdruck = re.sub(r"\\\{[^}]*\\\}", "[^/]+", ausdruck)
        muster.append(re.compile("^" + ausdruck + "/?$"))
    return muster


def _quellen(screen: dict) -> list[tuple[str, str]]:
    quellen: list[tuple[str, str]] = []
    if screen.get("summaryEndpoint"):
        quellen.append(("summaryEndpoint", screen["summaryEndpoint"]))
    for quelle in screen.get("dataSources") or []:
        if quelle.get("endpoint"):
            quellen.append((f"dataSource:{quelle.get('key')}", quelle["endpoint"]))
    for aktion in screen.get("actions") or []:
        if aktion.get("commandEndpoint"):
            quellen.append((f"action:{aktion.get('key')}", aktion["commandEndpoint"]))
    return quellen


def test_jede_maskenquelle_hat_eine_route() -> None:
    muster = _route_muster()

    def erreichbar(endpunkt: str) -> bool:
        konkret = re.sub(r"\{[^}]+\}", "x", endpunkt.split("?")[0])
        return any(m.match(konkret) for m in muster)

    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry

    # Stamm-Masken registrieren sich beim ersten Abruf nach; vorher laden, sonst aendert sich das Register beim Lauf.
    ensure_stamm_screen_registry()
    fehlend: list[str] = []
    for screen_id in list(SCREEN_DEFINITION_BUILDERS):
        screen = get_screen_definition(screen_id)
        assert screen is not None
        if (screen.get("adapter") or {}).get("temporary"):
            continue
        for art, endpunkt in _quellen(screen):
            if not endpunkt.startswith("/api/"):
                continue
            if not erreichbar(endpunkt):
                fehlend.append(f"{screen_id} {art} -> {endpunkt}")

    import json
    from pathlib import Path

    # Altlast Runtime46 (config/mask_endpoint_altlast.json): darf nur schrumpfen.
    altlast = set(json.loads(Path("config/mask_endpoint_altlast.json").read_text(encoding="utf-8"))["quellen_ohne_route"])
    neu = [eintrag for eintrag in fehlend if eintrag not in altlast]
    assert neu == [], "Maskenquellen ohne Route:\n  " + "\n  ".join(neu)
    behoben = sorted(altlast - set(fehlend))
    assert behoben == [], "Repariert - bitte aus config/mask_endpoint_altlast.json nehmen: " + ", ".join(behoben)


def test_keine_maske_zeigt_auf_den_entity_stub() -> None:
    """Der Stub liefert Platzhalter mit ``_stub: true`` — Felder bleiben leer.

    Geprueft wird die **entity**-Quelle, denn sie fuellt den Kopf der Maske: Ein
    Beleg, dessen Kopffelder alle leer sind, sieht aus wie ein leerer Vorgang.
    Tabellenregister am Stub sind das kleinere Uebel — sie zeigen eine leere
    Tabelle statt falscher Zahlen — und werden hier bewusst nicht verboten.

    Die Liste ist der Rest, nicht der Plan: Sie darf schrumpfen, nicht wachsen.
    """
    erlaubt: set[str] = set()
    auf_stub = set()
    for screen_id in SCREEN_DEFINITION_BUILDERS:
        screen = get_screen_definition(screen_id)
        if screen is None or (screen.get("adapter") or {}).get("temporary"):
            continue
        for quelle in screen.get("dataSources") or []:
            if quelle.get("key") != "entity":
                continue
            endpunkt = str(quelle.get("endpoint") or "")
            if "/api/v1/masks/" in endpunkt and "/entity/" in endpunkt:
                auf_stub.add(screen_id)

    neu = auf_stub - erlaubt
    assert neu == set(), (
        "Diese Masken haengen neu am Entity-Stub statt an einem Fachendpunkt: "
        f"{sorted(neu)}"
    )
