"""GoBD: Archiv (document_artifacts), E-Rechnung XML, Audit-Package Export (Z1/Z2/Z3)."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import zipfile
from datetime import date, datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.gobd_archiv_schemas import GobdArchivOut


router = APIRouter(prefix="/gobd", tags=["GoBD", "Archiv"])
DEFAULT_TENANT = settings.DEFAULT_TENANT_ID


# ---------- Document Artifacts (Archiv mit Content-Hash) ----------

@router.post("/artifacts", response_model=DocumentArtifactOut, summary="Document artifact registrieren")
async def register_document_artifact(
    payload: DocumentArtifactCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Belegartefakt registrieren (PDF/XML) mit Content-Hash für GoBD-Aufbewahrung."""
    from fastapi.responses import JSONResponse

    from app.core.blockchain_anchor_runtime import anchor_document_artifact

    effective_tenant = tenant_id or DEFAULT_TENANT
    art_id = str(uuid4())
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
            "tenant_id": effective_tenant,
            "header_id": payload.header_id,
            "artifact_type": payload.artifact_type,
            "content_hash_sha256": payload.content_hash_sha256,
            "storage_key": payload.storage_key,
            "file_name": payload.file_name,
            "created_by": payload.created_by,
        },
    )
    db.commit()
    row = db.execute(
        text(
            "SELECT id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key, file_name, created_at, created_by "
            "FROM domain_docflow.document_artifacts WHERE id = :id"
        ),
        {"id": art_id},
    ).mappings().first()
    r = dict(row)
    body = DocumentArtifactOut(
        id=r["id"],
        tenant_id=r["tenant_id"],
        header_id=r["header_id"],
        artifact_type=r["artifact_type"],
        content_hash_sha256=r["content_hash_sha256"],
        storage_key=r["storage_key"],
        file_name=r.get("file_name"),
        created_at=r["created_at"],
        created_by=r.get("created_by"),
    ).model_dump(mode="json")
    body["blockchain_anchor"] = anchor_document_artifact(
        db,
        tenant_id=effective_tenant,
        artifact_id=art_id,
        header_id=payload.header_id,
        artifact_type=payload.artifact_type,
        content_hash_sha256=payload.content_hash_sha256,
        storage_key=payload.storage_key,
        file_name=payload.file_name,
        created_by=payload.created_by,
    ).as_dict()
    return JSONResponse(content=body)


