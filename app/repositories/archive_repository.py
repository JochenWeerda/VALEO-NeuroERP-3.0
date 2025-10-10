"""
Archive Repository
Archive-Index-Operations
"""

from __future__ import annotations
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid

from app.models.documents import ArchiveIndex


class ArchiveRepository:
    """Repository für Archiv-Index"""

    def __init__(self, db: Session):
        self.db = db

    def add_entry(
        self,
        domain: str,
        doc_number: str,
        ts: int,
        file_path: str,
        sha256: str,
        user: str,
    ) -> ArchiveIndex:
        """Fügt Archiv-Eintrag hinzu"""
        entry = ArchiveIndex(
            id=str(uuid.uuid4()),
            domain=domain,
            doc_number=doc_number,
            ts=ts,
            file_path=file_path,
            sha256=sha256,
            user=user,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def get_history(self, domain: str, doc_number: str) -> List[ArchiveIndex]:
        """Holt Archiv-Historie"""
        stmt = (
            select(ArchiveIndex)
            .where(
                ArchiveIndex.domain == domain, ArchiveIndex.doc_number == doc_number
            )
            .order_by(ArchiveIndex.ts.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def verify_hash(self, domain: str, doc_number: str, sha256: str) -> bool:
        """Verifiziert SHA-256 Hash"""
        stmt = select(ArchiveIndex).where(
            ArchiveIndex.domain == domain,
            ArchiveIndex.doc_number == doc_number,
            ArchiveIndex.sha256 == sha256,
        )
        entry = self.db.execute(stmt).scalar_one_or_none()
        return entry is not None

