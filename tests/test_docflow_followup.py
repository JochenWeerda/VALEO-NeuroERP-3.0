"""Reine Logik-Tests der Vorgangs-Followups (DOM-DOC-004.3)."""

from __future__ import annotations

from datetime import date

import pytest

from app.services.docflow_followup_service import followup_overdue

pytestmark = pytest.mark.unit

TODAY = date(2026, 6, 11)


def test_offen_und_faellig_in_vergangenheit_ist_ueberfaellig():
    assert followup_overdue(date(2026, 6, 1), "offen", TODAY) is True


def test_offen_und_zukuenftig_nicht_ueberfaellig():
    assert followup_overdue(date(2026, 7, 1), "offen", TODAY) is False


def test_erledigt_nie_ueberfaellig():
    assert followup_overdue(date(2026, 1, 1), "erledigt", TODAY) is False


def test_ohne_faelligkeit_nicht_ueberfaellig():
    assert followup_overdue(None, "offen", TODAY) is False


def test_heute_faellig_nicht_ueberfaellig():
    assert followup_overdue(TODAY, "offen", TODAY) is False
