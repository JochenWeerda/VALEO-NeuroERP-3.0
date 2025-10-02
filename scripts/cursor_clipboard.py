#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cursor.ai Prompt in die Zwischenablage kopieren

Dieses Skript liest den Prompt aus der latest_prompt.json-Datei und kopiert ihn in die Zwischenablage.
"""

import os
import json
import pyperclip
import subprocess

# Konfiguration
PROMPT_FILE = "data/cursor_prompts/latest_prompt.json"
CURSOR_PATH = "C:\\Program Files\\Cursor\\Cursor.exe"

def read_prompt():
    """Liest den Prompt aus der Datei."""
    try:
        if os.path.exists(PROMPT_FILE):
            with open(PROMPT_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                return data.get("prompt", "")
        return ""
    except Exception as e:
        print(f"Fehler beim Lesen des Prompts: {str(e)}")
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

def start_cursor():
    """Startet Cursor.ai, falls es nicht läuft."""
    try:
        if os.path.exists(CURSOR_PATH):
            subprocess.Popen([CURSOR_PATH])
            print("Cursor.ai gestartet.")
            return True
        else:
            print(f"Cursor.ai konnte nicht gefunden werden unter: {CURSOR_PATH}")
            return False
    except Exception as e:
        print(f"Fehler beim Starten von Cursor.ai: {str(e)}")
        return False

def main():
    """Hauptfunktion"""
    print("Cursor.ai Prompt in die Zwischenablage kopieren")
    
    # Prompt aus Datei lesen
    prompt = read_prompt()
    if not prompt:
        print("Kein Prompt gefunden.")
        return
    
    print(f"Prompt gefunden: {prompt[:50]}...")
    
    # Prompt in die Zwischenablage kopieren
    if not copy_to_clipboard(prompt):
        return
    
    # Cursor.ai starten
    start_cursor()
    
    print("Der Prompt wurde in die Zwischenablage kopiert.")
    print("Bitte öffnen Sie das Chat-Fenster in Cursor.ai mit Alt+C und fügen Sie den Prompt mit Strg+V ein.")

if __name__ == "__main__":
    main() 