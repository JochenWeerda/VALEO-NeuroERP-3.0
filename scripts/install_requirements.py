#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Installationsskript für VALEO-NeuroERP Streamlit-App und Cursor-Integration

Dieses Skript installiert alle benötigten Abhängigkeiten für die Streamlit-App
und die Cursor-Integration.
"""

import os
import sys
import subprocess
import platform

# Liste der benötigten Pakete
REQUIRED_PACKAGES = [
    "streamlit>=1.22.0",
    "flask>=2.0.0",
    "pyyaml>=6.0",
    "requests>=2.28.0",
    "pyperclip>=1.8.2",
    "openai>=0.27.0",
    "watchdog>=2.1.0",
    "modelcontextprotocol>=0.1.0",  # Falls verfügbar, ansonsten muss angepasst werden
]

def check_python_version():
    """Überprüft die Python-Version."""
    if sys.version_info < (3, 8):
        print("Python 3.8 oder höher wird benötigt.")
        sys.exit(1)

def install_packages():
    """Installiert die benötigten Pakete."""
    print("Installiere benötigte Pakete...")
    
    try:
        # Pip aktualisieren
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Pakete installieren
        for package in REQUIRED_PACKAGES:
            try:
                print(f"Installiere {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError:
                print(f"Fehler bei der Installation von {package}. Versuche ohne Version...")
                package_name = package.split(">=")[0]
                subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        
        print("Alle Pakete wurden erfolgreich installiert!")
    
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Installation: {str(e)}")
        sys.exit(1)

def create_directories():
    """Erstellt die benötigten Verzeichnisse."""
    directories = [
        "config",
        "data/reports",
        "data/handover",
        "data/cursor_prompts",
        "assets"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Verzeichnis {directory} erstellt oder bereits vorhanden.")

def create_config_files():
    """Erstellt die benötigten Konfigurationsdateien."""
    # Version-Konfiguration
    if not os.path.exists("config/version.yaml"):
        with open("config/version.yaml", "w") as file:
            file.write("current_version: '1.8.1'\n")
        print("Konfigurationsdatei config/version.yaml erstellt.")
    
    # Pipeline-Status
    if not os.path.exists("data/pipeline_status.json"):
        with open("data/pipeline_status.json", "w") as file:
            file.write('{"phase": "none", "progress": 0, "status": "idle", "completed": []}\n')
        print("Pipeline-Status-Datei data/pipeline_status.json erstellt.")

def create_environment_file():
    """Erstellt eine .env-Datei für Umgebungsvariablen."""
    if not os.path.exists(".env"):
        with open(".env", "w") as file:
            file.write("# Umgebungsvariablen für VALEO-NeuroERP\n")
            file.write("OPENAI_API_KEY=\n")
            file.write("CURSOR_API_KEY=\n")
            file.write("CURSOR_API_URL=http://localhost:6500/api/v1\n")
        print(".env-Datei erstellt. Bitte API-Keys eintragen.")

def create_startup_script():
    """Erstellt ein Startskript für die Anwendung."""
    if platform.system() == "Windows":
        with open("start_app.bat", "w") as file:
            file.write("@echo off\n")
            file.write("echo Starte VALEO-NeuroERP Streamlit-App...\n")
            file.write("start \"Cursor Prompt Integration\" python scripts/cursor_prompt_integration.py\n")
            file.write("start \"VALEO-NeuroERP App\" streamlit run scripts/streamlit_app_mcp_integration.py\n")
        print("Windows-Startskript start_app.bat erstellt.")
    else:
        with open("start_app.sh", "w") as file:
            file.write("#!/bin/bash\n")
            file.write("echo \"Starte VALEO-NeuroERP Streamlit-App...\"\n")
            file.write("python scripts/cursor_prompt_integration.py &\n")
            file.write("streamlit run scripts/streamlit_app_mcp_integration.py\n")
        os.chmod("start_app.sh", 0o755)
        print("Unix-Startskript start_app.sh erstellt.")

def main():
    """Hauptfunktion des Installationsskripts."""
    print("VALEO-NeuroERP Installation")
    print("==========================")
    
    # Python-Version prüfen
    check_python_version()
    
    # Verzeichnisse erstellen
    create_directories()
    
    # Konfigurationsdateien erstellen
    create_config_files()
    
    # Umgebungsvariablen-Datei erstellen
    create_environment_file()
    
    # Pakete installieren
    install_packages()
    
    # Startskript erstellen
    create_startup_script()
    
    print("\nInstallation abgeschlossen!")
    print("Um die Anwendung zu starten, führen Sie das Startskript aus:")
    if platform.system() == "Windows":
        print("  start_app.bat")
    else:
        print("  ./start_app.sh")
    
    print("\nHinweis: Bitte tragen Sie Ihre API-Keys in der .env-Datei ein.")

if __name__ == "__main__":
    main() 