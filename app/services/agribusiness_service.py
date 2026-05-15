"""Service layer for compat agribusiness/setup/management domain routes."""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.core.uuid7 import uuid7
from app.services.compat_helpers import enqueue_event, list_docs, now_iso, doc_repo, safe_float

logger = logging.getLogger(__name__)


class AgribusinessService:
    """Field-service tasks, management dashboard, notifications."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Field Service Tasks ───────────────────────────────────────────────────

    def list_field_service_tasks(self, status: Optional[str] = None) -> list:
        tasks = list_docs(self.db, "field_service_task", tenant_id=self.tenant_id)
        if status:
            tasks = [t for t in tasks if t.get("status") == status]
        return tasks

    def get_field_service_task(self, task_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("field_service_task", task_id)
        if doc is None:
            raise EntityNotFoundError(f"Field service task {task_id} not found")
        return doc

    async def create_field_service_task(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "OFFEN",
               "created_at": now_iso(), **payload}
        repo.save("field_service_task", doc["id"], doc)
        await enqueue_event(self.db, event_type="field_service_task.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    def update_field_service_task(self, task_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("field_service_task", task_id)
        if doc is None:
            raise EntityNotFoundError(f"Field service task {task_id} not found")
        doc = {**doc, **payload, "updated_at": now_iso()}
        repo.save("field_service_task", task_id, doc)
        return doc

    async def complete_field_service_task(self, task_id: str, completion_data: dict) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("field_service_task", task_id)
        if doc is None:
            raise EntityNotFoundError(f"Field service task {task_id} not found")
        doc["status"] = "ABGESCHLOSSEN"
        doc["completion"] = completion_data
        doc["completed_at"] = now_iso()
        repo.save("field_service_task", task_id, doc)
        await enqueue_event(self.db, event_type="field_service_task.completed",
                            aggregate_id=task_id, payload=doc, tenant_id=self.tenant_id)
        return doc

    # ── Management Dashboard ──────────────────────────────────────────────────

    def get_management_dashboard(self) -> dict:
        from sqlalchemy import text
        try:
            row = self.db.execute(
                text("""SELECT
                    COUNT(*) FILTER (WHERE status = 'OFFEN') AS open_tasks,
                    COUNT(*) FILTER (WHERE status = 'ABGESCHLOSSEN') AS completed_tasks
                    FROM field_service_tasks WHERE tenant_id = :tid"""),
                {"tid": self.tenant_id},
            ).fetchone()
            task_stats = dict(row._mapping) if row else {}
        except Exception:
            task_stats = {}

        notifications = list_docs(self.db, "benachrichtigung", tenant_id=self.tenant_id)
        unread = len([n for n in notifications if not n.get("gelesen")])

        return {
            "task_stats": task_stats,
            "unread_notifications": unread,
            "generated_at": now_iso(),
        }

    # ── Benachrichtigungen ────────────────────────────────────────────────────

    def list_benachrichtigungen(self, nur_ungelesen: bool = False) -> list:
        items = list_docs(self.db, "benachrichtigung", tenant_id=self.tenant_id)
        if nur_ungelesen:
            items = [n for n in items if not n.get("gelesen")]
        return items

    def mark_benachrichtigung_gelesen(self, notification_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("benachrichtigung", notification_id)
        if doc is None:
            raise EntityNotFoundError(f"Benachrichtigung {notification_id} not found")
        doc["gelesen"] = True
        doc["gelesen_at"] = now_iso()
        repo.save("benachrichtigung", notification_id, doc)
        return doc

    def mark_all_gelesen(self) -> dict:
        items = list_docs(self.db, "benachrichtigung", tenant_id=self.tenant_id)
        repo = doc_repo(self.db)
        count = 0
        for item in items:
            if not item.get("gelesen"):
                item["gelesen"] = True
                item["gelesen_at"] = now_iso()
                repo.save("benachrichtigung", item["id"], item)
                count += 1
        return {"marked_read": count}


class SetupCompatService:
    """Service for setup/firma configuration routes."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def get_firma(self) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("firma_config", self.tenant_id)
        return doc or {"tenant_id": self.tenant_id, "configured": False}

    def update_firma(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        existing = repo.get("firma_config", self.tenant_id) or {}
        doc = {**existing, **payload, "tenant_id": self.tenant_id, "updated_at": now_iso()}
        if not existing:
            doc["created_at"] = now_iso()
        repo.save("firma_config", self.tenant_id, doc)
        return doc

    def get_system_info(self) -> dict:
        import sys
        return {
            "tenant_id": self.tenant_id,
            "python_version": sys.version,
            "timestamp": now_iso(),
        }
