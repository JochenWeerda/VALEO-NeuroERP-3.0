"""Wave 77 — Unit-Tests fuer docflow_artifact_service, docflow_followup_service, docflow_gobd_service (pure)."""

from __future__ import annotations

import pytest
from datetime import date


# ---------------------------------------------------------------------------
# docflow_artifact_service  (pure version/hash/transition logic)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_next_version_empty_list() -> None:
    from app.services.docflow_artifact_service import next_version
    assert next_version([]) == 1


@pytest.mark.unit
def test_next_version_increments_max() -> None:
    from app.services.docflow_artifact_service import next_version
    assert next_version([1, 2, 3]) == 4


@pytest.mark.unit
def test_next_version_single_element() -> None:
    from app.services.docflow_artifact_service import next_version
    assert next_version([5]) == 6


@pytest.mark.unit
def test_sha256_hex_returns_string() -> None:
    from app.services.docflow_artifact_service import sha256_hex
    result = sha256_hex("test content")
    assert isinstance(result, str)
    assert len(result) == 64  # SHA-256 hex is always 64 chars


@pytest.mark.unit
def test_sha256_hex_deterministic() -> None:
    from app.services.docflow_artifact_service import sha256_hex
    assert sha256_hex("hello") == sha256_hex("hello")


@pytest.mark.unit
def test_sha256_hex_different_input() -> None:
    from app.services.docflow_artifact_service import sha256_hex
    assert sha256_hex("hello") != sha256_hex("world")


@pytest.mark.unit
def test_valid_transition_entwurf_to_freigegeben() -> None:
    from app.services.docflow_artifact_service import valid_transition
    assert valid_transition("entwurf", "freigegeben") is True


@pytest.mark.unit
def test_valid_transition_freigegeben_to_archiviert() -> None:
    from app.services.docflow_artifact_service import valid_transition
    assert valid_transition("freigegeben", "archiviert") is True


@pytest.mark.unit
def test_valid_transition_archiviert_no_transitions() -> None:
    from app.services.docflow_artifact_service import valid_transition
    assert valid_transition("archiviert", "entwurf") is False
    assert valid_transition("archiviert", "freigegeben") is False


@pytest.mark.unit
def test_valid_transition_skip_state_blocked() -> None:
    from app.services.docflow_artifact_service import valid_transition
    # Cannot skip from entwurf directly to archiviert
    assert valid_transition("entwurf", "archiviert") is False


# ---------------------------------------------------------------------------
# docflow_followup_service — followup_overdue  (pure predicate)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_followup_overdue_past_date() -> None:
    from app.services.docflow_followup_service import followup_overdue
    assert followup_overdue(date(2024, 1, 1), "offen", date(2024, 6, 1)) is True


@pytest.mark.unit
def test_followup_not_overdue_future_date() -> None:
    from app.services.docflow_followup_service import followup_overdue
    assert followup_overdue(date(2025, 6, 1), "offen", date(2024, 6, 1)) is False


@pytest.mark.unit
def test_followup_not_overdue_closed_status() -> None:
    from app.services.docflow_followup_service import followup_overdue
    # Closed followup is never overdue
    assert followup_overdue(date(2024, 1, 1), "closed", date(2024, 6, 1)) is False


@pytest.mark.unit
def test_followup_not_overdue_no_date() -> None:
    from app.services.docflow_followup_service import followup_overdue
    assert followup_overdue(None, "offen", date(2024, 6, 1)) is False


@pytest.mark.unit
def test_followup_not_overdue_none_status_treated_as_offen() -> None:
    from app.services.docflow_followup_service import followup_overdue
    # None status is treated as "offen"
    assert followup_overdue(date(2024, 1, 1), None, date(2024, 6, 1)) is True


# ---------------------------------------------------------------------------
# docflow_gobd_service — build_gobd_manifest  (pure manifest builder)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_build_gobd_manifest_structure() -> None:
    from app.services.docflow_gobd_service import build_gobd_manifest
    result = build_gobd_manifest(
        {"doc_id": "DOC-001", "doc_type": "invoice"},
        "2024-01-15T10:00:00Z",
        "USR-001",
    )
    assert isinstance(result, dict)
    for key in ("vorgang", "exportiert_am", "exportiert_von", "revisionssicher", "pruefsumme_sha256"):
        assert key in result


@pytest.mark.unit
def test_build_gobd_manifest_sha256_not_empty() -> None:
    from app.services.docflow_gobd_service import build_gobd_manifest
    result = build_gobd_manifest({"doc_id": "DOC-001"}, "2024-01-15T10:00:00Z", "USR-001")
    assert len(result["pruefsumme_sha256"]) > 0
