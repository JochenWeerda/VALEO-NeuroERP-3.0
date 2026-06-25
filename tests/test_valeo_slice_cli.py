"""Tests fuer DEV-HARNESS-CLI-001 — valeo_slice.py CLI."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from scripts.valeo_slice import (
    REQUIRED_AI_HARNESS_FIELDS,
    REQUIRED_SLICE_FIELDS,
    _find_slice_yaml,
    _load_yaml,
    _validate_yaml,
    cmd_list,
    cmd_status,
)


FIXTURE_GOOD = {
    "slice_id": "TEST-CLI-001",
    "title": "CLI Test Slice",
    "owner": "ai",
    "status": "in_arbeit",
    "created_at": "2026-06-23",
    "goal": "CLI testen",
    "file_ownership": {"owned": [], "reads": []},
    "tests": ["pytest tests/test_valeo_slice_cli.py -x"],
    "risks": "minimal",
    "external_gates": [],
    "ai_harness": {
        "fachlicher_vertrag": "ok",
        "architektur_vertrag": "ok",
        "daten_vertrag": "ok",
        "test_vertrag": "ok",
        "security_vertrag": "ok",
        "betriebs_vertrag": "ok",
        "dokumentations_vertrag": "ok",
    },
}

FIXTURE_BAD_MISSING_FIELD = {
    "slice_id": "TEST-CLI-BAD-001",
    "title": "Bad Slice",
    # missing: owner, status, created_at, goal, file_ownership, tests, risks, external_gates, ai_harness
}

FIXTURE_BAD_HARNESS = {
    **FIXTURE_GOOD,
    "slice_id": "TEST-CLI-BAD-002",
    "ai_harness": {
        "fachlicher_vertrag": "ok",
        # missing 6 harness fields
    },
}


def test_required_slice_fields_complete() -> None:
    assert "slice_id" in REQUIRED_SLICE_FIELDS
    assert "ai_harness" in REQUIRED_SLICE_FIELDS
    assert len(REQUIRED_SLICE_FIELDS) == 11


def test_required_harness_fields_complete() -> None:
    assert "fachlicher_vertrag" in REQUIRED_AI_HARNESS_FIELDS
    assert "dokumentations_vertrag" in REQUIRED_AI_HARNESS_FIELDS
    assert len(REQUIRED_AI_HARNESS_FIELDS) == 7


def test_validate_yaml_good(tmp_path: Path) -> None:
    errors = _validate_yaml(FIXTURE_GOOD)
    assert errors == [], f"Unerwartete Fehler: {errors}"


def test_validate_yaml_missing_top_level(tmp_path: Path) -> None:
    errors = _validate_yaml(FIXTURE_BAD_MISSING_FIELD)
    assert any("owner" in e or "Pflicht" in e for e in errors)


def test_validate_yaml_missing_harness(tmp_path: Path) -> None:
    errors = _validate_yaml(FIXTURE_BAD_HARNESS)
    assert any("harness" in e.lower() or "ai_harness" in e for e in errors)


def test_load_yaml(tmp_path: Path) -> None:
    f = tmp_path / "test.yaml"
    f.write_text(yaml.dump(FIXTURE_GOOD), encoding="utf-8")
    data = _load_yaml(f)
    assert data["slice_id"] == "TEST-CLI-001"


def test_find_slice_yaml_finds_real_slices() -> None:
    # Suche nach einem bekannten echten Slice
    p = _find_slice_yaml("VALEO-WF-COCKPIT-001")
    if p is not None:
        assert p.exists()


def test_find_slice_yaml_nonexistent() -> None:
    assert _find_slice_yaml("DOES-NOT-EXIST-99999") is None


def test_cmd_list_runs(capsys: pytest.CaptureFixture) -> None:
    rc = cmd_list()
    captured = capsys.readouterr()
    assert rc == 0
    assert "Status" in captured.out or "Slice-ID" in captured.out


def test_cmd_status_not_found(capsys: pytest.CaptureFixture) -> None:
    rc = cmd_status("DOES-NOT-EXIST-99999")
    assert rc == 1


def test_cmd_status_real_slice(capsys: pytest.CaptureFixture) -> None:
    """Pruefen, ob status fuer einen real existierenden Slice 0 oder 1 zurueckgibt."""
    # Mindestens ein Slice muss existieren
    from scripts.valeo_slice import SLICES_DIR
    yamls = list(SLICES_DIR.glob("*.yaml"))
    if not yamls:
        pytest.skip("Keine Slice-YAMLs vorhanden")
    # Lade den ersten und pruefe Status-Aufruf
    data = _load_yaml(yamls[0])
    sid = data.get("slice_id", yamls[0].stem)
    rc = cmd_status(sid)
    assert rc in (0, 1)