@router.get("/artifacts", response_model=list[DocumentArtifactOut], summary="Document artifacts auflisten")
async def list_document_artifacts(
    header_id: Optional[str] = Query(None),
    tenant_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Artifacts nach header_id oder Tenant auflisten."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    if header_id:
        rows = db.execute(
            text(
                "SELECT id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key, file_name, created_at, created_by "
                "FROM domain_docflow.document_artifacts WHERE tenant_id = :tenant_id AND header_id = :header_id ORDER BY created_at DESC"
            ),
            {"tenant_id": effective_tenant, "header_id": header_id},
        ).mappings().all()
    else:
        rows = db.execute(
            text(
                "SELECT id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key, file_name, created_at, created_by "
                "FROM domain_docflow.document_artifacts WHERE tenant_id = :tenant_id ORDER BY created_at DESC LIMIT :limit"
            ),
            {"tenant_id": effective_tenant, "limit": limit},
        ).mappings().all()
    return [
        DocumentArtifactOut(
            id=r["id"],
            tenant_id=r["tenant_id"],
            header_id=r["header_id"],
            artifact_type=r["artifact_type"],
            content_hash_sha256=r["content_hash_sha256"],
            storage_key=r["storage_key"],
            file_name=r.get("file_name"),
            created_at=r["created_at"],
            created_by=r.get("created_by"),
        )
        for r in rows
    ]

@router.get("/artifacts/{art_id}/veri4", response_model=Optional[ArtifactVeri4Out], summary="Artifact veri4 abrufen")
async def get_artifact_veri4(
    art_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Integritätsprüfung: Liefert Artifact-Metadaten (Hash, storage_key) für Verifikation (z. B. Veri4)."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    row = db.execute(
        text(
            "SELECT id, tenant_id, header_id, artifact_type, content_hash_sha256, storage_key, file_name "
            "FROM domain_docflow.document_artifacts WHERE id = :id AND tenant_id = :tenant_id"
        ),
        {"id": art_id, "tenant_id": effective_tenant},
    ).mappings().first()
    if not row:
        return None
    r = dict(row)
    return ArtifactVeri4Out(
        id=r["id"],
        header_id=r["header_id"],
        artifact_type=r["artifact_type"],
        content_hash_sha256=r["content_hash_sha256"],
        storage_key=r["storage_key"],
        file_name=r.get("file_name"),
    )


# ---------- E-Rechnung XML (führendes Original) ----------

@router.post("/e-invoice-xml", response_model=InvoiceXmlOut, summary="Invoice xml store")
async def store_invoice_xml(
    payload: InvoiceXmlCreate,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """E-Rechnung XML als führendes Original speichern (XRechnung/ZUGFeRD)."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    rec_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_docflow.invoice_xml_store
            (id, tenant_id, header_id, content_hash_sha256, storage_key, format_type, validation_status, created_at, created_by)
            VALUES (:id, :tenant_id, :header_id, :content_hash_sha256, :storage_key, :format_type, 'pending', NOW(), :created_by)
            ON CONFLICT ON CONSTRAINT uq_invoice_xml_header
            DO UPDATE SET content_hash_sha256 = EXCLUDED.content_hash_sha256, storage_key = EXCLUDED.storage_key,
                          format_type = EXCLUDED.format_type, validation_status = 'pending', validation_errors = NULL
            """
        ),
        {
            "id": rec_id,
            "tenant_id": effective_tenant,
            "header_id": payload.header_id,
            "content_hash_sha256": payload.content_hash_sha256,
            "storage_key": payload.storage_key,
            "format_type": payload.format_type,
            "created_by": payload.created_by,
        },
    )
    db.commit()
    row = db.execute(
        text(
            "SELECT id, tenant_id, header_id, content_hash_sha256, storage_key, format_type, validation_status, validation_errors, created_at, created_by "
            "FROM domain_docflow.invoice_xml_store WHERE header_id = :header_id AND tenant_id = :tenant_id"
        ),
        {"header_id": payload.header_id, "tenant_id": effective_tenant},
    ).mappings().first()
    if not row:
        row = db.execute(
            text("SELECT id, tenant_id, header_id, content_hash_sha256, storage_key, format_type, validation_status, validation_errors, created_at, created_by FROM domain_docflow.invoice_xml_store WHERE id = :id"),
            {"id": rec_id},
        ).mappings().first()
    r = dict(row)
    return InvoiceXmlOut(
        id=r["id"],
        tenant_id=r["tenant_id"],
        header_id=r["header_id"],
        content_hash_sha256=r["content_hash_sha256"],
        storage_key=r["storage_key"],
        format_type=r["format_type"],
        validation_status=r["validation_status"],
        validation_errors=r.get("validation_errors"),
        created_at=r["created_at"],
        created_by=r.get("created_by"),
    )


