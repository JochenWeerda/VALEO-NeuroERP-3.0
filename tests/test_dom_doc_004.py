"""DOM-DOC-004 Unit-Tests — Nachweisraum Dokument-Lifecycle + GoBD-Export."""
from __future__ import annotations

from unittest.mock import MagicMock
import pytest

from app.services.doc_nachweisraum_lifecycle_service import (
    VALID_DOKUMENT_TRANSITIONS,
    VALID_GOBD_TRANSITIONS,
    NachweisraumError,
    transition_dokument,
    transition_gobd_export,
)


def test_valid_dokument_transitions():
    assert ("EINGEGANGEN", "IN_PRUEFUNG") in VALID_DOKUMENT_TRANSITIONS
    assert ("IN_PRUEFUNG", "FREIGEGEBEN") in VALID_DOKUMENT_TRANSITIONS
    assert ("IN_PRUEFUNG", "WIEDERVORLAGE") in VALID_DOKUMENT_TRANSITIONS
    assert ("WIEDERVORLAGE", "IN_PRUEFUNG") in VALID_DOKUMENT_TRANSITIONS
    assert ("FREIGEGEBEN", "ARCHIVIERT") in VALID_DOKUMENT_TRANSITIONS


def test_valid_gobd_transitions():
    assert ("OFFEN", "IN_ERSTELLUNG") in VALID_GOBD_TRANSITIONS
    assert ("IN_ERSTELLUNG", "EXPORTIERT") in VALID_GOBD_TRANSITIONS
    assert ("EXPORTIERT", "PRUEFBAR") in VALID_GOBD_TRANSITIONS
    assert ("PRUEFBAR", "ABGENOMMEN") in VALID_GOBD_TRANSITIONS


def test_dokument_transition_not_found():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(NachweisraumError):
        transition_dokument(db, "D1", "IN_PRUEFUNG", "T1", "op")


def test_dokument_invalid_transition():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "ARCHIVIERT", "id": "D1"
    }
    with pytest.raises(NachweisraumError):
        transition_dokument(db, "D1", "IN_PRUEFUNG", "T1", "op")


def test_dokument_eingegangen_to_in_pruefung():
    db = MagicMock()
    rec = {"status": "EINGEGANGEN", "id": "D1", "tenant_id": "T1"}
    updated = {**rec, "status": "IN_PRUEFUNG"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_dokument(db, "D1", "IN_PRUEFUNG", "T1", "op")
    assert result["status"] == "IN_PRUEFUNG"


def test_dokument_wiedervorlage_flow():
    db = MagicMock()
    rec = {"status": "IN_PRUEFUNG", "id": "D1", "tenant_id": "T1"}
    updated = {**rec, "status": "WIEDERVORLAGE", "wiedervorlage_datum": "2026-07-01"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_dokument(
        db, "D1", "WIEDERVORLAGE", "T1", "op",
        kommentar="Nachforderung", wiedervorlage_datum="2026-07-01"
    )
    assert result["status"] == "WIEDERVORLAGE"


def test_gobd_export_not_found():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(NachweisraumError):
        transition_gobd_export(db, "E1", "IN_ERSTELLUNG", "T1", "op")


def test_gobd_export_offen_to_in_erstellung():
    db = MagicMock()
    rec = {"status": "OFFEN", "id": "E1", "tenant_id": "T1"}
    updated = {**rec, "status": "IN_ERSTELLUNG"}
    db.execute.return_value.mappings.return_value.first.side_effect = [rec, updated]
    result = transition_gobd_export(db, "E1", "IN_ERSTELLUNG", "T1", "op")
    assert result["status"] == "IN_ERSTELLUNG"


def test_gobd_export_invalid_transition():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {
        "status": "ABGENOMMEN", "id": "E1"
    }
    with pytest.raises(NachweisraumError):
        transition_gobd_export(db, "E1", "OFFEN", "T1", "op")
