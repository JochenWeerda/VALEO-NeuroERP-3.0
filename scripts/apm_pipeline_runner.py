#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline-Runner fuer VALEO-NeuroERP

Dieses Skript fuehrt Pipelines nach bestimmten APM-Phasen aus.
"""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import os
import sys
import time
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.apm_pipeline_contract import PipelineConfigContractError, load_pipeline_config


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "apm_pipeline_integration.json")
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "reports", "pipeline_results")


def load_config() -> dict[str, Any]:
    try:
        return load_pipeline_config(CONFIG_FILE)
    except PipelineConfigContractError as exc:
        logger.error("Fehler: %s", exc)
        sys.exit(1)


def save_result(pipeline_id: str, result: dict[str, Any]) -> None:
    os.makedirs(RESULTS_DIR, exist_ok=True)

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{pipeline_id}_{timestamp}.json"
    filepath = os.path.join(RESULTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    logger.info("Ergebnis der Pipeline %s wurde in %s gespeichert.", pipeline_id, filepath)


def load_pipeline_class(pipeline_id: str) -> type | None:
    try:
        module_path = f"pipelines.{pipeline_id}_pipeline"
        class_name = "".join(word.capitalize() for word in pipeline_id.split("_")) + "Pipeline"
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as exc:
        logger.error("Fehler beim Laden der Pipeline-Klasse %s: %s", pipeline_id, exc)
        return None


def run_pipelines_for_phase(phase: str) -> None:
    config = load_config()

    if not config["pipeline_integration"]["enabled"]:
        logger.info("Pipeline-Modus ist deaktiviert.")
        print("\nErgebnisse der Pipeline-Ausfuehrung nach Phase", phase.upper() + ":")
        print("  - Uebersprungen: Pipeline-Modus ist deaktiviert.")
        return

    integration_point = f"post_{phase.lower()}"
    pipelines_to_run: list[tuple[str, str]] = []

    for pipeline_id, pipeline_config in config["pipelines"].items():
        if pipeline_config["enabled"] and integration_point in pipeline_config["integration_points"]:
            pipelines_to_run.append((pipeline_id, pipeline_config["priority"]))

    priority_map = {"high": 0, "medium": 1, "low": 2}
    pipelines_to_run.sort(key=lambda item: priority_map.get(item[1], 99))

    if not pipelines_to_run:
        logger.info("Keine Pipelines fuer Phase %s konfiguriert.", phase)
        print("\nErgebnisse der Pipeline-Ausfuehrung nach Phase", phase.upper() + ":")
        print("  - Keine Pipelines fuer diese Phase konfiguriert.")
        return

    results: list[tuple[str, str, Any]] = []

    for pipeline_id, _ in pipelines_to_run:
        pipeline_class = load_pipeline_class(pipeline_id)

        if pipeline_class is None:
            logger.error("Pipeline %s konnte nicht geladen werden.", pipeline_id)
            results.append((pipeline_id, "error", "Pipeline konnte nicht geladen werden."))
            continue

        try:
            pipeline = pipeline_class()
            result = pipeline.execute()
            save_result(pipeline_id, result)
            results.append((pipeline_id, result["overall_status"], result["summary"]["success_rate"]))
        except Exception as exc:
            logger.exception("Fehler bei der Ausfuehrung der Pipeline %s: %s", pipeline_id, exc)
            results.append((pipeline_id, "error", str(exc)))

    print("\nErgebnisse der Pipeline-Ausfuehrung nach Phase", phase.upper() + ":")
    for pipeline_id, status, details in results:
        print(f"  - {pipeline_id}: {status} ({details})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fuehrt Pipelines nach bestimmten APM-Phasen aus")
    parser.add_argument(
        "--phase",
        required=True,
        choices=["van", "plan", "implement", "verify"],
        help="Die Phase, nach der Pipelines ausgefuehrt werden sollen",
    )

    args = parser.parse_args()

    logger.info("Phase geaendert zu: PIPELINE")
    run_pipelines_for_phase(args.phase)


if __name__ == "__main__":
    main()