@router.get("/e-invoice-xml/{header_id}", response_model=Optional[InvoiceXmlOut], summary="Invoice xml abrufen")
async def get_invoice_xml(
    header_id: str,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """E-Rechnung XML-Metadaten zu einem Docflow-Header abrufen."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    row = db.execute(
        text(
            "SELECT id, tenant_id, header_id, content_hash_sha256, storage_key, format_type, validation_status, validation_errors, created_at, created_by "
            "FROM domain_docflow.invoice_xml_store WHERE tenant_id = :tenant_id AND header_id = :header_id"
        ),
        {"tenant_id": effective_tenant, "header_id": header_id},
    ).mappings().first()
    if not row:
        return None
    r = dict(row)
    return InvoiceXmlOut(
        id=r["id"],
        tenant_id=r["tenant_id"],
        header_id=r["header_id"],
        content_hash_sha256=r["content_hash_sha256"],
        storage_key=r["storage_key"],
        format_type=r["format_type"],
        validation_status=r["validation_status"],
        validation_errors=r.get("validation_errors"),
        created_at=r["created_at"],
        created_by=r.get("created_by"),
    )


# ---------- Audit-Package Export (Z1/Z2/Z3) ----------


def _export_docflow_headers_csv(db: Session, tenant_id: str, from_date: Optional[date], to_date: Optional[date]) -> str:
    conditions = ["tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if from_date:
        conditions.append("document_date::date >= :from_date")
        params["from_date"] = from_date
    if to_date:
        conditions.append("document_date::date <= :to_date")
        params["to_date"] = to_date
    rows = db.execute(
        text(
            f"""
            SELECT id, tenant_id, doc_type, doc_number, status, source_system, customer_id, supplier_id, currency,
                   total_net, total_tax, total_gross, document_date, posting_date, version, created_at, updated_at
            FROM domain_docflow.document_headers
            WHERE {" AND ".join(conditions)}
            ORDER BY document_date, created_at
            """
        ),
        params,
    ).mappings().all()
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["id", "tenant_id", "doc_type", "doc_number", "status", "source_system", "customer_id", "supplier_id", "currency", "total_net", "total_tax", "total_gross", "document_date", "posting_date", "version", "created_at", "updated_at"])
    for r in rows:
        w.writerow([r.get(k) for k in ["id", "tenant_id", "doc_type", "doc_number", "status", "source_system", "customer_id", "supplier_id", "currency", "total_net", "total_tax", "total_gross", "document_date", "posting_date", "version", "created_at", "updated_at"]])
    return buf.getvalue()


def _export_audit_log_csv(
    db: Session,
    tenant_id: Optional[str],
    from_date: Optional[date],
    to_date: Optional[date],
) -> str:
    conditions = ["1=1"]
    params: dict[str, Any] = {}
    if tenant_id:
        conditions.append("tenant_id = :tenant_id")
        params["tenant_id"] = tenant_id
    if from_date:
        conditions.append("created_at::date >= :from_date")
        params["from_date"] = from_date
    if to_date:
        conditions.append("created_at::date <= :to_date")
        params["to_date"] = to_date
    try:
        rows = db.execute(
            text(
                f"""
                SELECT id, user_id, user_email, tenant_id, action, entity_type, entity_id,
                       old_values, new_values, created_at
                FROM domain_shared.audit_logs
                WHERE {" AND ".join(conditions)}
                ORDER BY created_at
                LIMIT 50000
                """
            ),
            params,
        ).mappings().all()
    except Exception:
        return "id;user_id;user_email;tenant_id;action;entity_type;entity_id;old_values;new_values;created_at\n"
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";")
    w.writerow(["id", "user_id", "user_email", "tenant_id", "action", "entity_type", "entity_id", "old_values", "new_values", "created_at"])
    for r in rows:
        old = r.get("old_values")
        new = r.get("new_values")
        w.writerow([
            r.get("id"),
            r.get("user_id"),
            r.get("user_email"),
            r.get("tenant_id"),
            r.get("action"),
            r.get("entity_type"),
            r.get("entity_id"),
            json.dumps(old) if old is not None else "",
            json.dumps(new) if new is not None else "",
            r.get("created_at"),
        ])
    return buf.getvalue()


def _export_journal_entries_csv(
    db: Session,
    tenant_id: str,
    from_date: Optional[date],
    to_date: Optional[date],
) -> str:
    conditions = ["tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if from_date:
        conditions.append("entry_date::date >= :from_date")
        params["from_date"] = from_date
    if to_date:
        conditions.append("entry_date::date <= :to_date")
        params["to_date"] = to_date
    try:
        rows = db.execute(
            text(
                f"""
                SELECT id, tenant_id, entry_number, entry_date, posting_date, description, reference, source,
                       status, total_debit, total_credit, posted_by, posted_at, created_at, updated_at
                FROM domain_erp.journal_entries
                WHERE {" AND ".join(conditions)}
                ORDER BY entry_date, created_at
                LIMIT 100000
                """
            ),
            params,
        ).mappings().all()
    except Exception:
        return "id;tenant_id;entry_number;entry_date;posting_date;description;reference;source;status;total_debit;total_credit;posted_by;posted_at;created_at;updated_at\n"
    buf = io.StringIO()
    cols = ["id", "tenant_id", "entry_number", "entry_date", "posting_date", "description", "reference", "source", "status", "total_debit", "total_credit", "posted_by", "posted_at", "created_at", "updated_at"]
    w = csv.writer(buf, delimiter=";")
    w.writerow(cols)
    for r in rows:
        w.writerow([r.get(k) for k in cols])
    return buf.getvalue()


def _export_docflow_items_csv(
    db: Session,
    tenant_id: str,
    from_date: Optional[date],
    to_date: Optional[date],
) -> str:
    conditions = ["di.tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if from_date:
        conditions.append("dh.document_date::date >= :from_date")
        params["from_date"] = from_date
    if to_date:
        conditions.append("dh.document_date::date <= :to_date")
        params["to_date"] = to_date
    try:
        rows = db.execute(
            text(
                f"""
                SELECT di.id, di.tenant_id, di.header_id, di.line_number, di.source_line_id, di.article_number,
                       di.description, di.quantity, di.unit, di.unit_price, di.discount_percent, di.tax_rate,
                       di.line_total_net, di.line_total_tax, di.line_total_gross, di.batch_id, di.charge,
                       di.created_at, di.updated_at
                FROM domain_docflow.document_items di
                JOIN domain_docflow.document_headers dh ON dh.id = di.header_id AND dh.tenant_id = di.tenant_id
                WHERE {" AND ".join(conditions)} AND dh.deleted_at IS NULL
                ORDER BY di.header_id, di.line_number
                LIMIT 200000
                """
            ),
            params,
        ).mappings().all()
    except Exception:
        return "id;tenant_id;header_id;line_number;article_number;quantity;unit;unit_price;line_total_net;line_total_tax;line_total_gross;created_at\n"
    buf = io.StringIO()
    cols = ["id", "tenant_id", "header_id", "line_number", "source_line_id", "article_number", "description", "quantity", "unit", "unit_price", "discount_percent", "tax_rate", "line_total_net", "line_total_tax", "line_total_gross", "batch_id", "charge", "created_at", "updated_at"]
    w = csv.writer(buf, delimiter=";")
    w.writerow(cols)
    for r in rows:
        w.writerow([r.get(k) for k in cols])
    return buf.getvalue()


def _export_artifact_hashes_csv(
    db: Session,
    tenant_id: str,
    from_date: Optional[date],
    to_date: Optional[date],
) -> str:
    conditions = ["a.tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if from_date:
        conditions.append("dh.document_date::date >= :from_date")
        params["from_date"] = from_date
    if to_date:
        conditions.append("dh.document_date::date <= :to_date")
        params["to_date"] = to_date
    try:
        rows = db.execute(
            text(
                f"""
                SELECT a.id, a.tenant_id, a.header_id, a.artifact_type, a.content_hash_sha256, a.storage_key, a.file_name, a.created_at
                FROM domain_docflow.document_artifacts a
                JOIN domain_docflow.document_headers dh ON dh.id = a.header_id AND dh.tenant_id = a.tenant_id
                WHERE {" AND ".join(conditions)} AND dh.deleted_at IS NULL
                ORDER BY a.created_at
                LIMIT 100000
                """
            ),
            params,
        ).mappings().all()
    except Exception:
        return "id;tenant_id;header_id;artifact_type;content_hash_sha256;storage_key;file_name;created_at\n"
    buf = io.StringIO()
    cols = ["id", "tenant_id", "header_id", "artifact_type", "content_hash_sha256", "storage_key", "file_name", "created_at"]
    w = csv.writer(buf, delimiter=";")
    w.writerow(cols)
    for r in rows:
        w.writerow([r.get(k) for k in cols])
    return buf.getvalue()


def _sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


@router.get("/audit-package", summary="Audit package abrufen",
    response_model=GobdArchivOut
)
async def get_audit_package(
    from_date: Optional[date] = Query(None, description="Von-Datum (inkl.)"),
    to_date: Optional[date] = Query(None, description="Bis-Datum (inkl.)"),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Betriebsprüfung: ZIP mit Z1/Z2/Z3-Struktur und Integrity-Manifest."""
    effective_tenant = tenant_id or DEFAULT_TENANT
    manifest_entries: list[tuple[str, str]] = []  # (path, sha256_hex)

    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # --- Z1: Stammdaten / Struktur ---
        data_dict = (
            "Z1 Stammdaten: docflow_headers (Belegköpfe), data_dictionary\n"
            "Z2 Bewegungsdaten: audit_logs, journal_entries, docflow_items\n"
            "Z3 Archiv: artifact_hashes (Content-Hashes der Belegartefakte)\n"
            f"Export: {datetime.now(timezone.utc).isoformat()}\n"
            f"Tenant: {effective_tenant}\n"
            f"Zeitraum: {from_date or 'unbegrenzt'} bis {to_date or 'unbegrenzt'}\n"
        )
        zf.writestr("Z1/data_dictionary.txt", data_dict.encode("utf-8"))
        manifest_entries.append(("Z1/data_dictionary.txt", _sha256_hex(data_dict.encode("utf-8"))))

        try:
            docflow_csv = _export_docflow_headers_csv(db, effective_tenant, from_date, to_date)
            raw = docflow_csv.encode("utf-8-sig")
            zf.writestr("Z1/docflow_headers.csv", raw)
            manifest_entries.append(("Z1/docflow_headers.csv", _sha256_hex(raw)))
        except Exception:
            raw = "id;tenant_id;doc_type;doc_number;status\n".encode("utf-8-sig")
            zf.writestr("Z1/docflow_headers.csv", raw)
            manifest_entries.append(("Z1/docflow_headers.csv", _sha256_hex(raw)))

        # --- Z2: Bewegungsdaten ---
        try:
            audit_csv = _export_audit_log_csv(db, effective_tenant, from_date, to_date)
            raw = audit_csv.encode("utf-8-sig")
            zf.writestr("Z2/audit_logs.csv", raw)
            manifest_entries.append(("Z2/audit_logs.csv", _sha256_hex(raw)))
        except Exception:
            raw = "id;user_id;tenant_id;action;entity_type;entity_id;timestamp\n".encode("utf-8-sig")
            zf.writestr("Z2/audit_logs.csv", raw)
            manifest_entries.append(("Z2/audit_logs.csv", _sha256_hex(raw)))

        try:
            journal_csv = _export_journal_entries_csv(db, effective_tenant, from_date, to_date)
            raw = journal_csv.encode("utf-8-sig")
            zf.writestr("Z2/journal_entries.csv", raw)
            manifest_entries.append(("Z2/journal_entries.csv", _sha256_hex(raw)))
        except Exception:
            raw = "id;tenant_id;entry_number;entry_date;status\n".encode("utf-8-sig")
            zf.writestr("Z2/journal_entries.csv", raw)
            manifest_entries.append(("Z2/journal_entries.csv", _sha256_hex(raw)))

        try:
            items_csv = _export_docflow_items_csv(db, effective_tenant, from_date, to_date)
            raw = items_csv.encode("utf-8-sig")
            zf.writestr("Z2/docflow_items.csv", raw)
            manifest_entries.append(("Z2/docflow_items.csv", _sha256_hex(raw)))
        except Exception:
            raw = "id;tenant_id;header_id;line_number;article_number;quantity;line_total_net\n".encode("utf-8-sig")
            zf.writestr("Z2/docflow_items.csv", raw)
            manifest_entries.append(("Z2/docflow_items.csv", _sha256_hex(raw)))

        # --- Z3: Archiv / Hashes ---
        try:
            artifact_csv = _export_artifact_hashes_csv(db, effective_tenant, from_date, to_date)
            raw = artifact_csv.encode("utf-8-sig")
            zf.writestr("Z3/artifact_hashes.csv", raw)
            manifest_entries.append(("Z3/artifact_hashes.csv", _sha256_hex(raw)))
        except Exception:
            raw = "id;tenant_id;header_id;artifact_type;content_hash_sha256;storage_key;created_at\n".encode("utf-8-sig")
            zf.writestr("Z3/artifact_hashes.csv", raw)
            manifest_entries.append(("Z3/artifact_hashes.csv", _sha256_hex(raw)))

        # --- Integrity-Manifest (SHA-256 pro Datei) ---
        manifest_lines = ["path;sha256"]
        for path, sha in manifest_entries:
            manifest_lines.append(f"{path};{sha}")
        manifest_body = "\n".join(manifest_lines).encode("utf-8")
        zf.writestr("integrity_manifest.csv", manifest_body)
        manifest_entries.append(("integrity_manifest.csv", _sha256_hex(manifest_body)))
    zip_buf.seek(0)
    filename = f"audit-package-{effective_tenant}-{from_date or 'start'}-{to_date or 'end'}.zip"
    return StreamingResponse(
        zip_buf,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ============================================================================
# Artifact-Integritätsprüfung
# ============================================================================

@router.get("/artifacts/{artifact_id}/verify", response_model=ArtifactVerifyOut, summary="Artifact hash verifizieren")
async def verify_artifact_hash(
    artifact_id: str,
    provided_hash: Optional[str] = Query(
        None,
        min_length=64,
        max_length=64,
        description="SHA-256 des Inhalts zum Abgleich mit dem gespeicherten Hash",
    ),
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Integritätsprüfung für ein Belegartefakt (read-only).

    Vergleicht den gespeicherten SHA-256-Content-Hash mit einem optional
    übergebenen Hash (z. B. nach erneutem Einlesen aus dem Storage).
    Status: 'verified' (Hashes stimmen überein), 'mismatch' (Manipulation!),
            'unchecked' (kein provided_hash übergeben).
    """
    from fastapi import HTTPException as _HTTPException

    effective_tenant = tenant_id or DEFAULT_TENANT
    row = db.execute(
        text(
            "SELECT id, content_hash_sha256 "
            "FROM domain_docflow.document_artifacts "
            "WHERE id = :id AND tenant_id = :tid"
        ),
        {"id": artifact_id, "tid": effective_tenant},
    ).mappings().first()
    if not row:
        raise _HTTPException(status_code=404, detail="Artifact nicht gefunden")

    stored = row["content_hash_sha256"]
    if provided_hash:
        match: Optional[bool] = stored == provided_hash
        integrity_status = "verified" if match else "mismatch"
    else:
        match = None
        integrity_status = "unchecked"

    return ArtifactVerifyOut(
        id=artifact_id,
        stored_hash=stored,
        provided_hash=provided_hash,
        match=match,
        integrity_status=integrity_status,
    )


# ============================================================================
# E-Rechnung XML – Validierungsstatus setzen
# ============================================================================

@router.patch("/e-invoice-xml/{header_id}/validate", response_model=InvoiceXmlOut, summary="Invoice xml validation setzen")
async def set_invoice_xml_validation(
    header_id: str,
    payload: InvoiceXmlValidateIn,
    tenant_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Validierungsergebnis (XSD/Schematron) für eine E-Rechnung setzen.

    Setzt validation_status (valid|invalid|pending) und optional validation_errors
    mit den XSD-Fehlerdetails. Kein Löschen oder Ersetzen des XML.
    """
    import json as _json
    from fastapi import HTTPException as _HTTPException

    effective_tenant = tenant_id or DEFAULT_TENANT
    errors_json = _json.dumps(payload.validation_errors) if payload.validation_errors else None

    result = db.execute(
        text(
            """
            UPDATE domain_docflow.invoice_xml_store
               SET validation_status = :status,
                   validation_errors  = CAST(:errors AS jsonb)
             WHERE header_id = :header_id
               AND tenant_id = :tenant_id
            RETURNING id, tenant_id, header_id, content_hash_sha256, storage_key,
                      format_type, validation_status, validation_errors,
                      created_at, created_by
            """
        ),
        {
            "status": payload.validation_status,
            "errors": errors_json,
            "header_id": header_id,
            "tenant_id": effective_tenant,
        },
    ).mappings().first()

    if not result:
        raise _HTTPException(
            status_code=404,
            detail=f"Kein XML-Eintrag für header_id={header_id}",
        )
    db.commit()
    r = dict(result)
    return InvoiceXmlOut(**r)
