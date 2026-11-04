"""Jede Studio-Seite rendert eine Maske, die das Backend kennt.

Seit deeb707b4 renderten 127 Seiten eine Native-Seite mit einer screenId, die es nicht gibt; sie zeigten nur
"Workspace konnte nicht geladen werden". 14 sind auf ihre vorhandene Maske umgehaengt (02.11.2026, Weg 1); der
Rest steht als nur schrumpfende Altlast in config/frontend_seiten_ohne_maske.json (Studio-Umbau).
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEITEN = "packages/frontend-web/src/pages"
_SCREEN = re.compile(r'<(?:Native\w+Page|UniversalNative\w+)\s[^>]*screenId="([^"]+)"')


def _seiten_ohne_maske() -> dict[str, str]:
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry

    ensure_stamm_screen_registry()
    dateien = subprocess.run(["git", "ls-files", SEITEN], capture_output=True, text=True, cwd=ROOT).stdout.split()
    ohne: dict[str, str] = {}
    for datei in sorted(dateien):
        if not datei.endswith(".tsx") or "__tests__" in datei:
            continue
        for screen_id in _SCREEN.findall((ROOT / datei).read_text(encoding="utf-8", errors="ignore")):
            if screen_id not in SCREEN_DEFINITION_BUILDERS:
                ohne[datei.removeprefix(SEITEN + "/")] = screen_id
    return ohne


def test_keine_neue_seite_ohne_maske_und_altlast_schrumpft():
    altlast = json.loads((ROOT / "config/frontend_seiten_ohne_maske.json").read_text(encoding="utf-8"))["seiten"]
    ist = _seiten_ohne_maske()
    neu = {seite: sid for seite, sid in ist.items() if altlast.get(seite) != sid}
    assert not neu, f"Seite rendert eine unbekannte Maske: {neu}"
    behoben = sorted(set(altlast) - set(ist))
    assert not behoben, f"Repariert - bitte aus config/frontend_seiten_ohne_maske.json nehmen: {behoben}"
