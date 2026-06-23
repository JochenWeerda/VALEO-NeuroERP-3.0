"""DOM-FEED-PROD-004 Unit-Tests — Mischfutter Produktion Lifecycle + Rezeptur."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.feed_produktion_lifecycle_service import (
    VALID_PRODUKTION_TRANSITIONS,
    FeedProduktionError,
    transition_produktionsauftrag,
)
from app.services.feed_rezeptur_service import (
    VALID_REZEPTUR_TRANSITIONS,
    RezepturError,
    transition_rezeptur,
    _fetch_rezeptur,
)


# ---------------------------------------------------------------------------
# Produktionsauftrag Tests
# ---------------------------------------------------------------------------

def test_valid_produktion_transitions():
    assert ("GEPLANT", "IN_PRODUKTION") in VALID_PRODUKTION_TRANSITIONS
    assert ("IN_PRODUKTION", "FERTIG") in VALID_PRODUKTION_TRANSITIONS
    assert ("FERTIG", "QS_FREIGEGEBEN") in VALID_PRODUKTION_TRANSITIONS
    assert ("FERTIG", "QS_GESPERRT") in VALID_PRODUKTION_TRANSITIONS
    assert ("QS_FREIGEGEBEN", "AUSGELAGERT") in VALID_PRODUKTION_TRANSITIONS


def test_transition_auftrag_not_found():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(FeedProduktionError):
        transition_produktionsauftrag(db, "A1", "IN_PRODUKTION", "T1", None, "op")


def test_transition_auftrag_invalid():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "AUSGELAGERT", "id": "A1"
    }
    with pytest.raises(FeedProduktionError):
        transition_produktionsauftrag(db, "A1", "GEPLANT", "T1", None, "op")


def test_transition_geplant_to_in_produktion():
    db = MagicMock()
    rec = {"status": "GEPLANT", "id": "A1", "tenant_id": "T1"}
    updated = {**rec, "status": "IN_PRODUKTION"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_produktionsauftrag(db, "A1", "IN_PRODUKTION", "T1", None, "op")
    assert result["status"] == "IN_PRODUKTION"


def test_transition_fertig_with_ist_menge():
    db = MagicMock()
    rec = {"status": "IN_PRODUKTION", "id": "A1", "tenant_id": "T1"}
    updated = {**rec, "status": "FERTIG", "ist_menge_kg": 950.0}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_produktionsauftrag(db, "A1", "FERTIG", "T1", 950.0, "op")
    assert result["status"] == "FERTIG"


def test_transition_qs_gesperrt_to_vernichtet():
    db = MagicMock()
    rec = {"status": "QS_GESPERRT", "id": "A1", "tenant_id": "T1"}
    updated = {**rec, "status": "VERNICHTET"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_produktionsauftrag(db, "A1", "VERNICHTET", "T1", None, "op")
    assert result["status"] == "VERNICHTET"


# ---------------------------------------------------------------------------
# Rezeptur Tests
# ---------------------------------------------------------------------------

def test_valid_rezeptur_transitions():
    assert ("ENTWURF", "FREIGEGEBEN") in VALID_REZEPTUR_TRANSITIONS
    assert ("FREIGEGEBEN", "ARCHIVIERT") in VALID_REZEPTUR_TRANSITIONS
    assert ("GESPERRT", "FREIGEGEBEN") in VALID_REZEPTUR_TRANSITIONS


def test_rezeptur_freigabe_rejects_invalid_sum():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "ENTWURF", "id": "R1"
    }
    # Summe != 100
    db.execute.return_value.scalar.return_value = 95.0
    with pytest.raises(RezepturError, match="100%"):
        transition_rezeptur(db, "R1", "FREIGEGEBEN", "T1", "op")


def test_rezeptur_transition_not_found():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(RezepturError):
        transition_rezeptur(db, "R99", "FREIGEGEBEN", "T1", "op")


def test_rezeptur_invalid_transition():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "ARCHIVIERT", "id": "R1"
    }
    with pytest.raises(RezepturError):
        transition_rezeptur(db, "R1", "FREIGEGEBEN", "T1", "op")
