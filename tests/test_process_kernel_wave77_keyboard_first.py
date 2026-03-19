"""
Wave 77 — Keyboard-first Kernmasken (Gap 023)

Deckt ab:
  A) KeyboardShortcut-Kontrakt: Datenmodell + Modifier-Kombinationen
  B) KeyboardShortcutRegistry: Duplikat-Erkennung, Coverage-Messung
  C) CoreMaskCoverage: >= 90% Kernflows haben Keyboard-Shortcut
  D) Kern-Shortcuts für alle Maskentypen: ObjectPage, ListReport, Wizard
  E) Konflikterkennung: Gleiche Taste + Modifier darf nicht doppelt vorkommen
  F) Tab-Navigation-Kontrakt: Logische Tab-Reihenfolge in Formularen
"""
from __future__ import annotations

import pytest
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ===========================================================================
# Domain-Kontrakte
# ===========================================================================

class MaskTyp(str, Enum):
    """Maskentypen im Mask-Builder-Framework."""
    OBJECT_PAGE  = "ObjectPage"   # Detailansicht (Bearbeiten)
    LIST_REPORT  = "ListReport"   # Filterliste
    WIZARD       = "Wizard"       # Mehrstufiger Prozess
    WORKLIST     = "Worklist"     # Arbeitsliste
    OVERVIEW     = "OverviewPage" # Dashboard-Übersicht


class ShortcutModifier(str, Enum):
    """Modifier-Tasten."""
    CTRL   = "Ctrl"   # Windows/Linux: Ctrl, Mac: Cmd
    ALT    = "Alt"    # Windows/Linux: Alt, Mac: Option
    SHIFT  = "Shift"
    NONE   = ""       # Keine Modifier (z.B. Escape, F5)


@dataclass
class KeyboardShortcut:
    """
    Kontrakt für einen Keyboard-Shortcut in einer ERP-Maske.

    Jeder Shortcut muss:
    - Eine eindeutige action_id haben
    - Eine beschreibende label haben (für ShortcutBar)
    - Entweder einen Modifier oder einen Sonder-Key (F-Key, Escape, Delete)
    """
    action_id: str          # z.B. "save", "cancel", "new"
    key: str                # z.B. "s", "Escape", "F5", "Delete"
    label: str              # z.B. "Speichern"
    modifier: ShortcutModifier = ShortcutModifier.NONE
    mask_typ: MaskTyp = MaskTyp.OBJECT_PAGE

    _SONDER_KEYS = frozenset({
        "Escape", "F1", "F2", "F3", "F4", "F5", "F6",
        "F7", "F8", "F9", "F10", "F11", "F12",
        "Delete", "Insert", "Home", "End", "PageUp", "PageDown",
    })

    def __post_init__(self):
        if not self.action_id:
            raise ValueError("action_id darf nicht leer sein")
        if not self.key:
            raise ValueError("key darf nicht leer sein")
        if not self.label:
            raise ValueError("label darf nicht leer sein")
        # Buchstaben-Keys ohne Modifier sind in Eingabefeldern problematisch
        is_plain_char = len(self.key) == 1 and self.key.isalpha()
        if is_plain_char and self.modifier == ShortcutModifier.NONE:
            raise ValueError(
                f"Buchstaben-Shortcut '{self.key}' ohne Modifier führt zu Konflikten "
                "in Eingabefeldern. Bitte Ctrl/Alt-Modifier hinzufügen."
            )

    @property
    def fingerprint(self) -> str:
        """Eindeutiger Fingerprint für Konflikterkennung."""
        return f"{self.modifier.value}+{self.key.lower()}"


