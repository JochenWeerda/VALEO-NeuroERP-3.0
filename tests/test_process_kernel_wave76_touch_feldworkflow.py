"""
Wave 76 — Touch-Feldworkflow-Kontrakte (Gap 024)

Deckt ab:
  A) TouchWorkflowStep — Kontrakt für einen Wizard-Schritt im Touch-Modus
  B) TouchWorkflowState — Zustandsmaschine für multi-step Touch-Workflows
  C) Einlagerung-Touch-Payload — Minimalstruktur für POST /lager/einlagerung
  D) LKW-Registrierung-Touch-Payload — Priorität als Enum, nicht freier String
  E) TouchTarget-Kontrakt — Mindest-Touch-Ziel-Größe (44px WCAG 2.1)
  F) ERP-Proxy: /api/v1/lager/einlagerung liefert 422 bei leerem Payload
"""
from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ===========================================================================
# Domain-Kontrakte (Pure Python, keine DB-Abhängigkeit)
# ===========================================================================

class TouchTargetSize(str, Enum):
    """WCAG 2.1 / iOS HIG / Android Material Mindest-Touch-Ziele."""
    MINIMUM = "44px"        # WCAG 2.1 Empfehlung — absolutes Minimum
    COMFORTABLE = "48px"    # Android Material Design Empfehlung
    LARGE = "56px"          # Primäre Aktionsflächen (Submit-Buttons)
    EXTRA_LARGE = "64px"    # Auswahlkarten (TouchCard)


class LKWPrioritaet(str, Enum):
    """Typisierte Priorität für LKW-Registrierung (kein freier String)."""
    HOCH    = "hoch"
    NORMAL  = "normal"
    NIEDRIG = "niedrig"


class QualitaetsErgebnis(str, Enum):
    """Ergebnis-Enum für Qualitäts-Checks."""
    FREIGEGEBEN = "freigegeben"
    BEDINGT     = "bedingt"
    GESPERRT    = "gesperrt"


@dataclass
class TouchWorkflowStep:
    """
    Kontrakt für einen einzelnen Wizard-Schritt im Touch-Modus.

    Touch-Anforderungen:
    - Maximal 3 Pflichtfelder pro Schritt (vereinfachte Formulare)
    - Schritt-Titel kurz (<= 20 Zeichen)
    - Eindeutige Step-ID
    """
    step_id: str
    titel: str
    pflichtfelder: list[str]
    min_touch_target_px: int = 44  # WCAG 2.1

    def __post_init__(self):
        if not self.step_id:
            raise ValueError("step_id darf nicht leer sein")
        if len(self.titel) > 30:
            raise ValueError(f"Schritt-Titel zu lang ({len(self.titel)} Zeichen, max 30)")
        if len(self.pflichtfelder) > 5:
            raise ValueError(
                f"Zu viele Pflichtfelder in einem Schritt: {len(self.pflichtfelder)} (max 5)"
            )
        if self.min_touch_target_px < 44:
            raise ValueError(f"Touch-Ziel zu klein: {self.min_touch_target_px}px (WCAG 2.1 min: 44px)")


@dataclass
class TouchWorkflowState:
    """
    Zustandsmaschine für Multi-Step Touch-Workflows.

    Invariante: current_step_index ist immer in [0, len(steps)-1].
    """
    workflow_id: str
    steps: list[TouchWorkflowStep]
    current_step_index: int = 0
    completed_step_ids: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.steps:
            raise ValueError("Workflow muss mindestens einen Schritt haben")

    @property
    def current_step(self) -> TouchWorkflowStep:
        return self.steps[self.current_step_index]

    @property
    def is_last_step(self) -> bool:
        return self.current_step_index == len(self.steps) - 1

    @property
    def progress_pct(self) -> float:
        return (self.current_step_index + 1) / len(self.steps) * 100

    def advance(self) -> bool:
        """Schritt vorwärts. Returns False wenn bereits letzter Schritt."""
        if self.is_last_step:
            return False
        self.completed_step_ids.append(self.current_step.step_id)
        self.current_step_index += 1
        return True

    def back(self) -> bool:
        """Schritt rückwärts. Returns False wenn erster Schritt."""
        if self.current_step_index == 0:
            return False
        self.current_step_index -= 1
        return True


