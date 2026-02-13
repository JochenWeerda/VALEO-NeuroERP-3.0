#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test-Skript für den MCP-Server
"""

import requests
import json
import time
import os

def main():
    """Hauptfunktion"""
    print("Sende Test-Prompt an den MCP-Server...")
    
    # API-Key (aus dem MCP-Server-Code)
    API_KEY = "aca0b877-88dd-4423-a35b-97de39012db9"
    
    # Test-Prompt
    data = {
        "prompt": "Test-Prompt für Cursor-Integration",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "phase": "TEST",
        "source": "test_script",
        "target": "cursor.ai",
        "version": "1.0.0"
    }
    
    # Speichere den Prompt in der latest_prompt.json-Datei
    os.makedirs("data/cursor_prompts", exist_ok=True)
    with open("data/cursor_prompts/latest_prompt.json", "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    print("Prompt in latest_prompt.json gespeichert.")
    
    # Sende den Prompt an den MCP-Server
    try:
        response = requests.post(
            "http://localhost:8000/api/prompt",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            },
            json={"prompt": data["prompt"]}
        )
        
        print(f"Status-Code: {response.status_code}")
        print(f"Antwort: {response.text}")
    except Exception as e:
        print(f"Fehler beim Senden des Prompts: {str(e)}")

if __name__ == "__main__":
    main() 
