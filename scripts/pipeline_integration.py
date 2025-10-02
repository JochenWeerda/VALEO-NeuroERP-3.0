#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline-Integration für VALEO-NeuroERP

Dieses Skript bereitet die Integration der Pipelines mit dem APM-Framework vor.
"""

import json
import logging
import os
import sys
from typing import Dict, Any, List
import argparse

# Füge das Hauptverzeichnis zum Pythonpfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.config import get_settings
from core.apm_phases import APMPhase, PhaseManager

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/pipeline_integration.log')
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

def create_apm_integration_config(output_path: str) -> None:
    """
    Erstellt eine Konfigurationsdatei für die Integration der Pipelines mit dem APM-Framework.
    
    Args:
        output_path: Der Pfad, an dem die Konfigurationsdatei gespeichert werden soll
    """
    pipeline_config = load_pipeline_config()
    pipelines = pipeline_config.get("pipelines", {})
    
    # Erstelle die APM-Integration-Konfiguration
    apm_integration = {
        "pipeline_mode": {
            "enabled": True,
            "description": "Pipeline-Modus für das VALEO-NeuroERP-System",
            "phase": "PIPELINE",
            "integration": {
                "van_mode": {
                    "enabled": True,
                    "description": "Integration mit dem VAN-Modus",
                    "entry_point": "post_van_phase"
                },
                "plan_mode": {
                    "enabled": True,
                    "description": "Integration mit dem PLAN-Modus",
                    "entry_point": "post_plan_phase"
                },
                "create_mode": {
                    "enabled": True,
                    "description": "Integration mit dem CREATE-Modus",
                    "entry_point": "post_create_phase"
                },
                "implement_mode": {
                    "enabled": True,
                    "description": "Integration mit dem IMPLEMENT-Modus",
                    "entry_point": "post_implement_phase"
                },
                "reflect_mode": {
                    "enabled": True,
                    "description": "Integration mit dem REFLECT-Modus",
                    "entry_point": "post_reflect_phase"
                }
            }
        },
        "pipelines": {}
    }
    
    # Füge die Pipelines zur Konfiguration hinzu
    for name, pipeline in pipelines.items():
        apm_integration["pipelines"][name] = {
            "name": pipeline.get("name"),
            "description": pipeline.get("description"),
            "file": pipeline.get("file"),
            "class": pipeline.get("class"),
            "enabled": pipeline.get("enabled", True),
            "priority": pipeline.get("priority", 0),
            "integration_points": {
                "van": pipeline.get("priority", 0) == 1,  # Nur die erste Pipeline wird nach VAN ausgeführt
                "plan": True,  # Alle Pipelines werden nach PLAN ausgeführt
                "create": pipeline.get("priority", 0) in [3, 4, 5],  # Nur bestimmte Pipelines werden nach CREATE ausgeführt
                "implement": pipeline.get("priority", 0) in [2, 3],  # Nur bestimmte Pipelines werden nach IMPLEMENT ausgeführt
                "reflect": True  # Alle Pipelines werden nach REFLECT ausgeführt
            }
        }
    
    # Speichere die Konfiguration
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(apm_integration, f, indent=2, ensure_ascii=False)
        logger.info(f"APM-Integration-Konfiguration gespeichert unter: {output_path}")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der APM-Integration-Konfiguration: {e}")

def create_apm_integration_module(output_path: str) -> None:
    """
    Erstellt ein Python-Modul für die Integration der Pipelines mit dem APM-Framework.
    
    Args:
        output_path: Der Pfad, an dem das Modul gespeichert werden soll
    """
    module_content = """# -*- coding: utf-8 -*-
\"\"\"
APM-Pipeline-Integration für VALEO-NeuroERP

Dieses Modul integriert die Pipelines mit dem APM-Framework.
\"\"\"

import json
import logging
import os
from typing import Dict, Any, List, Optional

from core.apm_phases import APMPhase, PhaseManager
from linkup_mcp.apm_framework import Pipeline, PipelineContext
from linkup_mcp.tools import (
    NetworkSimulator, 
    SynchronizationAnalyzer, 
    DataConsistencyValidator
)

logger = logging.getLogger(__name__)

