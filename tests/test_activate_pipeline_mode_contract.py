from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import activate_pipeline_mode
from scripts.json_state_contract import JsonStateContractError


def test_load_pipeline_config_requires_real_config(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(parents=True)
    monkeypatch.setattr(activate_pipeline_mode, "__file__", str(scripts_dir / "activate_pipeline_mode.py"))

    with pytest.raises(JsonStateContractError):
        activate_pipeline_mode.load_pipeline_config()


def test_load_pipeline_config_reads_required_sections(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir(parents=True)
    (config_dir / "development_pipelines.json").write_text(
        json.dumps(
            {
                "pipelines": {"demo": {"name": "Demo"}},
                "tools": {"tool": {"name": "Tool"}},
                "framework": {"fw": {"name": "Framework"}},
            }
        ),
        encoding="utf-8",
    )
    scripts_dir = tmp_path / "scripts"
    scripts_dir.mkdir(parents=True)
    monkeypatch.setattr(activate_pipeline_mode, "__file__", str(scripts_dir / "activate_pipeline_mode.py"))

    loaded = activate_pipeline_mode.load_pipeline_config()

    assert loaded["pipelines"]["demo"]["name"] == "Demo"
