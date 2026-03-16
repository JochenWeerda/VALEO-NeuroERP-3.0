from __future__ import annotations

from pathlib import Path

import pytest

from scripts.json_state_contract import JsonStateContractError, load_json_state, save_json_state


def test_load_json_state_returns_default_for_missing_optional_file(tmp_path: Path):
    result = load_json_state(tmp_path / "missing.json", default={"phase": "VAN"})
    assert result == {"phase": "VAN"}


def test_load_json_state_rejects_invalid_json(tmp_path: Path):
    path = tmp_path / "state.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(JsonStateContractError) as exc:
        load_json_state(path)

    assert "ungueltiges JSON" in str(exc.value)


def test_load_json_state_rejects_schema_drift(tmp_path: Path):
    path = tmp_path / "state.json"
    path.write_text('{"phase": "VAN", "progress": "0", "status": "idle"}', encoding="utf-8")

    with pytest.raises(JsonStateContractError) as exc:
        load_json_state(path, required_keys={"phase": str, "progress": int, "status": str})

    assert "progress" in str(exc.value)


def test_save_json_state_roundtrip(tmp_path: Path):
    path = tmp_path / "state.json"
    payload = {"phase": "PLAN", "progress": 10, "status": "running"}

    save_json_state(path, payload)

    assert load_json_state(path) == payload
