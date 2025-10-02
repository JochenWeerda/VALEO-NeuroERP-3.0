#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
GENXAIS v1.9 Starter
--------------------
Dieses Skript startet den GENXAIS v1.9 Zyklus.
"""

import os
import sys
import json
import subprocess
import time
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Pfade konfigurieren
BASE_DIR = Path(__file__).resolve().parent.parent
TASKS_DIR = BASE_DIR / "tasks"
OUTPUT_DIR = BASE_DIR / "output"
CONFIG_PATH = OUTPUT_DIR / "dashboard_config.json"

def load_config() -> Dict[str, Any]:
    """
    Lädt die Dashboard-Konfiguration.
    
    Returns:
        Dict mit der Konfiguration
    """
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Fehler beim Laden der Konfiguration: {str(e)}")
            return {
                "version": "v1.9",
                "phase": "VAN",
                "load_components": ["handover", "memorybank", "rag", "todos", "artefacts"],
                "start_time": datetime.datetime.now().isoformat()
            }
    
    # Wenn keine Konfiguration existiert, erstelle eine neue
    config = {
        "version": "v1.9",
        "phase": "VAN",
        "load_components": ["handover", "memorybank", "rag", "todos", "artefacts"],
        "start_time": datetime.datetime.now().isoformat()
    }
    save_config(config)
    return config

def save_config(config: Dict[str, Any]) -> None:
    """
    Speichert die Dashboard-Konfiguration.
    
    Args:
        config: Die zu speichernde Konfiguration
    """
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, default=str)
    except Exception as e:
        print(f"Fehler beim Speichern der Konfiguration: {str(e)}")

def start_streamlit_dashboard() -> None:
    """
    Startet das Streamlit-Dashboard.
    """
    print("Starte Streamlit-Dashboard...")
    
    try:
        # Starte das Dashboard im Hintergrund
        subprocess.Popen(
            ["streamlit", "run", "scripts/streamlit_dashboard.py", "--server.port=8502"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        print("Streamlit-Dashboard gestartet auf Port 8502.")
        print("Öffne http://localhost:8502 im Browser.")
    except Exception as e:
        print(f"Fehler beim Starten des Streamlit-Dashboards: {str(e)}")

def start_langgraph_cycle() -> None:
    """
    Startet den LangGraph-Zyklus.
    """
    print("Starte LangGraph-Zyklus...")
    
    try:
        # Starte den LangGraph-Zyklus
        subprocess.run(
            ["python", "scripts/start_langgraph_cycle.py"],
            check=True
        )
        
        print("LangGraph-Zyklus abgeschlossen.")
    except Exception as e:
        print(f"Fehler beim Starten des LangGraph-Zyklus: {str(e)}")

def main() -> None:
    """
    Hauptfunktion zum Starten von GENXAIS v1.9.
    """
    print("=" * 80)
    print("GENXAIS v1.9 Starter")
    print("=" * 80)
    print(f"Startzeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Projektverzeichnis: {BASE_DIR}")
    print("-" * 80)
    
    # Lade die Konfiguration
    config = load_config()
    
    # Starte das Streamlit-Dashboard
    start_streamlit_dashboard()
    
    # Warte kurz, damit das Dashboard starten kann
    time.sleep(2)
    
    # Starte den LangGraph-Zyklus
    start_langgraph_cycle()
    
    print("-" * 80)
    print(f"Endzeit: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

if __name__ == "__main__":
    main() 