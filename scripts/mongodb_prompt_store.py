#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MongoDB Prompt Store und Cursor.ai AutoGUI Integration

Dieses Skript:
1. Speichert den Prompt in der MongoDB-Datenbank
2. Öffnet Cursor.ai in der Taskleiste
3. Fügt den Prompt aus der Datenbank ein
"""

import os
import sys
import json
import time
import pyperclip
import pyautogui
import subprocess
from datetime import datetime
from pathlib import Path
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

# Konfiguration
PROMPT_FILE = "data/cursor_prompts/latest_prompt.json"
CURSOR_PATH = "C:\\Program Files\\Cursor\\Cursor.exe"
WAIT_TIME_AFTER_START = 3  # Sekunden zu warten nach dem Start von Cursor.ai
WAIT_TIME_AFTER_HOTKEY = 1  # Sekunden zu warten nach dem Drücken von Alt+C

# MongoDB-Konfiguration
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
MONGODB_DB_NAME = os.environ.get("MONGODB_DB_NAME", "valeo_neuroerp")
MONGODB_COLLECTION = "cursor_prompts"

def connect_to_mongodb():
    """Stellt eine Verbindung zur MongoDB her."""
    try:
        client = MongoClient(MONGODB_URI)
        db = client[MONGODB_DB_NAME]
        
        # Verbindung testen
        client.admin.command('ping')
        print(f"Verbindung zu MongoDB ({MONGODB_URI}, Datenbank: {MONGODB_DB_NAME}) hergestellt")
        
        return client, db
    except ConnectionFailure as e:
        print(f"Verbindung zu MongoDB fehlgeschlagen: {str(e)}")
        return None, None

def store_prompt_in_mongodb(prompt_text):
    """Speichert den Prompt in MongoDB."""
    client, db = connect_to_mongodb()
    if not client or not db:
        print("MongoDB-Verbindung konnte nicht hergestellt werden.")
        return False
    
    try:
        # Prompt-Dokument erstellen
        prompt_doc = {
            "prompt": prompt_text,
            "created_at": datetime.now(),
            "source": "streamlit_dashboard",
            "target": "cursor.ai",
            "status": "created"
        }
        
        # In MongoDB einfügen
        result = db[MONGODB_COLLECTION].insert_one(prompt_doc)
        prompt_id = str(result.inserted_id)
        print(f"Prompt in MongoDB gespeichert mit ID: {prompt_id}")
        
        # MongoDB-Verbindung schließen
        client.close()
        
        return prompt_id
    except Exception as e:
        print(f"Fehler beim Speichern des Prompts in MongoDB: {str(e)}")
        if client:
            client.close()
        return None

def read_prompt_from_mongodb(prompt_id):
    """Liest einen Prompt aus MongoDB anhand seiner ID."""
    client, db = connect_to_mongodb()
    if not client or not db:
        print("MongoDB-Verbindung konnte nicht hergestellt werden.")
        return None
    
    try:
        # Prompt aus MongoDB lesen
        from bson.objectid import ObjectId
        prompt_doc = db[MONGODB_COLLECTION].find_one({"_id": ObjectId(prompt_id)})
        
        # MongoDB-Verbindung schließen
        client.close()
        
        if prompt_doc:
            return prompt_doc.get("prompt", "")
        else:
            print(f"Kein Prompt mit ID {prompt_id} gefunden.")
            return None
    except Exception as e:
        print(f"Fehler beim Lesen des Prompts aus MongoDB: {str(e)}")
        if client:
            client.close()
        return None

def read_latest_prompt_from_file():
    """Liest den neuesten Prompt aus der Datei."""
    try:
        if os.path.exists(PROMPT_FILE):
            with open(PROMPT_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("prompt", "")
        return ""
    except Exception as e:
        print(f"Fehler beim Lesen des Prompts aus der Datei: {str(e)}")
        return ""

def copy_to_clipboard(text):
    """Kopiert den Text in die Zwischenablage."""
    try:
        pyperclip.copy(text)
        print("Prompt in die Zwischenablage kopiert.")
        return True
    except Exception as e:
        print(f"Fehler beim Kopieren in die Zwischenablage: {str(e)}")
        return False

def is_cursor_running():
    """Überprüft, ob Cursor.ai läuft."""
    try:
        # Windows-Befehl zum Überprüfen, ob ein Prozess läuft
        result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq Cursor.exe"], 
                              capture_output=True, text=True)
        return "Cursor.exe" in result.stdout
    except Exception as e:
        print(f"Fehler beim Überprüfen, ob Cursor.ai läuft: {str(e)}")
        return False

def start_cursor():
    """Startet Cursor.ai, falls es nicht läuft."""
    if not is_cursor_running():
        try:
            if os.path.exists(CURSOR_PATH):
                subprocess.Popen([CURSOR_PATH])
                print("Cursor.ai gestartet.")
                print(f"Warte {WAIT_TIME_AFTER_START} Sekunden, bis Cursor.ai vollständig geladen ist...")
                time.sleep(WAIT_TIME_AFTER_START)
                return True
            else:
                print(f"Cursor.ai konnte nicht gefunden werden unter: {CURSOR_PATH}")
                return False
        except Exception as e:
            print(f"Fehler beim Starten von Cursor.ai: {str(e)}")
            return False
    else:
        print("Cursor.ai läuft bereits.")
        # Bringe Cursor.ai in den Vordergrund
        try:
            # Finde das Cursor.ai-Fenster
            windows = pyautogui.getWindowsWithTitle("Cursor")
            if windows:
                cursor_window = windows[0]
                cursor_window.activate()
                print("Cursor.ai in den Vordergrund gebracht.")
                time.sleep(1)  # Kurz warten, bis das Fenster im Vordergrund ist
            else:
                print("Cursor.ai-Fenster konnte nicht gefunden werden.")
        except Exception as e:
            print(f"Fehler beim Aktivieren des Cursor.ai-Fensters: {str(e)}")
    return True

def open_chat_window():
    """Öffnet das Chat-Fenster in Cursor.ai mit Alt+C."""
    try:
        # Alt+C ist die Tastenkombination für das Chat-Fenster in Cursor.ai
        pyautogui.hotkey('alt', 'c')
        print("Chat-Fenster geöffnet (Alt+C).")
        
        # Kurz warten, bis das Chat-Fenster geöffnet ist
        print(f"Warte {WAIT_TIME_AFTER_HOTKEY} Sekunden, bis das Chat-Fenster geöffnet ist...")
        time.sleep(WAIT_TIME_AFTER_HOTKEY)
        return True
    except Exception as e:
        print(f"Fehler beim Öffnen des Chat-Fensters: {str(e)}")
        return False

def paste_and_send():
    """Fügt den Text aus der Zwischenablage ein und sendet ihn."""
    try:
        # Einfügen mit Strg+V
        pyautogui.hotkey('ctrl', 'v')
        print("Text eingefügt (Strg+V).")
        
        # Kurz warten
        time.sleep(0.5)
        
        # Enter drücken, um den Prompt zu senden
        pyautogui.press('enter')
        print("Enter gedrückt, Prompt gesendet.")
        return True
    except Exception as e:
        print(f"Fehler beim Einfügen und Senden: {str(e)}")
        return False

def update_prompt_status_in_mongodb(prompt_id, status):
    """Aktualisiert den Status eines Prompts in MongoDB."""
    client, db = connect_to_mongodb()
    if not client or not db:
        print("MongoDB-Verbindung konnte nicht hergestellt werden.")
        return False
    
    try:
        from bson.objectid import ObjectId
        result = db[MONGODB_COLLECTION].update_one(
            {"_id": ObjectId(prompt_id)},
            {"$set": {"status": status, "updated_at": datetime.now()}}
        )
        
        client.close()
        
        if result.modified_count > 0:
            print(f"Status des Prompts {prompt_id} auf '{status}' aktualisiert.")
            return True
        else:
            print(f"Prompt {prompt_id} konnte nicht aktualisiert werden.")
            return False
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Prompt-Status: {str(e)}")
        if client:
            client.close()
        return False

def main():
    """Hauptfunktion"""
    print("MongoDB Prompt Store und Cursor.ai AutoGUI Integration gestartet.")
    
    # Prompt aus Datei lesen
    prompt = read_latest_prompt_from_file()
    if not prompt:
        print("Kein Prompt in der Datei gefunden.")
        return
    
    print(f"Prompt gefunden: {prompt[:50]}...")
    
    # Prompt in MongoDB speichern
    prompt_id = store_prompt_in_mongodb(prompt)
    if not prompt_id:
        print("Prompt konnte nicht in MongoDB gespeichert werden.")
        return
    
    # Prompt aus MongoDB lesen (zur Verifizierung)
    stored_prompt = read_prompt_from_mongodb(prompt_id)
    if not stored_prompt:
        print("Prompt konnte nicht aus MongoDB gelesen werden.")
        return
    
    # Prompt in die Zwischenablage kopieren
    if not copy_to_clipboard(stored_prompt):
        update_prompt_status_in_mongodb(prompt_id, "clipboard_error")
        return
    
    # Status aktualisieren
    update_prompt_status_in_mongodb(prompt_id, "copied_to_clipboard")
    
    # Cursor.ai starten oder in den Vordergrund bringen
    if not start_cursor():
        print("Cursor.ai konnte nicht gestartet werden.")
        update_prompt_status_in_mongodb(prompt_id, "cursor_start_error")
        return
    
    # Chat-Fenster öffnen
    if not open_chat_window():
        print("Chat-Fenster konnte nicht geöffnet werden.")
        update_prompt_status_in_mongodb(prompt_id, "chat_window_error")
        return
    
    # Prompt einfügen und senden
    if not paste_and_send():
        print("Prompt konnte nicht eingefügt und gesendet werden.")
        update_prompt_status_in_mongodb(prompt_id, "paste_error")
        return
    
    # Status aktualisieren
    update_prompt_status_in_mongodb(prompt_id, "sent_to_cursor")
    
    print("Automatisierung erfolgreich abgeschlossen!")
    print("Der Prompt wurde in MongoDB gespeichert und an Cursor.ai übergeben.")

if __name__ == "__main__":
    # Sicherheitsabfrage, da das Skript die Kontrolle über die Tastatur übernimmt
    if len(sys.argv) > 1 and sys.argv[1] == "--force":
        main()
    else:
        print("ACHTUNG: Dieses Skript übernimmt die Kontrolle über Tastatur und Maus.")
        print("Stellen Sie sicher, dass Sie keine anderen Anwendungen verwenden, während das Skript läuft.")
        print("Drücken Sie Enter, um fortzufahren, oder Strg+C, um abzubrechen.")
        try:
            input()
            main()
        except KeyboardInterrupt:
            print("\nVorgang abgebrochen.") 