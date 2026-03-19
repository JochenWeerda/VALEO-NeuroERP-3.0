"""
Repository for persistent knowledge core objects.
"""

from __future__ import annotations

from datetime import datetime, timezone
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
from app.models.knowledge import (
    KnowledgeImprovementProposalRecord,
    KnowledgeObjectRecord,
    KnowledgeVersionRecord,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


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

    def list_proposals(self) -> list[KnowledgeImprovementProposalRecord]:
        stmt = select(KnowledgeImprovementProposalRecord).order_by(KnowledgeImprovementProposalRecord.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get_proposal(self, proposal_id: str) -> KnowledgeImprovementProposalRecord | None:
        stmt = select(KnowledgeImprovementProposalRecord).where(
            KnowledgeImprovementProposalRecord.proposal_id == proposal_id
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def create_proposal(
        self,
        *,
        tenant_id: str,
        titel: str,
        typ: str,
        format: str,
        inhalt: str,
        target_knowledge_id: str | None = None,
        beschreibung: str = "",
        tags: list[str] | None = None,
        zielrollen: list[str] | None = None,
        strukturierte_daten: dict[str, Any] | None = None,
        quelle: str = "improvement-workflow",
        vorgeschlagen_von_typ: str = "human",
        vorgeschlagen_von_ref: str = "unknown",
        vorgeschlagen_von_rolle: str | None = None,
        kanal: str | None = None,
        begruendung: str = "",
    ) -> KnowledgeImprovementProposalRecord:
        record = KnowledgeImprovementProposalRecord(
            tenant_id=tenant_id,
            target_knowledge_id=target_knowledge_id,
            titel=titel,
            typ=typ,
            status="EINGEREICHT",
            beschreibung=beschreibung,
            tags=list(tags or []),
            zielrollen=list(zielrollen or []),
            format=format,
            inhalt=inhalt,
            strukturierte_daten=dict(strukturierte_daten or {}),
            quelle=quelle,
            vorgeschlagen_von_typ=vorgeschlagen_von_typ,
            vorgeschlagen_von_ref=vorgeschlagen_von_ref,
            vorgeschlagen_von_rolle=vorgeschlagen_von_rolle,
            kanal=kanal,
            begruendung=begruendung,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def review_proposal(
        self,
        proposal_id: str,
        *,
        entscheidung: str,
        reviewer_ref: str,
        reviewer_rolle: str | None = None,
        review_notiz: str | None = None,
    ) -> tuple[KnowledgeImprovementProposalRecord | None, KnowledgeObjectRecord | None]:
        proposal = self.get_proposal(proposal_id)
        if proposal is None:
            return None, None

        normalized = entscheidung.strip().upper()
        proposal.reviewer_ref = reviewer_ref
        proposal.reviewer_rolle = reviewer_rolle
        proposal.review_notiz = review_notiz
        proposal.reviewed_at = _utcnow()

        if normalized == "ABGELEHNT":
            proposal.status = "ABGELEHNT"
            self.db.commit()
            self.db.refresh(proposal)
            return proposal, None

        if normalized != "GENEHMIGT":
            raise ValueError("Ungueltige Entscheidung")

        applied_record: KnowledgeObjectRecord | None = None
        if proposal.target_knowledge_id:
            applied_record = self.add_version(
                proposal.target_knowledge_id,
                {
                    "format": proposal.format,
                    "inhalt": proposal.inhalt,
                    "strukturierte_daten": dict(proposal.strukturierte_daten or {}),
                    "quelle": proposal.quelle,
                    "status": KnowledgeStatus.FREIGEGEBEN.value,
                },
            )
        else:
            knowledge_id = f"KNW-IMP-{proposal.proposal_id[-8:].upper()}"
            applied_record = self.create_object(
                knowledge_id=knowledge_id,
                titel=proposal.titel,
                typ=proposal.typ,
                status=KnowledgeStatus.FREIGEGEBEN.value,
                tenant_id=proposal.tenant_id,
                beschreibung=proposal.beschreibung or proposal.begruendung or "",
                tags=list(proposal.tags or []),
                zielrollen=list(proposal.zielrollen or []),
                agentenfreigabe=True,
                version_payload={
                    "version": 1,
                    "format": proposal.format,
                    "inhalt": proposal.inhalt,
                    "strukturierte_daten": dict(proposal.strukturierte_daten or {}),
                    "quelle": proposal.quelle,
                },
            )

        if applied_record is None:
            raise ValueError("Ziel-Wissensobjekt konnte nicht angewendet werden")

        proposal.status = "UEBERNOMMEN"
        proposal.applied_knowledge_id = applied_record.knowledge_id
        proposal.applied_version = max(
            (version.version for version in applied_record.versionen),
            default=1,
        )
        self.db.add(proposal)
        self.db.commit()
        self.db.refresh(proposal)
        self.db.refresh(applied_record)
        return proposal, applied_record

    def proposal_as_dict(self, proposal: KnowledgeImprovementProposalRecord) -> dict[str, Any]:
        return {
            "proposal_id": proposal.proposal_id,
            "tenant_id": proposal.tenant_id,
            "target_knowledge_id": proposal.target_knowledge_id,
            "titel": proposal.titel,
            "typ": proposal.typ,
            "status": proposal.status,
            "beschreibung": proposal.beschreibung or "",
            "tags": list(proposal.tags or []),
            "zielrollen": list(proposal.zielrollen or []),
            "format": proposal.format,
            "inhalt": proposal.inhalt,
            "strukturierte_daten": dict(proposal.strukturierte_daten or {}),
            "quelle": proposal.quelle,
            "vorgeschlagen_von_typ": proposal.vorgeschlagen_von_typ,
            "vorgeschlagen_von_ref": proposal.vorgeschlagen_von_ref,
            "vorgeschlagen_von_rolle": proposal.vorgeschlagen_von_rolle,
            "kanal": proposal.kanal,
            "begruendung": proposal.begruendung or "",
            "reviewer_ref": proposal.reviewer_ref,
            "reviewer_rolle": proposal.reviewer_rolle,
            "review_notiz": proposal.review_notiz,
            "reviewed_at": proposal.reviewed_at.isoformat() if proposal.reviewed_at else None,
            "applied_knowledge_id": proposal.applied_knowledge_id,
            "applied_version": proposal.applied_version,
            "created_at": proposal.created_at.isoformat() if proposal.created_at else None,
        }