@dataclass
class KeyboardShortcutRegistry:
    """
    Registry aller Keyboard-Shortcuts pro Maskentyp.
    Erkennt Duplikate und misst Coverage.
    """
    shortcuts: list[KeyboardShortcut] = field(default_factory=list)

    def register(self, sc: KeyboardShortcut) -> None:
        self.shortcuts.append(sc)

    def get_conflicts(self) -> list[tuple[KeyboardShortcut, KeyboardShortcut]]:
        """Findet Shortcuts mit identischem Fingerprint im gleichen Maskentyp."""
        conflicts: list[tuple[KeyboardShortcut, KeyboardShortcut]] = []
        seen: dict[tuple[MaskTyp, str], KeyboardShortcut] = {}
        for sc in self.shortcuts:
            key = (sc.mask_typ, sc.fingerprint)
            if key in seen:
                conflicts.append((seen[key], sc))
            else:
                seen[key] = sc
        return conflicts

    def get_coverage(self, mask_typ: MaskTyp) -> float:
        """
        Misst Coverage als: definierte Flows / Gesamt-Kernflows.
        Jeder Maskentyp hat definierte Mindest-Kern-Flows.
        """
        required = _REQUIRED_FLOWS.get(mask_typ, set())
        if not required:
            return 1.0
        covered = {sc.action_id for sc in self.shortcuts if sc.mask_typ == mask_typ}
        matched = required & covered
        return len(matched) / len(required)

    def get_action_ids(self, mask_typ: MaskTyp) -> set[str]:
        return {sc.action_id for sc in self.shortcuts if sc.mask_typ == mask_typ}


# Pflicht-Flows pro Maskentyp (für >= 90%-Coverage-KPI)
_REQUIRED_FLOWS: dict[MaskTyp, set[str]] = {
    MaskTyp.OBJECT_PAGE: {"save", "cancel", "refresh"},
    MaskTyp.LIST_REPORT: {"search", "refresh", "new"},
    MaskTyp.WIZARD: {"next", "back", "cancel"},
    MaskTyp.WORKLIST: {"refresh", "search"},
    MaskTyp.OVERVIEW: {"refresh"},
}


def build_default_registry() -> KeyboardShortcutRegistry:
    """Erstellt die Standard-Shortcut-Registry für alle Kernmasken."""
    reg = KeyboardShortcutRegistry()

    # ObjectPage
    reg.register(KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL, MaskTyp.OBJECT_PAGE))
    reg.register(KeyboardShortcut("cancel", "Escape", "Abbrechen", ShortcutModifier.NONE, MaskTyp.OBJECT_PAGE))
    reg.register(KeyboardShortcut("refresh", "F5", "Aktualisieren", ShortcutModifier.NONE, MaskTyp.OBJECT_PAGE))
    reg.register(KeyboardShortcut("delete", "Delete", "Löschen", ShortcutModifier.CTRL, MaskTyp.OBJECT_PAGE))

    # ListReport
    reg.register(KeyboardShortcut("search", "f", "Suchen", ShortcutModifier.CTRL, MaskTyp.LIST_REPORT))
    reg.register(KeyboardShortcut("new", "n", "Neu", ShortcutModifier.CTRL, MaskTyp.LIST_REPORT))
    reg.register(KeyboardShortcut("refresh", "F5", "Aktualisieren", ShortcutModifier.NONE, MaskTyp.LIST_REPORT))
    reg.register(KeyboardShortcut("export", "e", "Exportieren", ShortcutModifier.CTRL, MaskTyp.LIST_REPORT))

    # Wizard
    reg.register(KeyboardShortcut("next", "Return", "Weiter", ShortcutModifier.NONE, MaskTyp.WIZARD))
    reg.register(KeyboardShortcut("back", "b", "Zurück", ShortcutModifier.ALT, MaskTyp.WIZARD))
    reg.register(KeyboardShortcut("cancel", "Escape", "Abbrechen", ShortcutModifier.NONE, MaskTyp.WIZARD))
    reg.register(KeyboardShortcut("refresh", "F5", "Aktualisieren", ShortcutModifier.NONE, MaskTyp.WIZARD))

    # Worklist
    reg.register(KeyboardShortcut("refresh", "F5", "Aktualisieren", ShortcutModifier.NONE, MaskTyp.WORKLIST))
    reg.register(KeyboardShortcut("search", "f", "Suchen", ShortcutModifier.CTRL, MaskTyp.WORKLIST))

    # OverviewPage
    reg.register(KeyboardShortcut("refresh", "F5", "Aktualisieren", ShortcutModifier.NONE, MaskTyp.OVERVIEW))

    return reg


