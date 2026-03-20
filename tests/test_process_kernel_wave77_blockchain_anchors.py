from __future__ import annotations

from app.core.blockchain_anchor_contracts import (
    BlockchainNetzwerkProfil,
    BlockchainObjektTyp,
    build_blockchain_anchor,
    canonicalize_blockchain_payload,
    compute_sha256_hex,
)


def test_blockchain_anchor_uses_deterministic_sha256_payload_hash():
    payload = {"b": 2, "a": 1}
    expected = compute_sha256_hex(canonicalize_blockchain_payload({"a": 1, "b": 2}))
    anchor = build_blockchain_anchor(
        tenant_id="test-tenant",
        subject_type=BlockchainObjektTyp.SETTLEMENT_AUDIT_CHAIN,
        subject_ref="SET-100",
        payload=payload,
        network_profile=BlockchainNetzwerkProfil.HYPERLEDGER_FABRIC_DIRECT,
    )
    assert anchor.payload_hash_algorithm == "SHA-256"
    assert anchor.canonical_payload_hash == expected
    assert anchor.anchor_payload["canonical_payload_hash"] == expected


def test_oracle_fabric_profile_uses_private_collection_pattern():
    anchor = build_blockchain_anchor(
        tenant_id="test-tenant",
        subject_type=BlockchainObjektTyp.KNOWLEDGE_VERSION,
        subject_ref="KNW-1:v2",
        payload={"format": "markdown", "version": 2},
        private_payload={"inhalt": "# intern"},
        network_profile=BlockchainNetzwerkProfil.ORACLE_FABRIC_PERMISSIONED,
    )
    assert anchor.adapter_hint.adapter_typ == "oracle-blockchain-platform"
    assert anchor.adapter_hint.private_data_collection == "valeoPrivateAuditCollection"
    assert anchor.private_payload_hash is not None


def test_sap_hana_adapter_profile_exposes_virtualized_read_hints():
    anchor = build_blockchain_anchor(
        tenant_id="test-tenant",
        subject_type=BlockchainObjektTyp.CHANNEL_PROCESS_THREAD,
        subject_ref="cht-1",
        payload={"status": "pending_approval"},
        network_profile=BlockchainNetzwerkProfil.SAP_HANA_BLOCKCHAIN_ADAPTER,
    )
    assert anchor.adapter_hint.adapter_typ == "sap-hana-blockchain-adapter"
    assert anchor.adapter_hint.read_pattern == "virtual-table-world-state-and-chronology"
    assert anchor.adapter_hint.world_state_view_name == "VT_VALEO_ANCHORS_WORLD_STATE"
