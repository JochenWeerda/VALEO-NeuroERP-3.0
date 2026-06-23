"""DOM-HRM-004 Unit-Tests — Zeiterfassung, Arbeitszeitkonto, Abwesenheit."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.hrm_zeiterfassung_service import (
    VALID_ZEITBUCHUNG_TRANSITIONS,
    ZeiterfassungError,
    _berechne_stunden,
    transition_zeitbuchung,
    get_arbeitszeitkonto,
)
from app.services.hrm_abwesenheit_service import (
    VALID_ABWESENHEIT_TRANSITIONS,
    ABWESENHEIT_TYPEN,
    AbwesenheitError,
    create_abwesenheitsantrag,
    transition_abwesenheit,
)


# ---------------------------------------------------------------------------
# Zeiterfassung
# ---------------------------------------------------------------------------

def test_berechne_stunden_normal():
    assert _berechne_stunden("08:00", "17:00") == pytest.approx(9.0)


def test_berechne_stunden_halb():
    assert _berechne_stunden("08:00", "12:30") == pytest.approx(4.5)


def test_berechne_stunden_negativ():
    assert _berechne_stunden("17:00", "08:00") < 0


def test_valid_zeitbuchung_transitions():
    assert ("OFFEN", "GEBUCHT") in VALID_ZEITBUCHUNG_TRANSITIONS
    assert ("GEBUCHT", "KORRIGIERT") in VALID_ZEITBUCHUNG_TRANSITIONS
    assert ("KORRIGIERT", "STORNIERT") in VALID_ZEITBUCHUNG_TRANSITIONS


def test_zeitbuchung_transition_not_found():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(ZeiterfassungError):
        transition_zeitbuchung(db, "B1", "GEBUCHT", "T1", "op")


def test_zeitbuchung_invalid_transition():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "STORNIERT", "id": "B1"
    }
    with pytest.raises(ZeiterfassungError):
        transition_zeitbuchung(db, "B1", "GEBUCHT", "T1", "op")


def test_zeitbuchung_offen_to_gebucht():
    db = MagicMock()
    rec = {"status": "OFFEN", "id": "B1", "tenant_id": "T1"}
    updated = {**rec, "status": "GEBUCHT"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_zeitbuchung(db, "B1", "GEBUCHT", "T1", "op")
    assert result["status"] == "GEBUCHT"


def test_arbeitszeitkonto_ampel_gruen():
    db = MagicMock()
    db.execute.return_value.scalar.side_effect = [165.0, 168.0]
    result = get_arbeitszeitkonto(db, "M1", "T1", "2026-06")
    assert result["ampel"] == "gruen"
    assert result["differenz"] == pytest.approx(-3.0)


def test_arbeitszeitkonto_ampel_rot():
    db = MagicMock()
    db.execute.return_value.scalar.side_effect = [140.0, 168.0]
    result = get_arbeitszeitkonto(db, "M1", "T1", "2026-06")
    assert result["ampel"] == "rot"


# ---------------------------------------------------------------------------
# Abwesenheit
# ---------------------------------------------------------------------------

def test_abwesenheit_typen_vollstaendig():
    assert "URLAUB" in ABWESENHEIT_TYPEN
    assert "KRANKHEIT" in ABWESENHEIT_TYPEN
    assert "ELTERNZEIT" in ABWESENHEIT_TYPEN


def test_create_abwesenheit_invalid_typ():
    db = MagicMock()
    with pytest.raises(AbwesenheitError, match="Unbekannter"):
        create_abwesenheitsantrag(db, "T1", "M1", "GOLF", "2026-06-01", "2026-06-05", 5)


def test_create_abwesenheit_invalid_tage():
    db = MagicMock()
    with pytest.raises(AbwesenheitError, match="> 0"):
        create_abwesenheitsantrag(db, "T1", "M1", "URLAUB", "2026-06-01", "2026-06-01", 0)


def test_abwesenheit_transition_beantragt_to_genehmigt():
    db = MagicMock()
    rec = {"status": "BEANTRAGT", "id": "A1", "tenant_id": "T1"}
    updated = {**rec, "status": "GENEHMIGT"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_abwesenheit(db, "A1", "GENEHMIGT", "T1", "hr_manager")
    assert result["status"] == "GENEHMIGT"


def test_abwesenheit_transition_invalid():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "VERBRAUCHT", "id": "A1"
    }
    with pytest.raises(AbwesenheitError):
        transition_abwesenheit(db, "A1", "BEANTRAGT", "T1", "op")
