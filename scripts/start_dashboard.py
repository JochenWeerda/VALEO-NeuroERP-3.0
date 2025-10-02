***REMOVED***!/usr/bin/env python
***REMOVED*** -*- coding: utf-8 -*-

"""
GENXAIS Dashboard Starter
Dieses Skript startet das Streamlit-Dashboard zur Überwachung des GENXAIS-Zyklus.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def main():
    """Hauptfunktion zum Starten des Dashboards"""
    print("Starte GENXAIS Dashboard...")
    
    ***REMOVED*** Prüfe, ob Streamlit installiert ist
    try:
        import streamlit
        print("Streamlit gefunden.")
    except ImportError:
        print("Streamlit nicht gefunden. Installiere Streamlit...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"], check=True)
        print("Streamlit installiert.")
    
    ***REMOVED*** Prüfe, ob das Dashboard-Skript existiert
    dashboard_script = Path("scripts/enhanced_dashboard.py")
    if not dashboard_script.exists():
        print(f"Fehler: Dashboard-Skript {dashboard_script} nicht gefunden.")
        return
    
    ***REMOVED*** Starte das Dashboard
    print("Starte Streamlit-Server...")
    
    ***REMOVED*** Setze Umgebungsvariablen für Streamlit
    os.environ["STREAMLIT_SERVER_PORT"] = "8501"
    os.environ["STREAMLIT_SERVER_HEADLESS"] = "true"
    
    ***REMOVED*** Starte Streamlit-Server
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(dashboard_script),
            "--server.port", "8501",
            "--server.headless", "true"
        ], check=True)
    except KeyboardInterrupt:
        print("\nDashboard beendet.")
    except Exception as e:
        print(f"Fehler beim Starten des Dashboards: {e}")

if __name__ == "__main__":
    main() 