#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cursor.ai Automatische Prompt-Übergabe

Dieses Skript automatisiert die Übergabe eines Prompts an Cursor.ai:
1. Liest den Prompt aus der latest_prompt.json-Datei
2. Kopiert den Prompt in die Zwischenablage
3. Startet Cursor.ai (falls nicht bereits gestartet)
4. Öffnet das Chat-Fenster mit Alt+C
5. Fügt den Prompt ein und sendet ihn mit Enter
"""

import os
import json
import time
import pyperclip
import subprocess
import pyautogui
import sys

# Konfiguration
PROMPT_FILE = "data/cursor_prompts/latest_prompt.json"
CURSOR_PATH = "C:\\Program Files\\Cursor\\Cursor.exe"
WAIT_TIME_AFTER_START = 3  # Sekunden zu warten nach dem Start von Cursor.ai
WAIT_TIME_AFTER_HOTKEY = 1  # Sekunden zu warten nach dem Drücken von Alt+C

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

def main():
    """Hauptfunktion"""
    print("Cursor.ai Automatische Prompt-Übergabe gestartet.")
    
    # Prompt aus Datei lesen
    prompt = read_prompt()
    if not prompt:
        print("Kein Prompt gefunden.")
        return
    
    print(f"Prompt gefunden: {prompt[:50]}...")
    
    # Prompt in die Zwischenablage kopieren
    if not copy_to_clipboard(prompt):
        return
    
    # Cursor.ai starten oder in den Vordergrund bringen
    if not start_cursor():
        print("Cursor.ai konnte nicht gestartet werden.")
        return
    
    # Chat-Fenster öffnen
    if not open_chat_window():
        print("Chat-Fenster konnte nicht geöffnet werden.")
        return
    
    # Prompt einfügen und senden
    if not paste_and_send():
        print("Prompt konnte nicht eingefügt und gesendet werden.")
        return
    
    print("Automatisierung erfolgreich abgeschlossen!")
    print("Der Prompt wurde an Cursor.ai übergeben.")

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