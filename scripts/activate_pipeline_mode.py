#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Aktiviert den Pipeline-Modus für VALEO-NeuroERP

Dieses Skript aktiviert den Pipeline-Modus und führt die implementierten Pipelines aus.
"""

import json
import logging
import os
import sys
from typing import Dict, Any, List

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

def list_pipeline_implementation_status() -> None:
    """
    Listet den Implementierungsstatus der Pipelines auf.
    """
    config = load_pipeline_config()
    pipelines = config.get("pipelines", {})
    tools = config.get("tools", {})
    framework = config.get("framework", {})
    
    if not pipelines:
        logger.info("Keine Pipelines verfügbar.")
        return
    
    logger.info("VALEO-NeuroERP Pipeline-Implementierung")
    logger.info("=====================================")
    logger.info("")
    
    logger.info("Implementierte Pipelines:")
    for name, pipeline in pipelines.items():
        enabled = "Aktiv" if pipeline.get("enabled", True) else "Inaktiv"
        logger.info(f"- {pipeline.get('name')} ({enabled})")
        logger.info(f"  {pipeline.get('description')}")
        logger.info(f"  Datei: {pipeline.get('file')}")
        logger.info("")
    
    logger.info("Implementierte Tools:")
    for name, tool in tools.items():
        enabled = "Aktiv" if tool.get("enabled", True) else "Inaktiv"
        logger.info(f"- {tool.get('name')} ({enabled})")
        logger.info(f"  {tool.get('description')}")
        logger.info(f"  Datei: {tool.get('file')}")
        logger.info("")
    
    logger.info("Framework-Komponenten:")
    for name, component in framework.items():
        enabled = "Aktiv" if component.get("enabled", True) else "Inaktiv"
        logger.info(f"- {component.get('name')} ({enabled})")
        logger.info(f"  {component.get('description')}")
        logger.info(f"  Datei: {component.get('file')}")
        logger.info("")

def main():
    """
    Hauptfunktion zum Ausführen der Pipelines.
    """
    logger.info("Starte VALEO-NeuroERP Pipeline-Modus")
    
    try:
        # Erstelle das logs-Verzeichnis, falls es nicht existiert
        os.makedirs('logs', exist_ok=True)
        
        # Zeige Implementierungsstatus
        list_pipeline_implementation_status()
        
        # Hinweis zur Ausführung
        logger.info("Hinweis zur Pipeline-Ausführung:")
        logger.info("Die Pipelines wurden erfolgreich implementiert, aber die Ausführung erfordert")
        logger.info("weitere Anpassungen an der Systemarchitektur. Die folgenden Komponenten müssen")
        logger.info("noch integriert werden:")
        logger.info("")
        logger.info("1. Integration der Edge-Komponenten mit dem Pipeline-Framework")
        logger.info("2. Implementierung der fehlenden Simulationsumgebung für Edge-Tests")
        logger.info("3. Konfiguration der Testdaten für die Pipeline-Ausführung")
        logger.info("")
        logger.info("Bitte konsultieren Sie die Dokumentation in data/reports/pipeline_implementation_summary.md")
        logger.info("für weitere Informationen zur Integration der Pipelines mit dem APM-Framework.")
    
    except Exception as e:
        logger.exception(f"Unerwarteter Fehler im Pipeline-Modus: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
