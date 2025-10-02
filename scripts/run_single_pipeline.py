#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Führt eine einzelne Pipeline für VALEO-NeuroERP aus

Dieses Skript führt eine einzelne Pipeline basierend auf dem übergebenen Namen aus.
"""

import asyncio
import json
import logging
import os
import sys
import argparse
from typing import Dict, Any, Optional

# Füge das Hauptverzeichnis zum Pythonpfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/pipeline_execution.log')
    ]
)

logger = logging.getLogger(__name__)

def load_pipeline_config() -> Dict[str, Any]:
    """
    Lädt die Pipeline-Konfiguration aus der JSON-Datei.
    
    Returns:
        Die Pipeline-Konfiguration
    """
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "development_pipelines.json")
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Fehler beim Laden der Pipeline-Konfiguration: {e}")
        return {"pipelines": {}}

def list_available_pipelines() -> None:
    """
    Listet alle verfügbaren Pipelines auf.
    """
    config = load_pipeline_config()
    pipelines = config.get("pipelines", {})
    
    if not pipelines:
        logger.info("Keine Pipelines verfügbar.")
        return
    
    logger.info("Verfügbare Pipelines:")
    for name, pipeline in pipelines.items():
        enabled = "Aktiv" if pipeline.get("enabled", True) else "Inaktiv"
        logger.info(f"- {name}: {pipeline.get('name')} ({enabled})")
        logger.info(f"  {pipeline.get('description')}")

def main():
    """
    Hauptfunktion zum Ausführen einer einzelnen Pipeline.
    """
    # Parse Kommandozeilenargumente
    parser = argparse.ArgumentParser(description="Führt eine einzelne Pipeline für VALEO-NeuroERP aus")
    parser.add_argument("pipeline", nargs="?", help="Name der auszuführenden Pipeline")
    parser.add_argument("--list", action="store_true", help="Listet alle verfügbaren Pipelines auf")
    args = parser.parse_args()
    
    # Erstelle das logs-Verzeichnis, falls es nicht existiert
    os.makedirs('logs', exist_ok=True)
    
    # Liste alle verfügbaren Pipelines auf
    if args.list or not args.pipeline:
        list_available_pipelines()
        return
    
    logger.info(f"Um eine Pipeline auszuführen, muss das System erst angepasst werden.")
    logger.info(f"Bitte führen Sie 'python scripts/activate_pipeline_mode.py' aus, um alle Pipelines auszuführen.")

if __name__ == "__main__":
    main() 