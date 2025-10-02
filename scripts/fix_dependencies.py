#!/usr/bin/env python
"""
Abhängigkeiten-Reparaturskript für das ERP-System.

Dieses Skript behebt häufige Abhängigkeitsprobleme des ERP-Systems:
1. SQLAlchemy JSONB-Unterstützung
2. Fehlende Module (batch_processing, performance)
3. Fehlende Klassen in Modulen (LagerOrt, KundenGruppe, etc.)

Verwendung: python scripts/fix_dependencies.py
"""

import os
import sys
import subprocess
import logging
import importlib
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set

# Konfiguriere Logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("fix_dependencies")

# Definiere Konstanten
WORKSPACE_ROOT = Path(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
BACKEND_DIR = WORKSPACE_ROOT / "backend"
MODELS_DIR = BACKEND_DIR / "models"
API_DIR = BACKEND_DIR / "api"
DB_DIR = BACKEND_DIR / "db"

# Minimale Versionen der erforderlichen Pakete
REQUIRED_PACKAGES = {
    "sqlalchemy": "2.0.0",  # SQLAlchemy 2.0+ für JSONB-Unterstützung
    "fastapi": "0.100.0",
    "uvicorn": "0.22.0",
    "pydantic": "2.0.0",
    "celery": "5.3.0",
    "redis": "4.5.0",
    "flower": "2.0.0",
}

# Fehlende Module und ihre Pfade
MISSING_MODULES = {
    "backend.api.batch_processing": API_DIR / "batch_processing.py",
    "backend.api.performance": API_DIR / "performance.py",
}

# Fehlende Klassen in Modulen
MISSING_CLASSES = {
    "backend.models.lager": ["LagerOrt"],
    "backend.models.partner": ["KundenGruppe"],
    "backend.models.produktion": ["ProduktionsAuftrag"],
    "backend.models.user": ["Permission"],
    "backend.models.notfall": ["NotfallPlan"],
    "backend.db.performance_monitor": ["DBPerformanceMiddleware"],
}

def check_python_version() -> bool:
    """Überprüft, ob die Python-Version kompatibel ist."""
    major, minor, _ = sys.version_info
    if major < 3 or (major == 3 and minor < 11):
        logger.error(f"Python 3.11+ erforderlich, gefunden: {major}.{minor}")
        return False
    
    logger.info(f"Python-Version {major}.{minor} ist kompatibel")
    return True

def check_package_versions() -> List[str]:
    """Überprüft die installierten Pakete und gibt eine Liste der zu aktualisierenden Pakete zurück."""
    to_update = []
    
    for package, min_version in REQUIRED_PACKAGES.items():
        try:
            module = importlib.import_module(package)
            if hasattr(module, "__version__"):
                installed_version = module.__version__
            elif hasattr(module, "VERSION"):
                installed_version = module.VERSION
            else:
                # Versuche, die Version mit importlib.metadata zu ermitteln (Python 3.8+)
                try:
                    import importlib.metadata
                    installed_version = importlib.metadata.version(package)
                except:
                    logger.warning(f"Konnte Version für {package} nicht ermitteln, nehme an es muss aktualisiert werden")
                    to_update.append(f"{package}>={min_version}")
                    continue
            
            # Einfacher Versionsvergleich (nicht perfekt, aber für die meisten Fälle ausreichend)
            installed_parts = installed_version.split(".")
            required_parts = min_version.split(".")
            
            needs_update = False
            for i in range(min(len(installed_parts), len(required_parts))):
                if int(installed_parts[i]) < int(required_parts[i]):
                    needs_update = True
                    break
                elif int(installed_parts[i]) > int(required_parts[i]):
                    break
            
            if needs_update:
                logger.warning(f"{package} {installed_version} gefunden, aber {min_version}+ erforderlich")
                to_update.append(f"{package}>={min_version}")
            else:
                logger.info(f"{package} {installed_version} ist kompatibel")
        
        except ImportError:
            logger.warning(f"{package} nicht installiert")
            to_update.append(f"{package}>={min_version}")
    
    return to_update

def update_packages(packages: List[str]) -> bool:
    """Aktualisiert die angegebenen Pakete mit pip."""
    if not packages:
        logger.info("Keine Pakete müssen aktualisiert werden")
        return True
    
    logger.info(f"Aktualisiere {len(packages)} Pakete: {', '.join(packages)}")
    
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + packages
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info("Paketaktualisierung erfolgreich")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Fehler bei der Paketaktualisierung: {e}")
        logger.error(f"Ausgabe: {e.stdout}")
        logger.error(f"Fehler: {e.stderr}")
        return False

def create_missing_modules() -> bool:
    """Erstellt fehlende Module."""
    success = True
    
    for module_path, file_path in MISSING_MODULES.items():
        if file_path.exists():
            logger.info(f"Modul {module_path} existiert bereits als {file_path}")
            continue
        
        logger.info(f"Erstelle fehlendes Modul {module_path} in {file_path}")
        
        # Stelle sicher, dass das Verzeichnis existiert
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Erstelle eine __init__.py, falls noch nicht vorhanden
        init_file = file_path.parent / "__init__.py"
        if not init_file.exists():
            init_file.touch()
        
        # Generiere den Modulinhalt basierend auf dem Modulnamen
        content = ""
        
        if module_path == "backend.api.batch_processing":
            content = """\"\"\"
Batch-Processing-API-Modul.

Dieses Modul implementiert API-Endpunkte für Batch-Verarbeitungsfunktionen.
\"\"\"

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/batch", tags=["Batch Processing"])

class BatchJob(BaseModel):
    # Modell für einen Batch-Job.
    id: Optional[str] = None
    name: str
    type: str
    parameters: Dict[str, Any] = {}
    status: str = "pending"
    
# In-Memory-Speicher für Batch-Jobs (temporär)
batch_jobs = {}

@router.post("/jobs", response_model=BatchJob)
async def create_batch_job(job: BatchJob, background_tasks: BackgroundTasks):
    # Erstellt einen neuen Batch-Job.
    import uuid
    job_id = str(uuid.uuid4())
    job.id = job_id
    batch_jobs[job_id] = job.dict()
    
    # Simuliere asynchrone Verarbeitung
    background_tasks.add_task(process_batch_job, job_id)
    
    return job

@router.get("/jobs", response_model=List[BatchJob])
async def get_batch_jobs():
    # Gibt alle Batch-Jobs zurück.
    return list(batch_jobs.values())

@router.get("/jobs/{job_id}", response_model=BatchJob)
async def get_batch_job(job_id: str):
    # Gibt einen bestimmten Batch-Job zurück.
    if job_id not in batch_jobs:
        raise HTTPException(status_code=404, detail="Batch-Job nicht gefunden")
    return batch_jobs[job_id]

async def process_batch_job(job_id: str):
    # Verarbeitet einen Batch-Job im Hintergrund.
    import asyncio
    import random
    
    # Simuliere Verarbeitung
    batch_jobs[job_id]["status"] = "processing"
    await asyncio.sleep(random.randint(2, 5))
    batch_jobs[job_id]["status"] = "completed"
"""
        elif module_path == "backend.api.performance":
            content = """\"\"\"
Performance-API-Modul.

Dieses Modul implementiert API-Endpunkte für Performance-Metriken und -Monitoring.
\"\"\"

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/performance", tags=["Performance"])

class PerformanceMetric(BaseModel):
    # Modell für eine Performance-Metrik.
    id: Optional[str] = None
    name: str
    value: float
    timestamp: Optional[datetime] = None
    tags: Dict[str, str] = {}
    
# In-Memory-Speicher für Metriken (temporär)
performance_metrics = {}

@router.post("/metrics", response_model=PerformanceMetric)
async def create_metric(metric: PerformanceMetric):
    # Speichert eine neue Performance-Metrik.
    import uuid
    metric_id = str(uuid.uuid4())
    metric.id = metric_id
    performance_metrics[metric_id] = metric.dict()
    return metric

@router.get("/metrics", response_model=List[PerformanceMetric])
async def get_metrics():
    # Gibt alle Performance-Metriken zurück.
    return list(performance_metrics.values())

@router.get("/metrics/{metric_name}/history", response_model=List[PerformanceMetric])
async def get_metric_history(metric_name: str, days: int = 7):
    # Gibt den Verlauf einer bestimmten Metrik zurück.
    # Simuliere historische Daten
    result = []
    now = datetime.now()
    
    for i in range(days):
        timestamp = now - timedelta(days=i)
        for hour in range(0, 24, 4):  # Alle 4 Stunden
            metric = PerformanceMetric(
                id=f"{metric_name}-{i}-{hour}",
                name=metric_name,
                value=random.uniform(0.1, 100.0),
                unit="ms" if "time" in metric_name else "%",
                timestamp=timestamp.replace(hour=hour)
            )
            result.append(metric.dict())
    
    return result

@router.get("/dashboard")
async def get_performance_dashboard():
    # Gibt Performance-Dashboard-Daten zurück.
    return {
        "summary": {
            "api_response_time_avg": random.uniform(20, 100),
            "database_query_time_avg": random.uniform(5, 50),
            "cpu_usage_avg": random.uniform(10, 80),
            "memory_usage_avg": random.uniform(20, 70),
        },
        "alerts": [
            {"severity": "warning", "message": "API response time above threshold (100ms)", "timestamp": datetime.now() - timedelta(hours=2)}
        ] if random.random() > 0.7 else [],
        "recommendations": [
            {"type": "index", "description": "Add index to table 'transactions' on column 'created_at'"},
            {"type": "cache", "description": "Enable caching for frequent queries on 'products'"}
        ]
    }
"""
        
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Modul {module_path} erfolgreich erstellt")
        except Exception as e:
            logger.error(f"Fehler beim Erstellen von {module_path}: {e}")
            success = False
    
    return success

def create_missing_classes() -> bool:
    """Erstellt fehlende Klassen in vorhandenen Modulen."""
    success = True
    
    for module_path, class_names in MISSING_CLASSES.items():
        # Extrahiere den Dateipfad aus dem Modulpfad
        parts = module_path.split(".")
        if parts[-1] == "__init__":
            file_path = WORKSPACE_ROOT.joinpath(*parts[:-1]) / "__init__.py"
        else:
            file_path = WORKSPACE_ROOT.joinpath(*parts[:-1]) / f"{parts[-1]}.py"
        
        # Erstelle das Verzeichnis und die Datei, falls sie nicht existieren
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Erstelle __init__.py in übergeordneten Verzeichnissen
            for i in range(1, len(parts) - 1):
                init_path = WORKSPACE_ROOT.joinpath(*parts[:i]) / "__init__.py"
                if not init_path.exists():
                    init_path.touch()
            
            # Wenn es sich um ein __init__.py handelt, erstelle die Verzeichnisstruktur
            if parts[-1] == "__init__":
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch()
            else:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(f'"""\n{parts[-1]} module.\n"""\n\n')
        
        try:
            # Lese die bestehende Datei
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Füge fehlende Klassen hinzu
            new_content = content
            
            for class_name in class_names:
                if f"class {class_name}" not in content:
                    logger.info(f"Füge Klasse {class_name} zu {module_path} hinzu")
                    
                    if module_path == "backend.models.lager":
                        class_def = f"""
class {class_name}:
    # Modell für einen Lagerort.
    
    def __init__(self, id=None, name=None, beschreibung=None, lager_typ=None):
        self.id = id
        self.name = name
        self.beschreibung = beschreibung
        self.lager_typ = lager_typ
        
    def __repr__(self):
        return f"<{class_name}(id={{self.id}}, name={{self.name}})>"
"""
                    elif module_path == "backend.models.partner":
                        class_def = f"""
class {class_name}:
    # Modell für eine Kundengruppe.
    
    def __init__(self, id=None, name=None, beschreibung=None, rabatt=0.0):
        self.id = id
        self.name = name
        self.beschreibung = beschreibung
        self.rabatt = rabatt
        
    def __repr__(self):
        return f"<{class_name}(id={{self.id}}, name={{self.name}})>"
"""
                    elif module_path == "backend.models.produktion":
                        class_def = f"""
class {class_name}:
    # Modell für einen Produktionsauftrag.
    
    def __init__(self, id=None, name=None, start_datum=None, end_datum=None, status="geplant"):
        self.id = id
        self.name = name
        self.start_datum = start_datum
        self.end_datum = end_datum
        self.status = status
        
    def __repr__(self):
        return f"<{class_name}(id={{self.id}}, name={{self.name}}, status={{self.status}})>"
"""
                    elif module_path == "backend.models.user":
                        class_def = f"""
class {class_name}:
    # Modell für eine Benutzererlaubnis.
    
    def __init__(self, id=None, name=None, beschreibung=None):
        self.id = id
        self.name = name
        self.beschreibung = beschreibung
        
    def __repr__(self):
        return f"<{class_name}(id={{self.id}}, name={{self.name}})>"
"""
                    elif module_path == "backend.models.notfall":
                        class_def = f"""
class {class_name}:
    # Modell für einen Notfallplan.
    
    def __init__(self, id=None, name=None, beschreibung=None, prioritaet="mittel", aktiviert=False):
        self.id = id
        self.name = name
        self.beschreibung = beschreibung
        self.prioritaet = prioritaet
        self.aktiviert = aktiviert
        
    def __repr__(self):
        return f"<{class_name}(id={{self.id}}, name={{self.name}}, prioritaet={{self.prioritaet}})>"
"""
                    elif module_path == "backend.db.performance_monitor":
                        class_def = f"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import logging

logger = logging.getLogger(__name__)

class {class_name}(BaseHTTPMiddleware):
    # Middleware zur Überwachung der Datenbankleistung.
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Datenbankzugriffe vor der Anfrage zählen
        db_queries_before = self.count_db_queries()
        
        response = await call_next(request)
        
        # Datenbankzugriffe nach der Anfrage zählen
        db_queries_after = self.count_db_queries()
        
        # Leistungsmetriken berechnen
        processing_time = time.time() - start_time
        db_queries = db_queries_after - db_queries_before
        
        # Metriken protokollieren
        logger.info(
            f"Anfrage: {{request.method}} {{request.url.path}} - "
            f"Verarbeitungszeit: {{processing_time:.4f}}s, "
            f"DB-Abfragen: {{db_queries}}"
        )
        
        # Speichere Metriken in der Datenbank (simuliert)
        self.store_metrics(request, processing_time, db_queries)
        
        return response
    
    def count_db_queries(self):
        # Zählt die Anzahl der Datenbankabfragen (simuliert).
        # In einer realen Implementierung würde dies die tatsächlichen DB-Abfragen zählen
        # Hier geben wir einen simulierten Wert zurück
        return 0
    
    def store_metrics(self, request, processing_time, db_queries):
        # Speichert die Leistungsmetriken (simuliert).
        # In einer realen Implementierung würden die Metriken in einer Datenbank gespeichert
        pass
"""
                    else:
                        class_def = f"""
class {class_name}:
    # Automatisch generierte Klasse für {class_name}.
    
    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
        
    def __repr__(self):
        return f"<{class_name}(id={{self.id}}, name={{self.name}})>"
"""
                    
                    new_content += class_def
            
            # Schreibe die aktualisierte Datei zurück, wenn Änderungen vorgenommen wurden
            if new_content != content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                logger.info(f"Modul {module_path} erfolgreich aktualisiert")
        
        except Exception as e:
            logger.error(f"Fehler beim Aktualisieren von {module_path}: {e}")
            success = False
    
    return success

def fix_sqlalchemy_jsonb() -> bool:
    """Behebt das Problem mit SQLAlchemy JSONB."""
    try:
        # Prüfe SQLAlchemy-Version
        import sqlalchemy
        logger.info(f"SQLAlchemy-Version: {sqlalchemy.__version__}")
        
        # SQLAlchemy 2.0+ hat JSONB in sqlalchemy.types
        major_version = int(sqlalchemy.__version__.split('.')[0])
        
        if major_version >= 2:
            # Erstelle ein Patch-Modul
            patch_file = BACKEND_DIR / "db" / "sqlalchemy_patch.py"
            
            with open(patch_file, "w", encoding="utf-8") as f:
                f.write("""\"\"\"
SQLAlchemy-Patch für JSONB-Kompatibilität.

Dieses Modul bietet eine einheitliche Schnittstelle für JSONB in verschiedenen SQLAlchemy-Versionen.
\"\"\"

from sqlalchemy.types import JSON

# Für Kompatibilität mit Code, der sqlalchemy.JSONB erwartet
# Verwende JSON-Typ von SQLAlchemy 2.0+ als Ersatz für JSONB
JSONB = JSON

# Exportiere JSON explizit, da es auch in importierenden Modulen benötigt werden könnte
__all__ = ['JSONB', 'JSON']
""")
            
            # Aktualisiere __init__.py, um den Patch zu importieren
            init_file = BACKEND_DIR / "db" / "__init__.py"
            
            if not init_file.exists():
                with open(init_file, "w", encoding="utf-8") as f:
                    f.write("""\"\"\"
Datenbankmodul.
\"\"\"

from .sqlalchemy_patch import JSONB, JSON
""")
            else:
                # Prüfe, ob der Import bereits vorhanden ist
                with open(init_file, "r", encoding="utf-8") as f:
                    content = f.read()
                
                if "from .sqlalchemy_patch import JSONB" not in content:
                    with open(init_file, "a", encoding="utf-8") as f:
                        f.write("\n\n# Importiere JSONB-Patch für SQLAlchemy 2.0+ Kompatibilität\nfrom .sqlalchemy_patch import JSONB, JSON\n")
            
            logger.info("SQLAlchemy JSONB-Patch erfolgreich erstellt")
            return True
        else:
            logger.warning(f"SQLAlchemy {sqlalchemy.__version__} ist möglicherweise nicht kompatibel mit JSONB. Version 2.0+ wird empfohlen.")
            return False
    
    except ImportError:
        logger.error("SQLAlchemy ist nicht installiert")
        return False
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des SQLAlchemy-Patches: {e}")
        return False

def main():
    """Hauptfunktion."""
    logger.info("Starte Abhängigkeiten-Reparatur...")
    
    if not check_python_version():
        logger.error("Python-Version ist nicht kompatibel, breche ab")
        sys.exit(1)
    
    packages_to_update = check_package_versions()
    
    if packages_to_update:
        if not update_packages(packages_to_update):
            logger.warning("Einige Pakete konnten nicht aktualisiert werden")
    
    # SQLAlchemy JSONB-Problem beheben
    if not fix_sqlalchemy_jsonb():
        logger.warning("SQLAlchemy JSONB-Problem konnte nicht behoben werden")
    
    # Fehlende Module erstellen
    if not create_missing_modules():
        logger.warning("Einige fehlende Module konnten nicht erstellt werden")
    
    # Fehlende Klassen erstellen
    if not create_missing_classes():
        logger.warning("Einige fehlende Klassen konnten nicht erstellt werden")
    
    logger.info("Abhängigkeiten-Reparatur abgeschlossen")

if __name__ == "__main__":
    main() 