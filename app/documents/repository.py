"""
Document Repository
Datenbank-Zugriff für Dokumente (Sales, Purchase)
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Repository für Dokument-Verwaltung"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save_document(self, doc_type: str, doc_number: str, data: dict) -> dict:
        """Speichert oder aktualisiert ein Dokument"""
        try:
            import uuid
            
            # Prüfe ob Dokument existiert
            existing = self.db.execute(
                text("""
                    SELECT id, data FROM documents 
                    WHERE doc_type = :doc_type AND doc_number = :doc_number
                """),
                {"doc_type": doc_type, "doc_number": doc_number}
            ).fetchone()
            
            # Stelle sicher, dass number im data enthalten ist
            data["number"] = doc_number
            data["type"] = doc_type
            
            now = datetime.utcnow()
            
            if existing:
                # Update
                self.db.execute(
                    text("""
                        UPDATE documents 
                        SET data = :data::jsonb, updated_at = :updated_at
                        WHERE id = :id
                    """),
                    {"id": existing.id, "data": json.dumps(data), "updated_at": now}
                )
            else:
                # Insert
                doc_id = str(uuid.uuid4())
                self.db.execute(
                    text("""
                        INSERT INTO documents (id, doc_type, doc_number, data, created_at, updated_at)
                        VALUES (:id, :doc_type, :doc_number, :data::jsonb, :created_at, :updated_at)
                    """),
                    {
                        "id": doc_id,
                        "doc_type": doc_type,
                        "doc_number": doc_number,
                        "data": json.dumps(data),
                        "created_at": now,
                        "updated_at": now
                    }
                )
            
            self.db.commit()
            logger.info(f"Saved document: {doc_type}/{doc_number}")
            return {"ok": True, "number": doc_number}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save document: {e}")
            raise
    
    def get_document(self, doc_type: str, doc_number: str) -> Optional[dict]:
        """Holt ein einzelnes Dokument"""
        try:
            result = self.db.execute(
                text("""
                    SELECT data FROM documents 
                    WHERE doc_type = :doc_type AND doc_number = :doc_number
                """),
                {"doc_type": doc_type, "doc_number": doc_number}
            ).fetchone()
            
            if result:
                # PostgreSQL JSONB wird bereits als dict zurückgegeben
                if isinstance(result.data, dict):
                    return result.data
                return json.loads(result.data) if isinstance(result.data, str) else result.data
            return None
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            raise
    
    def list_documents(
        self, 
        doc_type: str, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[dict]:
        """Listet Dokumente eines Typs"""
        try:
            query = """
                SELECT data FROM documents 
                WHERE doc_type = :doc_type
            """
            params = {"doc_type": doc_type, "skip": skip, "limit": limit}
            
            # Filter hinzufügen falls vorhanden
            if filters:
                if "status" in filters:
                    query += " AND data::jsonb->>'status' = :status"
                    params["status"] = filters["status"]
                if "customerId" in filters:
                    query += " AND data::jsonb->>'customerId' = :customerId"
                    params["customerId"] = filters["customerId"]
            
            query += " ORDER BY created_at DESC LIMIT :limit OFFSET :skip"
            
            results = self.db.execute(text(query), params).fetchall()
            # PostgreSQL JSONB wird bereits als dict zurückgegeben
            return [
                row.data if isinstance(row.data, dict) else json.loads(row.data) 
                for row in results
            ]
        except Exception as e:
            raise
    
    def delete_document(self, doc_type: str, doc_number: str) -> bool:
        """Löscht ein Dokument"""
        try:
            result = self.db.execute(
                text("""
                    DELETE FROM documents 
                    WHERE doc_type = :doc_type AND doc_number = :doc_number
                """),
                {"doc_type": doc_type, "doc_number": doc_number}
            )
            self.db.commit()
            return result.rowcount > 0
        except Exception as e:
            self.db.rollback()
            raise
    
    def count_documents(self, doc_type: str, filters: Optional[Dict[str, Any]] = None) -> int:
        """Zählt Dokumente eines Typs"""
        try:
            query = "SELECT COUNT(*) FROM documents WHERE doc_type = :doc_type"
            params = {"doc_type": doc_type}
            
            if filters:
                if "status" in filters:
                    query += " AND data::jsonb->>'status' = :status"
                    params["status"] = filters["status"]
            
            result = self.db.execute(text(query), params).scalar()
            return result or 0
        except Exception as e:
            raise

