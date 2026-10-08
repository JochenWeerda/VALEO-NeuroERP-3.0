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
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def sha256_hex(content: bytes) -> str:
    """SHA256-Hash des Inhalts als Hex-String (64 Zeichen)."""
    return hashlib.sha256(content).hexdigest()


class GobdArtifactError(RuntimeError):
    """Das Belegartefakt liess sich nicht archivieren; der Vorgang gilt als gescheitert."""


def register_artifact(
    db: Session,
    tenant_id: str,
    doc_number: str,
    artifact_type: str,
    content_hash_sha256: str,
    storage_key: str,
    file_name: Optional[str] = None,
    created_by: Optional[str] = None,
    *,
    doc_type: str,
    content: Optional[bytes] = None,
) -> str:
    """
    Belegartefakt in domain_docflow.document_artifacts eintragen (GoBD).

    Das Artefakt haengt an einem Belegkopf (``document_headers``, eindeutig je
    Mandant, Belegart und Belegnummer); fehlt der Kopf, wird er angelegt. Mit
    ``content`` liegt der Inhalt selbst im Archiv (PostgreSQL, gegen Aendern und
    Loeschen geschuetzt) und ``storage_key`` zeigt darauf; der Hash muss passen.

    Laeuft in der Transaktion des Aufrufers: kein Commit, kein Rollback. Der
    Aufrufer committet Beleg und Archiveintrag gemeinsam; scheitert der Eintrag,
    scheitert der Vorgang (:class:`GobdArtifactError`).

    Bis 07.10.2026 committete diese Funktion selbst — und schrieb damit die halbe
    Arbeit des Aufrufers fest —, trug die **Belegnummer** als ``header_id`` ein
    (der Fremdschluessel auf ``document_headers`` liess jeden Eintrag scheitern),
    rollte dann **die Transaktion des Aufrufers** zurueck, gab ``None`` zurueck und
    protokollierte eine Warnung. Kein Aufrufer pruefte das: Archiviert wurde nie,
    und eine Rechnung galt als gebucht, deren Buchung verworfen war.

    Returns:
        Artifact-ID
    """
    if artifact_type not in ("pdf", "xml", "html", "other"):
        artifact_type = "other"
    if content is not None and sha256_hex(content) != content_hash_sha256:
        raise GobdArtifactError(f"Belegartefakt {doc_number}: Hash passt nicht zum Inhalt")
    art_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_docflow.document_headers
                    (id, tenant_id, doc_type, doc_number, status, source_system, currency)
                VALUES (:id, :tenant_id, :doc_type, :doc_number, 'completed', 'gobd_artifact', 'EUR')
                ON CONFLICT (tenant_id, doc_type, doc_number) DO NOTHING
                """
            ),
            {"id": str(uuid4()), "tenant_id": tenant_id, "doc_type": doc_type, "doc_number": doc_number},
        )
        header_id = db.execute(
            text(
                "SELECT id FROM domain_docflow.document_headers "
                "WHERE tenant_id = :tenant_id AND doc_type = :doc_type AND doc_number = :doc_number"
            ),
            {"tenant_id": tenant_id, "doc_type": doc_type, "doc_number": doc_number},
        ).scalar_one()
        version = db.execute(
            text(
                "SELECT COALESCE(MAX(version), 0) + 1 FROM domain_docflow.document_artifacts "
                "WHERE tenant_id = :tenant_id AND header_id = :header_id AND artifact_type = :artifact_type"
            ),
            {"tenant_id": tenant_id, "header_id": header_id, "artifact_type": artifact_type},
        ).scalar_one()
        db.execute(
            text(
                """
                INSERT INTO domain_docflow.document_artifacts
                (id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key, file_name,
                 created_at, created_by, version, freigabe_status, content_bytes)
                VALUES (:id, :tenant_id, :header_id, :artifact_type, :content_hash_sha256, :storage_key,
                        :file_name, NOW(), :created_by, :version, :status, :content)
                """
            ),
            {
                "id": art_id,
                "tenant_id": tenant_id,
                "header_id": header_id,
                "artifact_type": artifact_type,
                "content_hash_sha256": content_hash_sha256,
                "storage_key": f"postgresql:document_artifacts:{art_id}" if content is not None else storage_key,
                "file_name": file_name,
                "created_by": created_by,
                "version": version,
                "status": "archiviert" if content is not None else "entwurf",
                "content": content,
            },
        )
    except SQLAlchemyError as e:
        logger.error("GoBD artifact registration failed: %s", e)
        raise GobdArtifactError(f"Belegartefakt {doc_number} nicht archiviert: {e}") from e
    return art_id
