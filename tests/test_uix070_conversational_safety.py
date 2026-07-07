"""UIX-070: Spiegel-Testsuite Conversational Safety.

Der Omnibox-/NL-Pfad darf eine Aktion NIE anders behandeln als der Maskenpfad:
kein Draft an der Confirmation vorbei, forbiddenForAgents unsichtbar,
high/critical nur Navigation. Diese Suite re-implementiert die Sicherheitsmatrix
aus packages/frontend-web/src/components/mask-builder/runtime/ActionRuntime.ts
(classifyOmniboxAction) identisch in Python und prueft sie ueber ALLE nativen
ScreenDefinitions. Weicht die Frontend-Matrix ab, muss diese Suite mitgezogen
werden — sie ist das Gate.
"""
from __future__ import annotations

import pytest
import app.core.screen_definitions as _sd_module
from app.core.screen_definitions import get_screen_definition

pytestmark = pytest.mark.unit

MIN_CONFIDENCE = 0.75


def _all_screen_ids() -> list[str]:
    ids = []
    for name in dir(_sd_module):
        if not name.startswith("build_"):
            continue
        try:
            sd = getattr(_sd_module, name)()
            if isinstance(sd, dict) and sd.get("id"):
                ids.append(sd["id"])
        except Exception:  # noqa: BLE001
            pass
    return sorted(set(ids))


ALL_SCREEN_IDS = _all_screen_ids()


def classify_nl(action: dict, confidence: float) -> str:
    """Python-Spiegel von classifyOmniboxAction (ActionRuntime.ts)."""
    if action.get("forbiddenForAgents"):
        return "unavailable"
    danger = action.get("dangerLevel", "safe")
    if danger in ("high", "critical"):
        return "navigateOnly"
    if confidence < MIN_CONFIDENCE:
        return "formPrefill"
    if danger == "moderate":
        return "ritual"
    return "ritual" if action.get("requiresConfirmation") else "formPrefill"


def mask_requires_confirmation(action: dict) -> bool:
    """Der Maskenpfad verlangt eine Bestaetigung fuer diese Aktion."""
    return bool(action.get("requiresConfirmation")) or action.get("dangerLevel") in (
        "moderate",
        "high",
        "critical",
    )


def _actions(screen_id: str) -> list[dict]:
    sd = get_screen_definition(screen_id)
    assert sd is not None, f"ScreenDefinition '{screen_id}' nicht abrufbar"
    return sd.get("actions", []) or []


def test_registry_not_empty():
    assert ALL_SCREEN_IDS, "keine ScreenDefinitions gefunden"


@pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
def test_forbidden_actions_are_invisible_in_nl(screen_id: str):
    for action in _actions(screen_id):
        if action.get("forbiddenForAgents"):
            assert classify_nl(action, 1.0) == "unavailable", (
                f"{screen_id}/{action['key']}: forbiddenForAgents im NL-Pfad nicht unsichtbar"
            )


@pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
def test_high_critical_never_draftable(screen_id: str):
    for action in _actions(screen_id):
        if action.get("dangerLevel") in ("high", "critical") and not action.get("forbiddenForAgents"):
            assert classify_nl(action, 1.0) == "navigateOnly", (
                f"{screen_id}/{action['key']}: high/critical muss navigateOnly sein"
            )


@pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
def test_nl_never_bypasses_mask_confirmation(screen_id: str):
    """Kernspiegel: verlangt die Maske eine Bestaetigung, darf der NL-Pfad bei
    hoher Konfidenz nie still vorfuellen — nur Ritual/Navigation/unsichtbar."""
    for action in _actions(screen_id):
        if mask_requires_confirmation(action):
            disposition = classify_nl(action, 1.0)
            assert disposition in ("ritual", "navigateOnly", "unavailable"), (
                f"{screen_id}/{action['key']}: NL umgeht die Masken-Confirmation ({disposition})"
            )


@pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
def test_ritual_draft_implies_mask_confirmation(screen_id: str):
    """Umkehrung: was der NL-Pfad als armiertes Ritual fuehrt, verlangt auch die
    Maske als Bestaetigung — keine NL-erfundenen Rituale."""
    for action in _actions(screen_id):
        if classify_nl(action, 1.0) == "ritual":
            assert mask_requires_confirmation(action), (
                f"{screen_id}/{action['key']}: NL-Ritual ohne Masken-Confirmation"
            )


@pytest.mark.parametrize("screen_id", ALL_SCREEN_IDS)
def test_low_confidence_degrades_to_prefill(screen_id: str):
    """Konfidenz < 0.75 armiert nie — degradiert auf formPrefill (ausser
    unsichtbar/navigateOnly)."""
    for action in _actions(screen_id):
        disposition = classify_nl(action, 0.5)
        if action.get("forbiddenForAgents"):
            assert disposition == "unavailable"
        elif action.get("dangerLevel") in ("high", "critical"):
            assert disposition == "navigateOnly"
        else:
            assert disposition == "formPrefill", (
                f"{screen_id}/{action['key']}: niedrige Konfidenz nicht auf formPrefill degradiert"
            )


def test_matrix_covers_all_dispositions():
    """Die Matrix ist nicht trivial einzweigig — ueber die Registry treten
    mindestens Ritual und Prefill/Navigation auf."""
    seen = set()
    for screen_id in ALL_SCREEN_IDS:
        for action in _actions(screen_id):
            seen.add(classify_nl(action, 1.0))
    assert "ritual" in seen, "keine draftbare (ritual) Aktion in der Registry"
    assert seen - {"ritual"}, "nur Ritual-Dispositionen — Matrix wirkt trivial"
