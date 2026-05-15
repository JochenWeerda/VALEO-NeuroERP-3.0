"""Service layer for compat POS domain routes."""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError
from app.core.uuid7 import uuid7
from app.services.compat_helpers import enqueue_event, list_docs, now_iso, doc_repo, safe_float

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

    # ── Tagesabschluss (with FiBu integration) ───────────────────────────────

    async def create_tagesabschluss(self, payload: dict) -> dict:
        """Create daily closing entry and write FiBu journal entries."""
        abschluss_id = uuid7()
        total_sales = safe_float(payload.get("total_sales", 0))
        total_cash = safe_float(payload.get("total_cash", 0))
        total_card = safe_float(payload.get("total_card", 0))
        closing_date = payload.get("closing_date", now_iso()[:10])

        # Write FiBu journal entries
        await self._write_fibu_entries(abschluss_id, closing_date, total_sales,
                                       total_cash, total_card)

        repo = doc_repo(self.db)
        doc = {
            "id": abschluss_id,
            "tenantId": self.tenant_id,
            "status": "ABGESCHLOSSEN",
            "total_sales": total_sales,
            "total_cash": total_cash,
            "total_card": total_card,
            "closing_date": closing_date,
            "created_at": now_iso(),
            **{k: v for k, v in payload.items()
               if k not in ("total_sales", "total_cash", "total_card", "closing_date")},
        }
        repo.save("pos_tagesabschluss", abschluss_id, doc)
        await enqueue_event(self.db, event_type="pos.tagesabschluss.created",
                            aggregate_id=abschluss_id, payload=doc, tenant_id=self.tenant_id)
        return doc

    async def _write_fibu_entries(
        self,
        abschluss_id: str,
        closing_date: str,
        total_sales: float,
        total_cash: float,
        total_card: float,
    ) -> None:
        from sqlalchemy import text
        journal_id = uuid7()
        try:
            self.db.execute(
                text("""INSERT INTO domain_erp.journal_entries
                        (id, tenant_id, entry_date, description, status, source_doc_id, source_doc_type)
                        VALUES (:id, :tid, :dt, :desc, 'POSTED', :src_id, 'pos_tagesabschluss')"""),
                {"id": journal_id, "tid": self.tenant_id, "dt": closing_date,
                 "desc": f"POS Tagesabschluss {closing_date}", "src_id": abschluss_id},
            )
            lines = [
                (uuid7(), journal_id, "4000", "Umsatz POS", total_sales, 0.0),
                (uuid7(), journal_id, "1000", "Kasse", total_cash, 0.0),
                (uuid7(), journal_id, "1200", "Kartenzahlung", total_card, 0.0),
            ]
            for line_id, jid, account, desc, debit, credit in lines:
                self.db.execute(
                    text("""INSERT INTO domain_erp.journal_entry_lines
                            (id, journal_entry_id, account_code, description, debit, credit)
                            VALUES (:id, :jid, :acc, :desc, :deb, :cred)"""),
                    {"id": line_id, "jid": jid, "acc": account, "desc": desc,
                     "deb": debit, "cred": credit},
                )
            self.db.flush()
        except Exception as exc:
            logger.warning("FiBu journal write failed for Tagesabschluss %s: %s", abschluss_id, exc)

    def list_tagesabschluesse(self) -> list:
        return list_docs(self.db, "pos_tagesabschluss", tenant_id=self.tenant_id)
