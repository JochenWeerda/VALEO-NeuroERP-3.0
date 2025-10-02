#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
App-Schutz für VALEO-NeuroERP

Dieses Skript implementiert Schutzmaßnahmen für die VALEO-NeuroERP-Anwendung,
um sie gegen unbeabsichtigte Änderungen zu härten und die Integrität zu gewährleisten.
"""

import os
import sys
import time
import json
import yaml
import hashlib
import logging
import shutil
import threading
import subprocess
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple

# Importiere den ErrorHandler
try:
    from error_handler import error_handler, handle_exception
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
    try:
        from scripts.error_handler import error_handler, handle_exception
    except ImportError:
        print("ErrorHandler konnte nicht importiert werden. Stelle sicher, dass error_handler.py existiert.")
        sys.exit(1)

# Konfiguration
PROTECTION_CONFIG = "config/app_protection.yaml"
LOCK_FILE = "config/app.lock"
INTEGRITY_CHECK_INTERVAL = 60  # Sekunden
AUTO_BACKUP_INTERVAL = 3600  # Sekunden (1 Stunde)
MAX_RECOVERY_ATTEMPTS = 3

# Logging konfigurieren
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "app_protection.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("app_protection")

class AppProtection:
    """Hauptklasse für den App-Schutz."""
    
    def __init__(self):
        self.config = self._load_config()
        self.file_hashes = {}
        self.protected_files = set()
        self.recovery_attempts = 0
        self.last_backup = 0
        self.running = False
        self.lock_acquired = False
        
        # Threads
        self.integrity_thread = None
        self.backup_thread = None
    
    def _load_config(self) -> Dict[str, Any]:
        """Lädt die Konfiguration aus der YAML-Datei."""
        default_config = {
            "protected_files": [
                "scripts/streamlit_app_mcp_integration.py",
                "scripts/cursor_prompt_integration.py",
                "scripts/error_handler.py",
                "scripts/app_protection.py",
                "scripts/genxais_prompt_generator.py",
                "scripts/launch_genxais_prompt_generator.py",
                "scripts/streamlit_dashboard.py",
                "config/version.yaml",
                "start_app.sh",
                "start_app.bat",
                "start_dashboard.sh",
                "start_dashboard.bat",
                "start_genxais_prompt_generator.sh",
                "start_genxais_prompt_generator.bat"
            ],
            "protected_dirs": [
                "data/cursor_prompts",
                "data/cursor_prompts/specs",
                "data/cursor_prompts/genxais",
                "data/handover",
                "data/dashboard"
            ],
            "integrity_check_interval": INTEGRITY_CHECK_INTERVAL,
            "auto_backup_interval": AUTO_BACKUP_INTERVAL,
            "max_recovery_attempts": MAX_RECOVERY_ATTEMPTS,
            "backup_dir": "backups",
            "enable_auto_recovery": True,
            "notify_on_changes": True
        }
        
        try:
            if os.path.exists(PROTECTION_CONFIG):
                with open(PROTECTION_CONFIG, "r") as f:
                    config = yaml.safe_load(f)
                
                # Fehlende Konfigurationsoptionen mit Standardwerten ergänzen
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                
                return config
            else:
                # Konfigurationsdatei erstellen, falls sie nicht existiert
                os.makedirs(os.path.dirname(PROTECTION_CONFIG), exist_ok=True)
                with open(PROTECTION_CONFIG, "w") as f:
                    yaml.dump(default_config, f)
                
                return default_config
        except Exception as e:
            logger.error(f"Fehler beim Laden der Konfiguration: {str(e)}")
            return default_config
    
    def save_config(self) -> None:
        """Speichert die Konfiguration in der YAML-Datei."""
        try:
            with open(PROTECTION_CONFIG, "w") as f:
                yaml.dump(self.config, f)
            logger.info("Konfiguration gespeichert")
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Konfiguration: {str(e)}")
    
    def acquire_lock(self) -> bool:
        """Versucht, die App-Sperre zu erwerben."""
        try:
            if os.path.exists(LOCK_FILE):
                # Prüfen, ob die Sperre noch gültig ist
                with open(LOCK_FILE, "r") as f:
                    lock_data = json.load(f)
                
                pid = lock_data.get("pid")
                timestamp = lock_data.get("timestamp", 0)
                
                # Prüfen, ob der Prozess noch läuft
                if pid and self._is_process_running(pid):
                    logger.warning(f"App-Sperre wird bereits von Prozess {pid} gehalten")
                    return False
                
                # Prüfen, ob die Sperre abgelaufen ist (älter als 1 Stunde)
                if time.time() - timestamp > 3600:
                    logger.warning("App-Sperre ist abgelaufen und wird übernommen")
                else:
                    logger.warning(f"App-Sperre wird von einem anderen Prozess gehalten (PID: {pid})")
                    return False
            
            # Sperre erwerben
            with open(LOCK_FILE, "w") as f:
                json.dump({
                    "pid": os.getpid(),
                    "timestamp": time.time(),
                    "hostname": os.environ.get("COMPUTERNAME", "unknown")
                }, f)
            
            self.lock_acquired = True
            logger.info(f"App-Sperre erworben (PID: {os.getpid()})")
            return True
        
        except Exception as e:
            logger.error(f"Fehler beim Erwerben der App-Sperre: {str(e)}")
            return False
    
    def release_lock(self) -> None:
        """Gibt die App-Sperre frei."""
        if not self.lock_acquired:
            return
        
        try:
            if os.path.exists(LOCK_FILE):
                with open(LOCK_FILE, "r") as f:
                    lock_data = json.load(f)
                
                if lock_data.get("pid") == os.getpid():
                    os.remove(LOCK_FILE)
                    logger.info("App-Sperre freigegeben")
                    self.lock_acquired = False
        except Exception as e:
            logger.error(f"Fehler beim Freigeben der App-Sperre: {str(e)}")
    
    def _is_process_running(self, pid: int) -> bool:
        """Prüft, ob ein Prozess mit der angegebenen PID läuft."""
        try:
            # Windows
            if os.name == "nt":
                output = subprocess.check_output(["tasklist", "/FI", f"PID eq {pid}"])
                return str(pid) in output.decode()
            # Unix
            else:
                os.kill(pid, 0)
                return True
        except (subprocess.CalledProcessError, ProcessLookupError, PermissionError):
            return False
    
    def calculate_hash(self, file_path: str) -> str:
        """Berechnet den Hash einer Datei."""
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"Fehler beim Berechnen des Hashes für {file_path}: {str(e)}")
            return ""
    
    def initialize_protection(self) -> None:
        """Initialisiert den App-Schutz."""
        logger.info("Initialisiere App-Schutz...")
        
        # Geschützte Dateien registrieren
        for file_path in self.config["protected_files"]:
            if os.path.exists(file_path):
                self.protected_files.add(file_path)
                self.file_hashes[file_path] = self.calculate_hash(file_path)
                logger.info(f"Datei {file_path} wird geschützt")
            else:
                logger.warning(f"Geschützte Datei {file_path} existiert nicht")
        
        # Dateien auch beim ErrorHandler registrieren
        for file_path in self.protected_files:
            error_handler.file_monitor.add_protected_file(file_path)
        
        # Initiales Backup erstellen
        self.create_backup("initial_protection_backup")
        
        logger.info(f"{len(self.protected_files)} Dateien werden geschützt")
    
    def start_protection(self) -> None:
        """Startet den App-Schutz."""
        if self.running:
            logger.warning("App-Schutz läuft bereits")
            return
        
        if not self.acquire_lock():
            logger.error("Konnte App-Sperre nicht erwerben. App-Schutz wird nicht gestartet.")
            return
        
        self.running = True
        logger.info("App-Schutz gestartet")
        
        # Threads starten
        self.integrity_thread = threading.Thread(target=self._integrity_check_loop, daemon=True)
        self.integrity_thread.start()
        
        self.backup_thread = threading.Thread(target=self._auto_backup_loop, daemon=True)
        self.backup_thread.start()
    
    def stop_protection(self) -> None:
        """Stoppt den App-Schutz."""
        if not self.running:
            return
        
        self.running = False
        logger.info("App-Schutz wird gestoppt...")
        
        # Auf Threads warten
        if self.integrity_thread and self.integrity_thread.is_alive():
            self.integrity_thread.join(timeout=5)
        
        if self.backup_thread and self.backup_thread.is_alive():
            self.backup_thread.join(timeout=5)
        
        # Sperre freigeben
        self.release_lock()
        
        logger.info("App-Schutz gestoppt")
    
    def _integrity_check_loop(self) -> None:
        """Führt regelmäßige Integritätsprüfungen durch."""
        logger.info(f"Starte Integritätsprüfungs-Loop (Intervall: {self.config['integrity_check_interval']} Sekunden)")
        
        while self.running:
            try:
                modified_files = self.check_integrity()
                
                if modified_files:
                    logger.warning(f"Modifizierte Dateien gefunden: {modified_files}")
                    
                    if self.config["enable_auto_recovery"] and self.recovery_attempts < self.config["max_recovery_attempts"]:
                        self.recover_files(modified_files)
                        self.recovery_attempts += 1
                    elif self.config["notify_on_changes"]:
                        logger.error(f"Zu viele Wiederherstellungsversuche ({self.recovery_attempts}). Automatische Wiederherstellung deaktiviert.")
                else:
                    # Zurücksetzen der Wiederherstellungsversuche, wenn keine Änderungen gefunden wurden
                    self.recovery_attempts = 0
            
            except Exception as e:
                logger.error(f"Fehler bei der Integritätsprüfung: {str(e)}")
            
            # Warten bis zur nächsten Prüfung
            for _ in range(int(self.config["integrity_check_interval"] / 0.1)):
                if not self.running:
                    break
                time.sleep(0.1)
    
    def _auto_backup_loop(self) -> None:
        """Führt regelmäßige automatische Backups durch."""
        logger.info(f"Starte Auto-Backup-Loop (Intervall: {self.config['auto_backup_interval']} Sekunden)")
        
        while self.running:
            try:
                # Prüfen, ob ein Backup fällig ist
                if time.time() - self.last_backup > self.config["auto_backup_interval"]:
                    self.create_backup(f"auto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    self.last_backup = time.time()
            
            except Exception as e:
                logger.error(f"Fehler beim automatischen Backup: {str(e)}")
            
            # Warten bis zum nächsten Backup
            for _ in range(int(self.config["auto_backup_interval"] / 10)):
                if not self.running:
                    break
                time.sleep(10)
    
    def check_integrity(self) -> List[str]:
        """Prüft die Integrität der geschützten Dateien."""
        modified_files = []
        
        for file_path in self.protected_files:
            if not os.path.exists(file_path):
                logger.warning(f"Geschützte Datei {file_path} existiert nicht mehr")
                modified_files.append(file_path)
                continue
            
            current_hash = self.calculate_hash(file_path)
            if current_hash != self.file_hashes.get(file_path, ""):
                logger.warning(f"Datei {file_path} wurde modifiziert (Hash: {current_hash} != {self.file_hashes.get(file_path, '')})")
                modified_files.append(file_path)
        
        return modified_files
    
    def create_backup(self, backup_name: str) -> str:
        """Erstellt ein Backup der geschützten Dateien."""
        backup_dir = os.path.join(self.config["backup_dir"], backup_name)
        os.makedirs(backup_dir, exist_ok=True)
        
        for file_path in self.protected_files:
            if os.path.exists(file_path):
                # Zielverzeichnis erstellen
                target_dir = os.path.join(backup_dir, os.path.dirname(file_path))
                os.makedirs(target_dir, exist_ok=True)
                
                # Datei kopieren
                target_path = os.path.join(backup_dir, file_path)
                shutil.copy2(file_path, target_path)
                logger.info(f"Datei {file_path} gesichert nach {target_path}")
        
        logger.info(f"Backup erstellt: {backup_dir}")
        self.last_backup = time.time()
        
        # Alte Backups aufräumen
        self._cleanup_old_backups()
        
        return backup_dir
    
    def _cleanup_old_backups(self) -> None:
        """Entfernt alte Backups, wenn zu viele vorhanden sind."""
        max_backups = self.config.get("max_backups", 5)
        backup_dir = self.config["backup_dir"]
        
        if not os.path.exists(backup_dir):
            return
        
        backups = [d for d in os.listdir(backup_dir) 
                  if os.path.isdir(os.path.join(backup_dir, d)) and not d.startswith(".")]
        
        if len(backups) <= max_backups:
            return
        
        # Sortiere Backups nach Erstellungsdatum
        backups.sort(key=lambda x: os.path.getctime(os.path.join(backup_dir, x)))
        
        # Entferne die ältesten Backups
        for old_backup in backups[:-max_backups]:
            try:
                shutil.rmtree(os.path.join(backup_dir, old_backup))
                logger.info(f"Altes Backup {old_backup} entfernt")
            except Exception as e:
                logger.error(f"Fehler beim Entfernen des alten Backups {old_backup}: {str(e)}")
    
    def recover_files(self, files: List[str]) -> bool:
        """Stellt modifizierte Dateien aus dem Backup wieder her."""
        backup_dir = self.config["backup_dir"]
        
        if not os.path.exists(backup_dir):
            logger.error(f"Backup-Verzeichnis {backup_dir} existiert nicht")
            return False
        
        # Neuestes Backup finden
        backups = [d for d in os.listdir(backup_dir) 
                  if os.path.isdir(os.path.join(backup_dir, d)) and not d.startswith(".")]
        
        if not backups:
            logger.error("Keine Backups gefunden")
            return False
        
        # Sortiere Backups nach Erstellungsdatum (neueste zuerst)
        backups.sort(key=lambda x: os.path.getctime(os.path.join(backup_dir, x)), reverse=True)
        latest_backup = backups[0]
        
        logger.info(f"Stelle Dateien aus Backup {latest_backup} wieder her")
        success = True
        
        for file_path in files:
            backup_file = os.path.join(backup_dir, latest_backup, file_path)
            
            if not os.path.exists(backup_file):
                logger.error(f"Backup-Datei {backup_file} existiert nicht")
                success = False
                continue
            
            try:
                # Zielverzeichnis erstellen
                target_dir = os.path.dirname(file_path)
                os.makedirs(target_dir, exist_ok=True)
                
                # Datei kopieren
                shutil.copy2(backup_file, file_path)
                logger.info(f"Datei {file_path} wiederhergestellt")
                
                # Hash aktualisieren
                self.file_hashes[file_path] = self.calculate_hash(file_path)
            
            except Exception as e:
                logger.error(f"Fehler beim Wiederherstellen von {file_path}: {str(e)}")
                success = False
        
        return success
    
    def add_protected_file(self, file_path: str) -> None:
        """Fügt eine Datei zur Liste der geschützten Dateien hinzu."""
        if not os.path.exists(file_path):
            logger.warning(f"Datei {file_path} existiert nicht und kann nicht geschützt werden")
            return
        
        self.protected_files.add(file_path)
        self.file_hashes[file_path] = self.calculate_hash(file_path)
        
        # Auch beim ErrorHandler registrieren
        error_handler.file_monitor.add_protected_file(file_path)
        
        # Konfiguration aktualisieren
        if file_path not in self.config["protected_files"]:
            self.config["protected_files"].append(file_path)
            self.save_config()
        
        logger.info(f"Datei {file_path} wird jetzt geschützt")
    
    def remove_protected_file(self, file_path: str) -> None:
        """Entfernt eine Datei aus der Liste der geschützten Dateien."""
        if file_path in self.protected_files:
            self.protected_files.remove(file_path)
            if file_path in self.file_hashes:
                del self.file_hashes[file_path]
            
            # Konfiguration aktualisieren
            if file_path in self.config["protected_files"]:
                self.config["protected_files"].remove(file_path)
                self.save_config()
            
            logger.info(f"Datei {file_path} wird nicht mehr geschützt")
    
    def get_status(self) -> Dict[str, Any]:
        """Gibt den Status des App-Schutzes zurück."""
        return {
            "running": self.running,
            "lock_acquired": self.lock_acquired,
            "protected_files": list(self.protected_files),
            "recovery_attempts": self.recovery_attempts,
            "last_backup": datetime.fromtimestamp(self.last_backup).strftime("%Y-%m-%d %H:%M:%S") if self.last_backup else "Nie",
            "config": self.config
        }

# Singleton-Instanz
app_protection = AppProtection()

@handle_exception
def initialize_and_start():
    """Initialisiert und startet den App-Schutz."""
    app_protection.initialize_protection()
    app_protection.start_protection()
    return app_protection.get_status()

@handle_exception
def stop_protection():
    """Stoppt den App-Schutz."""
    app_protection.stop_protection()
    return {"status": "stopped"}

@handle_exception
def check_integrity():
    """Prüft die Integrität der geschützten Dateien."""
    modified_files = app_protection.check_integrity()
    return {
        "modified_files": modified_files,
        "integrity_ok": len(modified_files) == 0
    }

@handle_exception
def create_backup(backup_name: Optional[str] = None):
    """Erstellt ein Backup der geschützten Dateien."""
    if not backup_name:
        backup_name = f"manual_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    backup_path = app_protection.create_backup(backup_name)
    return {
        "backup_name": backup_name,
        "backup_path": backup_path
    }

@handle_exception
def add_protected_file(file_path: str):
    """Fügt eine Datei zur Liste der geschützten Dateien hinzu."""
    app_protection.add_protected_file(file_path)
    return {
        "file_path": file_path,
        "protected": file_path in app_protection.protected_files
    }

@handle_exception
def get_status():
    """Gibt den Status des App-Schutzes zurück."""
    return app_protection.get_status()

if __name__ == "__main__":
    # Kommandozeilenargumente verarbeiten
    import argparse
    
    parser = argparse.ArgumentParser(description="App-Schutz für VALEO-NeuroERP")
    parser.add_argument("--start", action="store_true", help="Startet den App-Schutz")
    parser.add_argument("--stop", action="store_true", help="Stoppt den App-Schutz")
    parser.add_argument("--status", action="store_true", help="Zeigt den Status des App-Schutzes an")
    parser.add_argument("--check", action="store_true", help="Prüft die Integrität der geschützten Dateien")
    parser.add_argument("--backup", action="store_true", help="Erstellt ein Backup der geschützten Dateien")
    parser.add_argument("--add-file", metavar="FILE", help="Fügt eine Datei zur Liste der geschützten Dateien hinzu")
    
    args = parser.parse_args()
    
    if args.start:
        status = initialize_and_start()
        print(f"App-Schutz gestartet. Status: {json.dumps(status, indent=2)}")
    
    elif args.stop:
        result = stop_protection()
        print(f"App-Schutz gestoppt. Ergebnis: {json.dumps(result, indent=2)}")
    
    elif args.status:
        status = get_status()
        print(f"Status des App-Schutzes: {json.dumps(status, indent=2)}")
    
    elif args.check:
        result = check_integrity()
        if result["integrity_ok"]:
            print("Alle Dateien sind unverändert.")
        else:
            print(f"Modifizierte Dateien gefunden: {', '.join(result['modified_files'])}")
    
    elif args.backup:
        result = create_backup()
        print(f"Backup erstellt: {result['backup_path']}")
    
    elif args.add_file:
        result = add_protected_file(args.add_file)
        if result["protected"]:
            print(f"Datei {args.add_file} wird jetzt geschützt.")
        else:
            print(f"Datei {args.add_file} konnte nicht geschützt werden.")
    
    else:
        parser.print_help()