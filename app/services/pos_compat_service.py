"""Service layer for compat POS domain routes."""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError
from app.core.uuid7 import uuid7
from app.services.compat_helpers import list_docs, now_iso, doc_repo

logger = logging.getLogger(__name__)


class PosCompatService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    # ── Suspended Sales ───────────────────────────────────────────────────────

    def list_suspended_sales(self) -> list:
        return list_docs(self.db, "pos_suspended_sale", tenant_id=self.tenant_id)

    def get_suspended_sale(self, sale_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("pos_suspended_sale", sale_id)
        if doc is None:
            raise EntityNotFoundError(f"Suspended sale {sale_id} not found")
        return doc

    async def suspend_sale(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "SUSPENDED",
               "suspended_at": now_iso(), **payload}
        repo.save("pos_suspended_sale", doc["id"], doc)
        return doc

    async def resume_sale(self, sale_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("pos_suspended_sale", sale_id)
        if doc is None:
            raise EntityNotFoundError(f"Suspended sale {sale_id} not found")
        if doc.get("status") == "RESUMED":
            raise ConflictError("Sale already resumed")
        doc["status"] = "RESUMED"
        doc["resumed_at"] = now_iso()
        repo.save("pos_suspended_sale", sale_id, doc)
        return doc

    def delete_suspended_sale(self, sale_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("pos_suspended_sale", sale_id)
        if doc is None:
            raise EntityNotFoundError(f"Suspended sale {sale_id} not found")
        repo.delete("pos_suspended_sale", sale_id)
        return {"deleted": True, "id": sale_id}

    # ── Tagesabschluss ──────────────────────────────────────────────────────
    #
    # Hier lagen bis 2026-09-10 ein zweites ``create_tagesabschluss`` und ein
    # ``_write_fibu_entries``. Beide stammten aus dem Service-Layer-Refactor
    # 2803a3433 und wurden nie verdrahtet; ausserdem waren sie defekt
    # (nicht existierende Spalten, fehlende NOT-NULL-Felder, keine tenant_id,
    # drei Zeilen samtlich im Soll). Entfernt in POS-FIBU-CLEANUP-20260910.
    #
    # Gebucht wird ausschliesslich ueber ``POST /pos/tagesabschluss`` in
    # ``app/api/v1/endpoints/compat.py`` mit den Buchungssaetzen aus
    # ``app/services/pos_accounting_service.build_pos_closing_lines``.

    def list_tagesabschluesse(self) -> list:
        return list_docs(self.db, "pos_tagesabschluss", tenant_id=self.tenant_id)