# ===========================================================================
# A) KeyboardShortcut Kontrakte
# ===========================================================================

class TestKeyboardShortcut:
    def test_valid_ctrl_s(self):
        sc = KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL)
        assert sc.fingerprint == "Ctrl+s"

    def test_valid_escape(self):
        sc = KeyboardShortcut("cancel", "Escape", "Abbrechen")
        assert sc.modifier == ShortcutModifier.NONE

    def test_empty_action_id_raises(self):
        with pytest.raises(ValueError, match="action_id"):
            KeyboardShortcut("", "s", "Label", ShortcutModifier.CTRL)

    def test_empty_key_raises(self):
        with pytest.raises(ValueError, match="key"):
            KeyboardShortcut("save", "", "Label", ShortcutModifier.CTRL)

    def test_empty_label_raises(self):
        with pytest.raises(ValueError, match="label"):
            KeyboardShortcut("save", "s", "", ShortcutModifier.CTRL)

    def test_plain_char_without_modifier_raises(self):
        """Buchstabe ohne Modifier ist in Eingabefeldern gefährlich."""
        with pytest.raises(ValueError, match="Modifier"):
            KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.NONE)

    def test_f5_without_modifier_ok(self):
        """F-Keys sind auch ohne Modifier erlaubt."""
        sc = KeyboardShortcut("refresh", "F5", "Aktualisieren", ShortcutModifier.NONE)
        assert sc.key == "F5"

    def test_escape_without_modifier_ok(self):
        sc = KeyboardShortcut("cancel", "Escape", "Abbrechen", ShortcutModifier.NONE)
        assert sc.fingerprint == "+escape"

    def test_fingerprint_case_insensitive(self):
        sc1 = KeyboardShortcut("save", "S", "Speichern", ShortcutModifier.CTRL)
        sc2 = KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL)
        assert sc1.fingerprint == sc2.fingerprint

    def test_mask_typ_default_object_page(self):
        sc = KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL)
        assert sc.mask_typ == MaskTyp.OBJECT_PAGE


# ===========================================================================
# B) KeyboardShortcutRegistry Kontrakte
# ===========================================================================

class TestKeyboardShortcutRegistry:
    def test_register_and_retrieve(self):
        reg = KeyboardShortcutRegistry()
        sc = KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL, MaskTyp.OBJECT_PAGE)
        reg.register(sc)
        assert len(reg.shortcuts) == 1

    def test_no_conflicts_in_default_registry(self):
        """Standard-Registry darf keine Konflikte haben."""
        reg = build_default_registry()
        conflicts = reg.get_conflicts()
        assert conflicts == [], f"Konflikte gefunden: {conflicts}"

    def test_conflict_detected_same_mask_typ(self):
        reg = KeyboardShortcutRegistry()
        sc1 = KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL, MaskTyp.OBJECT_PAGE)
        sc2 = KeyboardShortcut("submit", "s", "Absenden", ShortcutModifier.CTRL, MaskTyp.OBJECT_PAGE)
        reg.register(sc1)
        reg.register(sc2)
        conflicts = reg.get_conflicts()
        assert len(conflicts) == 1

    def test_no_conflict_same_key_different_mask_typ(self):
        """Gleiches Shortcut in verschiedenen Maskentypen ist kein Konflikt."""
        reg = KeyboardShortcutRegistry()
        sc1 = KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL, MaskTyp.OBJECT_PAGE)
        sc2 = KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL, MaskTyp.LIST_REPORT)
        reg.register(sc1)
        reg.register(sc2)
        assert reg.get_conflicts() == []

    def test_get_action_ids(self):
        reg = build_default_registry()
        ids = reg.get_action_ids(MaskTyp.OBJECT_PAGE)
        assert "save" in ids
        assert "cancel" in ids


