"""Persistent settlement PDF versions in the existing PostgreSQL Docflow archive."""
import hashlib
import re

from fastapi import HTTPException
from sqlalchemy import text

from app.core.uuid7 import uuid7


def archive_pdf(db, tenant_id, settlement, content: bytes, created_by=None):
    if not content.startswith(b"%PDF-"):
        raise ValueError("Archivinhalt ist kein PDF")
    source = db.execute(text("SELECT id FROM domain_inventory.agrar_settlements WHERE id = :id AND tenant_id = :tid FOR UPDATE"), {"id": str(settlement.id), "tid": tenant_id}).scalar()
    if not source:
        raise HTTPException(404, "Abrechnung nicht gefunden")
    number = str(settlement.settlement_number or settlement.id)
    filename = "abrechnung_" + re.sub(r"[^A-Za-z0-9_.-]", "_", number) + ".pdf"
    db.execute(text("""
        INSERT INTO domain_docflow.document_headers
            (id, tenant_id, doc_type, doc_number, status, source_system, source_ref, currency)
        VALUES (:id, :tid, 'agrar_settlement', :number, 'completed', 'domain_inventory.agrar_settlements', :source, 'EUR')
        ON CONFLICT (tenant_id, doc_type, doc_number) DO NOTHING
    """), {"id": str(uuid7()), "tid": tenant_id, "number": number, "source": str(settlement.id)})
    header = db.execute(text("""
        SELECT id, source_ref FROM domain_docflow.document_headers
        WHERE tenant_id = :tid AND doc_type = 'agrar_settlement' AND doc_number = :number
        FOR UPDATE
    """), {"tid": tenant_id, "number": number}).mappings().one()
    if header["source_ref"] != str(settlement.id):
        raise HTTPException(409, "Abrechnungsnummer gehoert zu einem anderen Beleg")
    version = db.execute(text("SELECT COALESCE(MAX(version), 0) + 1 FROM domain_docflow.document_artifacts WHERE tenant_id = :tid AND header_id = :header AND artifact_type = 'pdf'"), {"tid": tenant_id, "header": header["id"]}).scalar_one()
    artifact_id = str(uuid7())
    digest = hashlib.sha256(content).hexdigest()
    storage_key = "postgresql:document_artifacts:" + artifact_id
    db.execute(text("""
        INSERT INTO domain_docflow.document_artifacts
            (id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key,
             file_name, created_by, content_bytes, version, freigabe_status)
        VALUES (:id, :tid, :header, 'pdf', :hash, :key, :file, :actor, :content, :version, 'archiviert')
    """), {"id": artifact_id, "tid": tenant_id, "header": header["id"], "hash": digest,
             "key": storage_key, "file": filename, "actor": created_by, "content": content, "version": version})
    return {"artifact_id": artifact_id, "artifact_path": storage_key, "filename": filename,
            "sha256": digest, "size_bytes": len(content), "version": version,
            "content_type": "application/pdf", "pdf_bytes": content,
            "download_url": f"/api/v1/agrar/settlements/archive/{artifact_id}"}


def read_pdf(db, tenant_id, artifact_id):
    row = db.execute(text("""
        SELECT a.content_bytes, a.content_hash_sha256, a.file_name
        FROM domain_docflow.document_artifacts a
        JOIN domain_docflow.document_headers h ON h.id = a.header_id AND h.tenant_id = a.tenant_id
        WHERE a.id = :id AND a.tenant_id = :tid AND h.doc_type = 'agrar_settlement'
          AND a.artifact_type = 'pdf' AND a.content_bytes IS NOT NULL
    """), {"id": artifact_id, "tid": tenant_id}).mappings().first()
    if not row:
        raise HTTPException(404, "Archiviertes PDF nicht gefunden")
    content = bytes(row["content_bytes"])
    if hashlib.sha256(content).hexdigest() != row["content_hash_sha256"]:
        raise HTTPException(409, "Integritaetspruefung des archivierten PDFs fehlgeschlagen")
    return content, row["file_name"]
