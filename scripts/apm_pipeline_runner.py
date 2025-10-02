#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline-Runner für VALEO-NeuroERP

Dieses Skript führt Pipelines nach bestimmten APM-Phasen aus.
"""

import argparse
import importlib
import json
import logging
import os
import sys
import time
from typing import Dict, Any, List, Optional

# Füge das Hauptverzeichnis zum Pythonpfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'apm_pipeline_integration.json')
RESULTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'reports', 'pipeline_results')

def load_config() -> Dict[str, Any]:
    """
    Lädt die Konfiguration aus der Datei.
    
    Returns:
        Die geladene Konfiguration
    """
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Fehler: Konfigurationsdatei {CONFIG_FILE} nicht gefunden.")
        sys.exit(1)
    except json.JSONDecodeError:
        logger.error(f"Fehler: Konfigurationsdatei {CONFIG_FILE} enthält ungültiges JSON.")
        sys.exit(1)

def save_result(pipeline_id: str, result: Dict[str, Any]) -> None:
    """
    Speichert das Ergebnis einer Pipeline-Ausführung.
    
    Args:
        pipeline_id: Die ID der Pipeline
        result: Das Ergebnis der Pipeline-Ausführung
    """
    # Erstelle das Verzeichnis, falls es nicht existiert
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    # Generiere den Dateinamen
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"{pipeline_id}_{timestamp}.json"
    filepath = os.path.join(RESULTS_DIR, filename)
    
    # Speichere das Ergebnis
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=4, ensure_ascii=False)
    
    logger.info(f"Ergebnis der Pipeline {pipeline_id} wurde in {filepath} gespeichert.")

def load_pipeline_class(pipeline_id: str, config: Dict[str, Any]) -> Optional[type]:
    """
    Lädt die Klasse einer Pipeline.
    
    Args:
        pipeline_id: Die ID der Pipeline
        config: Die Konfiguration
    
    Returns:
        Die Klasse der Pipeline oder None, wenn die Klasse nicht geladen werden konnte
    """
    try:
        # Bestimme den Modulpfad und den Klassennamen
        module_path = f"pipelines.{pipeline_id}_pipeline"
        class_name = ''.join(word.capitalize() for word in pipeline_id.split('_')) + 'Pipeline'
        
        # Importiere das Modul
        module = importlib.import_module(module_path)
        
        # Hole die Klasse
        pipeline_class = getattr(module, class_name)
        
        return pipeline_class
    except (ImportError, AttributeError) as e:
        logger.error(f"Fehler beim Laden der Pipeline-Klasse {pipeline_id}: {e}")
        return None

def run_pipelines_for_phase(phase: str) -> None:
    """
    Führt alle Pipelines für eine bestimmte Phase aus.
    
    Args:
        phase: Die Phase, für die Pipelines ausgeführt werden sollen
    """
    config = load_config()
    
    # Prüfe, ob die Pipeline-Integration aktiviert ist
    if not config['pipeline_integration']['enabled']:
        logger.info("Pipeline-Modus ist deaktiviert.")
        print("\nErgebnisse der Pipeline-Ausführung nach Phase", phase.upper() + ":")
        print("  - Übersprungen: Pipeline-Modus ist deaktiviert.")
        return
    
    # Bestimme die Pipelines für diese Phase
    integration_point = f"post_{phase.lower()}"
    pipelines_to_run = []
    
    for pipeline_id, pipeline_config in config['pipelines'].items():
        if pipeline_config['enabled'] and integration_point in pipeline_config['integration_points']:
            pipelines_to_run.append((pipeline_id, pipeline_config['priority']))
    
    # Sortiere die Pipelines nach Priorität (high > medium > low)
    priority_map = {'high': 0, 'medium': 1, 'low': 2}
    pipelines_to_run.sort(key=lambda x: priority_map.get(x[1], 99))
    
    if not pipelines_to_run:
        logger.info(f"Keine Pipelines für Phase {phase} konfiguriert.")
        print("\nErgebnisse der Pipeline-Ausführung nach Phase", phase.upper() + ":")
        print("  - Keine Pipelines für diese Phase konfiguriert.")
        return
    
    # Führe die Pipelines aus
    results = []
    
    for pipeline_id, _ in pipelines_to_run:
        # Lade die Pipeline-Klasse
        pipeline_class = load_pipeline_class(pipeline_id, config)
        
        if pipeline_class is None:
            logger.error(f"Pipeline {pipeline_id} konnte nicht geladen werden.")
            results.append((pipeline_id, "error", "Pipeline konnte nicht geladen werden."))
            continue
        
        try:
            # Instanziiere und führe die Pipeline aus
            pipeline = pipeline_class()
            result = pipeline.execute()
            
            # Speichere das Ergebnis
            save_result(pipeline_id, result)
            
            # Füge das Ergebnis zur Liste hinzu
            results.append((pipeline_id, result['overall_status'], result['summary']['success_rate']))
        except Exception as e:
            logger.exception(f"Fehler bei der Ausführung der Pipeline {pipeline_id}: {e}")
            results.append((pipeline_id, "error", str(e)))
    
    # Zeige die Ergebnisse an
    print("\nErgebnisse der Pipeline-Ausführung nach Phase", phase.upper() + ":")
    for pipeline_id, status, details in results:
        print(f"  - {pipeline_id}: {status} ({details})")

def main() -> None:
    """
    Hauptfunktion des Skripts.
    """
    parser = argparse.ArgumentParser(description='Führt Pipelines nach bestimmten APM-Phasen aus')
    
    parser.add_argument(
        '--phase',
        required=True,
        choices=['van', 'plan', 'implement', 'verify'],
        help='Die Phase, nach der Pipelines ausgeführt werden sollen'
    )
    
    args = parser.parse_args()
    
    # Simuliere eine Phase-Änderung (in der Realität würde dies vom APM-Framework kommen)
    logger.info(f"Phase geändert zu: PIPELINE")
    
    # Führe die Pipelines für die angegebene Phase aus
    run_pipelines_for_phase(args.phase)

if __name__ == '__main__':
    main()