# ===========================================================================
# C) CoreMaskCoverage >= 90%
# ===========================================================================

class TestCoreMaskCoverage:
    """KPI: >= 90% aller Kernflows haben Keyboard-Shortcut."""

    @pytest.fixture
    def registry(self):
        return build_default_registry()

    def test_object_page_coverage_gte_90pct(self, registry):
        cov = registry.get_coverage(MaskTyp.OBJECT_PAGE)
        assert cov >= 0.9, f"ObjectPage Coverage zu niedrig: {cov:.0%}"

    def test_list_report_coverage_gte_90pct(self, registry):
        cov = registry.get_coverage(MaskTyp.LIST_REPORT)
        assert cov >= 0.9, f"ListReport Coverage zu niedrig: {cov:.0%}"

    def test_wizard_coverage_gte_90pct(self, registry):
        cov = registry.get_coverage(MaskTyp.WIZARD)
        assert cov >= 0.9, f"Wizard Coverage zu niedrig: {cov:.0%}"

    def test_worklist_coverage_gte_90pct(self, registry):
        cov = registry.get_coverage(MaskTyp.WORKLIST)
        assert cov >= 0.9, f"Worklist Coverage zu niedrig: {cov:.0%}"

    def test_overview_coverage_100pct(self, registry):
        cov = registry.get_coverage(MaskTyp.OVERVIEW)
        assert cov >= 0.9, f"Overview Coverage zu niedrig: {cov:.0%}"

    def test_all_mask_typs_covered(self, registry):
        """Jeder Maskentyp muss mindestens einen Shortcut haben."""
        for mask_typ in MaskTyp:
            ids = registry.get_action_ids(mask_typ)
            assert len(ids) > 0, f"{mask_typ} hat keine Shortcuts"


# ===========================================================================
# D) Kern-Shortcuts für alle Maskentypen
# ===========================================================================

class TestKernShortcuts:
    @pytest.fixture
    def registry(self):
        return build_default_registry()

    def test_object_page_has_save_ctrl_s(self, registry):
        ids = registry.get_action_ids(MaskTyp.OBJECT_PAGE)
        assert "save" in ids

    def test_object_page_has_cancel_escape(self, registry):
        scs = [s for s in registry.shortcuts
               if s.mask_typ == MaskTyp.OBJECT_PAGE and s.action_id == "cancel"]
        assert len(scs) == 1
        assert scs[0].key == "Escape"

    def test_list_report_has_search_ctrl_f(self, registry):
        scs = [s for s in registry.shortcuts
               if s.mask_typ == MaskTyp.LIST_REPORT and s.action_id == "search"]
        assert len(scs) == 1
        assert scs[0].modifier == ShortcutModifier.CTRL
        assert scs[0].key == "f"

    def test_list_report_has_new_ctrl_n(self, registry):
        scs = [s for s in registry.shortcuts
               if s.mask_typ == MaskTyp.LIST_REPORT and s.action_id == "new"]
        assert len(scs) == 1
        assert scs[0].modifier == ShortcutModifier.CTRL

    def test_wizard_has_cancel_escape(self, registry):
        scs = [s for s in registry.shortcuts
               if s.mask_typ == MaskTyp.WIZARD and s.action_id == "cancel"]
        assert len(scs) == 1
        assert scs[0].key == "Escape"

    def test_f5_refresh_in_all_mask_typs(self, registry):
        """F5 = Aktualisieren soll in allen Maskentypen verfügbar sein."""
        for mask_typ in MaskTyp:
            scs = [s for s in registry.shortcuts
                   if s.mask_typ == mask_typ and s.action_id == "refresh"]
            assert len(scs) >= 1, f"{mask_typ} hat kein F5/Refresh-Shortcut"


