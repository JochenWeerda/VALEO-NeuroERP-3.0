"""
Audit Evidence API — Wave 3 AP2

Verknuepft Audit-Eintraege mit DMS-Dokumenten und liefert GoBD-konforme Belegnachweise.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from ....core.audit_evidence import (
    AuditEvidenceEntry,
    EvidenceReference,
    EvidenceSourceSystem,
    EvidenceType,
    build_default_evidence_policy,
)

logger = logging.getLogger(__name__)

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.audit_evidence_schemas import AuditEvidenceOut


router = APIRouter(prefix="/audit-evidence", tags=["audit", "evidence", "gobd"])

# In-memory fallback if DB table does not exist yet
_STORE: dict[str, dict[str, Any]] = {}   # tenant_id → {audit_entry_id → AuditEvidenceEntry}


def _tenant_store(tenant_id: str) -> dict[str, Any]:
    return _STORE.setdefault(tenant_id, {})


# ---------------------------------------------------------------------------
# Evidence-Eintraege
# ---------------------------------------------------------------------------

@router.get("", response_model=list[AuditEvidenceOut], summary="Evidence entries auflisten")
async def list_evidence_entries(
    aggregate_type: str | None = None,
    aggregate_id: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Listet alle Audit-Evidence-Eintraege, optional gefiltert nach Aggregat."""
    try:
        clauses = ["tenant_id = :tid"]
        params: dict[str, Any] = {"tid": tenant_id}
        if aggregate_type:
            clauses.append("aggregate_type = :atype")
            params["atype"] = aggregate_type
        if aggregate_id:
            clauses.append("aggregate_id = :aid")
            params["aid"] = aggregate_id
        where = " AND ".join(clauses)
        result = db.execute(text(f"""
            SELECT audit_entry_id, tenant_id, aggregate_type, aggregate_id,
                   action, evidence_refs, schema_version, created_at
            FROM domain_shared.audit_evidence
            WHERE {where}
            ORDER BY created_at DESC
        """), params)  # nosec S608 — reviewed-safe: column names code-controlled, values parameterized
        rows = result.fetchall()
        entries = []
        for row in rows:
            refs = row.evidence_refs if row.evidence_refs else []
            if isinstance(refs, str):
                refs = json.loads(refs)
            entries.append({
                "audit_entry_id": row.audit_entry_id,
                "tenant_id": row.tenant_id,
                "aggregate_type": row.aggregate_type,
                "aggregate_id": row.aggregate_id,
                "action": row.action,
                "evidence_refs": refs,
                "schema_version": row.schema_version,
                "gobd_compliant": len(refs) > 0,
            })
        return entries
    except Exception:
        logger.debug("audit_evidence table not available, falling back to in-memory store")
        store = _tenant_store(tenant_id)
        entries = [e.model_dump(mode="json") for e in store.values()]
        if aggregate_type:
            entries = [e for e in entries if e.get("aggregate_type") == aggregate_type]
        if aggregate_id:
            entries = [e for e in entries if e.get("aggregate_id") == aggregate_id]
        return entries


