"""
GoBD-Archiv: Hilfsfunktion zum Registrieren von Belegartefakten in domain_docflow.document_artifacts.
Wird von Rechnung, Mahnung, Export etc. aufgerufen, um jeden relevanten Beleg/Export zu archivieren.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Optional
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def sha256_hex(content: bytes) -> str:
    """SHA256-Hash des Inhalts als Hex-String (64 Zeichen)."""
    return hashlib.sha256(content).hexdigest()


def register_artifact(
    db: Session,
    tenant_id: str,
    header_id: str,
    artifact_type: str,
    content_hash_sha256: str,
    storage_key: str,
    file_name: Optional[str] = None,
    created_by: Optional[str] = None,
) -> Optional[str]:
    """
    Belegartefakt in domain_docflow.document_artifacts eintragen (GoBD).

    Args:
        db: SQLAlchemy Session
        tenant_id: Mandanten-ID
        header_id: Referenz auf Beleg/Export (z. B. Rechnungs-ID, Export-Id)
        artifact_type: pdf | xml | html | other
        content_hash_sha256: 64 Zeichen Hex (SHA256 des Inhalts)
        storage_key: Speicherort/Key (z. B. export/asc/...)
        file_name: Optional Dateiname
        created_by: Optional Benutzer

    Returns:
        Artifact-ID oder None bei Fehler
    """
    if artifact_type not in ("pdf", "xml", "html", "other"):
        artifact_type = "other"
    art_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_docflow.document_artifacts
                (id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key, file_name, created_at, created_by)
                VALUES (:id, :tenant_id, :header_id, :artifact_type, :content_hash_sha256, :storage_key, :file_name, NOW(), :created_by)
                """
            ),
            {
                "id": art_id,
                "tenant_id": tenant_id,
                "header_id": header_id,
                "artifact_type": artifact_type,
                "content_hash_sha256": content_hash_sha256,
                "storage_key": storage_key,
                "file_name": file_name,
                "created_by": created_by,
            },
        )
        db.commit()
        return art_id
    except Exception as e:
        logger.warning("GoBD artifact registration failed: %s", e)
        db.rollback()
        return None