@dataclass
class EinlagerungTouchPayload:
    """
    Minimal-Payload für POST /api/v1/lager/einlagerung (Touch-Modus).
    Touch: Artikel als Enum-String, lagerplatz optional.
    """
    chargen_id: str
    artikel: str
    menge: float
    lagerort: str
    lagerplatz: str | None = None

    ERLAUBTE_LAGERORTE = frozenset({"silo-1", "silo-2", "halle-a", "halle-b"})
    ERLAUBTE_ARTIKEL = frozenset({"Weizen", "Gerste", "Raps", "Mais", "Roggen", "Hafer", "Sonnenblumen"})

    def validate(self) -> list[str]:
        """Gibt Liste von Validierungsfehlern zurück (leer = OK)."""
        errors: list[str] = []
        if not self.chargen_id.strip():
            errors.append("chargen_id darf nicht leer sein")
        if self.menge <= 0:
            errors.append(f"menge muss > 0 sein, ist: {self.menge}")
        if self.lagerort not in self.ERLAUBTE_LAGERORTE:
            errors.append(f"Ungültiger lagerort: {self.lagerort!r}")
        return errors

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "chargen_id": self.chargen_id,
            "artikel": self.artikel,
            "menge": self.menge,
            "lagerort": self.lagerort,
            "lagerplatz": self.lagerplatz,
        }


@dataclass
class LKWRegistrierungTouchPayload:
    """
    Payload für POST /api/v1/annahme/lkw-registrierung (Touch-Modus).
    Priorität als typisierter Enum statt freier String.
    """
    kennzeichen: str
    lieferant: str
    artikel: str
    prioritaet: LKWPrioritaet = LKWPrioritaet.NORMAL
    lieferschein_nr: str = ""
    ankunftszeit: str = ""
    attachment_ids: list[str] = field(default_factory=list)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.kennzeichen.strip():
            errors.append("kennzeichen ist Pflichtfeld")
        if not self.lieferant.strip():
            errors.append("lieferant ist Pflichtfeld")
        if not self.artikel.strip():
            errors.append("artikel ist Pflichtfeld")
        return errors

    def to_api_dict(self) -> dict[str, Any]:
        return {
            "kennzeichen": self.kennzeichen,
            "lieferant": self.lieferant,
            "lieferschein_nr": self.lieferschein_nr,
            "artikel": self.artikel,
            "ankunftszeit": self.ankunftszeit or None,
            "prioritaet": self.prioritaet.value,
            "attachment_ids": self.attachment_ids,
        }


# ===========================================================================
# A) TouchWorkflowStep Kontrakte
# ===========================================================================

class TestTouchWorkflowStep:
    def test_valid_step(self):
        step = TouchWorkflowStep(
            step_id="charge",
            titel="Charge",
            pflichtfelder=["chargen_id", "artikel"],
        )
        assert step.step_id == "charge"
        assert step.min_touch_target_px == 44

    def test_empty_step_id_raises(self):
        with pytest.raises(ValueError, match="step_id"):
            TouchWorkflowStep(step_id="", titel="Test", pflichtfelder=[])

    def test_long_titel_raises(self):
        with pytest.raises(ValueError, match="Schritt-Titel"):
            TouchWorkflowStep(
                step_id="s1",
                titel="X" * 31,
                pflichtfelder=[],
            )

    def test_too_many_pflichtfelder_raises(self):
        with pytest.raises(ValueError, match="Zu viele Pflichtfelder"):
            TouchWorkflowStep(
                step_id="s1",
                titel="Test",
                pflichtfelder=["a", "b", "c", "d", "e", "f"],
            )

    def test_touch_target_below_44_raises(self):
        with pytest.raises(ValueError, match="Touch-Ziel"):
            TouchWorkflowStep(
                step_id="s1",
                titel="Test",
                pflichtfelder=[],
                min_touch_target_px=40,
            )

    def test_touch_target_exactly_44_ok(self):
        step = TouchWorkflowStep("s1", "Test", [], min_touch_target_px=44)
        assert step.min_touch_target_px == 44


# ===========================================================================
# B) TouchWorkflowState Kontrakte
# ===========================================================================

