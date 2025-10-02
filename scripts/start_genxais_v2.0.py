#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS v2.0 Starter
------------------
Dieses Skript startet den GENXAIS v2.0 Produktions-Zyklus für VALEO-NeuroERP mit Landhandel-Modulen.
"""

import os
import sys
import json
import yaml
import datetime
import logging
import subprocess
from pathlib import Path

# Pfade konfigurieren
BASE_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = BASE_DIR / "tasks"
OUTPUT_DIR = BASE_DIR / "output"
CONFIG_DIR = BASE_DIR / "config"
PROMPTS_DIR = BASE_DIR / "prompts"
SCRIPTS_DIR = BASE_DIR / "scripts"

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(OUTPUT_DIR / "genxais_v2.0.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("GENXAIS-v2.0")

def check_prerequisites():
    """
    Überprüft, ob alle Voraussetzungen für den Start des Zyklus erfüllt sind.
    
    Returns:
        bool: True, wenn alle Voraussetzungen erfüllt sind, sonst False
    """
    # Überprüfe, ob die Konfigurationsdatei existiert
    config_path = TASKS_DIR / "genxais_cycle_v2.0.yaml"
    if not config_path.exists():
        logger.error(f"Konfigurationsdatei nicht gefunden: {config_path}")
        return False
    
    # Überprüfe, ob der Prompt existiert
    prompt_path = PROMPTS_DIR / "genxais_prompt_v2.0.md"
    if not prompt_path.exists():
        logger.error(f"Prompt-Datei nicht gefunden: {prompt_path}")
        return False
    
    # Überprüfe, ob das LangGraph-Skript existiert
    langgraph_path = SCRIPTS_DIR / "start_langgraph_cycle.py"
    if not langgraph_path.exists():
        logger.error(f"LangGraph-Skript nicht gefunden: {langgraph_path}")
        return False
    
    # Überprüfe, ob das Dashboard-Skript existiert
    dashboard_path = SCRIPTS_DIR / "streamlit_dashboard.py"
    if not dashboard_path.exists():
        logger.error(f"Dashboard-Skript nicht gefunden: {dashboard_path}")
        return False
    
    # Überprüfe, ob die API-Schlüssel vorhanden sind
    api_keys_path = CONFIG_DIR / "api_keys.local.json"
    if not api_keys_path.exists():
        logger.error(f"API-Schlüssel-Datei nicht gefunden: {api_keys_path}")
        return False
    
    return True

def update_dashboard_config():
    """
    Aktualisiert die Dashboard-Konfiguration für GENXAIS v2.0.
    """
    config_path = OUTPUT_DIR / "dashboard_config.json"
    
    # Standardkonfiguration
    config = {
        "version": "v2.0",
        "phase": "VAN",
        "load_components": ["handover", "memorybank", "rag", "todos", "artefacts", "landhandel", "ai_models"],
        "start_time": datetime.datetime.now().isoformat(),
        "title": "GENXAIS v2.0 VALEO-NeuroERP für Landhandel"
    }
    
    # Speichere die Konfiguration
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, default=str)
        logger.info(f"Dashboard-Konfiguration aktualisiert: {config_path}")
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Dashboard-Konfiguration: {str(e)}")

def start_dashboard():
    """
    Startet das Streamlit-Dashboard.
    
    Returns:
        subprocess.Popen: Der Prozess des Dashboards
    """
    try:
        # Starte das Dashboard im Hintergrund
        dashboard_process = subprocess.Popen(
            ["streamlit", "run", str(SCRIPTS_DIR / "streamlit_dashboard.py"), "--server.port=8502"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logger.info("Dashboard gestartet auf http://localhost:8502")
        return dashboard_process
    except Exception as e:
        logger.error(f"Fehler beim Starten des Dashboards: {str(e)}")
        return None

def start_langgraph_cycle():
    """
    Startet den LangGraph-Zyklus.
    
    Returns:
        int: Der Exit-Code des LangGraph-Zyklus
    """
    try:
        # Kopiere den Prompt in die Umgebungsvariable
        with open(PROMPTS_DIR / "genxais_prompt_v2.0.md", "r", encoding="utf-8") as f:
            os.environ["GENXAIS_PROMPT"] = f.read()
        
        # Setze die Version in der Umgebungsvariable
        os.environ["GENXAIS_VERSION"] = "2.0"
        
        # Starte den LangGraph-Zyklus
        result = subprocess.run(
            ["python", str(SCRIPTS_DIR / "start_langgraph_cycle.py")],
            capture_output=True,
            text=True
        )
        
        # Logge die Ausgabe
        logger.info(f"LangGraph-Zyklus abgeschlossen mit Exit-Code {result.returncode}")
        if result.stdout:
            logger.info(f"Ausgabe: {result.stdout}")
        if result.stderr:
            logger.error(f"Fehler: {result.stderr}")
        
        return result.returncode
    except Exception as e:
        logger.error(f"Fehler beim Starten des LangGraph-Zyklus: {str(e)}")
        return -1

def main():
    """
    Hauptfunktion zum Starten des GENXAIS v2.0 Zyklus.
    """
    print("=" * 80)
    print("GENXAIS v2.0 Starter für VALEO-NeuroERP mit Landhandel-Modulen")
    print("=" * 80)
    print(f"Startzeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Projektverzeichnis: {BASE_DIR}")
    print("-" * 80)
    
    # Überprüfe die Voraussetzungen
    if not check_prerequisites():
        logger.error("Voraussetzungen nicht erfüllt. Beende Programm.")
        sys.exit(1)
    
    # Aktualisiere die Dashboard-Konfiguration
    update_dashboard_config()
    
    # Starte das Dashboard
    dashboard_process = start_dashboard()
    
    # Starte den LangGraph-Zyklus
    exit_code = start_langgraph_cycle()
    
    print("-" * 80)
    if exit_code == 0:
        print("GENXAIS v2.0 Zyklus erfolgreich abgeschlossen.")
    else:
        print(f"GENXAIS v2.0 Zyklus mit Fehler beendet (Exit-Code: {exit_code}).")
    print(f"Endzeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Warte auf Benutzer-Eingabe, um das Dashboard zu beenden
    input("Drücken Sie Enter, um das Dashboard zu beenden...")
    
    # Beende das Dashboard
    if dashboard_process:
        dashboard_process.terminate()

if __name__ == "__main__":
    main() 