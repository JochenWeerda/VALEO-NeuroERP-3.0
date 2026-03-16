from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.apm_pipeline_contract import PipelineConfigContractError, load_pipeline_config


def _write_config(path: Path, payload) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _valid_config() -> dict:
    return {
        "pipeline_integration": {
            "enabled": True,
            "version": "1.0",
            "description": "test",
        },
        "pipelines": {
            "demo": {
                "enabled": True,
                "integration_points": ["post_plan"],
                "priority": "medium",
                "description": "demo pipeline",
            }
        },
        "apm_phases": {
            "plan": {
                "description": "Plan phase",
                "post_phase_pipelines": ["demo"],
            }
        },
    }


def test_load_pipeline_config_rejects_missing_file(tmp_path: Path):
    with pytest.raises(PipelineConfigContractError) as exc:
        load_pipeline_config(tmp_path / "missing.json")

    assert "nicht gefunden" in str(exc.value)


def test_load_pipeline_config_rejects_invalid_json(tmp_path: Path):
    path = tmp_path / "apm_pipeline_integration.json"
    path.write_text("{broken", encoding="utf-8")

    with pytest.raises(PipelineConfigContractError) as exc:
        load_pipeline_config(path)

    assert "ungueltiges JSON" in str(exc.value)


def test_load_pipeline_config_rejects_schema_drift(tmp_path: Path):
    path = tmp_path / "apm_pipeline_integration.json"
    payload = _valid_config()
    payload["pipelines"]["demo"]["integration_points"] = "post_plan"
    _write_config(path, payload)

    with pytest.raises(PipelineConfigContractError) as exc:
        load_pipeline_config(path)

    assert "integration_points" in str(exc.value)


def test_load_pipeline_config_accepts_valid_contract(tmp_path: Path):
    path = tmp_path / "apm_pipeline_integration.json"
    _write_config(path, _valid_config())

    loaded = load_pipeline_config(path)

    assert loaded["pipeline_integration"]["enabled"] is True
    assert loaded["pipelines"]["demo"]["priority"] == "medium"
