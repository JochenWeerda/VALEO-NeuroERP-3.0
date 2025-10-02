***REMOVED***!/usr/bin/env python3
***REMOVED*** -*- coding: utf-8 -*-

"""
MCP-Server für VALEO-NeuroERP

Dieser Server stellt API-Endpunkte für die Kommunikation mit dem MCP-System bereit.
"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from flask import Flask, request, jsonify

***REMOVED*** Verhindere, dass Flask nach .env-Dateien sucht
os.environ["FLASK_SKIP_DOTENV"] = "1"

***REMOVED*** Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

***REMOVED*** Erstelle das Logs-Verzeichnis, falls es nicht existiert
os.makedirs("logs", exist_ok=True)

***REMOVED*** Füge den File-Handler separat hinzu, um Fehler zu vermeiden
try:
    file_handler = logging.FileHandler("logs/mcp_server.log", mode="a", encoding="utf-8")
    logging.getLogger().addHandler(file_handler)
except Exception as e:
    print(f"Warnung: Konnte Log-Datei nicht erstellen: {str(e)}")

logger = logging.getLogger("mcp_server")

***REMOVED*** Flask-App initialisieren
app = Flask(__name__)

***REMOVED*** API-Key (standardmäßig der LinkUp API-Key)
API_KEY = os.environ.get("LINKUP_API_KEY", "aca0b877-88dd-4423-a35b-97de39012db9")

***REMOVED*** Status-Informationen
SERVER_STATUS = {
    "status": "running",
    "start_time": datetime.now().isoformat(),
    "processed_prompts": 0,
    "last_prompt_time": None,
    "api_key_set": bool(API_KEY)
}

def verify_api_key(request):
    """Überprüft den API-Key, falls einer gesetzt ist."""
    ***REMOVED*** Wenn kein API-Key gesetzt ist, erlaube alle Anfragen
    if not API_KEY:
        return True
    
    ***REMOVED*** Prüfe den API-Key im Header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        return token == API_KEY
    
    ***REMOVED*** Prüfe den API-Key als Parameter
    api_key = request.args.get("api_key") or (request.json or {}).get("api_key")
    return api_key == API_KEY

@app.route("/api/status", methods=["GET"])
def get_status():
    """Gibt den aktuellen Status des Servers zurück."""
    ***REMOVED*** API-Key-Überprüfung für Status-Endpunkt ist optional
    return jsonify({
        "status": SERVER_STATUS["status"],
        "uptime": (datetime.now() - datetime.fromisoformat(SERVER_STATUS["start_time"])).total_seconds(),
        "processed_prompts": SERVER_STATUS["processed_prompts"],
        "last_prompt_time": SERVER_STATUS["last_prompt_time"],
        "api_key_required": bool(API_KEY)
    })

@app.route("/api/prompt", methods=["POST"])
def process_prompt():
    """Verarbeitet einen eingehenden Prompt."""
    try:
        ***REMOVED*** API-Key-Überprüfung
        if API_KEY and not verify_api_key(request):
            return jsonify({"error": "Ungültiger API-Key"}), 401
        
        data = request.json
        
        if not data:
            return jsonify({"error": "Keine Daten empfangen"}), 400
        
        prompt = data.get("prompt")
        if not prompt:
            return jsonify({"error": "Kein Prompt gefunden"}), 400
        
        logger.info(f"Neuer Prompt empfangen: {prompt[:50]}...")
        
        ***REMOVED*** Prompt speichern
        save_prompt(prompt)
        
        ***REMOVED*** Status aktualisieren
        SERVER_STATUS["processed_prompts"] += 1
        SERVER_STATUS["last_prompt_time"] = datetime.now().isoformat()
        
        ***REMOVED*** Hier könnte die eigentliche Verarbeitung des Prompts stattfinden
        ***REMOVED*** z.B. Weiterleitung an ein LLM, Speicherung in einer Datenbank, etc.
        
        return jsonify({
            "success": True,
            "message": "Prompt erfolgreich verarbeitet",
            "timestamp": datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Fehler bei der Verarbeitung des Prompts: {str(e)}")
        return jsonify({"error": str(e)}), 500

def save_prompt(prompt):
    """Speichert einen Prompt in einer Datei."""
    try:
        os.makedirs("data/prompts", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with open(f"data/prompts/prompt_{timestamp}.md", "w", encoding="utf-8") as f:
            f.write(prompt)
        
        logger.info(f"Prompt gespeichert als prompt_{timestamp}.md")
    except Exception as e:
        logger.error(f"Fehler beim Speichern des Prompts: {str(e)}")

@app.route("/api/health", methods=["GET"])
def health_check():
    """Einfacher Health-Check-Endpunkt."""
    return jsonify({"status": "healthy"})

@app.route("/api/set_api_key", methods=["POST"])
def set_api_key():
    """Setzt den API-Key (nur für administrative Zwecke)."""
    ***REMOVED*** Diese Funktion sollte in einer Produktionsumgebung durch eine sichere Methode ersetzt werden
    global API_KEY  ***REMOVED*** Globale Variable vor der Verwendung deklarieren
    
    try:
        ***REMOVED*** Überprüfe, ob der aktuelle API-Key korrekt ist (falls gesetzt)
        if API_KEY and not verify_api_key(request):
            return jsonify({"error": "Ungültiger API-Key"}), 401
        
        data = request.json
        if not data or "new_api_key" not in data:
            return jsonify({"error": "Kein neuer API-Key gefunden"}), 400
        
        ***REMOVED*** API-Key setzen
        os.environ["LINKUP_API_KEY"] = data["new_api_key"]
        ***REMOVED*** Aktualisiere die globale Variable
        API_KEY = data["new_api_key"]
        SERVER_STATUS["api_key_set"] = bool(API_KEY)
        
        return jsonify({
            "success": True,
            "message": "API-Key erfolgreich gesetzt"
        })
    
    except Exception as e:
        logger.error(f"Fehler beim Setzen des API-Keys: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/linkup_search", methods=["POST"])
def linkup_search():
    """Führt eine Suche mit dem LinkUp-Client durch."""
    try:
        ***REMOVED*** API-Key-Überprüfung
        if API_KEY and not verify_api_key(request):
            return jsonify({"error": "Ungültiger API-Key"}), 401
        
        data = request.json
        if not data or "query" not in data:
            return jsonify({"error": "Keine Suchanfrage gefunden"}), 400
        
        query = data["query"]
        depth = data.get("depth", "standard")
        include_images = data.get("include_images", False)
        
        ***REMOVED*** Hier würde normalerweise die LinkUp-Integration stattfinden
        ***REMOVED*** Da wir die LinkUp-Bibliothek nicht direkt importieren können, simulieren wir das Verhalten
        logger.info(f"LinkUp-Suchanfrage: {query}")
        
        ***REMOVED*** Simulierte Antwort
        response_data = {
            "query": query,
            "results": [
                {
                    "title": "Simuliertes Suchergebnis",
                    "snippet": "Dies ist ein simuliertes Suchergebnis für die Anfrage.",
                    "url": "https://example.com/result"
                }
            ],
            "api_key_used": API_KEY[:8] + "..." ***REMOVED*** Zeige nur einen Teil des API-Keys aus Sicherheitsgründen
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.error(f"Fehler bei der LinkUp-Suche: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    logger.info("MCP-Server wird gestartet...")
    
    ***REMOVED*** Stellen Sie sicher, dass die Verzeichnisse existieren
    os.makedirs("data/prompts", exist_ok=True)
    
    ***REMOVED*** API-Key aus Umgebungsvariable laden
    if "LINKUP_API_KEY" in os.environ:
        API_KEY = os.environ["LINKUP_API_KEY"]
        SERVER_STATUS["api_key_set"] = bool(API_KEY)
        logger.info("API-Key aus Umgebungsvariable geladen.")
    else:
        ***REMOVED*** Standard-API-Key setzen
        os.environ["LINKUP_API_KEY"] = API_KEY
    
    ***REMOVED*** Server starten
    logger.info(f"Server wird auf Port 8000 gestartet. API-Key ist gesetzt: {bool(API_KEY)}")
    app.run(host="0.0.0.0", port=8000, debug=False) 