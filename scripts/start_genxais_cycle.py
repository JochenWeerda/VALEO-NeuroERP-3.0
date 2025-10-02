#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS v1.3/v1.4 Zyklus-Starter mit Prompt-Initialisierung
Dieses Script startet den GENXAIS-Zyklus basierend auf einem Initialisierungs-Prompt.
"""

import argparse
import yaml
import logging
import os
import sys
import time
import random
import datetime
import json
import subprocess
from pathlib import Path
import threading
import signal

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("genxais_cycle_prompt.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("genxais_cycle_prompt")

class GenxaisPromptRunner:
    """Klasse zum Ausführen des GENXAIS-Zyklus mit Prompt-Initialisierung"""
    
    def __init__(self, prompt_path):
        """Initialisiert den GENXAIS-Prompt-Runner"""
        self.prompt_path = prompt_path
        self.prompt_config = self.load_prompt_config()
        self.data_dir = Path("data/dashboard")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Extrahiere Phasen aus dem Prompt
        self.phases = self.extract_phases()
        self.current_phase = self.phases[0]
        
    def load_prompt_config(self):
        """Lädt die Prompt-Konfiguration"""
        try:
            with open(self.prompt_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info(f"Prompt-Konfiguration erfolgreich geladen aus {self.prompt_path}")
            return config
        except Exception as e:
            logger.error(f"Fehler beim Laden der Prompt-Konfiguration: {e}")
            sys.exit(1)
    
    def extract_phases(self):
        """Extrahiert die Phasen aus dem Prompt"""
        if isinstance(self.prompt_config, dict):
            return self.prompt_config.get("phases", ["VAN", "PLAN", "CREATE", "IMPLEMENTATION", "REFLEKTION"])
        return ["VAN", "PLAN", "CREATE", "IMPLEMENTATION", "REFLEKTION"]
    
    def generate_cycle_config(self):
        """Generiert die Zyklus-Konfiguration aus dem Prompt"""
        # Extrahiere Versioning-Informationen
        versioning = {}
        if isinstance(self.prompt_config, dict) and "versioning" in self.prompt_config:
            versioning = self.prompt_config["versioning"]
        
        current_version = "v1.3"
        next_version = "v1.4"
        
        if "current_version" in versioning:
            current_version = versioning["current_version"]
            if not current_version.startswith("v"):
                current_version = f"v{current_version}"
        
        if "next_version" in versioning:
            next_version = versioning["next_version"]
            if not next_version.startswith("v"):
                next_version = f"v{next_version}"
        elif "previous_version" in versioning:
            previous_version = versioning["previous_version"]
            if not previous_version.startswith("v"):
                previous_version = f"v{previous_version}"
            current_version = previous_version
            
            # Extrahiere die Versionsnummer und erhöhe sie
            if previous_version.startswith("v"):
                version_parts = previous_version[1:].split(".")
                if len(version_parts) > 1:
                    major = int(version_parts[0])
                    minor = int(version_parts[1])
                    minor += 1
                    next_version = f"v{major}.{minor}"
        
        # Extrahiere Kontext-Informationen
        context = {}
        if isinstance(self.prompt_config, dict):
            for key in ["orchestrator", "memory", "graph_knowledge", "database", "ui"]:
                if key in self.prompt_config:
                    context[key] = self.prompt_config[key]
        
        # Extrahiere Monitoring-Informationen
        monitoring = {
            "enabled": True,
            "streamlit_dashboard": True,
            "grafana_enabled": False,
            "prometheus_enabled": False,
            "ports": {
                "streamlit": 8501,
                "grafana": 3000,
                "prometheus": 9090
            }
        }
        
        if isinstance(self.prompt_config, dict) and "monitoring" in self.prompt_config:
            monitoring_config = self.prompt_config["monitoring"]
            if isinstance(monitoring_config, dict):
                if "grafana" in monitoring_config and monitoring_config["grafana"] == "enabled":
                    monitoring["grafana_enabled"] = True
                if "prometheus" in monitoring_config and monitoring_config["prometheus"] == "enabled":
                    monitoring["prometheus_enabled"] = True
        
        # Extrahiere Pipelines-Informationen
        pipelines = []
        if isinstance(self.prompt_config, dict) and "pipelines" in self.prompt_config:
            pipelines = self.prompt_config["pipelines"]
        
        # Extrahiere Ausgabe-Dokumente
        output_documents = []
        if isinstance(self.prompt_config, dict) and "output_documents" in self.prompt_config:
            output_documents = self.prompt_config["output_documents"]
        
        # Extrahiere Abschlussaktionen
        completion_actions = []
        if isinstance(self.prompt_config, dict):
            if "post_actions" in self.prompt_config:
                completion_actions = self.prompt_config["post_actions"]
            elif "actions" in self.prompt_config:
                completion_actions = self.prompt_config["actions"]
        
        # Generiere die Zyklus-Konfiguration
        cycle_config = {
            "name": f"GENXAIS Cycle {next_version} – Full Automation",
            "version": next_version.replace('v', ''),
            "type": "multi-phase-cycle",
            "phases": self.phases,
            "trigger": self.prompt_config.get("trigger", "cron"),
            "cron_schedule": self.prompt_config.get("schedule", "0 5 * * *"),
            "agent": "langgraph-mas",
            "context": context,
            "config": {
                "monitoring": monitoring
            },
            "pipeline": {
                "type": "multi-agent",
                "mode": "intelligent-parallel",
                "pipelines": len(pipelines)
            },
            "agents": self.extract_agents(pipelines),
            "goals": self.extract_goals(pipelines),
            "artifacts": {
                "track": output_documents
            },
            "versioning": {
                "current_version": current_version.replace('v', ''),
                "next_version": next_version.replace('v', ''),
                "version_function": "increment_version()"
            },
            "graphiti_config": {
                "activate": True,
                "enable_fallback_paths": True,
                "link_memory_to_graph": True,
                "visualize_decisions": True,
                "output": "graphiti_trace.md"
            },
            "completion": completion_actions
        }
        
        return cycle_config
    
    def extract_agents(self, pipelines):
        """Extrahiert die Agenten aus den Pipelines"""
        all_agents = []
        for pipeline in pipelines:
            if "agents" in pipeline:
                all_agents.extend(pipeline["agents"])
        
        # Entferne Duplikate und formatiere den GraphNavigator-Agenten
        unique_agents = list(set(all_agents))
        if "GraphitiAgent" in unique_agents:
            unique_agents.remove("GraphitiAgent")
            unique_agents.append("GraphNavigator (Graphiti)")
        
        return unique_agents
    
    def extract_goals(self, pipelines):
        """Extrahiert die Ziele aus den Pipelines"""
        all_goals = []
        for pipeline in pipelines:
            if "goals" in pipeline:
                all_goals.extend(pipeline["goals"])
        
        # Wähle die wichtigsten Ziele aus (maximal 5)
        if len(all_goals) > 5:
            return all_goals[:5]
        return all_goals
    
    def save_cycle_config(self):
        """Speichert die generierte Zyklus-Konfiguration"""
        cycle_config = self.generate_cycle_config()
        
        # Bestimme den Dateinamen basierend auf der Version
        version = cycle_config["version"]
        config_path = Path("tasks") / f"genxais_cycle_v{version}_from_prompt.yaml"
        
        # Stelle sicher, dass das Verzeichnis existiert
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Speichere die Konfiguration
        with open(config_path, 'w', encoding='utf-8') as file:
            yaml.dump(cycle_config, file, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Zyklus-Konfiguration gespeichert unter {config_path}")
        return config_path
    
    def initialize_dashboard_data(self):
        """Initialisiert die Dashboard-Daten basierend auf dem Prompt"""
        # Phasendaten
        phase_data = {
            "phases": self.phases,
            "current_phase": self.current_phase,
            "status": {
                phase: {
                    "status": "Ausstehend" if phase != self.current_phase else "Aktiv", 
                    "progress": 0
                } for phase in self.phases
            },
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        # Pipeline-Daten
        pipelines = []
        if isinstance(self.prompt_config, dict) and "pipelines" in self.prompt_config:
            pipelines = [pipeline.get("name", f"Pipeline {i+1}") for i, pipeline in enumerate(self.prompt_config["pipelines"])]
        else:
            pipelines = [f"Pipeline {i+1}" for i in range(5)]
        
        pipeline_data = {
            "pipelines": pipelines,
            "status": {
                pipeline: {
                    "status": "Initialisierung",
                    "progress": 0,
                    "runtime": "0h 0m"
                } for pipeline in pipelines
            },
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        # Artefakt-Daten
        artifacts = []
        if isinstance(self.prompt_config, dict) and "output_documents" in self.prompt_config:
            artifacts = self.prompt_config["output_documents"]
        
        artifact_data = {
            "artifacts": artifacts,
            "status": {
                artifact: {
                    "status": "Ausstehend",
                    "last_updated": None
                } for artifact in artifacts
            },
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        # Graphiti-Daten
        graphiti_data = {
            "nodes": [
                {"id": "start", "label": "Start", "type": "entry", "status": "completed"},
                {"id": "van_phase", "label": "VAN Phase", "type": "phase", "status": "active"},
                {"id": "plan_phase", "label": "PLAN Phase", "type": "phase", "status": "pending"},
                {"id": "create_phase", "label": "CREATE Phase", "type": "phase", "status": "pending"},
                {"id": "implementation_phase", "label": "IMPLEMENTATION Phase", "type": "phase", "status": "pending"},
                {"id": "reflection_phase", "label": "REFLECTION Phase", "type": "phase", "status": "pending"},
                {"id": "end", "label": "End", "type": "exit", "status": "pending"}
            ],
            "edges": [
                {"source": "start", "target": "van_phase", "label": "Start Cycle"},
                {"source": "van_phase", "target": "plan_phase", "label": "VAN Complete"},
                {"source": "plan_phase", "target": "create_phase", "label": "PLAN Complete"},
                {"source": "create_phase", "target": "implementation_phase", "label": "CREATE Complete"},
                {"source": "implementation_phase", "target": "reflection_phase", "label": "IMPLEMENTATION Complete"},
                {"source": "reflection_phase", "target": "end", "label": "REFLECTION Complete"}
            ],
            "config": {
                "activate": True,
                "enable_fallback_paths": True,
                "link_memory_to_graph": True,
                "visualize_decisions": True
            },
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        # Speichere die Daten
        phase_data_path = self.data_dir / "phase_data.json"
        pipeline_data_path = self.data_dir / "pipeline_data.json"
        artifact_data_path = self.data_dir / "artifact_data.json"
        graphiti_data_path = self.data_dir / "graphiti_data.json"
        
        with open(phase_data_path, 'w', encoding='utf-8') as file:
            json.dump(phase_data, file, ensure_ascii=False, indent=2)
        with open(pipeline_data_path, 'w', encoding='utf-8') as file:
            json.dump(pipeline_data, file, ensure_ascii=False, indent=2)
        with open(artifact_data_path, 'w', encoding='utf-8') as file:
            json.dump(artifact_data, file, ensure_ascii=False, indent=2)
        with open(graphiti_data_path, 'w', encoding='utf-8') as file:
            json.dump(graphiti_data, file, ensure_ascii=False, indent=2)
        
        logger.info("Dashboard-Daten initialisiert")
    
    def start_dashboard(self):
        """Startet das Streamlit-Dashboard"""
        try:
            # Prüfe, ob wir unter Windows oder Linux laufen
            if os.name == 'nt':  # Windows
                cmd = ["start", "powershell", "-ArgumentList", 
                       "-NoExit", "-Command", "python -m streamlit run scripts/init_dashboard.py"]
                subprocess.Popen(" ".join(cmd), shell=True)
            else:  # Linux/Mac
                cmd = ["python", "-m", "streamlit", "run", "scripts/init_dashboard.py"]
                subprocess.Popen(cmd, start_new_session=True)
            
            logger.info("Streamlit-Dashboard gestartet")
            # Kurz warten, damit das Dashboard Zeit hat zu starten
            time.sleep(2)
        except Exception as e:
            logger.error(f"Fehler beim Starten des Dashboards: {e}")
    
    def start_cycle(self):
        """Startet den GENXAIS-Zyklus"""
        # Generiere und speichere die Zyklus-Konfiguration
        config_path = self.save_cycle_config()
        
        # Initialisiere die Dashboard-Daten
        self.initialize_dashboard_data()
        
        # Starte das Dashboard
        self.start_dashboard()
        
        # Starte den Zyklus
        try:
            logger.info(f"Starte GENXAIS-Zyklus mit Konfiguration aus {config_path}")
            cmd = ["python", "launch_cycle.py", "--config", str(config_path)]
            subprocess.run(cmd)
            logger.info("GENXAIS-Zyklus abgeschlossen")
        except Exception as e:
            logger.error(f"Fehler beim Starten des GENXAIS-Zyklus: {e}")

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description="GENXAIS v1.3/v1.4 Zyklus-Starter mit Prompt-Initialisierung")
    parser.add_argument("--prompt", required=True, help="Pfad zum Initialisierungs-Prompt")
    args = parser.parse_args()
    
    runner = GenxaisPromptRunner(args.prompt)
    runner.start_cycle()

if __name__ == "__main__":
    main() 