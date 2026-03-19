"""
Repository for persistent knowledge core objects.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.knowledge_core_contracts import (
    KnowledgeFormat,
    KnowledgeObject,
    KnowledgeObjectTyp,
    KnowledgeRetrievalRequest,
    KnowledgeStatus,
    KnowledgeVersion,
    retrieve_knowledge_objects,
)
from app.models.knowledge import KnowledgeObjectRecord, KnowledgeVersionRecord


class KnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_objects(self) -> int:
        stmt = select(func.count()).select_from(KnowledgeObjectRecord)
        return int(self.db.execute(stmt).scalar_one())

    def list_objects(self) -> list[KnowledgeObjectRecord]:
        stmt = select(KnowledgeObjectRecord).order_by(KnowledgeObjectRecord.updated_at.desc())
        return list(self.db.execute(stmt).unique().scalars().all())

    def get_object(self, knowledge_id: str) -> KnowledgeObjectRecord | None:
        stmt = select(KnowledgeObjectRecord).where(KnowledgeObjectRecord.knowledge_id == knowledge_id)
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def has_version(self, knowledge_id: str, version: int) -> bool:
        stmt = select(KnowledgeVersionRecord.id).where(
            KnowledgeVersionRecord.knowledge_id == knowledge_id,
            KnowledgeVersionRecord.version == version,
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def create_object(
        self,
        *,
        knowledge_id: str,
        titel: str,
        typ: str,
        status: str,
        tenant_id: str = "system",
        beschreibung: str = "",
        tags: list[str] | None = None,
        zielrollen: list[str] | None = None,
        agentenfreigabe: bool = True,
        version_payload: dict[str, Any],
    ) -> KnowledgeObjectRecord:
        record = KnowledgeObjectRecord(
            knowledge_id=knowledge_id,
            titel=titel,
            typ=typ,
            status=status,
            tenant_id=tenant_id,
            beschreibung=beschreibung,
            tags=list(tags or []),
            zielrollen=list(zielrollen or []),
            agentenfreigabe=agentenfreigabe,
        )
        record.versionen.append(
            KnowledgeVersionRecord(
                version=int(version_payload.get("version", 1)),
                format=version_payload["format"],
                inhalt=version_payload["inhalt"],
                strukturierte_daten=dict(version_payload.get("strukturierte_daten", {})),
                quelle=version_payload.get("quelle", "api"),
            )
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def add_version(self, knowledge_id: str, version_payload: dict[str, Any]) -> KnowledgeObjectRecord | None:
        record = self.get_object(knowledge_id)
        if record is None:
            return None
        requested_version = int(version_payload.get("version", 0))
        if requested_version and self.has_version(knowledge_id, requested_version):
            return record
        naechste_version = max((version.version for version in record.versionen), default=0) + 1
        record.versionen.append(
            KnowledgeVersionRecord(
                version=requested_version or naechste_version,
                format=version_payload["format"],
                inhalt=version_payload["inhalt"],
                strukturierte_daten=dict(version_payload.get("strukturierte_daten", {})),
                quelle=version_payload.get("quelle", "api"),
            )
        )
        if "status" in version_payload and version_payload["status"]:
            record.status = version_payload["status"]
        self.db.commit()
        self.db.refresh(record)
        return record

    def to_domain_object(self, record: KnowledgeObjectRecord) -> KnowledgeObject:
        return KnowledgeObject(
            knowledge_id=record.knowledge_id,
            titel=record.titel,
            typ=KnowledgeObjectTyp(record.typ),
            status=KnowledgeStatus(record.status),
            tenant_id=record.tenant_id,
            beschreibung=record.beschreibung or "",
            tags=list(record.tags or []),
            zielrollen=list(record.zielrollen or []),
            agentenfreigabe=bool(record.agentenfreigabe),
            versionen=[
                KnowledgeVersion(
                    version=version.version,
                    format=KnowledgeFormat(version.format),
                    inhalt=version.inhalt,
                    strukturierte_daten=dict(version.strukturierte_daten or {}),
                    erstellt_am=version.erstellt_am,
                    quelle=version.quelle,
                )
                for version in sorted(record.versionen, key=lambda eintrag: eintrag.version)
            ],
        )

    def list_domain_objects(self) -> list[KnowledgeObject]:
        return [self.to_domain_object(record) for record in self.list_objects()]

    def retrieve(self, request: KnowledgeRetrievalRequest) -> list[dict[str, Any]]:
        return retrieve_knowledge_objects(request, objects=self.list_domain_objects())
