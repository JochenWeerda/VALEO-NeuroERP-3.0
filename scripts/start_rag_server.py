#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG-Server Starter für VALEO-NeuroERP

Dieses Skript startet den RAG-Service-Server mit den notwendigen Umgebungsvariablen.
"""

import os
import sys
import subprocess
import logging
import time
import json
from pathlib import Path

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Konstanten
RAG_API_TOKEN = "valeo_rag_api_token_2025"  # API-Token für den RAG-Server
MONGODB_URI = "mongodb://localhost:27017/"   # MongoDB-URI
MONGODB_DB = "valeo_neuroerp"               # MongoDB-Datenbankname
PROJECT_ID = "valeo_neuroerp_project"       # Projekt-ID

def create_token_file():
    """Erstellt eine Datei mit dem RAG-API-Token."""
    token_dir = Path("config/rag")
    token_dir.mkdir(parents=True, exist_ok=True)
    
    token_file = token_dir / "api_token.json"
    
    token_data = {
        "api_token": RAG_API_TOKEN,
        "created_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "expires_at": None  # Kein Ablaufdatum
    }
    
    with open(token_file, "w", encoding="utf-8") as f:
        json.dump(token_data, f, indent=2)
    
    logger.info(f"RAG-API-Token in {token_file} gespeichert")
    return token_file

def start_rag_server():
    """Startet den RAG-Service-Server."""
    # Umgebungsvariablen setzen
    env = os.environ.copy()
    env["RAG_API_TOKEN"] = RAG_API_TOKEN
    env["MONGODB_URI"] = MONGODB_URI
    env["MONGODB_DB"] = MONGODB_DB
    env["PROJECT_ID"] = PROJECT_ID
    
    # Token-Datei erstellen
    token_file = create_token_file()
    
    try:
        # Verzeichnis für Logs erstellen
        os.makedirs("logs", exist_ok=True)
        
        # RAG-Service-Server starten
        logger.info("Starte RAG-Service-Server...")
        
        # Befehl zum Starten des Servers
        cmd = [sys.executable, "-m", "backend.apm_framework.rag_service_server"]
        
        # Server im Hintergrund starten
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE  # Neues Konsolenfenster öffnen
        )
        
        # Kurz warten, um zu sehen, ob der Server startet
        time.sleep(2)
        
        # Prüfen, ob der Server läuft
        if process.poll() is None:
            logger.info("RAG-Service-Server erfolgreich gestartet")
            logger.info(f"API-Token: {RAG_API_TOKEN}")
            logger.info(f"Token-Datei: {token_file}")
            return True
        else:
            # Fehlerausgabe lesen
            stdout, stderr = process.communicate()
            logger.error(f"RAG-Service-Server konnte nicht gestartet werden")
            logger.error(f"Stdout: {stdout}")
            logger.error(f"Stderr: {stderr}")
            return False
    
    except Exception as e:
        logger.error(f"Fehler beim Starten des RAG-Service-Servers: {str(e)}")
        return False

def main():
    """Hauptfunktion."""
    print("=== VALEO-NeuroERP RAG-Server Starter ===")
    print(f"API-Token: {RAG_API_TOKEN}")
    print(f"MongoDB-URI: {MONGODB_URI}")
    print(f"MongoDB-DB: {MONGODB_DB}")
    print(f"Projekt-ID: {PROJECT_ID}")
    print("=========================================")
    
    success = start_rag_server()
    
    if success:
        print("\nRAG-Service-Server erfolgreich gestartet!")
        print("Der Server läuft jetzt im Hintergrund.")
        print(f"API-Token für Dashboard: {RAG_API_TOKEN}")
        print("\nBitte verwenden Sie diesen Token im Dashboard, wenn Sie")
        print("den RAG-Server als Informationsquelle auswählen.")
    else:
        print("\nFehler beim Starten des RAG-Service-Servers.")
        print("Bitte prüfen Sie die Logs für weitere Informationen.")
    
    input("\nDrücken Sie Enter, um fortzufahren...")

if __name__ == "__main__":
    main() 