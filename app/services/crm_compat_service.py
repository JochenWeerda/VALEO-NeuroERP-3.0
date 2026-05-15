"""Service layer for compat CRM domain routes."""
from __future__ import annotations

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.core.uuid7 import uuid7
from app.services.compat_helpers import enqueue_event, list_docs, now_iso, doc_repo

logger = logging.getLogger(__name__)


class CrmCompatService:
    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id

    def get_crm_dashboard(self) -> dict:
        try:
            from app.core.crm_core_client import crm_get_dashboard
            return crm_get_dashboard(tenant_id=self.tenant_id)
        except Exception:
            pass
        customers = list_docs(self.db, "crm_customer", tenant_id=self.tenant_id)
        cases = list_docs(self.db, "crm_case", tenant_id=self.tenant_id)
        return {
            "total_customers": len(customers),
            "open_cases": len([c for c in cases if c.get("status") == "OFFEN"]),
            "generated_at": now_iso(),
        }

    def list_customers(self, search: Optional[str] = None, limit: int = 100) -> list:
        try:
            from app.core.crm_core_client import crm_list_customers
            return crm_list_customers(tenant_id=self.tenant_id, search=search, limit=limit)
        except Exception:
            pass
        customers = list_docs(self.db, "crm_customer", tenant_id=self.tenant_id)
        if search:
            s = search.lower()
            customers = [c for c in customers
                         if s in (c.get("name") or "").lower()
                         or s in (c.get("email") or "").lower()]
        return customers[:limit]

    def get_customer(self, customer_id: str) -> dict:
        try:
            from app.core.crm_core_client import crm_get_customer
            return crm_get_customer(customer_id, tenant_id=self.tenant_id)
        except Exception:
            pass
        repo = doc_repo(self.db)
        doc = repo.get("crm_customer", customer_id)
        if doc is None:
            raise EntityNotFoundError(f"Customer {customer_id} not found")
        return doc

    def list_cases(self, status: Optional[str] = None) -> list:
        cases = list_docs(self.db, "crm_case", tenant_id=self.tenant_id)
        if status:
            cases = [c for c in cases if c.get("status") == status]
        return cases

    async def create_case(self, payload: dict) -> dict:
        try:
            from app.core.crm_core_client import crm_create_case
            return crm_create_case(payload, tenant_id=self.tenant_id)
        except Exception:
            pass
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "status": "OFFEN",
               "created_at": now_iso(), **payload}
        repo.save("crm_case", doc["id"], doc)
        await enqueue_event(self.db, event_type="crm_case.created",
                            aggregate_id=doc["id"], payload=doc, tenant_id=self.tenant_id)
        return doc

    def get_case(self, case_id: str) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("crm_case", case_id)
        if doc is None:
            raise EntityNotFoundError(f"Case {case_id} not found")
        return doc

    def update_case(self, case_id: str, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = repo.get("crm_case", case_id)
        if doc is None:
            raise EntityNotFoundError(f"Case {case_id} not found")
        doc = {**doc, **payload, "updated_at": now_iso()}
        repo.save("crm_case", case_id, doc)
        return doc

    def list_activities(self, customer_id: Optional[str] = None) -> list:
        activities = list_docs(self.db, "crm_activity", tenant_id=self.tenant_id)
        if customer_id:
            activities = [a for a in activities if a.get("customer_id") == customer_id]
        return activities

    async def create_activity(self, payload: dict) -> dict:
        repo = doc_repo(self.db)
        doc = {"id": uuid7(), "tenantId": self.tenant_id, "created_at": now_iso(), **payload}
        repo.save("crm_activity", doc["id"], doc)
        return doc
