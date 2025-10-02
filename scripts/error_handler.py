#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fehlerbehandlung für VALEO-NeuroERP

Dieses Modul implementiert eine robuste Fehlerbehandlung für die VALEO-NeuroERP-Anwendung.
Es protokolliert Fehler, analysiert sie und bietet Wiederherstellungsstrategien.
"""

import os
import sys
import time
import json
import logging
import traceback
import hashlib
import shutil
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional, Tuple, Union

# Konfiguration
LOG_DIR = "logs"
BACKUP_DIR = "backups"
CONFIG_DIR = "config"
MAX_BACKUPS = 5
ERROR_THRESHOLD = 3  # Anzahl der Fehler, bevor eine Wiederherstellung ausgelöst wird
ERROR_WINDOW = 300  # Zeitfenster für Fehler in Sekunden (5 Minuten)

# Logging konfigurieren
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "error_handler.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("error_handler")

class ErrorStats:
    """Klasse zur Verfolgung von Fehlerstatistiken."""
    
    def __init__(self):
        self.errors = []  # Liste von (timestamp, error_type, error_message)
        self.error_counts = {}  # Fehlertyp -> Anzahl
        self.last_recovery = 0  # Zeitstempel der letzten Wiederherstellung
    
    def add_error(self, error_type: str, error_message: str) -> None:
        """Fügt einen Fehler zu den Statistiken hinzu."""
        now = time.time()
        self.errors.append((now, error_type, error_message))
        
        # Alte Fehler entfernen
        self.errors = [(t, et, em) for t, et, em in self.errors if now - t < ERROR_WINDOW]
        
        # Fehleranzahl aktualisieren
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
    
    def should_recover(self) -> bool:
        """Prüft, ob eine Wiederherstellung ausgelöst werden sollte."""
        now = time.time()
        
        # Zu viele Fehler in kurzer Zeit?
        recent_errors = [(t, et, em) for t, et, em in self.errors if now - t < ERROR_WINDOW]
        if len(recent_errors) >= ERROR_THRESHOLD:
            # Nicht zu oft wiederherstellen
            if now - self.last_recovery > ERROR_WINDOW:
                self.last_recovery = now
                return True
        
        return False
    
    def get_most_common_error(self) -> Optional[str]:
        """Gibt den häufigsten Fehlertyp zurück."""
        if not self.error_counts:
            return None
        
        return max(self.error_counts.items(), key=lambda x: x[1])[0]
    
    def clear(self) -> None:
        """Löscht alle Fehlerstatistiken."""
        self.errors = []
        self.error_counts = {}

class FileIntegrityMonitor:
    """Überwacht die Integrität von Dateien."""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir
        self.file_hashes = {}
        self.protected_files = set()
    
    def calculate_hash(self, file_path: str) -> str:
        """Berechnet den Hash einer Datei."""
        try:
            with open(file_path, "rb") as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            return file_hash
        except Exception as e:
            logger.error(f"Fehler beim Berechnen des Hashes für {file_path}: {str(e)}")
            return ""
    
    def add_protected_file(self, file_path: str) -> None:
        """Fügt eine zu schützende Datei hinzu."""
        abs_path = os.path.join(self.base_dir, file_path)
        if os.path.exists(abs_path):
            self.protected_files.add(file_path)
            self.file_hashes[file_path] = self.calculate_hash(abs_path)
            logger.info(f"Datei {file_path} wird jetzt geschützt")
        else:
            logger.warning(f"Datei {file_path} existiert nicht und kann nicht geschützt werden")
    
    def check_file_integrity(self) -> List[str]:
        """Prüft die Integrität aller geschützten Dateien."""
        modified_files = []
        
        for file_path in self.protected_files:
            abs_path = os.path.join(self.base_dir, file_path)
            if not os.path.exists(abs_path):
                logger.warning(f"Geschützte Datei {file_path} existiert nicht mehr")
                modified_files.append(file_path)
                continue
            
            current_hash = self.calculate_hash(abs_path)
            if current_hash != self.file_hashes.get(file_path, ""):
                logger.warning(f"Datei {file_path} wurde modifiziert")
                modified_files.append(file_path)
        
        return modified_files
    
    def update_hash(self, file_path: str) -> None:
        """Aktualisiert den Hash einer Datei."""
        if file_path in self.protected_files:
            abs_path = os.path.join(self.base_dir, file_path)
            self.file_hashes[file_path] = self.calculate_hash(abs_path)
            logger.info(f"Hash für {file_path} aktualisiert")

class BackupManager:
    """Verwaltet Backups von Dateien und Konfigurationen."""
    
    def __init__(self, backup_dir: str = BACKUP_DIR):
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, file_paths: List[str], backup_name: Optional[str] = None) -> str:
        """Erstellt ein Backup der angegebenen Dateien."""
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        
        for file_path in file_paths:
            if os.path.exists(file_path):
                # Zielverzeichnis erstellen
                target_dir = os.path.join(backup_path, os.path.dirname(file_path))
                os.makedirs(target_dir, exist_ok=True)
                
                # Datei kopieren
                target_path = os.path.join(backup_path, file_path)
                shutil.copy2(file_path, target_path)
                logger.info(f"Datei {file_path} gesichert nach {target_path}")
        
        # Alte Backups entfernen
        self._cleanup_old_backups()
        
        return backup_path
    
    def restore_backup(self, backup_name: str, file_paths: Optional[List[str]] = None) -> bool:
        """Stellt ein Backup wieder her."""
        backup_path = os.path.join(self.backup_dir, backup_name)
        if not os.path.exists(backup_path):
            logger.error(f"Backup {backup_name} existiert nicht")
            return False
        
        success = True
        
        # Alle Dateien im Backup wiederherstellen
        for root, _, files in os.walk(backup_path):
            for file in files:
                backup_file = os.path.join(root, file)
                rel_path = os.path.relpath(backup_file, backup_path)
                
                # Prüfen, ob die Datei wiederhergestellt werden soll
                if file_paths and rel_path not in file_paths:
                    continue
                
                try:
                    # Zielverzeichnis erstellen
                    target_dir = os.path.dirname(rel_path)
                    os.makedirs(target_dir, exist_ok=True)
                    
                    # Datei kopieren
                    shutil.copy2(backup_file, rel_path)
                    logger.info(f"Datei {rel_path} wiederhergestellt")
                except Exception as e:
                    logger.error(f"Fehler beim Wiederherstellen von {rel_path}: {str(e)}")
                    success = False
        
        return success
    
    def list_backups(self) -> List[str]:
        """Listet alle verfügbaren Backups auf."""
        if not os.path.exists(self.backup_dir):
            return []
        
        return [d for d in os.listdir(self.backup_dir) 
                if os.path.isdir(os.path.join(self.backup_dir, d))]
    
    def _cleanup_old_backups(self) -> None:
        """Entfernt alte Backups, wenn zu viele vorhanden sind."""
        backups = self.list_backups()
        if len(backups) <= MAX_BACKUPS:
            return
        
        # Sortiere Backups nach Erstellungsdatum
        backups.sort(key=lambda x: os.path.getctime(os.path.join(self.backup_dir, x)))
        
        # Entferne die ältesten Backups
        for old_backup in backups[:-MAX_BACKUPS]:
            try:
                shutil.rmtree(os.path.join(self.backup_dir, old_backup))
                logger.info(f"Altes Backup {old_backup} entfernt")
            except Exception as e:
                logger.error(f"Fehler beim Entfernen des alten Backups {old_backup}: {str(e)}")

class ErrorHandler:
    """Hauptklasse für die Fehlerbehandlung."""
    
    def __init__(self):
        self.error_stats = ErrorStats()
        self.file_monitor = FileIntegrityMonitor()
        self.backup_manager = BackupManager()
        
        # Standardmäßig zu schützende Dateien
        self.critical_files = [
            "scripts/streamlit_app_mcp_integration.py",
            "scripts/cursor_prompt_integration.py",
            "scripts/error_handler.py",
            "config/version.yaml",
            "start_app.sh",
            "start_app.bat"
        ]
        
        # Fehlerbehandlungsstrategien
        self.error_strategies = {
            "FileNotFoundError": self._handle_file_not_found,
            "PermissionError": self._handle_permission_error,
            "ConnectionError": self._handle_connection_error,
            "TimeoutError": self._handle_timeout_error,
            "ValueError": self._handle_value_error,
            "KeyError": self._handle_key_error,
            "IndexError": self._handle_index_error,
            "TypeError": self._handle_type_error,
            "AttributeError": self._handle_attribute_error,
            "ImportError": self._handle_import_error,
            "ModuleNotFoundError": self._handle_module_not_found,
            "FileIntegrityError": self._handle_file_integrity_error,
            "default": self._handle_default_error
        }
        
        # Initialisieren
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialisiert den ErrorHandler."""
        # Verzeichnisse erstellen
        os.makedirs(LOG_DIR, exist_ok=True)
        os.makedirs(BACKUP_DIR, exist_ok=True)
        os.makedirs(CONFIG_DIR, exist_ok=True)
        
        # Kritische Dateien schützen
        for file_path in self.critical_files:
            self.file_monitor.add_protected_file(file_path)
        
        # Initiales Backup erstellen
        self.backup_manager.create_backup(self.critical_files, "initial_backup")
        
        logger.info("ErrorHandler initialisiert")
    
    def handle_error(self, error: Exception, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Behandelt einen Fehler."""
        if context is None:
            context = {}
        
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # Fehler protokollieren
        logger.error(f"Fehler aufgetreten: {error_type} - {error_message}")
        logger.error(f"Traceback: {error_traceback}")
        
        # Fehlerstatistik aktualisieren
        self.error_stats.add_error(error_type, error_message)
        
        # Dateien auf Integrität prüfen
        modified_files = self.file_monitor.check_file_integrity()
        if modified_files:
            logger.warning(f"Modifizierte Dateien gefunden: {modified_files}")
            self._handle_file_integrity_error(modified_files, context)
        
        # Fehlerbehandlungsstrategie auswählen und ausführen
        strategy = self.error_strategies.get(error_type, self.error_strategies["default"])
        result = strategy(error, context)
        
        # Prüfen, ob eine Wiederherstellung notwendig ist
        if self.error_stats.should_recover():
            self._perform_recovery()
        
        return result
    
    def _perform_recovery(self) -> None:
        """Führt eine Wiederherstellung durch."""
        logger.info("Führe Wiederherstellung durch...")
        
        # Neuestes Backup finden
        backups = self.backup_manager.list_backups()
        if not backups:
            logger.error("Keine Backups gefunden für die Wiederherstellung")
            return
        
        # Neuestes Backup wiederherstellen
        latest_backup = max(backups, key=lambda x: os.path.getctime(os.path.join(BACKUP_DIR, x)))
        logger.info(f"Stelle Backup {latest_backup} wieder her")
        
        # Modifizierte Dateien wiederherstellen
        modified_files = self.file_monitor.check_file_integrity()
        if modified_files:
            success = self.backup_manager.restore_backup(latest_backup, modified_files)
            if success:
                logger.info("Wiederherstellung erfolgreich")
                
                # Hashes aktualisieren
                for file_path in modified_files:
                    self.file_monitor.update_hash(file_path)
                
                # Fehlerstatistik zurücksetzen
                self.error_stats.clear()
            else:
                logger.error("Wiederherstellung fehlgeschlagen")
    
    def _handle_file_not_found(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt FileNotFoundError."""
        file_path = getattr(error, "filename", "Unbekannte Datei")
        logger.info(f"Datei nicht gefunden: {file_path}")
        
        # Prüfen, ob es sich um eine kritische Datei handelt
        if any(file_path.endswith(critical) for critical in self.critical_files):
            logger.warning(f"Kritische Datei nicht gefunden: {file_path}")
            
            # Versuche, die Datei aus dem Backup wiederherzustellen
            backups = self.backup_manager.list_backups()
            if backups:
                latest_backup = max(backups, key=lambda x: os.path.getctime(os.path.join(BACKUP_DIR, x)))
                self.backup_manager.restore_backup(latest_backup, [file_path])
        
        return {
            "error_type": "FileNotFoundError",
            "message": f"Die Datei '{file_path}' wurde nicht gefunden.",
            "suggestion": "Überprüfen Sie den Dateipfad und stellen Sie sicher, dass die Datei existiert.",
            "recovery_action": "Versuche, die Datei aus dem Backup wiederherzustellen."
        }
    
    def _handle_permission_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt PermissionError."""
        return {
            "error_type": "PermissionError",
            "message": f"Keine Berechtigung: {str(error)}",
            "suggestion": "Überprüfen Sie die Dateiberechtigungen.",
            "recovery_action": "Keine automatische Wiederherstellung möglich."
        }
    
    def _handle_connection_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt ConnectionError."""
        return {
            "error_type": "ConnectionError",
            "message": f"Verbindungsfehler: {str(error)}",
            "suggestion": "Überprüfen Sie Ihre Netzwerkverbindung.",
            "recovery_action": "Versuche, die Verbindung wiederherzustellen."
        }
    
    def _handle_timeout_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt TimeoutError."""
        return {
            "error_type": "TimeoutError",
            "message": f"Zeitüberschreitung: {str(error)}",
            "suggestion": "Die Operation hat zu lange gedauert. Versuchen Sie es später erneut.",
            "recovery_action": "Keine automatische Wiederherstellung möglich."
        }
    
    def _handle_value_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt ValueError."""
        return {
            "error_type": "ValueError",
            "message": f"Ungültiger Wert: {str(error)}",
            "suggestion": "Überprüfen Sie die Eingabewerte.",
            "recovery_action": "Keine automatische Wiederherstellung möglich."
        }
    
    def _handle_key_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt KeyError."""
        return {
            "error_type": "KeyError",
            "message": f"Schlüssel nicht gefunden: {str(error)}",
            "suggestion": "Überprüfen Sie die Schlüssel im Dictionary.",
            "recovery_action": "Keine automatische Wiederherstellung möglich."
        }
    
    def _handle_index_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt IndexError."""
        return {
            "error_type": "IndexError",
            "message": f"Index außerhalb des Bereichs: {str(error)}",
            "suggestion": "Überprüfen Sie die Indizes und die Länge der Liste.",
            "recovery_action": "Keine automatische Wiederherstellung möglich."
        }
    
    def _handle_type_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt TypeError."""
        return {
            "error_type": "TypeError",
            "message": f"Typfehler: {str(error)}",
            "suggestion": "Überprüfen Sie die Typen der Variablen.",
            "recovery_action": "Keine automatische Wiederherstellung möglich."
        }
    
    def _handle_attribute_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt AttributeError."""
        return {
            "error_type": "AttributeError",
            "message": f"Attributfehler: {str(error)}",
            "suggestion": "Überprüfen Sie, ob das Objekt das angegebene Attribut hat.",
            "recovery_action": "Keine automatische Wiederherstellung möglich."
        }
    
    def _handle_import_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt ImportError."""
        module = getattr(error, "name", "Unbekanntes Modul")
        return {
            "error_type": "ImportError",
            "message": f"Fehler beim Importieren von {module}: {str(error)}",
            "suggestion": "Überprüfen Sie, ob das Modul installiert ist.",
            "recovery_action": "Versuche, das Modul zu installieren."
        }
    
    def _handle_module_not_found(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt ModuleNotFoundError."""
        module = getattr(error, "name", "Unbekanntes Modul")
        return {
            "error_type": "ModuleNotFoundError",
            "message": f"Modul {module} nicht gefunden: {str(error)}",
            "suggestion": "Installieren Sie das fehlende Modul.",
            "recovery_action": f"Versuche, das Modul {module} zu installieren."
        }
    
    def _handle_file_integrity_error(self, modified_files: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt Fehler bei der Dateiintegrität."""
        # Backup erstellen
        backup_path = self.backup_manager.create_backup(self.critical_files)
        
        return {
            "error_type": "FileIntegrityError",
            "message": f"Die folgenden Dateien wurden modifiziert: {', '.join(modified_files)}",
            "suggestion": "Überprüfen Sie die Änderungen an den Dateien.",
            "recovery_action": f"Backup erstellt unter {backup_path}. Stellen Sie die Originaldateien wieder her, wenn nötig."
        }
    
    def _handle_default_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Behandelt alle anderen Fehler."""
        return {
            "error_type": type(error).__name__,
            "message": f"Ein Fehler ist aufgetreten: {str(error)}",
            "suggestion": "Überprüfen Sie die Anwendung und die Protokolle.",
            "recovery_action": "Keine spezifische Wiederherstellungsaktion verfügbar."
        }

# Singleton-Instanz
error_handler = ErrorHandler()

def handle_exception(func: Callable) -> Callable:
    """Decorator für die Fehlerbehandlung."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            context = {
                "function": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            result = error_handler.handle_error(e, context)
            logger.info(f"Fehlerbehandlung abgeschlossen: {result}")
            
            # Re-raise the exception if needed
            if "raise_exception" in result and result["raise_exception"]:
                raise
            
            return result
    return wrapper

def check_file_integrity() -> List[str]:
    """Prüft die Integrität der kritischen Dateien."""
    return error_handler.file_monitor.check_file_integrity()

def create_backup() -> str:
    """Erstellt ein Backup der kritischen Dateien."""
    return error_handler.backup_manager.create_backup(error_handler.critical_files)

def restore_backup(backup_name: str) -> bool:
    """Stellt ein Backup wieder her."""
    return error_handler.backup_manager.restore_backup(backup_name)

def list_backups() -> List[str]:
    """Listet alle verfügbaren Backups auf."""
    return error_handler.backup_manager.list_backups()

def add_protected_file(file_path: str) -> None:
    """Fügt eine zu schützende Datei hinzu."""
    error_handler.file_monitor.add_protected_file(file_path)
    error_handler.critical_files.append(file_path)

def get_error_stats() -> Dict[str, Any]:
    """Gibt die Fehlerstatistiken zurück."""
    return {
        "error_count": len(error_handler.error_stats.errors),
        "error_types": error_handler.error_stats.error_counts,
        "most_common_error": error_handler.error_stats.get_most_common_error()
    }

if __name__ == "__main__":
    # Test der Funktionalität
    logger.info("Teste ErrorHandler...")
    
    # Test: Datei nicht gefunden
    try:
        with open("nicht_existierende_datei.txt", "r") as f:
            content = f.read()
    except Exception as e:
        error_handler.handle_error(e)
    
    # Test: Backup erstellen
    backup_path = create_backup()
    logger.info(f"Backup erstellt: {backup_path}")
    
    # Test: Backups auflisten
    backups = list_backups()
    logger.info(f"Verfügbare Backups: {backups}")
    
    logger.info("ErrorHandler-Test abgeschlossen") 