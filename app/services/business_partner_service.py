"""Service layer for BusinessPartner aggregate management."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, EntityNotFoundError
from app.core.uuid7 import uuid7
from app.infrastructure.models import (
    BusinessPartner,
    BusinessPartnerAddress,
    BusinessPartnerBillingConfig,
    BusinessPartnerContact,
    BusinessPartnerCpdAccount,
    BusinessPartnerDiscountItem,
    BusinessPartnerInstruction,
    BusinessPartnerPriceAgreement,
)
from app.repositories.business_partner_repository import BusinessPartnerRepository

logger = logging.getLogger(__name__)


class BusinessPartnerService:
    """Facade over BusinessPartnerRepository with additional aggregate operations."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self.repo = BusinessPartnerRepository(db, tenant_id)

    # ── core CRUD ─────────────────────────────────────────────────────────────

    def list_partners(
        self,
        query: Optional[str] = None,
        is_customer: Optional[bool] = None,
        is_supplier: Optional[bool] = None,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[BusinessPartner], int]:
        return self.repo.search(
            query=query,
            is_customer=is_customer,
            is_supplier=is_supplier,
            status=status,
            skip=skip,
            limit=limit,
        )

    def get_partner(self, partner_id: str) -> BusinessPartner:
        return self.repo.get_by_id(partner_id)

    def create_partner(self, payload: dict) -> BusinessPartner:
        existing = self.repo.get_by_partner_number(payload.get("partner_number", ""))
        if existing:
            raise ConflictError(f"partner_number '{payload['partner_number']}' already exists")
        partner_id = payload.pop("partner_id", None) or uuid7()
        partner = BusinessPartner(partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        try:
            return self.repo.create(partner)
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Business partner with this number already exists") from exc

    def update_partner(self, partner_id: str, data: dict) -> BusinessPartner:
        partner = self.repo.get_by_id(partner_id)
        return self.repo.update(partner, data)

    def delete_partner(self, partner_id: str) -> None:
        self.repo.delete(partner_id)

    # ── discount items ────────────────────────────────────────────────────────

    def list_discount_items(self, partner_id: str) -> List[BusinessPartnerDiscountItem]:
        self.repo.get_by_id(partner_id)  # ownership check
        return (
            self.db.query(BusinessPartnerDiscountItem)
            .filter(
                BusinessPartnerDiscountItem.partner_id == partner_id,
                BusinessPartnerDiscountItem.tenant_id == self.tenant_id,
            )
            .all()
        )

    def get_discount_item(self, item_id: str) -> BusinessPartnerDiscountItem:
        obj = self.db.query(BusinessPartnerDiscountItem).filter(
            BusinessPartnerDiscountItem.id == item_id,
            BusinessPartnerDiscountItem.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerDiscountItem", item_id)
        return obj

    def create_discount_item(self, partner_id: str, payload: dict) -> BusinessPartnerDiscountItem:
        self.repo.get_by_id(partner_id)
        item = BusinessPartnerDiscountItem(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def update_discount_item(self, item_id: str, data: dict) -> BusinessPartnerDiscountItem:
        item = self.get_discount_item(item_id)
        for k, v in data.items():
            setattr(item, k, v)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_discount_item(self, item_id: str) -> None:
        item = self.get_discount_item(item_id)
        self.db.delete(item)
        self.db.commit()

    # ── price agreements ──────────────────────────────────────────────────────

    def list_price_agreements(self, partner_id: str) -> List[BusinessPartnerPriceAgreement]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerPriceAgreement)
            .filter(
                BusinessPartnerPriceAgreement.partner_id == partner_id,
                BusinessPartnerPriceAgreement.tenant_id == self.tenant_id,
            )
            .all()
        )

    def get_price_agreement(self, agreement_id: str) -> BusinessPartnerPriceAgreement:
        obj = self.db.query(BusinessPartnerPriceAgreement).filter(
            BusinessPartnerPriceAgreement.id == agreement_id,
            BusinessPartnerPriceAgreement.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerPriceAgreement", agreement_id)
        return obj

    def create_price_agreement(self, partner_id: str, payload: dict) -> BusinessPartnerPriceAgreement:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerPriceAgreement(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_price_agreement(self, agreement_id: str, data: dict) -> BusinessPartnerPriceAgreement:
        obj = self.get_price_agreement(agreement_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_price_agreement(self, agreement_id: str) -> None:
        obj = self.get_price_agreement(agreement_id)
        self.db.delete(obj)
        self.db.commit()

    # ── instructions ──────────────────────────────────────────────────────────

    def list_instructions(self, partner_id: str) -> List[BusinessPartnerInstruction]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerInstruction)
            .filter(
                BusinessPartnerInstruction.partner_id == partner_id,
                BusinessPartnerInstruction.tenant_id == self.tenant_id,
            )
            .all()
        )

    def get_instruction(self, instruction_id: str) -> BusinessPartnerInstruction:
        obj = self.db.query(BusinessPartnerInstruction).filter(
            BusinessPartnerInstruction.id == instruction_id,
            BusinessPartnerInstruction.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerInstruction", instruction_id)
        return obj

    def create_instruction(self, partner_id: str, payload: dict) -> BusinessPartnerInstruction:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerInstruction(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_instruction(self, instruction_id: str, data: dict) -> BusinessPartnerInstruction:
        obj = self.get_instruction(instruction_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_instruction(self, instruction_id: str) -> None:
        obj = self.get_instruction(instruction_id)
        self.db.delete(obj)
        self.db.commit()

    # ── contacts ──────────────────────────────────────────────────────────────

    def list_contacts(self, partner_id: str) -> List[BusinessPartnerContact]:
        self.repo.get_by_id(partner_id)
        return self.repo.list_contacts(partner_id)

    def get_contact(self, contact_id: str) -> BusinessPartnerContact:
        obj = self.db.query(BusinessPartnerContact).filter(
            BusinessPartnerContact.id == contact_id,
            BusinessPartnerContact.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerContact", contact_id)
        return obj

    def create_contact(self, partner_id: str, payload: dict) -> BusinessPartnerContact:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerContact(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_contact(self, contact_id: str, data: dict) -> BusinessPartnerContact:
        obj = self.get_contact(contact_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_contact(self, contact_id: str) -> None:
        obj = self.get_contact(contact_id)
        self.db.delete(obj)
        self.db.commit()

    # ── addresses ─────────────────────────────────────────────────────────────

    def list_addresses(self, partner_id: str) -> List[BusinessPartnerAddress]:
        self.repo.get_by_id(partner_id)
        return self.repo.list_addresses(partner_id)

    def get_address(self, address_id: str) -> BusinessPartnerAddress:
        obj = self.db.query(BusinessPartnerAddress).filter(
            BusinessPartnerAddress.id == address_id,
            BusinessPartnerAddress.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerAddress", address_id)
        return obj

    def create_address(self, partner_id: str, payload: dict) -> BusinessPartnerAddress:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerAddress(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **payload)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_address(self, address_id: str, data: dict) -> BusinessPartnerAddress:
        obj = self.get_address(address_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_address(self, address_id: str) -> None:
        obj = self.get_address(address_id)
        self.db.delete(obj)
        self.db.commit()
