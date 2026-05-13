"""Repository for BusinessPartner aggregate and its related sub-entities."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundError
from app.core.repository import BaseRepository
from app.infrastructure.models import (
    BusinessPartner,
    BusinessPartnerAddress,
    BusinessPartnerContact,
)


class BusinessPartnerRepository(BaseRepository[BusinessPartner]):
    model = BusinessPartner

    # ── search ────────────────────────────────────────────────────────────────

    def search(
        self,
        query: Optional[str] = None,
        is_customer: Optional[bool] = None,
        is_supplier: Optional[bool] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[BusinessPartner], int]:
        q = self._base_query()
        if query:
            term = f"%{query}%"
            q = q.filter(
                or_(
                    BusinessPartner.name_1.ilike(term),
                    BusinessPartner.partner_number.ilike(term),
                    BusinessPartner.matchcode.ilike(term),
                )
            )
        if is_customer is not None:
            q = q.filter(BusinessPartner.is_customer == is_customer)
        if is_supplier is not None:
            q = q.filter(BusinessPartner.is_supplier == is_supplier)
        if status:
            q = q.filter(BusinessPartner.status == status)
        total = q.count()
        items = q.order_by(BusinessPartner.name_1).offset(skip).limit(limit).all()
        return items, total

    def get_by_partner_number(self, partner_number: str) -> Optional[BusinessPartner]:
        return self._base_query().filter(
            BusinessPartner.partner_number == partner_number
        ).first()

    # ── related entities ──────────────────────────────────────────────────────

    def list_addresses(self, partner_id: str) -> List[BusinessPartnerAddress]:
        return (
            self.db.query(BusinessPartnerAddress)
            .filter(
                BusinessPartnerAddress.partner_id == partner_id,
                BusinessPartnerAddress.tenant_id == self.tenant_id,
            )
            .all()
        )

    def list_contacts(self, partner_id: str) -> List[BusinessPartnerContact]:
        return (
            self.db.query(BusinessPartnerContact)
            .filter(
                BusinessPartnerContact.partner_id == partner_id,
                BusinessPartnerContact.tenant_id == self.tenant_id,
            )
            .all()
        )

    def get_partner_or_404(self, partner_id: str) -> BusinessPartner:
        obj = self._base_query().filter(BusinessPartner.id == partner_id).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartner", partner_id)
        return obj
