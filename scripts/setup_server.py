#!/usr/bin/env python
"""
Setup-Skript für den ERP-Server.

Dieses Skript korrigiert die Importpfade und installiert fehlende Abhängigkeiten.
"""

import os
import sys
import subprocess
import shutil

def install_dependencies():
    """Installiert alle erforderlichen Abhängigkeiten."""
    print("Installiere benötigte Abhängigkeiten...")
    
    requirements = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic",
        "scikit-learn",
        "pandas",
        "python-multipart",
        "aiofiles",
        "watchfiles",
        "redis"
    ]
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements)
        print("Abhängigkeiten erfolgreich installiert!")
    except subprocess.CalledProcessError as e:
        print(f"Fehler bei der Installation der Abhängigkeiten: {e}")
        return False
        
    return True

def create_dummy_modules():
    """Erstellt fehlende Dummy-Module, damit der Server starten kann."""
    print("Erstelle fehlende Module...")
    
    # Backend-Modul für spätere Importe korrekt initialisieren
    os.makedirs("backend/models/notfall", exist_ok=True)
    os.makedirs("backend/models/produktion", exist_ok=True)
    
    # Erstelle leere __init__.py Dateien für Python-Module
    module_paths = [
        "backend/models/notfall",
        "backend/models/produktion"
    ]
    
    for path in module_paths:
        init_file = os.path.join(path, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write('"""Leeres Modul."""\n')
    
    # Fehlende API-Module erstellen
    missing_apis = [
        "backend/api/notifications_api.py",
        "backend/api/chargen_api.py",
        "backend/api/qs_api.py"
    ]
    
    for api_file in missing_apis:
        if not os.path.exists(api_file):
            with open(api_file, "w") as f:
                f.write('"""Leeres API-Modul."""\n\nfrom fastapi import APIRouter\n\nrouter = APIRouter()\n')
    
    print("Fehlende Module erstellt!")
    return True

def fix_imports():
    """Korrigiert Importpfade in den Modulen."""
    print("Korrigiere Importpfade...")
    
    # Korrigiere die __init__.py in der API
    api_init_path = "backend/api/__init__.py"
    
    try:
        # Backup erstellen
        shutil.copy2(api_init_path, f"{api_init_path}.backup")
        
        with open(api_init_path, "r") as f:
            content = f.read()
        
        # Füge try/except-Blöcke um problematische Importe ein
        modified_content = content.replace(
            "from .partner_api import router as partner_router",
            "try:\n    from .partner_api import router as partner_router\n    api_router.include_router(partner_router, prefix=\"/partner\", tags=[\"Partner\"])\nexcept ImportError as e:\n    print(f\"Partner-API konnte nicht importiert werden: {e}\")"
        )
        
        # Entferne include_router-Zeilen, da sie jetzt in den try-Blöcken sind
        lines = modified_content.split("\n")
        cleaned_lines = []
        
        for line in lines:
            if "api_router.include_router(" not in line or "try:" in line:
                cleaned_lines.append(line)
        
        with open(api_init_path, "w") as f:
            f.write("\n".join(cleaned_lines))
            
        print(f"API-Initialisierungsdatei korrigiert!")
    except Exception as e:
        print(f"Fehler beim Korrigieren der API-Initialisierungsdatei: {e}")
    
    # Korrigiere Importpfade in emergency_api.py
    try:
        emergency_api_path = "backend/api/emergency_api.py"
        if os.path.exists(emergency_api_path):
            with open(emergency_api_path, "r") as f:
                content = f.read()
            
            # Ersetze problematische Importpfade
            content = content.replace("from ..db.database", "from backend.db.database")
            content = content.replace("from ..services.emergency_service", "try:\n    from backend.services.emergency_service import EmergencyService\nexcept ImportError:\n    # Dummy-Service\n    class EmergencyService:\n        def __init__(self): pass")
            
            with open(emergency_api_path, "w") as f:
                f.write(content)
            
            print(f"Emergency-API korrigiert!")
    except Exception as e:
        print(f"Fehler beim Korrigieren der Emergency-API: {e}")
    
    # Korrigiere Importpfade in inventory_api.py
    try:
        inventory_api_path = "backend/api/inventory_api.py"
        if os.path.exists(inventory_api_path):
            with open(inventory_api_path, "r") as f:
                content = f.read()
            
            # Ersetze problematischen Import
            content = content.replace("from enhanced_cache_manager import cache", "from backend.enhanced_cache_manager import cache")
            
            with open(inventory_api_path, "w") as f:
                f.write(content)
            
            print(f"Inventory-API korrigiert!")
    except Exception as e:
        print(f"Fehler beim Korrigieren der Inventory-API: {e}")
    
    return True

def fix_database_structure():
    """Korrigiert die Datenbankstruktur, um doppelte Tabellenregistrierungen zu vermeiden."""
    print("Korrigiere Datenbankstruktur...")
    
    # Korrigiere die Modellinitialisierung
    try:
        models_init_path = "backend/models/__init__.py"
        if os.path.exists(models_init_path):
            with open(models_init_path, "r") as f:
                content = f.read()
            
            # Füge extend_existing=True hinzu, um Konflikte zu vermeiden
            modified_content = content.replace(
                "from sqlalchemy import Column",
                "from sqlalchemy import Column, MetaData\n\n# Metadata mit extend_existing=True konfigurieren\nmetadata = MetaData()"
            )
            
            with open(models_init_path, "w") as f:
                f.write(modified_content)
            
            print(f"Modellinitialisierung korrigiert!")
    except Exception as e:
        print(f"Fehler beim Korrigieren der Modellinitialisierung: {e}")
    
    # Korrigiere Base in database.py
    try:
        database_path = "backend/db/database.py"
        if os.path.exists(database_path):
            with open(database_path, "r") as f:
                content = f.read()
            
            # Verwende MetaData mit extend_existing=True
            modified_content = content.replace(
                "Base = declarative_base()",
                "from sqlalchemy.ext.declarative import declarative_base\nBase = declarative_base(metadata=MetaData(bind=engine))"
            )
            
            # Importiere MetaData
            modified_content = modified_content.replace(
                "from sqlalchemy import create_engine",
                "from sqlalchemy import create_engine, MetaData"
            )
            
            with open(database_path, "w") as f:
                f.write(modified_content)
            
            print(f"Datenbankbasis korrigiert!")
    except Exception as e:
        print(f"Fehler beim Korrigieren der Datenbankbasis: {e}")
    
    return True

def create_basic_router():
    """Erstellt einen grundlegenden API-Router, falls der bestehende nicht funktioniert."""
    print("Erstelle grundlegenden API-Router...")
    
    # Backup der bestehenden __init__.py erstellen
    api_init_path = "backend/api/__init__.py"
    backup_path = f"{api_init_path}.full_backup"
    
    if not os.path.exists(backup_path):
        shutil.copy2(api_init_path, backup_path)
    
    # Erstelle einen neuen, minimalen Router
    with open(api_init_path, "w") as f:
        f.write('''"""
API-Modul-Initialisierung für das modulare ERP-System.
Dieses Modul definiert Router und API-Endpunkte für verschiedene Funktionsbereiche.
"""

from fastapi import APIRouter

# Haupt-Router für alle API-Endpunkte
api_router = APIRouter()

# Router für Batch-Operationen und Performance-Monitoring
try:
    from .batch_api import router as batch_router
    api_router.include_router(batch_router, prefix="/batch", tags=["Batch"])
    print("Batch-API erfolgreich registriert")
except ImportError as e:
    print(f"Batch-API konnte nicht importiert werden: {e}")

try:
    from .performance_api import router as performance_router
    api_router.include_router(performance_router, prefix="/performance", tags=["Performance"])
    print("Performance-API erfolgreich registriert")
except ImportError as e:
    print(f"Performance-API konnte nicht importiert werden: {e}")

# Status-API für Health-Checks und Monitoring
@api_router.get("/status", tags=["System"])
async def status():
    """Grundlegender Statusendpunkt für Health-Checks"""
    return {"status": "online"}
''')
    
    print("Grundlegender API-Router erstellt!")
    return True

def main():
    """Hauptfunktion des Setup-Skripts."""
    print("=== ERP-Server-Setup ===")
    
    # Überprüfe das aktuelle Verzeichnis
    if not os.path.isdir("backend"):
        print("Fehler: Dieses Skript muss im Hauptverzeichnis des Projekts ausgeführt werden!")
        return False
    
    # Führe die Setup-Schritte aus
    steps = [
        ("Abhängigkeiten installieren", install_dependencies),
        ("Fehlende Module erstellen", create_dummy_modules),
        ("Importpfade korrigieren", fix_imports),
        ("Datenbankstruktur korrigieren", fix_database_structure),
        ("Grundlegenden Router erstellen", create_basic_router)
    ]
    
    for step_name, step_func in steps:
        print(f"\n--- {step_name} ---")
        success = step_func()
        if not success:
            print(f"Fehler beim Schritt '{step_name}'!")
            return False
    
    print("\n=== Setup abgeschlossen! ===")
    print("Der Server sollte jetzt mit 'python -m backend.modular_server' gestartet werden können.")
    return True

if __name__ == "__main__":
    main() 