class APMPipelineIntegration:
    \"\"\"
    Integration der Pipelines mit dem APM-Framework.
    \"\"\"
    
    def __init__(self, config_path: Optional[str] = None):
        \"\"\"
        Initialisiert die APM-Pipeline-Integration.
        
        Args:
            config_path: Der Pfad zur Konfigurationsdatei
        \"\"\"
        self.config_path = config_path or os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                                     "config", "apm_pipeline_integration.json")
        self.config = self._load_config()
        self.phase_manager = PhaseManager()
        self.pipeline_context = self._create_pipeline_context()
    
    def _load_config(self) -> Dict[str, Any]:
        \"\"\"
        Lädt die Konfiguration aus der JSON-Datei.
        
        Returns:
            Die Konfiguration
        \"\"\"
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Fehler beim Laden der APM-Pipeline-Integration-Konfiguration: {e}")
            return {"pipeline_mode": {"enabled": False}, "pipelines": {}}
    
    def _create_pipeline_context(self) -> PipelineContext:
        \"\"\"
        Erstellt den Pipeline-Kontext mit den benötigten Tools.
        
        Returns:
            Der Pipeline-Kontext
        \"\"\"
        # Initialisiere gemeinsame Tools
        network_simulator = NetworkSimulator()
        sync_analyzer = SynchronizationAnalyzer()
        data_consistency_validator = DataConsistencyValidator()
        
        # Initialisiere den gemeinsamen Kontext
        return PipelineContext({
            "network_simulator": network_simulator,
            "sync_analyzer": sync_analyzer,
            "data_consistency_validator": data_consistency_validator
        })
    
    def is_pipeline_mode_enabled(self) -> bool:
        \"\"\"
        Prüft, ob der Pipeline-Modus aktiviert ist.
        
        Returns:
            True, wenn der Pipeline-Modus aktiviert ist, sonst False
        \"\"\"
        return self.config.get("pipeline_mode", {}).get("enabled", False)
    
    def post_van_phase(self, van_result: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Wird nach der VAN-Phase ausgeführt.
        
        Args:
            van_result: Das Ergebnis der VAN-Phase
            
        Returns:
            Das Ergebnis der Pipeline-Ausführung
        \"\"\"
        if not self.is_pipeline_mode_enabled():
            return {"status": "skipped", "reason": "Pipeline-Modus ist deaktiviert"}
        
        # Setze die Phase
        self.phase_manager.set_phase(APMPhase.PIPELINE)
        
        # Führe nur die Pipelines aus, die für die VAN-Phase konfiguriert sind
        pipelines_to_run = self._get_pipelines_for_phase("van")
        
        # Führe die Pipelines aus
        return self._run_pipelines(pipelines_to_run)
    
    def post_plan_phase(self, plan_result: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Wird nach der PLAN-Phase ausgeführt.
        
        Args:
            plan_result: Das Ergebnis der PLAN-Phase
            
        Returns:
            Das Ergebnis der Pipeline-Ausführung
        \"\"\"
        if not self.is_pipeline_mode_enabled():
            return {"status": "skipped", "reason": "Pipeline-Modus ist deaktiviert"}
        
        # Setze die Phase
        self.phase_manager.set_phase(APMPhase.PIPELINE)
        
        # Führe nur die Pipelines aus, die für die PLAN-Phase konfiguriert sind
        pipelines_to_run = self._get_pipelines_for_phase("plan")
        
        # Führe die Pipelines aus
        return self._run_pipelines(pipelines_to_run)
    
    def post_create_phase(self, create_result: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Wird nach der CREATE-Phase ausgeführt.
        
        Args:
            create_result: Das Ergebnis der CREATE-Phase
            
        Returns:
            Das Ergebnis der Pipeline-Ausführung
        \"\"\"
        if not self.is_pipeline_mode_enabled():
            return {"status": "skipped", "reason": "Pipeline-Modus ist deaktiviert"}
        
        # Setze die Phase
        self.phase_manager.set_phase(APMPhase.PIPELINE)
        
        # Führe nur die Pipelines aus, die für die CREATE-Phase konfiguriert sind
        pipelines_to_run = self._get_pipelines_for_phase("create")
        
        # Führe die Pipelines aus
        return self._run_pipelines(pipelines_to_run)
    
    def post_implement_phase(self, implement_result: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Wird nach der IMPLEMENT-Phase ausgeführt.
        
        Args:
            implement_result: Das Ergebnis der IMPLEMENT-Phase
            
        Returns:
            Das Ergebnis der Pipeline-Ausführung
        \"\"\"
        if not self.is_pipeline_mode_enabled():
            return {"status": "skipped", "reason": "Pipeline-Modus ist deaktiviert"}
        
        # Setze die Phase
        self.phase_manager.set_phase(APMPhase.PIPELINE)
        
        # Führe nur die Pipelines aus, die für die IMPLEMENT-Phase konfiguriert sind
        pipelines_to_run = self._get_pipelines_for_phase("implement")
        
        # Führe die Pipelines aus
        return self._run_pipelines(pipelines_to_run)
    
    def post_reflect_phase(self, reflect_result: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Wird nach der REFLECT-Phase ausgeführt.
        
        Args:
            reflect_result: Das Ergebnis der REFLECT-Phase
            
        Returns:
            Das Ergebnis der Pipeline-Ausführung
        \"\"\"
        if not self.is_pipeline_mode_enabled():
            return {"status": "skipped", "reason": "Pipeline-Modus ist deaktiviert"}
        
        # Setze die Phase
        self.phase_manager.set_phase(APMPhase.PIPELINE)
        
        # Führe nur die Pipelines aus, die für die REFLECT-Phase konfiguriert sind
        pipelines_to_run = self._get_pipelines_for_phase("reflect")
        
        # Führe die Pipelines aus
        return self._run_pipelines(pipelines_to_run)
    
    def _get_pipelines_for_phase(self, phase: str) -> List[Dict[str, Any]]:
        \"\"\"
        Gibt die Pipelines zurück, die für eine bestimmte Phase konfiguriert sind.
        
        Args:
            phase: Die Phase
            
        Returns:
            Liste von Pipeline-Konfigurationen
        \"\"\"
        pipelines = []
        
        for name, pipeline in self.config.get("pipelines", {}).items():
            if (pipeline.get("enabled", True) and 
                pipeline.get("integration_points", {}).get(phase, False)):
                pipelines.append(pipeline)
        
        # Sortiere nach Priorität
        return sorted(pipelines, key=lambda p: p.get("priority", 0))
    
    def _run_pipelines(self, pipelines: List[Dict[str, Any]]) -> Dict[str, Any]:
        \"\"\"
        Führt die angegebenen Pipelines aus.
        
        Args:
            pipelines: Liste von Pipeline-Konfigurationen
            
        Returns:
            Das Ergebnis der Pipeline-Ausführung
        \"\"\"
        # Hier würde die tatsächliche Ausführung der Pipelines stattfinden
        # Da dies nur ein Vorbereitungsskript ist, geben wir eine Nachricht zurück
        
        pipeline_names = [p.get("name") for p in pipelines]
        
        logger.info(f"Pipelines würden ausgeführt werden: {', '.join(pipeline_names)}")
        
        return {
            "status": "success",
            "message": "Pipeline-Integration vorbereitet",
            "pipelines": pipeline_names
        }
"""
    
    # Speichere das Modul
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(module_content)
        logger.info(f"APM-Integration-Modul gespeichert unter: {output_path}")
    except Exception as e:
        logger.error(f"Fehler beim Speichern des APM-Integration-Moduls: {e}")

def main():
    """
    Hauptfunktion zur Vorbereitung der Pipeline-Integration.
    """
    # Parse Kommandozeilenargumente
    parser = argparse.ArgumentParser(description="Bereitet die Integration der Pipelines mit dem APM-Framework vor")
    parser.add_argument("--config-output", default="config/apm_pipeline_integration.json",
                       help="Pfad für die Ausgabe der Konfigurationsdatei")
    parser.add_argument("--module-output", default="linkup_mcp/apm_framework/pipeline_integration.py",
                       help="Pfad für die Ausgabe des Python-Moduls")
    args = parser.parse_args()
    
    logger.info("Starte Vorbereitung der Pipeline-Integration")
    
    try:
        # Erstelle das logs-Verzeichnis, falls es nicht existiert
        os.makedirs('logs', exist_ok=True)
        
        # Erstelle die Konfigurationsdatei
        create_apm_integration_config(args.config_output)
        
        # Erstelle das Python-Modul
        create_apm_integration_module(args.module_output)
        
        logger.info("Pipeline-Integration vorbereitet")
        logger.info(f"Konfigurationsdatei: {args.config_output}")
        logger.info(f"Python-Modul: {args.module_output}")
        logger.info("")
        logger.info("Nächste Schritte:")
        logger.info("1. Überprüfen Sie die Konfigurationsdatei und passen Sie sie bei Bedarf an")
        logger.info("2. Importieren Sie das Modul in Ihren APM-Framework-Code")
        logger.info("3. Instanziieren Sie die APMPipelineIntegration-Klasse")
        logger.info("4. Rufen Sie die entsprechenden post_*_phase-Methoden nach den APM-Phasen auf")
    
    except Exception as e:
        logger.exception(f"Unerwarteter Fehler bei der Vorbereitung der Pipeline-Integration: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
