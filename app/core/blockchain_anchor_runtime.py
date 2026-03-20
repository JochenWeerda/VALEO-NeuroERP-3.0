"""
Runtime helpers for anchoring ERP audit state to enterprise blockchain records.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.blockchain_anchor_contracts import (
    BlockchainNetzwerkProfil,
    BlockchainObjektTyp,
    build_blockchain_anchor,
)
from app.repositories.blockchain_anchor_repository import BlockchainAnchorRepository


def anchor_channel_process_thread(
    db: Session,
    *,
    thread: Any,
    network_profile: BlockchainNetzwerkProfil = BlockchainNetzwerkProfil.ORACLE_FABRIC_PERMISSIONED,
):
    payload = {
        "thread_id": thread.thread_id,
        "kanal": thread.kanal,
        "tenant_id": thread.tenant_id,
        "process_definition_key": thread.process_definition_key,
        "command_name": thread.command_name,
        "aggregate_type": thread.aggregate_type,
        "aggregate_id": thread.aggregate_id,
        "status": thread.status,
        "audit_count": len(thread.audit_trail),
    }
    private_payload = {
        "request_payload": thread.request_payload,
        "approval_record": thread.approval_record,
        "execution": thread.execution,
    }
    anchor = build_blockchain_anchor(
        tenant_id=thread.tenant_id,
        subject_type=BlockchainObjektTyp.CHANNEL_PROCESS_THREAD,
        subject_ref=thread.thread_id,
        payload=payload,
        private_payload=private_payload,
        network_profile=network_profile,
    )
    return BlockchainAnchorRepository(db).save(anchor)


def anchor_knowledge_object(
    db: Session,
    *,
    knowledge_record: Any,
    version: int,
    proposal_id: str | None = None,
    network_profile: BlockchainNetzwerkProfil = BlockchainNetzwerkProfil.ORACLE_FABRIC_PERMISSIONED,
):
    latest_version = None
    for entry in getattr(knowledge_record, "versionen", []):
        if entry.version == version:
            latest_version = entry
            break
    if latest_version is None and getattr(knowledge_record, "versionen", None):
        latest_version = max(knowledge_record.versionen, key=lambda item: item.version)

    payload = {
        "knowledge_id": knowledge_record.knowledge_id,
        "version": version,
        "titel": knowledge_record.titel,
        "typ": knowledge_record.typ,
        "status": knowledge_record.status,
        "proposal_id": proposal_id,
    }
    private_payload = {
        "format": getattr(latest_version, "format", None),
        "inhalt": getattr(latest_version, "inhalt", None),
        "strukturierte_daten": dict(getattr(latest_version, "strukturierte_daten", {}) or {}),
        "zielrollen": list(getattr(knowledge_record, "zielrollen", []) or []),
        "tags": list(getattr(knowledge_record, "tags", []) or []),
    }
    anchor = build_blockchain_anchor(
        tenant_id=knowledge_record.tenant_id,
        subject_type=BlockchainObjektTyp.KNOWLEDGE_VERSION,
        subject_ref=f"{knowledge_record.knowledge_id}:v{version}",
        payload=payload,
        private_payload=private_payload,
        network_profile=network_profile,
    )
    return BlockchainAnchorRepository(db).save(anchor)


def anchor_settlement_audit_chain(
    db: Session,
    *,
    chain: Any,
    network_profile: BlockchainNetzwerkProfil = BlockchainNetzwerkProfil.ORACLE_FABRIC_PERMISSIONED,
):
    payload = {
        "settlement_id": chain.settlement_id,
        "tenant_id": chain.tenant_id,
        "head_hash": chain.head_hash,
        "link_count": len(chain.links),
        "schema_version": chain.schema_version,
        "intact": chain.verify_integrity().intact,
    }
    private_payload = {
        "links": [link.as_dict() for link in chain.links],
    }
    anchor = build_blockchain_anchor(
        tenant_id=chain.tenant_id,
        subject_type=BlockchainObjektTyp.SETTLEMENT_AUDIT_CHAIN,
        subject_ref=chain.settlement_id,
        payload=payload,
        private_payload=private_payload,
        network_profile=network_profile,
    )
    return BlockchainAnchorRepository(db).save(anchor)


def anchor_journal_entry_event(
    db: Session,
    *,
    tenant_id: str,
    entry_id: str,
    action: str,
    payload: dict[str, Any],
    network_profile: BlockchainNetzwerkProfil = BlockchainNetzwerkProfil.ORACLE_FABRIC_PERMISSIONED,
):
    anchor = build_blockchain_anchor(
        tenant_id=tenant_id,
        subject_type=BlockchainObjektTyp.JOURNAL_ENTRY_AUDIT,
        subject_ref=entry_id,
        payload={"entry_id": entry_id, "action": action, **payload},
        private_payload=payload,
        network_profile=network_profile,
    )
    return BlockchainAnchorRepository(db).save(anchor)


def anchor_document_artifact(
    db: Session,
    *,
    tenant_id: str,
    artifact_id: str,
    header_id: str,
    artifact_type: str,
    content_hash_sha256: str,
    storage_key: str,
    file_name: str | None,
    created_by: str | None,
    network_profile: BlockchainNetzwerkProfil = BlockchainNetzwerkProfil.ORACLE_FABRIC_PERMISSIONED,
):
    payload = {
        "artifact_id": artifact_id,
        "header_id": header_id,
        "artifact_type": artifact_type,
        "content_hash_sha256": content_hash_sha256,
    }
    private_payload = {
        "storage_key": storage_key,
        "file_name": file_name,
        "created_by": created_by,
    }
    anchor = build_blockchain_anchor(
        tenant_id=tenant_id,
        subject_type=BlockchainObjektTyp.DOCUMENT_ARTIFACT,
        subject_ref=artifact_id,
        payload=payload,
        private_payload=private_payload,
        network_profile=network_profile,
    )
    return BlockchainAnchorRepository(db).save(anchor)


def anchor_governance_proposal(
    db: Session,
    *,
    proposal: Any,
    network_profile: BlockchainNetzwerkProfil = BlockchainNetzwerkProfil.ORACLE_FABRIC_PERMISSIONED,
):
    payload = {
        "proposal_id": proposal.proposal_id,
        "tenant_id": proposal.tenant_id,
        "titel": proposal.titel,
        "typ": proposal.typ,
        "status": proposal.status,
        "quelle": proposal.quelle,
        "target_knowledge_id": proposal.target_knowledge_id,
    }
    private_payload = {
        "inhalt": proposal.inhalt,
        "format": proposal.format,
        "strukturierte_daten": dict(proposal.strukturierte_daten or {}),
        "begruendung": proposal.begruendung,
        "vorgeschlagen_von_ref": proposal.vorgeschlagen_von_ref,
        "vorgeschlagen_von_typ": proposal.vorgeschlagen_von_typ,
    }
    anchor = build_blockchain_anchor(
        tenant_id=proposal.tenant_id,
        subject_type=BlockchainObjektTyp.KNOWLEDGE_VERSION,
        subject_ref=f"proposal:{proposal.proposal_id}",
        payload=payload,
        private_payload=private_payload,
        network_profile=network_profile,
    )
    return BlockchainAnchorRepository(db).save(anchor)
