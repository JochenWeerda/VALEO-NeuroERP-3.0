#!/usr/bin/env python3
"""
Entfernt Null-Bytes aus Python-Dateien im gesamten Projekt.
"""

import os
import sys
from pathlib import Path

def fix_file(file_path):
    """Entfernt Null-Bytes aus einer Datei."""
    try:
        # Datei im Binärmodus lesen
        with open(file_path, 'rb') as file:
            content = file.read()
        
        # Null-Bytes entfernen
        cleaned_content = content.replace(b'\x00', b'')
        
        # Prüfen, ob Änderungen vorgenommen wurden
        if content != cleaned_content:
            # Datei im Binärmodus schreiben
            with open(file_path, 'wb') as file:
                file.write(cleaned_content)
            print(f"Null-Bytes aus {file_path} entfernt.")
            return True
        else:
            print(f"Keine Null-Bytes in {file_path} gefunden.")
            return False
    except Exception as e:
        print(f"Fehler beim Bearbeiten von {file_path}: {str(e)}")
        return False

def process_directory(directory_path):
    """Verarbeitet alle Python-Dateien in einem Verzeichnis."""
    fixed_files = 0
    
    # Alle Python-Dateien im Verzeichnis durchlaufen
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if fix_file(file_path):
                    fixed_files += 1
    
    return fixed_files

def main():
    """Hauptfunktion."""
    # Pfad zum Projektverzeichnis
    project_path = Path(__file__).resolve().parent.parent
    
    if not project_path.exists():
        print(f"Verzeichnis nicht gefunden: {project_path}")
        sys.exit(1)
    
    # Zu überprüfende Verzeichnisse
    directories = [
        project_path / "backend",
        project_path / "scripts",
        project_path / "src",
        project_path / "tools",
        project_path / "modules"
    ]
    
    total_fixed = 0
    for directory in directories:
        if directory.exists():
            print(f"Verarbeite Dateien in {directory}...")
            fixed_files = process_directory(directory)
            total_fixed += fixed_files
        else:
            print(f"Verzeichnis nicht gefunden: {directory}")
    
    print(f"Abgeschlossen. {total_fixed} Dateien wurden bereinigt.")

if __name__ == "__main__":
    main() 