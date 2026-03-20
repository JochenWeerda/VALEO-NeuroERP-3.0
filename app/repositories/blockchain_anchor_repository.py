"""
Repository for persistent blockchain anchor records.
"""

from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.blockchain_anchor_contracts import BlockchainAnchorRecord, BlockchainAdapterHint
from app.models.blockchain_anchors import BlockchainAnchorRecordModel


class BlockchainAnchorRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, anchor: BlockchainAnchorRecord) -> BlockchainAnchorRecord:
        record = BlockchainAnchorRecordModel(
            anchor_id=anchor.anchor_id,
            tenant_id=anchor.tenant_id,
            subject_type=anchor.subject_type,
            subject_ref=anchor.subject_ref,
            network_profile=anchor.network_profile,
            payload_hash_algorithm=anchor.payload_hash_algorithm,
            canonical_payload_hash=anchor.canonical_payload_hash,
            private_payload_hash=anchor.private_payload_hash,
            anchor_payload=dict(anchor.anchor_payload),
            adapter_hint=anchor.adapter_hint.as_dict(),
            status=anchor.status,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return self._to_domain(record)

    def get(self, anchor_id: str) -> BlockchainAnchorRecord | None:
        record = self.db.get(BlockchainAnchorRecordModel, anchor_id)
        if record is None:
            return None
        return self._to_domain(record)

    def list(
        self,
        *,
        tenant_id: str | None = None,
        subject_type: str | None = None,
        network_profile: str | None = None,
        limit: int = 50,
    ) -> list[BlockchainAnchorRecord]:
        stmt = select(BlockchainAnchorRecordModel)
        if tenant_id:
            stmt = stmt.where(BlockchainAnchorRecordModel.tenant_id == tenant_id)
        if subject_type:
            stmt = stmt.where(BlockchainAnchorRecordModel.subject_type == subject_type)
        if network_profile:
            stmt = stmt.where(BlockchainAnchorRecordModel.network_profile == network_profile)
        stmt = stmt.order_by(desc(BlockchainAnchorRecordModel.created_at)).limit(max(limit, 1))
        return [self._to_domain(record) for record in self.db.execute(stmt).scalars().all()]

    @staticmethod
    def _to_domain(record: BlockchainAnchorRecordModel) -> BlockchainAnchorRecord:
        return BlockchainAnchorRecord(
            anchor_id=record.anchor_id,
            tenant_id=record.tenant_id,
            subject_type=record.subject_type,
            subject_ref=record.subject_ref,
            network_profile=record.network_profile,
            payload_hash_algorithm=record.payload_hash_algorithm,
            canonical_payload_hash=record.canonical_payload_hash,
            private_payload_hash=record.private_payload_hash,
            anchor_payload=dict(record.anchor_payload or {}),
            adapter_hint=BlockchainAdapterHint(**dict(record.adapter_hint or {})),
            status=record.status,
            created_at=record.created_at.isoformat() if record.created_at else "",
        )
