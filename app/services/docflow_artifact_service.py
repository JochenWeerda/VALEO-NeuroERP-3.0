"""Artefakt-Upload, Versionierung & Freigabe (DOM-DOC-004.2).

Schreibt revisionssichere Artefakte in domain_docflow.document_artifacts: Upload mit
SHA-256-Hash über den Inhalt, laufende Versionierung je Header/Artefakttyp und
Freigabe-Status-Transitions (entwurf→freigegeben→archiviert). Ergänzt den read-only
Nachweis-Spine (004.1) um die Schreibseite.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

_DEFAULT_TENANT = "00000000-0000-0000-0000-000000000001"

# Erlaubte Artefakttypen (DB-CHECK chk_doc_artifact_type).
_ALLOWED_TYPES = {"pdf", "xml", "html", "other"}

# Erlaubte Freigabe-Übergänge.
_TRANSITIONS = {
    "entwurf": {"freigegeben"},
    "freigegeben": {"archiviert"},
    "archiviert": set(),
}


def next_version(existing_versions: list[int]) -> int:
    """Nächste Versionsnummer (max + 1, beginnend bei 1)."""
    return (max(existing_versions) + 1) if existing_versions else 1


def valid_transition(from_status: str, to_status: str) -> bool:
    """Reine Prüfung eines Freigabe-Übergangs."""
    return to_status in _TRANSITIONS.get((from_status or "entwurf").lower(), set())


def sha256_hex(content: str) -> str:
    return hashlib.sha256((content or "").encode("utf-8")).hexdigest()


class ArtifactError(Exception):
    """Fachlicher Fehler bei Artefakt-Aktionen (→ HTTP 422)."""


class DocflowArtifactService:
    def __init__(self, db: Session, tenant_id: Optional[str] = None) -> None:
        self.db = db
        self.tenant_id = tenant_id or _DEFAULT_TENANT

    def _header(self, doc: str) -> Optional[dict]:
        r = self.db.execute(
            text("SELECT id, doc_number FROM domain_docflow.document_headers "
                 "WHERE tenant_id = :t AND (id::text = :v OR doc_number = :v) AND deleted_at IS NULL LIMIT 1"),
            {"t": self.tenant_id, "v": doc},
        ).mappings().first()
        return dict(r) if r else None

    def upload_artifact(self, doc: str, file_name: str, content: str, artifact_type: str = "pdf",
                        storage_key: Optional[str] = None, bediener: str = "KIM") -> dict[str, Any]:
        header = self._header(doc)
        if not header:
            raise ArtifactError(f"Dokument nicht gefunden: {doc}")
        if not (file_name or "").strip():
            raise ArtifactError("Dateiname ist erforderlich.")
        if content is None or content == "":
            raise ArtifactError("Artefakt-Inhalt ist erforderlich (für SHA-256).")
        if (artifact_type or "").lower() not in _ALLOWED_TYPES:
            raise ArtifactError(f"Artefakttyp muss eines von {sorted(_ALLOWED_TYPES)} sein.")
        existing = self.db.execute(
            text("SELECT COALESCE(version,1) AS v FROM domain_docflow.document_artifacts "
                 "WHERE header_id = :h AND tenant_id = :t AND artifact_type = :at"),
            {"h": header["id"], "t": self.tenant_id, "at": artifact_type},
        ).mappings().all()
        version = next_version([int(r["v"]) for r in existing])
        digest = sha256_hex(content)
        skey = storage_key or f"docflow/{header['id']}/{artifact_type}/v{version}/{uuid.uuid4().hex}"
        aid = str(uuid.uuid4())
        self.db.execute(
            text("INSERT INTO domain_docflow.document_artifacts "
                 "(id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key, "
                 "file_name, version, freigabe_status, created_by) "
                 "VALUES (:id, :t, :h, :at, :hash, :sk, :fn, :v, 'entwurf', :by)"),
            {"id": aid, "t": self.tenant_id, "h": header["id"], "at": artifact_type, "hash": digest,
             "sk": skey, "fn": file_name, "v": version, "by": bediener},
        )
        self.db.commit()
        return {"ok": True, "artifact_id": aid, "doc_number": header["doc_number"],
                "version": version, "sha256": digest, "freigabe_status": "entwurf"}

    def set_freigabe(self, artifact_id: str, ziel_status: str, bediener: str = "KIM") -> dict[str, Any]:
        r = self.db.execute(
            text("SELECT id, COALESCE(freigabe_status,'entwurf') AS st FROM domain_docflow.document_artifacts "
                 "WHERE id::text = :id AND tenant_id = :t LIMIT 1"),
            {"id": artifact_id, "t": self.tenant_id},
        ).mappings().first()
        if not r:
            raise ArtifactError(f"Artefakt nicht gefunden: {artifact_id}")
        ziel = (ziel_status or "").lower()
        if ziel not in ("freigegeben", "archiviert"):
            raise ArtifactError("Zielstatus muss 'freigegeben' oder 'archiviert' sein.")
        if not valid_transition(r["st"], ziel):
            raise ArtifactError(f"Unzulässiger Übergang {r['st']} → {ziel}.")
        freig = "freigegeben" if ziel == "freigegeben" else None
        self.db.execute(
            text("UPDATE domain_docflow.document_artifacts SET freigabe_status = :z, "
                 "freigegeben_at = CASE WHEN :z = 'freigegeben' THEN now() ELSE freigegeben_at END, "
                 "freigegeben_by = CASE WHEN :z = 'freigegeben' THEN :by ELSE freigegeben_by END "
                 "WHERE id = :id AND tenant_id = :t"),
            {"z": ziel, "by": bediener, "id": r["id"], "t": self.tenant_id, "freig": freig},
        )
        self.db.commit()
        return {"ok": True, "artifact_id": artifact_id, "freigabe_status": ziel}

    def list_artifacts(self, doc: str) -> dict[str, Any]:
        header = self._header(doc)
        if not header:
            return {"found": False, "detail": "Dokument nicht gefunden."}
        rows = self.db.execute(
            text("SELECT id, artifact_type, file_name, content_hash_sha256, COALESCE(version,1) AS version, "
                 "COALESCE(freigabe_status,'entwurf') AS freigabe_status, created_at, created_by, "
                 "freigegeben_at, freigegeben_by "
                 "FROM domain_docflow.document_artifacts WHERE header_id = :h AND tenant_id = :t "
                 "ORDER BY artifact_type, version"),
            {"h": header["id"], "t": self.tenant_id},
        ).mappings().all()
        # „Aktuell" = höchste Version je Artefakttyp.
        max_ver: dict[str, int] = {}
        for r in rows:
            max_ver[r["artifact_type"]] = max(max_ver.get(r["artifact_type"], 0), int(r["version"]))
        artifacts = [{
            "artifact_id": str(r["id"]), "artifact_type": r["artifact_type"], "file_name": r["file_name"],
            "sha256": r["content_hash_sha256"], "version": int(r["version"]),
            "aktuell": int(r["version"]) == max_ver.get(r["artifact_type"]),
            "freigabe_status": r["freigabe_status"],
            "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            "created_by": r["created_by"],
            "freigegeben_at": r["freigegeben_at"].isoformat() if r["freigegeben_at"] else None,
            "freigegeben_by": r["freigegeben_by"],
        } for r in rows]
        return {
            "found": True, "doc_number": header["doc_number"], "artifacts": artifacts,
            "summary": {
                "anzahl": len(artifacts),
                "freigegeben": sum(1 for a in artifacts if a["freigabe_status"] == "freigegeben"),
                "entwuerfe": sum(1 for a in artifacts if a["freigabe_status"] == "entwurf"),
            },
        }
