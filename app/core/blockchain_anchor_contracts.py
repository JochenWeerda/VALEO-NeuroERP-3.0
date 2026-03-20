"""
Enterprise blockchain anchor contracts for permissioned ERP audit anchoring.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from app.core.uuid7 import uuid7


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class BlockchainNetzwerkProfil(str, Enum):
    ORACLE_FABRIC_PERMISSIONED = "ORACLE_FABRIC_PERMISSIONED"
    HYPERLEDGER_FABRIC_DIRECT = "HYPERLEDGER_FABRIC_DIRECT"
    SAP_HANA_BLOCKCHAIN_ADAPTER = "SAP_HANA_BLOCKCHAIN_ADAPTER"


class BlockchainObjektTyp(str, Enum):
    SETTLEMENT_AUDIT_CHAIN = "SETTLEMENT_AUDIT_CHAIN"
    KNOWLEDGE_VERSION = "KNOWLEDGE_VERSION"
    CHANNEL_PROCESS_THREAD = "CHANNEL_PROCESS_THREAD"
    JOURNAL_ENTRY_AUDIT = "JOURNAL_ENTRY_AUDIT"
    DOCUMENT_ARTIFACT = "DOCUMENT_ARTIFACT"


def canonicalize_blockchain_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def compute_sha256_hex(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass
class BlockchainAdapterHint:
    netzwerk_profil: str
    adapter_typ: str
    write_pattern: str
    read_pattern: str
    channel_name: str | None = None
    chaincode_name: str | None = None
    endorsement_policy: str | None = None
    private_data_collection: str | None = None
    member_orgs: list[str] = field(default_factory=list)
    remote_source_name: str | None = None
    virtual_table_name: str | None = None
    chronology_view_name: str | None = None
    world_state_view_name: str | None = None
    oauth_credential_ref: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "netzwerk_profil": self.netzwerk_profil,
            "adapter_typ": self.adapter_typ,
            "write_pattern": self.write_pattern,
            "read_pattern": self.read_pattern,
            "channel_name": self.channel_name,
            "chaincode_name": self.chaincode_name,
            "endorsement_policy": self.endorsement_policy,
            "private_data_collection": self.private_data_collection,
            "member_orgs": list(self.member_orgs),
            "remote_source_name": self.remote_source_name,
            "virtual_table_name": self.virtual_table_name,
            "chronology_view_name": self.chronology_view_name,
            "world_state_view_name": self.world_state_view_name,
            "oauth_credential_ref": self.oauth_credential_ref,
        }


@dataclass
class BlockchainAnchorRecord:
    anchor_id: str
    tenant_id: str
    subject_type: str
    subject_ref: str
    network_profile: str
    payload_hash_algorithm: str
    canonical_payload_hash: str
    private_payload_hash: str | None
    anchor_payload: dict[str, Any]
    adapter_hint: BlockchainAdapterHint
    status: str = "prepared"
    created_at: str = field(default_factory=_utcnow)

    def as_dict(self) -> dict[str, Any]:
        return {
            "anchor_id": self.anchor_id,
            "tenant_id": self.tenant_id,
            "subject_type": self.subject_type,
            "subject_ref": self.subject_ref,
            "network_profile": self.network_profile,
            "payload_hash_algorithm": self.payload_hash_algorithm,
            "canonical_payload_hash": self.canonical_payload_hash,
            "private_payload_hash": self.private_payload_hash,
            "anchor_payload": self.anchor_payload,
            "adapter_hint": self.adapter_hint.as_dict(),
            "status": self.status,
            "created_at": self.created_at,
        }


def build_adapter_hint(
    *,
    network_profile: BlockchainNetzwerkProfil,
    channel_name: str | None = None,
    chaincode_name: str | None = None,
    private_data_collection: str | None = None,
    member_orgs: list[str] | None = None,
    remote_source_name: str | None = None,
    virtual_table_name: str | None = None,
    oauth_credential_ref: str | None = None,
) -> BlockchainAdapterHint:
    members = list(member_orgs or [])
    if network_profile == BlockchainNetzwerkProfil.ORACLE_FABRIC_PERMISSIONED:
        return BlockchainAdapterHint(
            netzwerk_profil=network_profile.value,
            adapter_typ="oracle-blockchain-platform",
            write_pattern="chaincode-invoke-with-private-data",
            read_pattern="channel-ledger-query",
            channel_name=channel_name or "valeo-audit",
            chaincode_name=chaincode_name or "valeo_anchor_cc",
            endorsement_policy="MAJORITY",
            private_data_collection=private_data_collection or "valeoPrivateAuditCollection",
            member_orgs=members or ["VALEO", "AUDITOR"],
        )
    if network_profile == BlockchainNetzwerkProfil.HYPERLEDGER_FABRIC_DIRECT:
        return BlockchainAdapterHint(
            netzwerk_profil=network_profile.value,
            adapter_typ="hyperledger-fabric",
            write_pattern="chaincode-lifecycle-governed-invoke",
            read_pattern="ledger-and-private-collection-query",
            channel_name=channel_name or "valeo-audit",
            chaincode_name=chaincode_name or "valeo_anchor_cc",
            endorsement_policy="OR('VALEO.member','AUDITOR.member')",
            private_data_collection=private_data_collection or "valeoPrivateAuditCollection",
            member_orgs=members or ["VALEO", "AUDITOR"],
        )
    return BlockchainAdapterHint(
        netzwerk_profil=network_profile.value,
        adapter_typ="sap-hana-blockchain-adapter",
        write_pattern="rest-oauth-anchor-write",
        read_pattern="virtual-table-world-state-and-chronology",
        remote_source_name=remote_source_name or "BLOCKCHAIN_REMOTE",
        virtual_table_name=virtual_table_name or "VT_VALEO_ANCHORS",
        chronology_view_name="VT_VALEO_ANCHORS_CHRONOLOGY",
        world_state_view_name="VT_VALEO_ANCHORS_WORLD_STATE",
        oauth_credential_ref=oauth_credential_ref or "sap-bc-service-account",
    )


def build_blockchain_anchor(
    *,
    tenant_id: str,
    subject_type: BlockchainObjektTyp,
    subject_ref: str,
    payload: dict[str, Any],
    network_profile: BlockchainNetzwerkProfil,
    private_payload: dict[str, Any] | None = None,
    channel_name: str | None = None,
    chaincode_name: str | None = None,
    private_data_collection: str | None = None,
    member_orgs: list[str] | None = None,
    remote_source_name: str | None = None,
    virtual_table_name: str | None = None,
    oauth_credential_ref: str | None = None,
) -> BlockchainAnchorRecord:
    anchor_id = uuid7()
    canonical_payload = canonicalize_blockchain_payload(payload)
    canonical_hash = compute_sha256_hex(canonical_payload)
    private_hash = None
    if private_payload is not None:
        private_hash = compute_sha256_hex(canonicalize_blockchain_payload(private_payload))
    adapter_hint = build_adapter_hint(
        network_profile=network_profile,
        channel_name=channel_name,
        chaincode_name=chaincode_name,
        private_data_collection=private_data_collection,
        member_orgs=member_orgs,
        remote_source_name=remote_source_name,
        virtual_table_name=virtual_table_name,
        oauth_credential_ref=oauth_credential_ref,
    )
    anchor_payload = {
        "anchor_id": anchor_id,
        "tenant_id": tenant_id,
        "subject_type": subject_type.value,
        "subject_ref": subject_ref,
        "payload_hash_algorithm": "SHA-256",
        "canonical_payload_hash": canonical_hash,
        "private_payload_hash": private_hash,
        "anchored_at": _utcnow(),
        "anchor_schema_version": 1,
    }
    return BlockchainAnchorRecord(
        anchor_id=anchor_id,
        tenant_id=tenant_id,
        subject_type=subject_type.value,
        subject_ref=subject_ref,
        network_profile=network_profile.value,
        payload_hash_algorithm="SHA-256",
        canonical_payload_hash=canonical_hash,
        private_payload_hash=private_hash,
        anchor_payload=anchor_payload,
        adapter_hint=adapter_hint,
    )
