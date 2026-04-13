#!/usr/bin/env python
"""
Vereinfachte Version des Skripts zum Aktivieren des REFLECT-ARCHIVE-Mode und Befuellen der MongoDB.
"""

from __future__ import annotations

import datetime
import logging
import sys
from dataclasses import dataclass
from pathlib import Path

import pymongo
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("simple_activate_reflect_archive.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("SimpleActivateReflectArchive")


MONGODB_CONNECTION_STRING = "mongodb://localhost:27017/"
MONGODB_DATABASE_NAME = "valeo_neuroerp"
SOURCE_DIR = "C:/AI_driven_ERP"


@dataclass(frozen=True)
class ArchiveTextFileSpec:
    path: Path
    required: bool = True


class ReflectArchiveSourceError(RuntimeError):
    pass


def read_archive_text_file(file_path: Path) -> str:
    if not file_path.exists():
        raise ReflectArchiveSourceError(f"Datei nicht gefunden: {file_path}")

    content_bytes = file_path.read_bytes()
    if b"\x00" in content_bytes:
        raise ReflectArchiveSourceError(f"Datei enthaelt Null-Bytes: {file_path}")

    try:
        return content_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return content_bytes.decode("latin-1")
        except UnicodeDecodeError as exc:
            raise ReflectArchiveSourceError(f"Datei konnte nicht dekodiert werden: {file_path}") from exc


def load_archive_documents(
    collection,
    specs: list[ArchiveTextFileSpec],
    *,
    collection_name: str,
) -> int:
    inserted = 0
    for spec in specs:
        if not spec.path.exists():
            if spec.required:
                raise ReflectArchiveSourceError(f"Pflichtdatei fehlt in {collection_name}: {spec.path}")
            continue

        content = read_archive_text_file(spec.path)
        collection.insert_one(
            {
                "filename": spec.path.name,
                "path": str(spec.path),
                "content": content,
                "last_modified": datetime.datetime.fromtimestamp(spec.path.stat().st_mtime),
                "timestamp": datetime.datetime.now(),
            }
        )
        inserted += 1
        logger.info("%s erfolgreich geladen.", spec.path.name)

    if inserted == 0:
        raise ReflectArchiveSourceError(f"Keine Dateien fuer {collection_name} geladen.")
    return inserted


def check_mongodb_connection():
    """
    Ueberprueft die Verbindung zur MongoDB.

    Returns:
        bool: True, wenn die Verbindung erfolgreich hergestellt wurde, sonst False
    """
    try:
        logger.info("Verbindung zu MongoDB wird hergestellt...")
        client = pymongo.MongoClient(
            MONGODB_CONNECTION_STRING,
            serverSelectionTimeoutMS=5000,
        )
        client.admin.command("ping")
        logger.info("Verbindung zu MongoDB erfolgreich hergestellt.")
        client.close()
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as exc:
        logger.error("Verbindung zu MongoDB fehlgeschlagen: %s", str(exc))
        return False


def activate_reflect_archive_mode():
    logger.info("Aktiviere REFLECT-ARCHIVE-Mode...")

    try:
        mode_file_path = Path("memory-bank") / "current_mode.txt"
        mode_file_path.parent.mkdir(exist_ok=True)
        mode_file_path.write_text("REFLECT-ARCHIVE", encoding="utf-8")

        logger.info("REFLECT-ARCHIVE-Mode erfolgreich aktiviert.")
        return True
    except Exception as exc:
        logger.error("Fehler beim Aktivieren des REFLECT-ARCHIVE-Mode: %s", exc)
        return False


def create_reflection_document():
    logger.info("Erstelle Reflexionsdokument...")

    try:
        reflection_file_path = Path("memory-bank") / "reflection" / "reflection_ai_driven_erp.md"
        reflection_file_path.parent.mkdir(exist_ok=True)

        content = """# Reflexion: AI_driven_ERP-Projekt

## Projektuebersicht
Das AI_driven_ERP-Projekt ist ein KI-gestuetztes ERP-System mit Fokus auf Stammdatenpflege. Es orientiert sich am Design und der Funktionalitaet von ORB-FMS, einem gemeinnuetzigen Farm-Management-System.

## Hauptkomponenten
- Backend: FastAPI-basiertes Backend mit Mikroservice-Architektur
- Frontend: React-basiertes Frontend im ORB-FMS-Design
- Datenmodelle: Optimierte Modelle fuer Partner, Artikel, Lager und Finanzen

## Erkenntnisse
- Die Projektstruktur folgt einer klaren Trennung von Backend und Frontend
- Das Backend nutzt FastAPI fuer eine performante API-Entwicklung
- Das Frontend basiert auf React und implementiert verschiedene Themes
- Es gibt eine umfangreiche Aufgabenliste mit verschiedenen Komplexitaetsstufen

## Naechste Schritte
1. Vervollstaendigung der Dashboard-Implementierung fuer VALERO Enterprise Suite
2. Entwicklung der Modelle fuer die Geschaeftslogik
3. Integration der Module mit bestehenden Community ERP-Funktionen
4. Testen der Module unter realen Bedingungen

## Archivierte Artefakte
- Projektstruktur
- Code-Dateien
- Dokumentation
- Aufgaben
- Kontext

Datum: {datetime}
"""
        content = content.replace("{datetime}", datetime.datetime.now().strftime("%d.%m.%Y %H:%M"))
        reflection_file_path.write_text(content, encoding="utf-8")

        logger.info("Reflexionsdokument erfolgreich erstellt: %s", reflection_file_path)
        return True
    except Exception as exc:
        logger.error("Fehler beim Erstellen des Reflexionsdokuments: %s", exc)
        return False


def load_project_structure():
    logger.info("Lade Projektstruktur in MongoDB...")

    try:
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["project_structure"]
        collection.delete_many({})

        source_dir = Path(SOURCE_DIR)
        structure = {
            "name": source_dir.name,
            "type": "directory",
            "path": str(source_dir),
            "children": [],
        }

        for item in source_dir.iterdir():
            if item.is_dir():
                if item.name.startswith(".") or item.name in {"node_modules", "venv"}:
                    continue
                structure["children"].append(
                    {
                        "name": item.name,
                        "type": "directory",
                        "path": str(item),
                        "has_children": any(True for _ in item.iterdir()),
                    }
                )
            else:
                structure["children"].append(
                    {
                        "name": item.name,
                        "type": "file",
                        "path": str(item),
                        "extension": item.suffix,
                        "size": item.stat().st_size,
                    }
                )

        collection.insert_one(
            {
                "timestamp": datetime.datetime.now(),
                "structure": structure,
            }
        )

        logger.info("Projektstruktur erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as exc:
        logger.error("Fehler beim Laden der Projektstruktur: %s", str(exc))
        return False


def load_tasks():
    logger.info("Lade Aufgaben in MongoDB...")

    try:
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["tasks"]
        collection.delete_many({})

        source_dir = Path(SOURCE_DIR)
        specs = [
            ArchiveTextFileSpec(source_dir / "memory-bank" / "tasks.md", required=True),
            ArchiveTextFileSpec(source_dir / "memory-bank" / "tasks-new.md", required=False),
        ]
        load_archive_documents(collection, specs, collection_name="tasks")

        logger.info("Aufgaben erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as exc:
        logger.error("Fehler beim Laden der Aufgaben: %s", str(exc))
        return False


def load_context():
    logger.info("Lade Kontext in MongoDB...")

    try:
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["context"]
        collection.delete_many({})

        source_dir = Path(SOURCE_DIR)
        specs = [
            ArchiveTextFileSpec(source_dir / "memory-bank" / "activeContext.md", required=True),
            ArchiveTextFileSpec(source_dir / "memory-bank" / "progress.md", required=True),
        ]
        load_archive_documents(collection, specs, collection_name="context")

        logger.info("Kontext erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as exc:
        logger.error("Fehler beim Laden des Kontexts: %s", str(exc))
        return False


def load_readme():
    logger.info("Lade README.md in MongoDB...")

    try:
        client = pymongo.MongoClient(MONGODB_CONNECTION_STRING)
        db = client[MONGODB_DATABASE_NAME]
        collection = db["documentation"]
        collection.delete_many({})

        source_dir = Path(SOURCE_DIR)
        specs = [ArchiveTextFileSpec(source_dir / "README.md", required=True)]
        load_archive_documents(collection, specs, collection_name="documentation")

        logger.info("README.md erfolgreich in MongoDB geladen.")
        client.close()
        return True
    except Exception as exc:
        logger.error("Fehler beim Laden der README.md: %s", str(exc))
        return False


def main():
    if not check_mongodb_connection():
        logger.error("Konnte keine Verbindung zur MongoDB herstellen.")
        return 1

    if not activate_reflect_archive_mode():
        logger.error("Konnte REFLECT-ARCHIVE-Mode nicht aktivieren.")
        return 1

    if not create_reflection_document():
        logger.error("Konnte Reflexionsdokument nicht erstellen.")
        return 1

    success = True

    if not load_project_structure():
        logger.error("Konnte Projektstruktur nicht laden.")
        success = False

    if not load_tasks():
        logger.error("Konnte Aufgaben nicht laden.")
        success = False

    if not load_context():
        logger.error("Konnte Kontext nicht laden.")
        success = False

    if not load_readme():
        logger.error("Konnte README.md nicht laden.")
        success = False

    if success:
        logger.info("REFLECT-ARCHIVE-Mode erfolgreich aktiviert und MongoDB mit Daten befuellt.")
        return 0

    logger.error("Es sind Fehler aufgetreten. Siehe Log fuer Details.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

