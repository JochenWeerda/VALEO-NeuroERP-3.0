#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test-Skript für die Zwischenablage-Funktionalität
"""

import pyperclip
import time

def main():
    """Hauptfunktion"""
    print("Teste die Zwischenablage-Funktionalität...")
    
    # Text in die Zwischenablage kopieren
    test_text = "Dies ist ein Test-Text für die Zwischenablage"
    print(f"Kopiere Text in die Zwischenablage: {test_text}")
    
    try:
        pyperclip.copy(test_text)
        print("Text wurde in die Zwischenablage kopiert.")
        
        # Kurz warten
        time.sleep(1)
        
        # Text aus der Zwischenablage lesen
        clipboard_content = pyperclip.paste()
        print(f"Inhalt der Zwischenablage: {clipboard_content}")
        
        # Prüfen, ob der Text korrekt kopiert wurde
        if clipboard_content == test_text:
            print("Test erfolgreich: Der Text wurde korrekt in die Zwischenablage kopiert.")
        else:
            print("Test fehlgeschlagen: Der Text in der Zwischenablage stimmt nicht mit dem kopierten Text überein.")
    
    except Exception as e:
        print(f"Fehler beim Testen der Zwischenablage: {str(e)}")

if __name__ == "__main__":
    main() 