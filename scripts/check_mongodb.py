#!/usr/bin/env python
"""
Überprüft, ob MongoDB installiert ist und gibt bei Bedarf Installationsanweisungen.
"""

import os
import sys
import subprocess
import platform
import logging

# Logger konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CheckMongoDB")

def check_mongodb_installed():
    """
    Überprüft, ob MongoDB installiert ist.
    
    Returns:
        bool: True, wenn MongoDB installiert ist, sonst False
    """
    system = platform.system().lower()
    
    if system == "windows":
        # Prüfe, ob der MongoDB-Dienst existiert
        try:
            result = subprocess.run(
                ["sc", "query", "MongoDB"],
                capture_output=True,
                text=True,
                check=False
            )
            if "RUNNING" in result.stdout:
                logger.info("MongoDB-Dienst ist installiert und läuft.")
                return True
            elif result.returncode == 0:
                logger.info("MongoDB-Dienst ist installiert, läuft aber nicht.")
                return True
        except Exception:
            pass
        
        # Prüfe, ob mongod.exe im Pfad ist
        try:
            result = subprocess.run(
                ["where", "mongod"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info("MongoDB ist installiert (mongod.exe gefunden).")
                return True
        except Exception:
            pass
    
    elif system == "linux":
        # Prüfe, ob der MongoDB-Dienst existiert
        try:
            result = subprocess.run(
                ["systemctl", "status", "mongodb"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info("MongoDB-Dienst ist installiert.")
                return True
        except Exception:
            pass
        
        # Alternative: Prüfe mit service
        try:
            result = subprocess.run(
                ["service", "mongodb", "status"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info("MongoDB-Dienst ist installiert.")
                return True
        except Exception:
            pass
        
        # Prüfe, ob mongod im Pfad ist
        try:
            result = subprocess.run(
                ["which", "mongod"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info("MongoDB ist installiert (mongod gefunden).")
                return True
        except Exception:
            pass
    
    elif system == "darwin":  # macOS
        # Prüfe mit Homebrew
        try:
            result = subprocess.run(
                ["brew", "services", "list"],
                capture_output=True,
                text=True,
                check=False
            )
            if "mongodb" in result.stdout.lower():
                logger.info("MongoDB ist über Homebrew installiert.")
                return True
        except Exception:
            pass
        
        # Prüfe, ob mongod im Pfad ist
        try:
            result = subprocess.run(
                ["which", "mongod"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                logger.info("MongoDB ist installiert (mongod gefunden).")
                return True
        except Exception:
            pass
    
    logger.warning("MongoDB scheint nicht installiert zu sein.")
    return False

def print_installation_instructions():
    """
    Gibt Anweisungen zur Installation von MongoDB aus.
    """
    system = platform.system().lower()
    
    print("\n" + "=" * 80)
    print("MongoDB-Installationsanweisungen".center(80))
    print("=" * 80 + "\n")
    
    if system == "windows":
        print("Installation von MongoDB unter Windows:")
        print("1. Besuche die MongoDB-Download-Seite: https://www.mongodb.com/try/download/community")
        print("2. Wähle die aktuelle Version und 'Windows' als Plattform")
        print("3. Lade die MSI-Datei herunter und führe sie aus")
        print("4. Folge den Anweisungen des Installationsassistenten")
        print("5. Wähle 'Complete' als Installationstyp")
        print("6. Aktiviere die Option 'Install MongoDB as a Service'")
        print("7. Nach der Installation sollte der MongoDB-Dienst automatisch starten")
    
    elif system == "linux":
        print("Installation von MongoDB unter Linux (Ubuntu):")
        print("1. Importiere den öffentlichen GPG-Schlüssel:")
        print("   sudo apt-get install gnupg")
        print("   curl -fsSL https://pgp.mongodb.com/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor")
        print("2. Erstelle eine Liste-Datei für MongoDB:")
        print("   echo 'deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse' | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list")
        print("3. Aktualisiere die Paketliste:")
        print("   sudo apt-get update")
        print("4. Installiere MongoDB:")
        print("   sudo apt-get install -y mongodb-org")
        print("5. Starte den MongoDB-Dienst:")
        print("   sudo systemctl start mongod")
        print("6. Aktiviere den automatischen Start beim Systemstart:")
        print("   sudo systemctl enable mongod")
    
    elif system == "darwin":  # macOS
        print("Installation von MongoDB unter macOS mit Homebrew:")
        print("1. Installiere Homebrew, falls noch nicht geschehen:")
        print("   /bin/bash -c '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'")
        print("2. Installiere MongoDB:")
        print("   brew tap mongodb/brew")
        print("   brew install mongodb-community")
        print("3. Starte den MongoDB-Dienst:")
        print("   brew services start mongodb-community")
    
    else:
        print(f"Installationsanweisungen für {system} sind nicht verfügbar.")
        print("Bitte besuche die offizielle MongoDB-Dokumentation: https://docs.mongodb.com/manual/installation/")
    
    print("\n" + "=" * 80)
    print("Nach der Installation".center(80))
    print("=" * 80)
    print("1. Führe dieses Skript erneut aus, um zu überprüfen, ob die Installation erfolgreich war.")
    print("2. Führe dann das Skript 'scripts/activate_reflect_archive.py' aus, um den REFLECT-ARCHIVE-Mode zu aktivieren.")
    print("=" * 80 + "\n")

def main():
    """
    Hauptfunktion.
    """
    if check_mongodb_installed():
        print("\n" + "=" * 80)
        print("MongoDB ist installiert.".center(80))
        print("=" * 80)
        print("Du kannst nun das Skript 'scripts/activate_reflect_archive.py' ausführen,")
        print("um den REFLECT-ARCHIVE-Mode zu aktivieren und die MongoDB mit Daten zu befüllen.")
        print("=" * 80 + "\n")
        return 0
    else:
        print_installation_instructions()
        return 1


if __name__ == "__main__":
    sys.exit(main())