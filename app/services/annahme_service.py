"""Service layer for compat Annahme (goods intake) and LKW queue routes."""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError, ValidationFailedError
from app.core.uuid7 import uuid7
from app.services.compat_helpers import enqueue_event, list_docs, now_iso, doc_repo

logger = logging.getLogger(__name__)


class AnnahmeService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── LKW Queue ─────────────────────────────────────────────────────────────

    def list_lkw_queue(self) -> list:
        return list_docs(self.db, "lkw_queue", tenant_id=self.tenant_id)

    def get_lkw_entry(self, entry_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("lkw_queue", entry_id)
        if doc is None:
            raise EntityNotFoundError(f"LKW queue entry {entry_id} not found")
        return doc

    async def register_lkw(self, payload: dict) -> dict:
        """Register a truck in the intake queue, resolving article reference."""
        artikel_id = payload.get("artikel_id")
        if not artikel_id:
            artikel_name = payload.get("artikel_name", "")
            if artikel_name:
                artikel_id = await self._resolve_article(artikel_name)
        repo = doc_repo(self.db)
        doc = {
            "id": uuid7(),
            "tenantId": self.tenant_id,
            "status": "WARTEND",
            "artikel_id": artikel_id,
            "created_at": now_iso(),
            **{k: v for k, v in payload.items() if k != "artikel_id"},
        }
        repo.save("lkw_queue", doc["id"], doc)
        await enqueue_event(self.db, event_type="lkw.registered",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    async def _resolve_article(self, artikel_name: str) -> Optional[str]:
        from sqlalchemy import text
        row = self.db.execute(
            text("SELECT id FROM artikel WHERE name ILIKE :name AND tenant_id = :tid LIMIT 1"),
            {"name": f"%{artikel_name}%", "tid": self.tenant_id},
        ).fetchone()
        return str(row[0]) if row else None

    def call_lkw(self, entry_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("lkw_queue", entry_id)
        if doc is None:
            raise EntityNotFoundError(f"LKW queue entry {entry_id} not found")
        if doc.get("status") != "WARTEND":
            raise ConflictError(f"Cannot call LKW in status '{doc.get('status')}'")
        doc["status"] = "GERUFEN"
        doc["called_at"] = now_iso()
        repo.save("lkw_queue", entry_id, doc)
        return doc

    def complete_lkw(self, entry_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("lkw_queue", entry_id)
        if doc is None:
            raise EntityNotFoundError(f"LKW queue entry {entry_id} not found")
        doc["status"] = "ABGEFERTIGT"
        doc["completed_at"] = now_iso()
        repo.save("lkw_queue", entry_id, doc)
        return doc

    def remove_lkw(self, entry_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("lkw_queue", entry_id)
        if doc is None:
            raise EntityNotFoundError(f"LKW queue entry {entry_id} not found")
        repo.delete("lkw_queue", entry_id)
        return {"deleted": True, "id": entry_id}

    # ── Qualitaets-Check ──────────────────────────────────────────────────────

    def list_qualitaets_checks(self) -> list:
        return list_docs(self.db, "qualitaets_check", tenant_id=self.tenant_id)

    async def create_qualitaets_check(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "OFFEN",
               "created_at": now_iso(), **payload}
        repo.save("qualitaets_check", doc["id"], doc)
        await enqueue_event(self.db, event_type="qualitaets_check.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    def get_qualitaets_check(self, check_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("qualitaets_check", check_id)
        if doc is None:
            raise EntityNotFoundError(f"Qualitaets-Check {check_id} not found")
        return doc

    async def complete_qualitaets_check(self, check_id: str, result: dict) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("qualitaets_check", check_id)
        if doc is None:
            raise EntityNotFoundError(f"Qualitaets-Check {check_id} not found")
        doc["status"] = "ABGESCHLOSSEN"
        doc["result"] = result
        doc["completed_at"] = now_iso()
        repo.save("qualitaets_check", check_id, doc)
        await enqueue_event(self.db, event_type="qualitaets_check.completed",
                            aggregate_id=check_id, payload=doc, tenant_id=self.tenant_id)
        return doc
