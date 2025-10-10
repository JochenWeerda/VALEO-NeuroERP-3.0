"""
Archive Service
Versionierte Archivierung von Belegen mit SHA-256 Integrität-Check
"""

from __future__ import annotations
import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ArchiveService:
    """Archivierungs-Service für Belege"""

    def __init__(self, base_path: str = "data/archives"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.base_path / "index.json"
        self._load_index()

    def _load_index(self):
        """Lädt Archiv-Index"""
        if self.index_file.exists():
            with open(self.index_file, "r") as f:
                self.index = json.load(f)
        else:
            self.index = {}

    def _save_index(self):
        """Speichert Archiv-Index"""
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)

    def archive(
        self, domain: str, doc_id: str, file_path: str, user: str = "system"
    ) -> Dict[str, Any]:
        """
        Archiviert Dokument mit Hash-Signatur

        Args:
            domain: Belegtyp (z.B. "sales_order")
            doc_id: Beleg-ID
            file_path: Pfad zur PDF-Datei
            user: User der archiviert hat

        Returns:
            Archive-Metadaten
        """
        # Hash berechnen
        with open(file_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()

        # Archiv-Pfad
        year = datetime.now().year
        archive_dir = self.base_path / domain / str(year)
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Datei kopieren
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = archive_dir / f"{doc_id}_{timestamp}.pdf"
        shutil.copy(file_path, archive_path)

        # Index aktualisieren
        if doc_id not in self.index:
            self.index[doc_id] = []

        entry = {
            "timestamp": datetime.now().isoformat(),
            "ts": int(datetime.now().timestamp()),
            "user": user,
            "path": str(archive_path),
            "sha256": file_hash,
            "domain": domain,
        }
        self.index[doc_id].append(entry)
        self._save_index()

        logger.info(f"Archived document: {doc_id} → {archive_path}")
        return entry

    def get_history(self, doc_id: str) -> List[Dict[str, Any]]:
        """
        Holt Archiv-Historie für Beleg

        Args:
            doc_id: Beleg-ID

        Returns:
            Liste von Archiv-Einträgen
        """
        return self.index.get(doc_id, [])

    def verify_integrity(self, doc_id: str, archive_path: str) -> bool:
        """
        Verifiziert Integrität einer archivierten Datei

        Args:
            doc_id: Beleg-ID
            archive_path: Pfad zur archivierten Datei

        Returns:
            True wenn Hash übereinstimmt
        """
        history = self.get_history(doc_id)
        entry = next((e for e in history if e["path"] == archive_path), None)

        if not entry:
            return False

        # Hash neu berechnen
        with open(archive_path, "rb") as f:
            current_hash = hashlib.sha256(f.read()).hexdigest()

        return current_hash == entry["sha256"]


# Global Archive Instance
archive = ArchiveService()

