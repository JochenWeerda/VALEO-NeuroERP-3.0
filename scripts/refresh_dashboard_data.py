#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS v1.3 Dashboard Daten-Aktualisierung
Dieses Script aktualisiert die Daten für das Streamlit-Dashboard.
"""

import os
import json
import yaml
import datetime
import time
import random
import logging
from pathlib import Path

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("dashboard_refresh.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("dashboard_refresh")

# Pfade definieren
SCRIPT_DIR = Path(__file__).parent
ROOT_DIR = SCRIPT_DIR.parent
DATA_DIR = ROOT_DIR / "data"
DASHBOARD_DATA_DIR = DATA_DIR / "dashboard"

# Stellen Sie sicher, dass die Verzeichnisse existieren
DASHBOARD_DATA_DIR.mkdir(parents=True, exist_ok=True)

class DashboardDataRefresher:
    """Klasse zum Aktualisieren der Dashboard-Daten"""
    
    def __init__(self):
        """Initialisiert den Dashboard-Daten-Aktualisierer"""
        self.config = self.load_config()
        self.phase_data = self.load_phase_data()
        self.pipeline_data = self.load_pipeline_data()
        self.artifact_data = self.load_artifact_data()
        
    def load_config(self):
        """Lädt die Konfigurationsdaten"""
        config_path = ROOT_DIR / "tasks" / "genxais_cycle_v1_3.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
            logger.info("Konfiguration erfolgreich geladen")
            return config
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {e}")
            # Fallback-Konfiguration
            return {
                "name": "GENXAIS Cycle v1.3",
                "version": "1.3",
                "phases": ["VAN", "PLAN", "CREATE", "IMPLEMENTATION", "REFLEKTION"]
            }
    
    def load_phase_data(self):
        """Lädt die Phasendaten oder erstellt Standarddaten"""
        phase_data_path = DASHBOARD_DATA_DIR / "phase_data.json"
        if phase_data_path.exists():
            try:
                with open(phase_data_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Phasendaten: {e}")
        
        # Standarddaten erstellen
        phases = self.config.get("phases", ["VAN", "PLAN", "CREATE", "IMPLEMENTATION", "REFLEKTION"])
        phase_data = {
            "phases": phases,
            "current_phase": "PLAN",
            "status": {
                "VAN": {"status": "Abgeschlossen", "progress": 100},
                "PLAN": {"status": "Aktiv", "progress": 45},
                "CREATE": {"status": "Ausstehend", "progress": 0},
                "IMPLEMENTATION": {"status": "Ausstehend", "progress": 0},
                "REFLEKTION": {"status": "Ausstehend", "progress": 0}
            },
            "last_updated": datetime.datetime.now().isoformat()
        }
        return phase_data
    
    def load_pipeline_data(self):
        """Lädt die Pipeline-Daten oder erstellt Standarddaten"""
        pipeline_data_path = DASHBOARD_DATA_DIR / "pipeline_data.json"
        if pipeline_data_path.exists():
            try:
                with open(pipeline_data_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Pipeline-Daten: {e}")
        
        # Standarddaten erstellen
        pipeline_count = self.config.get("pipeline", {}).get("pipelines", 5)
        pipeline_data = {
            "pipelines": [f"Pipeline {i+1}" for i in range(pipeline_count)],
            "status": {
                f"Pipeline {i+1}": {
                    "status": "Aktiv",
                    "progress": random.randint(40, 60),
                    "runtime": f"{random.randint(1, 2)}h {random.randint(0, 59)}m"
                } for i in range(pipeline_count)
            },
            "last_updated": datetime.datetime.now().isoformat()
        }
        return pipeline_data
    
    def load_artifact_data(self):
        """Lädt die Artefakt-Daten oder erstellt Standarddaten"""
        artifact_data_path = DASHBOARD_DATA_DIR / "artifact_data.json"
        if artifact_data_path.exists():
            try:
                with open(artifact_data_path, 'r', encoding='utf-8') as file:
                    return json.load(file)
            except Exception as e:
                logger.error(f"Fehler beim Laden der Artefakt-Daten: {e}")
        
        # Standarddaten erstellen
        artifacts = self.config.get("artifacts", {}).get("track", [
            "review_summary.md",
            "plan_overview.md",
            "create_snapshot.md",
            "implementation_review.md",
            "v1.3_final_review.md"
        ])
        
        now = datetime.datetime.now()
        artifact_data = {
            "artifacts": artifacts,
            "status": {
                "review_summary.md": {
                    "status": "Generiert",
                    "last_updated": (now - datetime.timedelta(hours=2, minutes=15)).isoformat()
                },
                "plan_overview.md": {
                    "status": "In Bearbeitung",
                    "last_updated": now.isoformat()
                },
                "create_snapshot.md": {
                    "status": "Ausstehend",
                    "last_updated": None
                },
                "implementation_review.md": {
                    "status": "Ausstehend",
                    "last_updated": None
                },
                "v1.3_final_review.md": {
                    "status": "Ausstehend",
                    "last_updated": None
                }
            },
            "last_updated": datetime.datetime.now().isoformat()
        }
        return artifact_data
    
    def update_phase_data(self):
        """Aktualisiert die Phasendaten"""
        current_phase = self.phase_data["current_phase"]
        phases = self.phase_data["phases"]
        
        # Aktuelle Phase aktualisieren
        if current_phase == "PLAN":
            # Fortschritt der aktuellen Phase erhöhen
            current_progress = self.phase_data["status"][current_phase]["progress"]
            new_progress = min(current_progress + random.randint(1, 5), 100)
            self.phase_data["status"][current_phase]["progress"] = new_progress
            
            # Wenn Phase abgeschlossen ist, zur nächsten Phase wechseln
            if new_progress >= 100:
                current_index = phases.index(current_phase)
                if current_index < len(phases) - 1:
                    next_phase = phases[current_index + 1]
                    self.phase_data["current_phase"] = next_phase
                    self.phase_data["status"][current_phase]["status"] = "Abgeschlossen"
                    self.phase_data["status"][next_phase]["status"] = "Aktiv"
                    logger.info(f"Phase gewechselt: {current_phase} -> {next_phase}")
        
        self.phase_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # Daten speichern
        phase_data_path = DASHBOARD_DATA_DIR / "phase_data.json"
        with open(phase_data_path, 'w', encoding='utf-8') as file:
            json.dump(self.phase_data, file, ensure_ascii=False, indent=2)
        
        logger.info("Phasendaten aktualisiert")
    
    def update_pipeline_data(self):
        """Aktualisiert die Pipeline-Daten"""
        for pipeline in self.pipeline_data["pipelines"]:
            # Fortschritt aktualisieren
            current_progress = self.pipeline_data["status"][pipeline]["progress"]
            new_progress = min(current_progress + random.randint(0, 3), 100)
            self.pipeline_data["status"][pipeline]["progress"] = new_progress
            
            # Laufzeit aktualisieren
            runtime = self.pipeline_data["status"][pipeline]["runtime"]
            hours, minutes = runtime.split("h ")
            minutes = minutes.replace("m", "")
            total_minutes = int(hours) * 60 + int(minutes) + random.randint(1, 5)
            new_hours = total_minutes // 60
            new_minutes = total_minutes % 60
            self.pipeline_data["status"][pipeline]["runtime"] = f"{new_hours}h {new_minutes}m"
            
            # Status aktualisieren
            if new_progress >= 100:
                self.pipeline_data["status"][pipeline]["status"] = "Abgeschlossen"
        
        self.pipeline_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # Daten speichern
        pipeline_data_path = DASHBOARD_DATA_DIR / "pipeline_data.json"
        with open(pipeline_data_path, 'w', encoding='utf-8') as file:
            json.dump(self.pipeline_data, file, ensure_ascii=False, indent=2)
        
        logger.info("Pipeline-Daten aktualisiert")
    
    def update_artifact_data(self):
        """Aktualisiert die Artefakt-Daten"""
        current_phase = self.phase_data["current_phase"]
        
        # Artefakte basierend auf der aktuellen Phase aktualisieren
        if current_phase == "PLAN":
            self.artifact_data["status"]["plan_overview.md"]["status"] = "In Bearbeitung"
            self.artifact_data["status"]["plan_overview.md"]["last_updated"] = datetime.datetime.now().isoformat()
        elif current_phase == "CREATE":
            self.artifact_data["status"]["plan_overview.md"]["status"] = "Generiert"
            self.artifact_data["status"]["create_snapshot.md"]["status"] = "In Bearbeitung"
            self.artifact_data["status"]["create_snapshot.md"]["last_updated"] = datetime.datetime.now().isoformat()
        
        self.artifact_data["last_updated"] = datetime.datetime.now().isoformat()
        
        # Daten speichern
        artifact_data_path = DASHBOARD_DATA_DIR / "artifact_data.json"
        with open(artifact_data_path, 'w', encoding='utf-8') as file:
            json.dump(self.artifact_data, file, ensure_ascii=False, indent=2)
        
        logger.info("Artefakt-Daten aktualisiert")
    
    def refresh_all(self):
        """Aktualisiert alle Dashboard-Daten"""
        logger.info("Starte Aktualisierung der Dashboard-Daten...")
        self.update_phase_data()
        self.update_pipeline_data()
        self.update_artifact_data()
        logger.info("Dashboard-Daten erfolgreich aktualisiert")

def main():
    """Hauptfunktion"""
    logger.info("Dashboard-Daten-Aktualisierung gestartet")
    refresher = DashboardDataRefresher()
    refresher.refresh_all()
    logger.info("Dashboard-Daten-Aktualisierung abgeschlossen")

if __name__ == "__main__":
    main() 