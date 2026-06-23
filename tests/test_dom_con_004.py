"""DOM-CON-004 Unit-Tests — Kontrakt Lifecycle, Fixing, Settlement."""
from __future__ import annotations

from unittest.mock import MagicMock, patch, call
import pytest

from app.services.kontrakt_lifecycle_service import (
    VALID_KONTRAKT_TRANSITIONS,
    KontraktLifecycleError,
    transition_kontrakt,
    create_kontrakt_lifecycle,
)
from app.services.kontrakt_fixing_service import (
    KontraktFixingError,
    get_fixing_summary,
)
from app.services.kontrakt_settlement_service import (
    KontraktSettlementError,
    transition_settlement,
    VALID_SETTLEMENT_TRANSITIONS,
)


# ---------------------------------------------------------------------------
# Lifecycle Tests
# ---------------------------------------------------------------------------

def test_valid_transitions_complete():
    expected = {
        ("ENTWURF", "FREIGEGEBEN"),
        ("ENTWURF", "STORNIERT"),
        ("FREIGEGEBEN", "AKTIV"),
        ("FREIGEGEBEN", "STORNIERT"),
        ("AKTIV", "TEIL_ERFUELLT"),
        ("AKTIV", "ERFUELLT"),
        ("AKTIV", "STORNIERT"),
        ("TEIL_ERFUELLT", "ERFUELLT"),
        ("TEIL_ERFUELLT", "STORNIERT"),
    }
    assert VALID_KONTRAKT_TRANSITIONS == expected


def test_transition_kontrakt_invalid_raises():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "ABGESCHLOSSEN", "kontrakt_id": "K1"
    }
    with pytest.raises(KontraktLifecycleError):
        transition_kontrakt(db, "K1", "ENTWURF", "T1", "op")


def test_transition_kontrakt_not_found():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(KontraktLifecycleError):
        transition_kontrakt(db, "MISSING", "FREIGEGEBEN", "T1", "op")


def test_transition_entwurf_to_freigegeben():
    db = MagicMock()
    existing = {"status": "ENTWURF", "kontrakt_id": "K1", "tenant_id": "T1"}
    updated = {**existing, "status": "FREIGEGEBEN"}
    db.execute.return_value.mappings.return_value.first.side_effect = [existing, updated]
    result = transition_kontrakt(db, "K1", "FREIGEGEBEN", "T1", "admin")
    assert result["status"] == "FREIGEGEBEN"


def test_create_kontrakt_lifecycle_idempotent():
    db = MagicMock()
    existing = {"kontrakt_id": "K2", "status": "ENTWURF"}
    db.execute.return_value.mappings.return_value.first.return_value = existing
    result = create_kontrakt_lifecycle(
        db, "K2", "T1", "KNR-001", "ART-1", 100.0, 200.0, "LFT-1", "2026-06", "op"
    )
    assert result["kontrakt_id"] == "K2"


# ---------------------------------------------------------------------------
# Fixing Tests
# ---------------------------------------------------------------------------

def test_fixing_summary_empty():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.all.return_value = []
    db.execute.return_value.mappings.return_value.first.return_value = {"menge_t": 500.0}
    result = get_fixing_summary(db, "K1", "T1")
    assert result["gefixte_menge_t"] == 0.0
    assert result["offene_menge_t"] == 500.0
    assert result["vollstaendig_gefixt"] is False


def test_fixing_summary_vollstaendig():
    db = MagicMock()
    rows = [{"fixing_preis_eur_t": 200.0, "menge_t": 300.0},
            {"fixing_preis_eur_t": 210.0, "menge_t": 200.0}]
    db.execute.return_value.mappings.return_value.all.return_value = rows
    db.execute.return_value.mappings.return_value.first.return_value = {"menge_t": 500.0}
    result = get_fixing_summary(db, "K1", "T1")
    assert result["gefixte_menge_t"] == 500.0
    assert result["vollstaendig_gefixt"] is True
    assert result["avg_fixing_preis_eur_t"] == pytest.approx(204.0)


def test_fixing_avg_preis_gewichtet():
    db = MagicMock()
    rows = [{"fixing_preis_eur_t": 200.0, "menge_t": 100.0},
            {"fixing_preis_eur_t": 300.0, "menge_t": 100.0}]
    db.execute.return_value.mappings.return_value.all.return_value = rows
    db.execute.return_value.mappings.return_value.first.return_value = {"menge_t": 200.0}
    result = get_fixing_summary(db, "K1", "T1")
    assert result["avg_fixing_preis_eur_t"] == pytest.approx(250.0)


# ---------------------------------------------------------------------------
# Settlement Tests
# ---------------------------------------------------------------------------

def test_settlement_valid_transitions():
    assert ("OFFEN", "IN_ABRECHNUNG") in VALID_SETTLEMENT_TRANSITIONS
    assert ("IN_ABRECHNUNG", "ABGERECHNET") in VALID_SETTLEMENT_TRANSITIONS
    assert ("ABGERECHNET", "STORNIERT") in VALID_SETTLEMENT_TRANSITIONS


def test_settlement_transition_not_found():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(KontraktSettlementError):
        transition_settlement(db, "S1", "ABGERECHNET", "T1", "op")


def test_settlement_invalid_transition():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "ABGERECHNET", "kontrakt_id": "K1"
    }
    with pytest.raises(KontraktSettlementError):
        transition_settlement(db, "S1", "IN_ABRECHNUNG", "T1", "op")


def test_settlement_offen_to_in_abrechnung():
    db = MagicMock()
    row = {"status": "OFFEN", "kontrakt_id": "K1", "id": "S1"}
    updated = {**row, "status": "IN_ABRECHNUNG"}
    db.execute.return_value.mappings.return_value.first.side_effect = [row, updated]
    result = transition_settlement(db, "S1", "IN_ABRECHNUNG", "T1", "op")
    assert result["status"] == "IN_ABRECHNUNG"