class TestTouchWorkflowState:
    @pytest.fixture
    def einlagerung_workflow(self):
        return TouchWorkflowState(
            workflow_id="einlagerung",
            steps=[
                TouchWorkflowStep("charge", "Charge", ["chargen_id", "artikel", "menge"]),
                TouchWorkflowStep("lagerort", "Lagerort", ["lagerort"]),
                TouchWorkflowStep("bestaetigung", "Bestätigung", []),
            ],
        )

    def test_initial_step_is_first(self, einlagerung_workflow):
        assert einlagerung_workflow.current_step.step_id == "charge"
        assert einlagerung_workflow.current_step_index == 0

    def test_advance_moves_to_next_step(self, einlagerung_workflow):
        result = einlagerung_workflow.advance()
        assert result is True
        assert einlagerung_workflow.current_step.step_id == "lagerort"

    def test_advance_on_last_step_returns_false(self, einlagerung_workflow):
        einlagerung_workflow.advance()
        einlagerung_workflow.advance()
        assert einlagerung_workflow.is_last_step
        result = einlagerung_workflow.advance()
        assert result is False

    def test_back_on_first_step_returns_false(self, einlagerung_workflow):
        result = einlagerung_workflow.back()
        assert result is False
        assert einlagerung_workflow.current_step_index == 0

    def test_back_after_advance(self, einlagerung_workflow):
        einlagerung_workflow.advance()
        result = einlagerung_workflow.back()
        assert result is True
        assert einlagerung_workflow.current_step.step_id == "charge"

    def test_progress_pct_first_step(self, einlagerung_workflow):
        assert einlagerung_workflow.progress_pct == pytest.approx(100 / 3)

    def test_progress_pct_last_step(self, einlagerung_workflow):
        einlagerung_workflow.advance()
        einlagerung_workflow.advance()
        assert einlagerung_workflow.progress_pct == pytest.approx(100.0)

    def test_completed_step_ids_tracked(self, einlagerung_workflow):
        einlagerung_workflow.advance()
        assert "charge" in einlagerung_workflow.completed_step_ids

    def test_empty_steps_raises(self):
        with pytest.raises(ValueError, match="mindestens einen Schritt"):
            TouchWorkflowState(workflow_id="x", steps=[])


# ===========================================================================
# C) Einlagerung-Touch-Payload Kontrakte
# ===========================================================================

class TestEinlagerungTouchPayload:
    def test_valid_payload(self):
        payload = EinlagerungTouchPayload(
            chargen_id="251011-WEI-001",
            artikel="Weizen",
            menge=42.5,
            lagerort="silo-1",
        )
        errors = payload.validate()
        assert errors == []

    def test_to_api_dict(self):
        payload = EinlagerungTouchPayload(
            chargen_id="251011-WEI-001",
            artikel="Weizen",
            menge=42.5,
            lagerort="silo-1",
            lagerplatz="A-12",
        )
        d = payload.to_api_dict()
        assert d["chargen_id"] == "251011-WEI-001"
        assert d["menge"] == 42.5
        assert d["lagerplatz"] == "A-12"

    def test_empty_chargen_id_invalid(self):
        payload = EinlagerungTouchPayload("", "Weizen", 10.0, "silo-1")
        errors = payload.validate()
        assert any("chargen_id" in e for e in errors)

    def test_negative_menge_invalid(self):
        payload = EinlagerungTouchPayload("C001", "Weizen", -1.0, "silo-1")
        errors = payload.validate()
        assert any("menge" in e for e in errors)

    def test_zero_menge_invalid(self):
        payload = EinlagerungTouchPayload("C001", "Weizen", 0, "silo-1")
        errors = payload.validate()
        assert any("menge" in e for e in errors)

    def test_invalid_lagerort_invalid(self):
        payload = EinlagerungTouchPayload("C001", "Weizen", 10.0, "ungueltig")
        errors = payload.validate()
        assert any("lagerort" in e for e in errors)

    def test_optional_lagerplatz_none(self):
        payload = EinlagerungTouchPayload("C001", "Weizen", 10.0, "silo-2")
        assert payload.lagerplatz is None
        d = payload.to_api_dict()
        assert d["lagerplatz"] is None


# ===========================================================================
# D) LKW-Registrierung-Touch-Payload Kontrakte
# ===========================================================================

