"""DOM-MEL-004 Unit-Tests — Meldewesen Lifecycle (Intrastat/ELSTER/ATLAS)."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.meldewesen_lifecycle_service import (
    VALID_MELDUNG_TRANSITIONS,
    MELDUNG_TYPEN,
    MeldungError,
    create_meldung,
    transition_meldung,
    simulate_uebermittlung,
)


def test_valid_transitions():
    assert ("ENTWURF", "IN_PRUEFUNG") in VALID_MELDUNG_TRANSITIONS
    assert ("IN_PRUEFUNG", "FREIGEGEBEN") in VALID_MELDUNG_TRANSITIONS
    assert ("FREIGEGEBEN", "UEBERMITTELT") in VALID_MELDUNG_TRANSITIONS
    assert ("UEBERMITTELT", "BESTAETIGT") in VALID_MELDUNG_TRANSITIONS
    assert ("ABGELEHNT", "IN_PRUEFUNG") in VALID_MELDUNG_TRANSITIONS


def test_meldung_typen():
    assert "INTRASTAT_EINGANG" in MELDUNG_TYPEN
    assert "ELSTER_UMSATZSTEUER" in MELDUNG_TYPEN
    assert "ATLAS_AUSFUHR" in MELDUNG_TYPEN


def test_create_meldung_invalid_typ():
    db = MagicMock()
    with pytest.raises(MeldungError, match="Unbekannter"):
        create_meldung(db, "T1", "FAXMELDUNG", "2026-06", 1000.0, "EUR", [])


def test_transition_not_found():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(MeldungError):
        transition_meldung(db, "M1", "IN_PRUEFUNG", "T1", "op")


def test_transition_invalid():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "BESTAETIGT", "id": "M1"
    }
    with pytest.raises(MeldungError):
        transition_meldung(db, "M1", "ENTWURF", "T1", "op")


def test_transition_entwurf_to_in_pruefung():
    db = MagicMock()
    rec = {"status": "ENTWURF", "id": "M1", "tenant_id": "T1"}
    updated = {**rec, "status": "IN_PRUEFUNG"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_meldung(db, "M1", "IN_PRUEFUNG", "T1", "op")
    assert result["status"] == "IN_PRUEFUNG"


def test_transition_freigegeben_to_uebermittelt_has_hinweis():
    db = MagicMock()
    rec = {"status": "FREIGEGEBEN", "id": "M1", "tenant_id": "T1"}
    updated = {**rec, "status": "UEBERMITTELT"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_meldung(
        db, "M1", "UEBERMITTELT", "T1", "op",
        externe_referenz="ELST-2026-001"
    )
    assert result["status"] == "UEBERMITTELT"
    assert "_hinweis" in result


def test_simulate_uebermittlung_deterministisch():
    r1 = simulate_uebermittlung("ELSTER_UMSATZSTEUER", "2026-06", 50000.0)
    r2 = simulate_uebermittlung("ELSTER_UMSATZSTEUER", "2026-06", 50000.0)
    assert r1["externe_referenz"] == r2["externe_referenz"]
    assert r1["simuliert"] is True


def test_simulate_uebermittlung_unterschiedliche_typen():
    r1 = simulate_uebermittlung("ELSTER_UMSATZSTEUER", "2026-06", 1000.0)
    r2 = simulate_uebermittlung("INTRASTAT_EINGANG", "2026-06", 1000.0)
    assert r1["externe_referenz"] != r2["externe_referenz"]