@router.get("/{audit_entry_id}", response_model=AuditEvidenceOut, summary="Evidence entry abrufen")
async def get_evidence_entry(
    audit_entry_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        result = db.execute(text("""
            SELECT audit_entry_id, tenant_id, aggregate_type, aggregate_id,
                   action, evidence_refs, schema_version, created_at
            FROM domain_shared.audit_evidence
            WHERE tenant_id = :tid AND audit_entry_id = :eid
        """), {"tid": tenant_id, "eid": audit_entry_id})
        row = result.fetchone()
        if row:
            refs = row.evidence_refs if row.evidence_refs else []
            if isinstance(refs, str):
                refs = json.loads(refs)
            return {
                "audit_entry_id": row.audit_entry_id,
                "tenant_id": row.tenant_id,
                "aggregate_type": row.aggregate_type,
                "aggregate_id": row.aggregate_id,
                "action": row.action,
                "evidence_refs": refs,
                "schema_version": row.schema_version,
                "gobd_compliant": len(refs) > 0,
            }
    except Exception:
        logger.debug("audit_evidence table not available, falling back to in-memory store")

    store = _tenant_store(tenant_id)
    entry = store.get(audit_entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Audit evidence entry {audit_entry_id} not found")
    return entry.model_dump(mode="json")


@router.post("", response_model=AuditEvidenceOut, status_code=201, summary="Evidence entry anlegen")
async def create_evidence_entry(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Erstellt einen neuen Audit-Evidence-Eintrag."""
    entry_id = body.get("audit_entry_id") or str(uuid.uuid4())
    entry = AuditEvidenceEntry(
        audit_entry_id=entry_id,
        tenant_id=tenant_id,
        aggregate_type=body.get("aggregate_type", ""),
        aggregate_id=body.get("aggregate_id", ""),
        action=body.get("action", ""),
        evidence_refs=[],
        schema_version=1,
    )
    try:
        db.execute(text("""
            INSERT INTO domain_shared.audit_evidence
                (audit_entry_id, tenant_id, aggregate_type, aggregate_id, action, evidence_refs, schema_version, created_at)
            VALUES
                (:eid, :tid, :atype, :aid, :action, :refs, :sv, NOW())
        """), {
            "eid": entry_id,
            "tid": tenant_id,
            "atype": entry.aggregate_type,
            "aid": entry.aggregate_id,
            "action": entry.action,
            "refs": json.dumps([]),
            "sv": 1,
        })
        db.commit()
    except Exception:
        db.rollback()
        logger.debug("audit_evidence table not available, falling back to in-memory store")
        store = _tenant_store(tenant_id)
        store[entry.audit_entry_id] = entry
    return entry.model_dump(mode="json")


@router.post("/{audit_entry_id}/evidence-refs", response_model=AuditEvidenceOut, status_code=201, summary="Evidence ref attach")
async def attach_evidence_ref(
    audit_entry_id: str,
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Haengt einen Dokumentenbeleg an einen Audit-Evidence-Eintrag."""
    ref = EvidenceReference(
        evidence_id=body.get("evidence_id") or str(uuid.uuid4()),
        source_system=body.get("source_system", EvidenceSourceSystem.UPLOAD),
        evidence_type=body.get("evidence_type", EvidenceType.INVOICE_SCAN),
        external_id=body.get("external_id", ""),
        filename=body.get("filename"),
        page_count=body.get("page_count"),
        ocr_confidence=body.get("ocr_confidence"),
        verified=body.get("verified", False),
        verified_by=body.get("verified_by"),
        verified_at=body.get("verified_at"),
    )
    ref_dict = ref.model_dump(mode="json")

    try:
        # Fetch current refs from DB
        result = db.execute(text("""
            SELECT evidence_refs FROM domain_shared.audit_evidence
            WHERE tenant_id = :tid AND audit_entry_id = :eid
        """), {"tid": tenant_id, "eid": audit_entry_id})
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f"Audit evidence entry {audit_entry_id} not found")
        existing_refs = row.evidence_refs if row.evidence_refs else []
        if isinstance(existing_refs, str):
            existing_refs = json.loads(existing_refs)
        existing_refs.append(ref_dict)
        db.execute(text("""
            UPDATE domain_shared.audit_evidence
            SET evidence_refs = :refs
            WHERE tenant_id = :tid AND audit_entry_id = :eid
        """), {"refs": json.dumps(existing_refs), "tid": tenant_id, "eid": audit_entry_id})
        db.commit()
        return {
            "audit_entry_id": audit_entry_id,
            "tenant_id": tenant_id,
            "evidence_refs": existing_refs,
            "gobd_compliant": len(existing_refs) > 0,
        }
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        logger.debug("audit_evidence table not available, falling back to in-memory store")

    # Fallback to in-memory
    store = _tenant_store(tenant_id)
    entry = store.get(audit_entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Audit evidence entry {audit_entry_id} not found")
    entry.add_evidence(ref)
    store[audit_entry_id] = entry
    return entry.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Belegpflicht-Richtlinie
# ---------------------------------------------------------------------------

@router.get("/policy/document-evidence", response_model=AuditEvidenceOut, summary="Evidence policy abrufen")
async def get_evidence_policy(tenant_id: str = Depends(get_tenant_id)):
    """Liefert die GoBD-Belegpflicht-Richtlinie des Mandanten."""
    policy = build_default_evidence_policy(tenant_id)
    return policy.model_dump(mode="json")


@router.get("/policy/gobd-check/{aggregate_type}/{aggregate_id}", response_model=AuditEvidenceOut, summary="Gobd compliance prüfen")
async def check_gobd_compliance(
    aggregate_type: str,
    aggregate_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    """Prueft ob ein Aggregat GoBD-konform belegt ist."""
    try:
        result = db.execute(text("""
            SELECT audit_entry_id, evidence_refs
            FROM domain_shared.audit_evidence
            WHERE tenant_id = :tid AND aggregate_type = :atype AND aggregate_id = :aid
        """), {"tid": tenant_id, "atype": aggregate_type, "aid": aggregate_id})
        rows = result.fetchall()
        audit_entries_count = len(rows)
        evidence_count = 0
        compliant = False
        for row in rows:
            refs = row.evidence_refs if row.evidence_refs else []
            if isinstance(refs, str):
                refs = json.loads(refs)
            evidence_count += len(refs)
            if len(refs) > 0:
                compliant = True
        return {
            "aggregate_type": aggregate_type,
            "aggregate_id": aggregate_id,
            "gobd_compliant": compliant,
            "evidence_count": evidence_count,
            "audit_entries_count": audit_entries_count,
        }
    except Exception:
        logger.debug("audit_evidence table not available, falling back to in-memory store")

    store = _tenant_store(tenant_id)
    entries = [e for e in store.values()
               if e.aggregate_type == aggregate_type and e.aggregate_id == aggregate_id]
    compliant = any(e.gobd_compliant for e in entries)
    evidence_count = sum(len(e.evidence_refs) for e in entries)
    return {
        "aggregate_type": aggregate_type,
        "aggregate_id": aggregate_id,
        "gobd_compliant": compliant,
        "evidence_count": evidence_count,
        "audit_entries_count": len(entries),
    }