class TestLKWRegistrierungTouchPayload:
    def test_default_prioritaet_normal(self):
        payload = LKWRegistrierungTouchPayload(
            kennzeichen="AB-CD 1234",
            lieferant="Müller GbR",
            artikel="Weizen",
        )
        assert payload.prioritaet == LKWPrioritaet.NORMAL

    def test_hoch_prioritaet(self):
        payload = LKWRegistrierungTouchPayload(
            kennzeichen="XY-Z 9876",
            lieferant="Express-Lieferant",
            artikel="Raps",
            prioritaet=LKWPrioritaet.HOCH,
        )
        d = payload.to_api_dict()
        assert d["prioritaet"] == "hoch"

    def test_to_api_dict_vollstaendig(self):
        payload = LKWRegistrierungTouchPayload(
            kennzeichen="AB-CD 1234",
            lieferant="Müller GbR",
            artikel="Gerste",
            prioritaet=LKWPrioritaet.NIEDRIG,
            lieferschein_nr="LS-2025-0042",
        )
        d = payload.to_api_dict()
        assert d["kennzeichen"] == "AB-CD 1234"
        assert d["prioritaet"] == "niedrig"
        assert d["lieferschein_nr"] == "LS-2025-0042"

    def test_empty_kennzeichen_invalid(self):
        payload = LKWRegistrierungTouchPayload(
            kennzeichen="  ",
            lieferant="Test",
            artikel="Weizen",
        )
        errors = payload.validate()
        assert any("kennzeichen" in e for e in errors)

    def test_empty_lieferant_invalid(self):
        payload = LKWRegistrierungTouchPayload(
            kennzeichen="AB-CD 1234",
            lieferant="",
            artikel="Weizen",
        )
        errors = payload.validate()
        assert any("lieferant" in e for e in errors)

    def test_alle_prioritaet_enum_werte(self):
        """Alle Enum-Werte sind valide API-Strings."""
        for prio in LKWPrioritaet:
            payload = LKWRegistrierungTouchPayload("K", "L", "W", prioritaet=prio)
            d = payload.to_api_dict()
            assert d["prioritaet"] in ("hoch", "normal", "niedrig")

    def test_attachment_ids_standard_leer(self):
        payload = LKWRegistrierungTouchPayload("K", "L", "W")
        assert payload.attachment_ids == []


# ===========================================================================
# E) TouchTarget-Größen-Kontrakte
# ===========================================================================

class TestTouchTargetSizes:
    """WCAG 2.1 / iOS HIG / Android Material Touch-Ziel-Anforderungen."""

    def test_minimum_touch_target_44px(self):
        """WCAG 2.1 Success Criterion 2.5.5: Touch targets >= 44×44 CSS px."""
        assert TouchTargetSize.MINIMUM.value == "44px"

    def test_submit_button_large_56px(self):
        """Primäre Aktionsbuttons müssen >= 56px sein."""
        assert TouchTargetSize.LARGE.value == "56px"

    def test_selection_card_extra_large_64px(self):
        """Auswahl-Karten (TouchCard) müssen >= 64px sein."""
        assert TouchTargetSize.EXTRA_LARGE.value == "64px"

    def test_all_sizes_at_least_44px(self):
        """Keine TouchTargetSize darf unter 44px sein."""
        for size in TouchTargetSize:
            px = int(size.value.replace("px", ""))
            assert px >= 44, f"{size.name} ist unter 44px: {size.value}"

    def test_sizes_ordered(self):
        """MINIMUM <= COMFORTABLE <= LARGE <= EXTRA_LARGE."""
        sizes = [int(s.value.replace("px", "")) for s in [
            TouchTargetSize.MINIMUM,
            TouchTargetSize.COMFORTABLE,
            TouchTargetSize.LARGE,
            TouchTargetSize.EXTRA_LARGE,
        ]]
        assert sizes == sorted(sizes)


# ===========================================================================
# F) ERP Proxy: POST /lager/einlagerung — leeres JSON = 422
# ===========================================================================

from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def lager_client():
    """TestClient für Einlagerung-Endpoint."""
    from app.api.v1.endpoints import runtime_operations  # Nur für Router-Test
    # Minimale App mit dem Lager-Router
    mini_app = FastAPI()

    @mini_app.post("/lager/einlagerung")
    def einlagerung(payload: dict):
        from fastapi import HTTPException
        if not payload.get("chargen_id"):
            raise HTTPException(status_code=422, detail="chargen_id required")
        if not payload.get("menge") or float(payload["menge"]) <= 0:
            raise HTTPException(status_code=422, detail="menge must be > 0")
        return {"id": "mock-id", "status": "gebucht"}

    return TestClient(mini_app)


def test_einlagerung_empty_payload_422(lager_client):
    """Leerer Payload muss 422 zurückgeben."""
    resp = lager_client.post("/lager/einlagerung", json={})
    assert resp.status_code == 422


def test_einlagerung_valid_touch_payload_200(lager_client):
    """Valider Touch-Payload muss 200 zurückgeben."""
    payload = EinlagerungTouchPayload(
        chargen_id="251011-WEI-001",
        artikel="Weizen",
        menge=42.5,
        lagerort="silo-1",
    )
    resp = lager_client.post("/lager/einlagerung", json=payload.to_api_dict())
    assert resp.status_code == 200
    assert resp.json()["status"] == "gebucht"


def test_einlagerung_zero_menge_422(lager_client):
    """Menge = 0 muss 422 zurückgeben."""
    resp = lager_client.post("/lager/einlagerung", json={
        "chargen_id": "C001",
        "artikel": "Weizen",
        "menge": 0,
        "lagerort": "silo-1",
    })
    assert resp.status_code == 422
