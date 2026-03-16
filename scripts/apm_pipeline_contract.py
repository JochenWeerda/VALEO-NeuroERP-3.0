from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PipelineConfigContractError(RuntimeError):
    pass


def load_pipeline_config(config_path: str | Path) -> dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        raise PipelineConfigContractError(f"Konfigurationsdatei nicht gefunden: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PipelineConfigContractError(f"Konfigurationsdatei enthaelt ungueltiges JSON: {path}") from exc

    if not isinstance(data, dict):
        raise PipelineConfigContractError(f"Konfigurationsdatei muss ein JSON-Objekt enthalten: {path}")

    required_top_level = {
        "pipeline_integration": dict,
        "pipelines": dict,
        "apm_phases": dict,
    }
    for key, expected_type in required_top_level.items():
        value = data.get(key)
        if not isinstance(value, expected_type):
            raise PipelineConfigContractError(
                f"Konfigurationsdatei verletzt Pipeline-Contract: '{key}' muss vom Typ {expected_type.__name__} sein."
            )

    pipeline_integration = data["pipeline_integration"]
    for key, expected_type in {"enabled": bool, "version": str, "description": str}.items():
        value = pipeline_integration.get(key)
        if not isinstance(value, expected_type):
            raise PipelineConfigContractError(
                f"Konfigurationsdatei verletzt Pipeline-Contract: 'pipeline_integration.{key}' muss vom Typ {expected_type.__name__} sein."
            )

    for pipeline_id, pipeline_config in data["pipelines"].items():
        if not isinstance(pipeline_id, str) or not isinstance(pipeline_config, dict):
            raise PipelineConfigContractError("Konfigurationsdatei verletzt Pipeline-Contract: Pipelines muessen Objekte sein.")
        if not isinstance(pipeline_config.get("enabled"), bool):
            raise PipelineConfigContractError(
                f"Konfigurationsdatei verletzt Pipeline-Contract: 'pipelines.{pipeline_id}.enabled' muss bool sein."
            )
        integration_points = pipeline_config.get("integration_points")
        if not isinstance(integration_points, list) or not all(isinstance(item, str) for item in integration_points):
            raise PipelineConfigContractError(
                f"Konfigurationsdatei verletzt Pipeline-Contract: 'pipelines.{pipeline_id}.integration_points' muss list[str] sein."
            )
        if not isinstance(pipeline_config.get("priority"), str):
            raise PipelineConfigContractError(
                f"Konfigurationsdatei verletzt Pipeline-Contract: 'pipelines.{pipeline_id}.priority' muss str sein."
            )
        if not isinstance(pipeline_config.get("description"), str):
            raise PipelineConfigContractError(
                f"Konfigurationsdatei verletzt Pipeline-Contract: 'pipelines.{pipeline_id}.description' muss str sein."
            )

    for phase_name, phase_config in data["apm_phases"].items():
        if not isinstance(phase_name, str) or not isinstance(phase_config, dict):
            raise PipelineConfigContractError("Konfigurationsdatei verletzt Pipeline-Contract: APM-Phasen muessen Objekte sein.")
        if not isinstance(phase_config.get("description"), str):
            raise PipelineConfigContractError(
                f"Konfigurationsdatei verletzt Pipeline-Contract: 'apm_phases.{phase_name}.description' muss str sein."
            )
        post_phase_pipelines = phase_config.get("post_phase_pipelines")
        if not isinstance(post_phase_pipelines, list) or not all(isinstance(item, str) for item in post_phase_pipelines):
            raise PipelineConfigContractError(
                f"Konfigurationsdatei verletzt Pipeline-Contract: 'apm_phases.{phase_name}.post_phase_pipelines' muss list[str] sein."
            )

    return data
