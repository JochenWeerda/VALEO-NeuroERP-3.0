"""DOM-POS-004 Unit-Tests — POS Tagesabschluss Lifecycle + TSE-Simulation."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.pos_tagesabschluss_service import (
    VALID_ABSCHLUSS_TRANSITIONS,
    POSTagesabschlussError,
    transition_tagesabschluss,
    simulate_tse_signatur,
)


def test_valid_transitions_complete():
    assert ("OFFEN", "IN_ABSCHLUSS") in VALID_ABSCHLUSS_TRANSITIONS
    assert ("IN_ABSCHLUSS", "Z_BON_ERSTELLT") in VALID_ABSCHLUSS_TRANSITIONS
    assert ("Z_BON_ERSTELLT", "TSE_SIGNIERT") in VALID_ABSCHLUSS_TRANSITIONS
    assert ("TSE_SIGNIERT", "DSFINVK_EXPORTIERT") in VALID_ABSCHLUSS_TRANSITIONS
    assert ("DSFINVK_EXPORTIERT", "ABGESCHLOSSEN") in VALID_ABSCHLUSS_TRANSITIONS


def test_transition_not_found():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(POSTagesabschlussError):
        transition_tagesabschluss(db, "TA1", "IN_ABSCHLUSS", "T1", "op")


def test_transition_invalid():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "ABGESCHLOSSEN", "id": "TA1"
    }
    with pytest.raises(POSTagesabschlussError):
        transition_tagesabschluss(db, "TA1", "OFFEN", "T1", "op")


def test_transition_offen_to_in_abschluss():
    db = MagicMock()
    rec = {"status": "OFFEN", "id": "TA1", "tenant_id": "T1"}
    updated = {**rec, "status": "IN_ABSCHLUSS"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_tagesabschluss(db, "TA1", "IN_ABSCHLUSS", "T1", "op")
    assert result["status"] == "IN_ABSCHLUSS"


def test_transition_in_abschluss_to_z_bon():
    db = MagicMock()
    rec = {"status": "IN_ABSCHLUSS", "id": "TA1", "tenant_id": "T1"}
    updated = {**rec, "status": "Z_BON_ERSTELLT", "z_bon_nr": "Z-2026-001"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_tagesabschluss(
        db, "TA1", "Z_BON_ERSTELLT", "T1", "op",
        payload={"z_bon_nr": "Z-2026-001", "umsatz_brutto_eur": 1234.56}
    )
    assert result["status"] == "Z_BON_ERSTELLT"


def test_tse_simulation_returns_sim_signatur():
    result = simulate_tse_signatur("KASSE-001", "Z-001", 999.99)
    assert "tse_signatur" in result
    assert result["tse_signatur"].startswith("SIM-SIG-")
    assert "hinweis" in result


def test_tse_simulation_deterministisch():
    r1 = simulate_tse_signatur("K1", "Z1", 100.0)
    r2 = simulate_tse_signatur("K1", "Z1", 100.0)
    assert r1["tse_signatur"] == r2["tse_signatur"]


def test_transition_fehler_path():
    db = MagicMock()
    rec = {"status": "IN_ABSCHLUSS", "id": "TA1", "tenant_id": "T1"}
    updated = {**rec, "status": "FEHLER", "fehler_grund": "TSE offline"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_tagesabschluss(
        db, "TA1", "FEHLER", "T1", "op",
        payload={"fehler_grund": "TSE offline"}
    )
    assert result["status"] == "FEHLER"
