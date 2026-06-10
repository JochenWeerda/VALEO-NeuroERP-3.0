#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aktiviert den Pipeline-Modus fuer VALEO-NeuroERP.

Dieses Skript aktiviert den Pipeline-Modus und zeigt den Implementierungsstand
der konfigurierten Development-Pipelines an.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.json_state_contract import load_json_state


LOG_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOG_DIRECTORY, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(LOG_DIRECTORY, "pipeline_execution.log")),
    ],
)

logger = logging.getLogger(__name__)


def load_pipeline_config() -> dict[str, Any]:
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "development_pipelines.json")
    return load_json_state(
        config_path,
        required_keys={"pipelines": dict, "tools": dict, "framework": dict},
    )


def list_pipeline_implementation_status() -> None:
    config = load_pipeline_config()
    pipelines = config.get("pipelines", {})
    tools = config.get("tools", {})
    framework = config.get("framework", {})

    if not pipelines:
        logger.info("Keine Pipelines verfuegbar.")
        return

    logger.info("VALEO-NeuroERP Pipeline-Implementierung")
    logger.info("=====================================")
    logger.info("")

    logger.info("Implementierte Pipelines:")
    for _, pipeline in pipelines.items():
        enabled = "Aktiv" if pipeline.get("enabled", True) else "Inaktiv"
        logger.info("- %s (%s)", pipeline.get("name"), enabled)
        logger.info("  %s", pipeline.get("description"))
        logger.info("  Datei: %s", pipeline.get("file"))
        logger.info("")

    logger.info("Implementierte Tools:")
    for _, tool in tools.items():
        enabled = "Aktiv" if tool.get("enabled", True) else "Inaktiv"
        logger.info("- %s (%s)", tool.get("name"), enabled)
        logger.info("  %s", tool.get("description"))
        logger.info("  Datei: %s", tool.get("file"))
        logger.info("")

    logger.info("Framework-Komponenten:")
    for _, component in framework.items():
        enabled = "Aktiv" if component.get("enabled", True) else "Inaktiv"
        logger.info("- %s (%s)", component.get("name"), enabled)
        logger.info("  %s", component.get("description"))
        logger.info("  Datei: %s", component.get("file"))
        logger.info("")


def main() -> None:
    logger.info("Starte VALEO-NeuroERP Pipeline-Modus")

    try:
        os.makedirs("logs", exist_ok=True)
        list_pipeline_implementation_status()

        logger.info("Hinweis zur Pipeline-Ausfuehrung:")
        logger.info("Die Pipelines wurden erfolgreich implementiert, aber die Ausfuehrung erfordert")
        logger.info("weitere Anpassungen an der Systemarchitektur. Die folgenden Komponenten muessen")
        logger.info("noch integriert werden:")
        logger.info("")
        logger.info("1. Integration der Edge-Komponenten mit dem Pipeline-Framework")
        logger.info("2. Implementierung der fehlenden Simulationsumgebung fuer Edge-Tests")
        logger.info("3. Konfiguration der Testdaten fuer die Pipeline-Ausfuehrung")
        logger.info("")
        logger.info("Bitte konsultieren Sie die Dokumentation in data/reports/pipeline_implementation_summary.md")
        logger.info("fuer weitere Informationen zur Integration der Pipelines mit dem APM-Framework.")
    except Exception as exc:
        logger.exception("Unerwarteter Fehler im Pipeline-Modus: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