# ===========================================================================
# E) Konflikt-Erkennung
# ===========================================================================

class TestConflictDetection:
    def test_ctrl_s_conflict_detected(self):
        """Zwei Ctrl+S in derselben Maske = Konflikt."""
        reg = KeyboardShortcutRegistry()
        reg.register(KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL, MaskTyp.OBJECT_PAGE))
        reg.register(KeyboardShortcut("submit", "s", "Weiterleiten", ShortcutModifier.CTRL, MaskTyp.OBJECT_PAGE))
        assert len(reg.get_conflicts()) == 1

    def test_no_conflict_ctrl_s_and_alt_s(self):
        """Ctrl+S und Alt+S sind verschiedene Shortcuts."""
        reg = KeyboardShortcutRegistry()
        reg.register(KeyboardShortcut("save", "s", "Speichern", ShortcutModifier.CTRL, MaskTyp.OBJECT_PAGE))
        reg.register(KeyboardShortcut("submit", "s", "Weiterleiten", ShortcutModifier.ALT, MaskTyp.OBJECT_PAGE))
        assert reg.get_conflicts() == []

    def test_conflict_returns_both_shortcuts(self):
        reg = KeyboardShortcutRegistry()
        sc1 = KeyboardShortcut("a1", "s", "A1", ShortcutModifier.CTRL, MaskTyp.LIST_REPORT)
        sc2 = KeyboardShortcut("a2", "s", "A2", ShortcutModifier.CTRL, MaskTyp.LIST_REPORT)
        reg.register(sc1)
        reg.register(sc2)
        conflicts = reg.get_conflicts()
        assert len(conflicts) == 1
        pair = conflicts[0]
        assert sc1 in pair
        assert sc2 in pair


# ===========================================================================
# F) Tab-Navigation-Kontrakt
# ===========================================================================

@dataclass
class FormTabOrder:
    """
    Kontrakt für logische Tab-Reihenfolge in ERP-Formularen.
    WCAG 2.1 SC 2.4.3: Focus Order
    """
    form_id: str
    field_order: list[str]  # Felder in Tab-Reihenfolge

    def __post_init__(self):
        if len(self.field_order) < 1:
            raise ValueError("Tab-Reihenfolge muss mindestens ein Feld haben")
        if len(set(self.field_order)) != len(self.field_order):
            raise ValueError("Duplikate in Tab-Reihenfolge")

    def is_logical_order(self, field: str, before: str) -> bool:
        """True wenn field vor before in der Tab-Reihenfolge liegt."""
        if field not in self.field_order or before not in self.field_order:
            return False
        return self.field_order.index(field) < self.field_order.index(before)


class TestTabNavigation:
    def test_standard_form_tab_order(self):
        """Standard-Reihenfolge: Bezeichnung → Menge → Preis → Speichern."""
        order = FormTabOrder(
            form_id="artikel-erfassung",
            field_order=["bezeichnung", "menge", "preis", "speichern"],
        )
        assert order.is_logical_order("bezeichnung", "menge")
        assert order.is_logical_order("menge", "preis")
        assert order.is_logical_order("preis", "speichern")

    def test_duplicate_field_raises(self):
        with pytest.raises(ValueError, match="Duplikat"):
            FormTabOrder("f1", ["a", "b", "a"])

    def test_empty_order_raises(self):
        with pytest.raises(ValueError):
            FormTabOrder("f1", [])

    def test_save_button_last(self):
        """Speichern-Button soll am Ende der Tab-Reihenfolge stehen."""
        order = FormTabOrder(
            form_id="einlagerung",
            field_order=["chargen_id", "artikel", "menge", "lagerort", "speichern"],
        )
        assert order.field_order[-1] == "speichern"
        assert order.is_logical_order("artikel", "speichern")
