"""
Document Repository
CRUD-Operations für Dokumente mit PostgreSQL
"""

from __future__ import annotations
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid
from datetime import date

from app.models.documents import DocumentHeader, DocumentLine


class DocumentRepository:
    """Repository für Dokumente"""

    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        doc_type: str,
        number: str,
        doc_date: date,
        lines: List[Dict[str, Any]],
        customer_id: Optional[str] = None,
        supplier_id: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> DocumentHeader:
        """Erstellt neues Dokument"""
        header = DocumentHeader(
            id=str(uuid.uuid4()),
            type=doc_type,
            number=number,
            status='draft',
            date=doc_date,
            customer_id=customer_id,
            supplier_id=supplier_id,
            created_by=created_by,
        )

        # Lines erstellen
        for idx, line_data in enumerate(lines):
            line = DocumentLine(
                id=str(uuid.uuid4()),
                header_id=header.id,
                line_number=idx + 1,
                article_id=line_data.get('article'),
                quantity=line_data.get('qty', 0),
                price=line_data.get('price'),
                cost=line_data.get('cost'),
                vat_rate=line_data.get('vatRate'),
            )
            header.lines.append(line)

        # Total berechnen
        header.total = sum(
            (line.quantity or 0) * (line.price or 0) for line in header.lines
        )

        self.db.add(header)
        self.db.commit()
        self.db.refresh(header)
        return header

    def get_by_number(self, doc_type: str, number: str) -> Optional[DocumentHeader]:
        """Holt Dokument nach Nummer"""
        stmt = select(DocumentHeader).where(
            DocumentHeader.type == doc_type, DocumentHeader.number == number
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_id(self, doc_id: str) -> Optional[DocumentHeader]:
        """Holt Dokument nach ID"""
        return self.db.get(DocumentHeader, doc_id)

    def update_status(self, doc_id: str, status: str) -> bool:
        """Aktualisiert Dokument-Status"""
        doc = self.db.get(DocumentHeader, doc_id)
        if not doc:
            return False
        doc.status = status
        self.db.commit()
        return True

    def list_by_type(
        self, doc_type: str, limit: int = 100, offset: int = 0
    ) -> List[DocumentHeader]:
        """Listet Dokumente nach Typ"""
        stmt = (
            select(DocumentHeader)
            .where(DocumentHeader.type == doc_type)
            .order_by(DocumentHeader.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(self.db.execute(stmt).scalars().all())

    def to_dict(self, doc: DocumentHeader) -> Dict[str, Any]:
        """Konvertiert Dokument zu Dictionary"""
        return {
            'id': doc.id,
            'type': doc.type,
            'number': doc.number,
            'status': doc.status,
            'date': doc.date.isoformat() if doc.date else None,
            'customer_id': doc.customer_id,
            'supplier_id': doc.supplier_id,
            'total': float(doc.total) if doc.total else None,
            'lines': [
                {
                    'article': line.article_id,
                    'qty': float(line.quantity) if line.quantity else 0,
                    'price': float(line.price) if line.price else None,
                    'cost': float(line.cost) if line.cost else None,
                    'vatRate': float(line.vat_rate) if line.vat_rate else None,
                }
                for line in doc.lines
            ],
        }

