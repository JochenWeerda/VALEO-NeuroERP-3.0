"""
Audit Evidence API — Wave 3 AP2

Verknuepft Audit-Eintraege mit DMS-Dokumenten und liefert GoBD-konforme Belegnachweise.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response

from ....core.tenant import get_tenant_id
from ....core.audit_evidence import (
    AuditEvidenceEntry,
    EvidenceReference,
    EvidenceSourceSystem,
    EvidenceType,
    DocumentEvidencePolicy,
    build_default_evidence_policy,
)

router = APIRouter(prefix="/audit-evidence", tags=["audit", "evidence", "gobd"])

_STORE: dict[str, dict[str, Any]] = {}   # tenant_id → {audit_entry_id → AuditEvidenceEntry}


def _tenant_store(tenant_id: str) -> dict[str, Any]:
    return _STORE.setdefault(tenant_id, {})


# ---------------------------------------------------------------------------
# Evidence-Eintraege
# ---------------------------------------------------------------------------

@router.get("", response_model=list[dict])
async def list_evidence_entries(
    aggregate_type: str | None = None,
    aggregate_id: str | None = None,
    tenant_id: str = Depends(get_tenant_id),
):
    """Listet alle Audit-Evidence-Eintraege, optional gefiltert nach Aggregat."""
    store = _tenant_store(tenant_id)
    entries = [e.model_dump(mode="json") for e in store.values()]
    if aggregate_type:
        entries = [e for e in entries if e.get("aggregate_type") == aggregate_type]
    if aggregate_id:
        entries = [e for e in entries if e.get("aggregate_id") == aggregate_id]
    return entries


@router.get("/{audit_entry_id}", response_model=dict)
async def get_evidence_entry(
    audit_entry_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    store = _tenant_store(tenant_id)
    entry = store.get(audit_entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Audit evidence entry {audit_entry_id} not found")
    return entry.model_dump(mode="json")


@router.post("", response_model=dict, status_code=201)
async def create_evidence_entry(
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Erstellt einen neuen Audit-Evidence-Eintrag."""
    entry = AuditEvidenceEntry(
        audit_entry_id=body.get("audit_entry_id") or str(uuid.uuid4()),
        tenant_id=tenant_id,
        aggregate_type=body.get("aggregate_type", ""),
        aggregate_id=body.get("aggregate_id", ""),
        action=body.get("action", ""),
        evidence_refs=[],
        schema_version=1,
    )
    store = _tenant_store(tenant_id)
    store[entry.audit_entry_id] = entry
    return entry.model_dump(mode="json")


@router.post("/{audit_entry_id}/evidence-refs", response_model=dict, status_code=201)
async def attach_evidence_ref(
    audit_entry_id: str,
    body: dict,
    tenant_id: str = Depends(get_tenant_id),
):
    """Haengt einen Dokumentenbeleg an einen Audit-Evidence-Eintrag."""
    store = _tenant_store(tenant_id)
    entry = store.get(audit_entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail=f"Audit evidence entry {audit_entry_id} not found")

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
    entry.add_evidence(ref)
    store[audit_entry_id] = entry
    return entry.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Belegpflicht-Richtlinie
# ---------------------------------------------------------------------------

@router.get("/policy/document-evidence", response_model=dict)
async def get_evidence_policy(tenant_id: str = Depends(get_tenant_id)):
    """Liefert die GoBD-Belegpflicht-Richtlinie des Mandanten."""
    policy = build_default_evidence_policy(tenant_id)
    return policy.model_dump(mode="json")


@router.get("/policy/gobd-check/{aggregate_type}/{aggregate_id}", response_model=dict)
async def check_gobd_compliance(
    aggregate_type: str,
    aggregate_id: str,
    tenant_id: str = Depends(get_tenant_id),
):
    """Prueft ob ein Aggregat GoBD-konform belegt ist."""
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
