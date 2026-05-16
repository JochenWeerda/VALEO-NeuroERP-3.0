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
    BusinessPartnerCommunity,
    BusinessPartnerCommunityMember,
    BusinessPartnerContact,
    BusinessPartnerCooperativeMembership,
    BusinessPartnerCpdAccount,
    BusinessPartnerDispatchMedium,
    BusinessPartnerDiscountItem,
    BusinessPartnerEmailDistribution,
    BusinessPartnerInstruction,
    BusinessPartnerInterfaceProfile,
    BusinessPartnerInterestSetting,
    BusinessPartnerPriceAgreement,
    BusinessPartnerPricingRule,
    BusinessPartnerProfile,
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

    def list_discount_items(
        self, partner_id: str, article_number: Optional[str] = None
    ) -> List[BusinessPartnerDiscountItem]:
        self.repo.get_by_id(partner_id)  # ownership check
        q = self.db.query(BusinessPartnerDiscountItem).filter(
            BusinessPartnerDiscountItem.partner_id == partner_id,
            BusinessPartnerDiscountItem.tenant_id == self.tenant_id,
        )
        if article_number:
            q = q.filter(BusinessPartnerDiscountItem.article_number.ilike(f"%{article_number}%"))
        return q.order_by(
            BusinessPartnerDiscountItem.article_number.asc(),
            BusinessPartnerDiscountItem.created_at.desc(),
        ).all()

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

    def list_price_agreements(
        self, partner_id: str, article_number: Optional[str] = None
    ) -> List[BusinessPartnerPriceAgreement]:
        self.repo.get_by_id(partner_id)
        q = self.db.query(BusinessPartnerPriceAgreement).filter(
            BusinessPartnerPriceAgreement.partner_id == partner_id,
            BusinessPartnerPriceAgreement.tenant_id == self.tenant_id,
        )
        if article_number:
            q = q.filter(BusinessPartnerPriceAgreement.article_number.ilike(f"%{article_number}%"))
        return q.order_by(
            BusinessPartnerPriceAgreement.article_number.asc(),
            BusinessPartnerPriceAgreement.created_at.desc(),
        ).all()

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

    def list_addresses(
        self, partner_id: str, address_type: Optional[str] = None, skip: int = 0, limit: int = 50
    ) -> List[BusinessPartnerAddress]:
        self.repo.get_by_id(partner_id)
        q = self.db.query(BusinessPartnerAddress).filter(
            BusinessPartnerAddress.partner_id == partner_id,
            BusinessPartnerAddress.tenant_id == self.tenant_id,
        )
        if address_type:
            q = q.filter(BusinessPartnerAddress.address_type == address_type)
        return q.order_by(
            BusinessPartnerAddress.is_default.desc(),
            BusinessPartnerAddress.created_at.asc(),
        ).offset(skip).limit(limit).all()

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

    # ── billing config (singleton upsert) ─────────────────────────────────────

    def get_billing_config(self, partner_id: str) -> BusinessPartnerBillingConfig:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerBillingConfig).filter(
            BusinessPartnerBillingConfig.partner_id == partner_id,
            BusinessPartnerBillingConfig.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerBillingConfig", partner_id)
        return obj

    def upsert_billing_config(self, partner_id: str, data: dict) -> BusinessPartnerBillingConfig:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerBillingConfig).filter(
            BusinessPartnerBillingConfig.partner_id == partner_id,
            BusinessPartnerBillingConfig.tenant_id == self.tenant_id,
        ).first()
        is_new = obj is None
        if is_new:
            obj = BusinessPartnerBillingConfig(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id)
            self.db.add(obj)
        for k, v in data.items():
            if k == "created_by" and not is_new:
                continue
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # ── cpd accounts ──────────────────────────────────────────────────────────

    def list_cpd_accounts(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerCpdAccount]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerCpdAccount)
            .filter(
                BusinessPartnerCpdAccount.partner_id == partner_id,
                BusinessPartnerCpdAccount.tenant_id == self.tenant_id,
            )
            .order_by(BusinessPartnerCpdAccount.cpd_customer_number.asc())
            .offset(skip).limit(limit).all()
        )

    def get_cpd_account(self, account_id: str) -> BusinessPartnerCpdAccount:
        obj = self.db.query(BusinessPartnerCpdAccount).filter(
            BusinessPartnerCpdAccount.id == account_id,
            BusinessPartnerCpdAccount.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerCpdAccount", account_id)
        return obj

    def create_cpd_account(self, partner_id: str, data: dict) -> BusinessPartnerCpdAccount:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerCpdAccount(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_cpd_account(self, account_id: str, data: dict) -> BusinessPartnerCpdAccount:
        obj = self.get_cpd_account(account_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_cpd_account(self, account_id: str) -> None:
        obj = self.get_cpd_account(account_id)
        self.db.delete(obj)
        self.db.commit()

    # ── pricing rules ─────────────────────────────────────────────────────────

    def list_pricing_rules(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerPricingRule]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerPricingRule)
            .filter(
                BusinessPartnerPricingRule.partner_id == partner_id,
                BusinessPartnerPricingRule.tenant_id == self.tenant_id,
            )
            .order_by(BusinessPartnerPricingRule.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_pricing_rule(self, rule_id: str) -> BusinessPartnerPricingRule:
        obj = self.db.query(BusinessPartnerPricingRule).filter(
            BusinessPartnerPricingRule.id == rule_id,
            BusinessPartnerPricingRule.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerPricingRule", rule_id)
        return obj

    def create_pricing_rule(self, partner_id: str, data: dict) -> BusinessPartnerPricingRule:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerPricingRule(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_pricing_rule(self, rule_id: str, data: dict) -> BusinessPartnerPricingRule:
        obj = self.get_pricing_rule(rule_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_pricing_rule(self, rule_id: str) -> None:
        obj = self.get_pricing_rule(rule_id)
        self.db.delete(obj)
        self.db.commit()

    # ── interest settings ─────────────────────────────────────────────────────

    def list_interest_settings(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerInterestSetting]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerInterestSetting)
            .filter(
                BusinessPartnerInterestSetting.partner_id == partner_id,
                BusinessPartnerInterestSetting.tenant_id == self.tenant_id,
            )
            .order_by(BusinessPartnerInterestSetting.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_interest_setting(self, setting_id: str) -> BusinessPartnerInterestSetting:
        obj = self.db.query(BusinessPartnerInterestSetting).filter(
            BusinessPartnerInterestSetting.id == setting_id,
            BusinessPartnerInterestSetting.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerInterestSetting", setting_id)
        return obj

    def create_interest_setting(self, partner_id: str, data: dict) -> BusinessPartnerInterestSetting:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerInterestSetting(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_interest_setting(self, setting_id: str, data: dict) -> BusinessPartnerInterestSetting:
        obj = self.get_interest_setting(setting_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_interest_setting(self, setting_id: str) -> None:
        obj = self.get_interest_setting(setting_id)
        self.db.delete(obj)
        self.db.commit()

    # ── dispatch media ────────────────────────────────────────────────────────

    def list_dispatch_media(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerDispatchMedium]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerDispatchMedium)
            .filter(
                BusinessPartnerDispatchMedium.partner_id == partner_id,
                BusinessPartnerDispatchMedium.tenant_id == self.tenant_id,
            )
            .order_by(
                BusinessPartnerDispatchMedium.document_type.asc(),
                BusinessPartnerDispatchMedium.dispatch_channel.asc(),
            )
            .offset(skip).limit(limit).all()
        )

    def get_dispatch_medium(self, medium_id: str) -> BusinessPartnerDispatchMedium:
        obj = self.db.query(BusinessPartnerDispatchMedium).filter(
            BusinessPartnerDispatchMedium.id == medium_id,
            BusinessPartnerDispatchMedium.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerDispatchMedium", medium_id)
        return obj

    def create_dispatch_medium(self, partner_id: str, data: dict) -> BusinessPartnerDispatchMedium:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerDispatchMedium(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update_dispatch_medium(self, medium_id: str, data: dict) -> BusinessPartnerDispatchMedium:
        obj = self.get_dispatch_medium(medium_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_dispatch_medium(self, medium_id: str) -> None:
        obj = self.get_dispatch_medium(medium_id)
        self.db.delete(obj)
        self.db.commit()

    # ── cooperative memberships ───────────────────────────────────────────────

    def list_cooperative_memberships(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerCooperativeMembership]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerCooperativeMembership)
            .filter(
                BusinessPartnerCooperativeMembership.partner_id == partner_id,
                BusinessPartnerCooperativeMembership.tenant_id == self.tenant_id,
            )
            .order_by(BusinessPartnerCooperativeMembership.created_at.desc())
            .offset(skip).limit(limit).all()
        )

    def get_cooperative_membership(self, membership_id: str) -> BusinessPartnerCooperativeMembership:
        obj = self.db.query(BusinessPartnerCooperativeMembership).filter(
            BusinessPartnerCooperativeMembership.id == membership_id,
            BusinessPartnerCooperativeMembership.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerCooperativeMembership", membership_id)
        return obj

    def create_cooperative_membership(self, partner_id: str, data: dict) -> BusinessPartnerCooperativeMembership:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerCooperativeMembership(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def patch_cooperative_membership(self, membership_id: str, data: dict) -> BusinessPartnerCooperativeMembership:
        obj = self.get_cooperative_membership(membership_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_cooperative_membership(self, membership_id: str) -> None:
        obj = self.get_cooperative_membership(membership_id)
        self.db.delete(obj)
        self.db.commit()

    # ── email distributions ───────────────────────────────────────────────────

    def list_email_distributions(self, partner_id: str, skip: int = 0, limit: int = 50) -> List[BusinessPartnerEmailDistribution]:
        self.repo.get_by_id(partner_id)
        return (
            self.db.query(BusinessPartnerEmailDistribution)
            .filter(
                BusinessPartnerEmailDistribution.partner_id == partner_id,
                BusinessPartnerEmailDistribution.tenant_id == self.tenant_id,
            )
            .order_by(
                BusinessPartnerEmailDistribution.distribution_name.asc(),
                BusinessPartnerEmailDistribution.email.asc(),
            )
            .offset(skip).limit(limit).all()
        )

    def get_email_distribution(self, distribution_id: str) -> BusinessPartnerEmailDistribution:
        obj = self.db.query(BusinessPartnerEmailDistribution).filter(
            BusinessPartnerEmailDistribution.id == distribution_id,
            BusinessPartnerEmailDistribution.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerEmailDistribution", distribution_id)
        return obj

    def create_email_distribution(self, partner_id: str, data: dict) -> BusinessPartnerEmailDistribution:
        self.repo.get_by_id(partner_id)
        obj = BusinessPartnerEmailDistribution(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id, **data)
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def patch_email_distribution(self, distribution_id: str, data: dict) -> BusinessPartnerEmailDistribution:
        obj = self.get_email_distribution(distribution_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete_email_distribution(self, distribution_id: str) -> None:
        obj = self.get_email_distribution(distribution_id)
        self.db.delete(obj)
        self.db.commit()

    # ── profile (singleton upsert) ────────────────────────────────────────────

    def get_profile(self, partner_id: str) -> BusinessPartnerProfile:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerProfile).filter(
            BusinessPartnerProfile.partner_id == partner_id,
            BusinessPartnerProfile.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerProfile", partner_id)
        return obj

    def upsert_profile(self, partner_id: str, data: dict) -> BusinessPartnerProfile:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerProfile).filter(
            BusinessPartnerProfile.partner_id == partner_id,
            BusinessPartnerProfile.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            obj = BusinessPartnerProfile(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id)
            self.db.add(obj)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def patch_profile(self, partner_id: str, data: dict) -> BusinessPartnerProfile:
        obj = self.get_profile(partner_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # ── interface profile (singleton upsert) ──────────────────────────────────

    def get_interface_profile(self, partner_id: str) -> BusinessPartnerInterfaceProfile:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerInterfaceProfile).filter(
            BusinessPartnerInterfaceProfile.partner_id == partner_id,
            BusinessPartnerInterfaceProfile.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            raise EntityNotFoundError("BusinessPartnerInterfaceProfile", partner_id)
        return obj

    def upsert_interface_profile(self, partner_id: str, data: dict) -> BusinessPartnerInterfaceProfile:
        self.repo.get_by_id(partner_id)
        obj = self.db.query(BusinessPartnerInterfaceProfile).filter(
            BusinessPartnerInterfaceProfile.partner_id == partner_id,
            BusinessPartnerInterfaceProfile.tenant_id == self.tenant_id,
        ).first()
        if obj is None:
            obj = BusinessPartnerInterfaceProfile(id=uuid7(), partner_id=partner_id, tenant_id=self.tenant_id)
            self.db.add(obj)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def patch_interface_profile(self, partner_id: str, data: dict) -> BusinessPartnerInterfaceProfile:
        obj = self.get_interface_profile(partner_id)
        for k, v in data.items():
            setattr(obj, k, v)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    # ── envelope create / update (with number-range assignment) ─────────────

    def assign_account_numbers(self, row: BusinessPartner) -> None:
        """Assign debtor/creditor account from number range if not set."""
        from app.services.number_range_service import NumberRangeService
        nrs = NumberRangeService(self.db)
        if row.is_customer and not row.debtor_account:
            try:
                row.debtor_account = nrs.next_number("debtor_account", self.tenant_id)
            except ValueError:
                pass
        if row.is_supplier and not row.creditor_account:
            try:
                row.creditor_account = nrs.next_number("creditor_account", self.tenant_id)
            except ValueError:
                pass

    def persist_new_partner(self, row: BusinessPartner) -> BusinessPartner:
        """Add, commit, and refresh a newly constructed BusinessPartner row."""
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Business partner with this number already exists") from exc
        self.db.refresh(row)
        return row

    def persist_updated_partner(self, row: BusinessPartner) -> BusinessPartner:
        """Commit and refresh an existing BusinessPartner row after field mutations."""
        self.db.commit()
        self.db.refresh(row)
        return row

    def check_partner_number_unique(self, partner_number: str, exclude_id: Optional[str] = None) -> None:
        existing = self.repo.get_by_partner_number(partner_number)
        if existing and existing.partner_id != exclude_id:
            raise ConflictError(f"partner_number '{partner_number}' already exists")

    # ── community catalog (tenant-agnostic) ───────────────────────────────────

    def list_communities(self) -> list:
        return self.db.query(BusinessPartnerCommunity).order_by(
            BusinessPartnerCommunity.description.asc()
        ).all()

    def create_community(self, data: dict) -> BusinessPartnerCommunity:
        row = BusinessPartnerCommunity(id=uuid7(), **data)
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Community code already exists") from exc
        self.db.refresh(row)
        return row

    def patch_community(self, community_id: str, data: dict) -> BusinessPartnerCommunity:
        row = self.db.query(BusinessPartnerCommunity).filter(
            BusinessPartnerCommunity.id == community_id
        ).first()
        if row is None:
            raise EntityNotFoundError("BusinessPartnerCommunity", community_id)
        for k, v in data.items():
            setattr(row, k, v)
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete_community(self, community_id: str) -> None:
        row = self.db.query(BusinessPartnerCommunity).filter(
            BusinessPartnerCommunity.id == community_id
        ).first()
        if row is None:
            raise EntityNotFoundError("BusinessPartnerCommunity", community_id)
        self.db.delete(row)
        self.db.commit()

    def list_community_members(self, community_id: str) -> list:
        return self.db.query(BusinessPartnerCommunityMember).filter(
            BusinessPartnerCommunityMember.community_id == community_id
        ).order_by(BusinessPartnerCommunityMember.partner_id).all()

    def create_community_member(self, community_id: str, data: dict) -> BusinessPartnerCommunityMember:
        row = BusinessPartnerCommunityMember(id=uuid7(), community_id=community_id, **data)
        self.db.add(row)
        try:
            self.db.commit()
        except IntegrityError as exc:
            self.db.rollback()
            raise ConflictError("Member already in community") from exc
        self.db.refresh(row)
        return row

    def patch_community_member(self, member_id: str, data: dict) -> BusinessPartnerCommunityMember:
        row = self.db.query(BusinessPartnerCommunityMember).filter(
            BusinessPartnerCommunityMember.id == member_id
        ).first()
        if row is None:
            raise EntityNotFoundError("BusinessPartnerCommunityMember", member_id)
        for k, v in data.items():
            setattr(row, k, v)
        self.db.commit()
        self.db.refresh(row)
        return row

    def delete_community_member(self, member_id: str) -> None:
        row = self.db.query(BusinessPartnerCommunityMember).filter(
            BusinessPartnerCommunityMember.id == member_id
        ).first()
        if row is None:
            raise EntityNotFoundError("BusinessPartnerCommunityMember", member_id)
        self.db.delete(row)
        self.db.commit()
