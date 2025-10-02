#!/usr/bin/env python
"""
Abhängigkeiten-Installationsskript für das ERP-System.

Dieses Skript installiert alle benötigten Python-Pakete für das ERP-System.
Es überprüft auch, ob die Installation erfolgreich war und gibt eine
Zusammenfassung der installierten Pakete aus.
"""

import subprocess
import sys
import os
import platform
import logging
from typing import List, Dict, Tuple, Set, Optional

# Konfiguriere Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("python_deps_install")

# Pakete nach Kategorien
PACKAGES = {
    "core": [
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "pydantic>=2.0.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.11.0",
        "python-dotenv>=1.0.0",
    ],
    "celery": [
        "celery>=5.3.0",
        "redis>=4.6.0",
        "flower>=2.0.0",
    ],
    "monitoring": [
        "prometheus-client>=0.17.0",
        "psutil>=5.9.0",
        "watchfiles>=0.19.0",
    ],
    "utils": [
        "httpx>=0.24.0",
        "rich>=13.4.0",
        "typer>=0.9.0",
        "pyyaml>=6.0.0",
        "jinja2>=3.1.0",
    ],
    "dev": [
        "black>=23.3.0",
        "isort>=5.12.0",
        "mypy>=1.3.0",
        "pytest>=7.3.0",
        "pytest-cov>=4.1.0",
    ],
}

def check_python_version() -> bool:
    """
    Überprüft, ob die Python-Version kompatibel ist.
    
    Returns:
        bool: True, wenn die Python-Version >= 3.9, sonst False
    """
    major, minor, _ = platform.python_version_tuple()
    if int(major) < 3 or (int(major) == 3 and int(minor) < 9):
        logger.error(
            f"Python {major}.{minor} wird nicht unterstützt. "
            "Python 3.9 oder höher wird benötigt."
        )
        return False
    return True

def pip_install(packages: List[str], upgrade: bool = False) -> Tuple[bool, List[str], List[str]]:
    """
    Installiert die angegebenen Pakete mit pip.
    
    Args:
        packages: Liste der zu installierenden Pakete
        upgrade: Ob Pakete aktualisiert werden sollen
        
    Returns:
        Tuple[bool, List[str], List[str]]: (Erfolg, Erfolgreich installierte Pakete, Fehlgeschlagene Pakete)
    """
    cmd = [sys.executable, "-m", "pip", "install"]
    if upgrade:
        cmd.append("--upgrade")
    
    successful = []
    failed = []
    
    for package in packages:
        package_cmd = cmd + [package]
        logger.info(f"Installiere {package}...")
        
        try:
            subprocess.check_call(package_cmd)
            successful.append(package)
            logger.info(f"{package} erfolgreich installiert")
        except subprocess.CalledProcessError:
            failed.append(package)
            logger.error(f"Fehler bei der Installation von {package}")
    
    return len(failed) == 0, successful, failed

def check_installed_packages(packages: List[str]) -> Tuple[bool, List[str], List[str]]:
    """
    Überprüft, ob die angegebenen Pakete installiert sind.
    
    Args:
        packages: Liste der zu überprüfenden Pakete
        
    Returns:
        Tuple[bool, List[str], List[str]]: (Alle installiert, Installierte Pakete, Fehlende Pakete)
    """
    import importlib
    
    installed = []
    missing = []
    
    for package in packages:
        # Extrahiere den Paketnamen ohne Version
        package_name = package.split(">=")[0].split("==")[0].strip()
        
        try:
            importlib.import_module(package_name)
            installed.append(package)
        except ImportError:
            missing.append(package)
    
    return len(missing) == 0, installed, missing

def main():
    """Hauptfunktion des Skripts."""
    logger.info("ERP-System Abhängigkeiten-Installationsskript")
    
    # Überprüfe Python-Version
    if not check_python_version():
        sys.exit(1)
    
    # Aktualisiere pip
    logger.info("Aktualisiere pip...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        logger.info("pip erfolgreich aktualisiert")
    except subprocess.CalledProcessError:
        logger.warning("Fehler beim Aktualisieren von pip, fahre trotzdem fort")
    
    # Installiere Pakete nach Kategorien
    all_successful = True
    all_packages = []
    
    for category, packages in PACKAGES.items():
        logger.info(f"Installiere {category}-Pakete...")
        success, successful, failed = pip_install(packages)
        
        if not success:
            all_successful = False
            logger.warning(f"Einige {category}-Pakete konnten nicht installiert werden: {', '.join(failed)}")
        
        all_packages.extend(packages)
    
    # Überprüfe die Installation
    logger.info("Überprüfe die Installation...")
    all_installed, installed, missing = check_installed_packages(all_packages)
    
    if all_installed:
        logger.info("Alle Pakete wurden erfolgreich installiert")
    else:
        logger.warning(f"Einige Pakete konnten nicht importiert werden: {', '.join(missing)}")
    
    # Ausgabe einer Zusammenfassung
    logger.info("\nZusammenfassung:")
    logger.info(f"Python-Version: {platform.python_version()}")
    logger.info(f"Betriebssystem: {platform.system()} {platform.release()}")
    logger.info(f"Installationsstatus: {'Erfolgreich' if all_successful and all_installed else 'Mit Fehlern'}")
    
    if not all_installed:
        logger.info("\nFehlende Pakete:")
        for package in missing:
            logger.info(f"  - {package}")
    
    logger.info("\nFür Redis unter Windows muss Redis separat heruntergeladen werden:")
    logger.info("1. Laden Sie Redis für Windows von https://github.com/microsoftarchive/redis/releases herunter")
    logger.info("2. Extrahieren Sie die Dateien in das Verzeichnis 'redis' im Projektverzeichnis")
    logger.info("3. Starten Sie Redis mit 'redis\\redis-server.exe'")
    
    logger.info("\nNächste Schritte:")
    logger.info("1. Redis-Server starten: cd redis && .\\redis-server.exe")
    logger.info("2. Celery-Worker starten: celery -A backend.tasks.celery_app worker --loglevel=info -Q default,reports,imports,exports,optimization")
    logger.info("3. Flower-Dashboard starten: celery -A backend.tasks.celery_app flower --port=5555")
    logger.info("4. Demo-Server starten: uvicorn backend.demo_server_celery:app --reload --host 0.0.0.0 --port 8003")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
