"""
Business partner master data endpoints.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.uuid7 import uuid7
from app.core.tenant import get_tenant_id
from app.infrastructure.models import (
    BusinessPartnerAddress,
    BusinessPartnerBillingConfig,
    BusinessPartner,
    BusinessPartnerCommunity,
    BusinessPartnerCommunityMember,
    BusinessPartnerCooperativeMembership,
    BusinessPartnerCpdAccount,
    BusinessPartnerContact,
    BusinessPartnerDispatchMedium,
    BusinessPartnerDiscountItem,
    BusinessPartnerEmailDistribution,
    BusinessPartnerInterfaceProfile,
    BusinessPartnerInterestSetting,
    BusinessPartnerInstruction,
    BusinessPartnerPricingRule,
    BusinessPartnerProfile,
    BusinessPartnerPriceAgreement,
)

router = APIRouter()


class CoreIdentity(BaseModel):
    partner_id: Optional[str] = None
    partner_number: str
    matchcode: Optional[str] = None
    name_1: str
    name_2: Optional[str] = None
    legal_form: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = "DE"
    state: Optional[str] = None
    language: Optional[str] = "de"
    status: str = "active"


class Roles(BaseModel):
    is_customer: bool = False
    is_supplier: bool = False
    is_carrier: bool = False
    is_employee: bool = False
    is_service_provider: bool = False


class ContactData(BaseModel):
    phone: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    fax: Optional[str] = None


class Banking(BaseModel):
    iban: Optional[str] = None
    bic: Optional[str] = None
    bank_name: Optional[str] = None
    sepa_mandate_reference: Optional[str] = None
    sepa_mandate_signed_at: Optional[datetime] = None


class Finance(BaseModel):
    debtor_account: Optional[str] = None
    creditor_account: Optional[str] = None
    tax_number: Optional[str] = None
    vat_id: Optional[str] = None
    tax_type: Optional[str] = "standard"
    payment_terms_id: Optional[str] = None
    credit_limit: Optional[float] = None
    dunning_level: Optional[int] = 0
    blocked_for_delivery: bool = False
    blocked_for_invoice: bool = False


class AgrarExtension(BaseModel):
    farm_number: Optional[str] = None
    eu_farm_id: Optional[str] = None
    harvest_year_default: Optional[int] = None
    qs_certificate_number: Optional[str] = None
    qs_valid_until: Optional[datetime] = None
    bio_certified: bool = False
    bio_certificate_valid_until: Optional[datetime] = None
    contract_group: Optional[str] = None
    default_silo_location: Optional[str] = None


class Logistics(BaseModel):
    default_route_id: Optional[str] = None
    preferred_carrier_id: Optional[str] = None
    loading_requirements: Optional[str] = None


class MarketingConsent(BaseModel):
    email_opt_in: bool = False
    email_opt_in_timestamp: Optional[datetime] = None
    sms_opt_in: bool = False
    sms_opt_in_timestamp: Optional[datetime] = None
    whatsapp_opt_in: bool = False
    whatsapp_opt_in_timestamp: Optional[datetime] = None
    newsletter_opt_in: bool = False
    newsletter_language: Optional[str] = None
    flyer_subscription: bool = False
    flyer_delivery_type: Optional[str] = None
    marketing_segment: Optional[str] = None


class Gdpr(BaseModel):
    privacy_policy_accepted: bool = False
    privacy_policy_version: Optional[str] = None
    privacy_policy_accepted_at: Optional[datetime] = None
    data_processing_agreement_signed: bool = False
    data_retention_until: Optional[datetime] = None
    contact_block_reason: Optional[str] = None
    anonymized_at: Optional[datetime] = None


class Audit(BaseModel):
    created_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None


class LegacyCustomerFields(BaseModel):
    salutation: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    account_holder: Optional[str] = None
    bank_connection_active: Optional[bool] = None
    payment_method: Optional[str] = None
    price_group: Optional[str] = None
    discount_percent: Optional[float] = None
    customer_group: Optional[str] = None

    wants_account_statement: Optional[bool] = None
    print_balance_on_invoice: Optional[bool] = None
    invoice_print_blocked: Optional[bool] = None
    delivery_note_print_blocked: Optional[bool] = None
    calculate_shipping_flat: Optional[bool] = None
    settlement_mode: Optional[str] = None
    collective_settlement_code: Optional[str] = None
    bonus_recipient: Optional[str] = None
    invoice_recipient: Optional[str] = None
    self_billing_customer: Optional[bool] = None
    customer_addition: Optional[str] = None

    payment_target_days: Optional[int] = None
    cash_discount_percent: Optional[float] = None
    cash_discount_days: Optional[int] = None
    dunning_procedure: Optional[str] = None
    currency_code: Optional[str] = None
    euro_conversion_rate: Optional[float] = None
    interest_table_code: Optional[str] = None
    last_interest_date: Optional[date] = None
    last_interest_balance: Optional[float] = None
    auto_offset_enabled: Optional[bool] = None

    loading_information: Optional[str] = None
    route_information: Optional[str] = None

    post_open_items_blocked: Optional[bool] = None
    insurance_info: Optional[str] = None
    statistics_code: Optional[str] = None
    agricultural_office: Optional[str] = None
    operation_number: Optional[str] = None
    market_price_evaluation: Optional[bool] = None
    threshold_value: Optional[float] = None
    webshop_customer: Optional[bool] = None
    fax_blocked: Optional[bool] = None

    industry_key: Optional[str] = None
    annual_revenue: Optional[float] = None
    employee_count: Optional[int] = None
    company_philosophy: Optional[str] = None
    competitive_differentiation: Optional[str] = None

    invoice_dispatch_channel: Optional[str] = None
    reminder_dispatch_channel: Optional[str] = None
    contact_dispatch_channel: Optional[str] = None
    zugferd_profile: Optional[str] = None

    delivery_condition: Optional[str] = None
    due_date_basis: Optional[str] = None
    proforma_invoice: Optional[bool] = None
    proforma_discount_1: Optional[float] = None
    proforma_discount_2: Optional[float] = None

    consent_valid_until: Optional[date] = None
    consent_note: Optional[str] = None

    membership_number: Optional[str] = None
    membership_terminated: Optional[bool] = None
    termination_reason: Optional[str] = None
    membership_entry_date: Optional[date] = None
    termination_date: Optional[date] = None
    exit_date: Optional[date] = None
    mandatory_shares: Optional[int] = None
    terminated_mandatory_shares: Optional[int] = None

    tank_card_ean: Optional[str] = None
    customer_card_flag: Optional[bool] = None
    edifact_invoic: Optional[bool] = None
    edifact_orders: Optional[bool] = None
    edifact_desadv: Optional[bool] = None
    webshop_customer_number: Optional[str] = None
    webshop_description: Optional[str] = None
    discount_items: Optional[list[dict[str, Any]]] = None
    price_agreements: Optional[list[dict[str, Any]]] = None
    # Tab 23 Kundenstamm-Erfassung (docs/migration/option2_masterdata_model.json)
    tab_23: Optional[dict[str, Any]] = None


class BusinessPartnerPayload(BaseModel):
    core_identity: CoreIdentity
    roles: Roles = Roles()
    contact_data: ContactData = ContactData()
    banking: Banking = Banking()
    finance: Finance = Finance()
    agrar_extension: AgrarExtension = AgrarExtension()
    logistics: Logistics = Logistics()
    marketing_consent: MarketingConsent = MarketingConsent()
    gdpr: Gdpr = Gdpr()
    audit: Audit = Audit()
    legacy_customer_fields: LegacyCustomerFields = LegacyCustomerFields()


class BusinessPartnerEnvelope(BaseModel):
    business_partner: BusinessPartnerPayload


class DiscountItemBase(BaseModel):
    article_number: str
    description: Optional[str] = None
    discount_percent: Decimal = Field(default=Decimal("0.00"), ge=Decimal("0"), le=Decimal("100"))
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    discount_list_number: Optional[str] = None
    source_type: Optional[str] = None  # import|batch|internal
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class DiscountItemCreate(DiscountItemBase):
    pass


class DiscountItemUpdate(BaseModel):
    article_number: Optional[str] = None
    description: Optional[str] = None
    discount_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    discount_list_number: Optional[str] = None
    source_type: Optional[str] = None
    updated_by: Optional[str] = None


class DiscountItem(DiscountItemBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PriceAgreementBase(BaseModel):
    article_number: str
    description: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    price_net: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    price_incl_freight: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    price_unit: Optional[str] = None
    discount_allowed: bool = True
    special_freight: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    payment_condition: Optional[str] = None
    source_type: Optional[str] = None  # import|batch|internal
    operator_name: Optional[str] = None
    operator_date: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class PriceAgreementCreate(PriceAgreementBase):
    pass


class PriceAgreementUpdate(BaseModel):
    article_number: Optional[str] = None
    description: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    price_net: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    price_incl_freight: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    price_unit: Optional[str] = None
    discount_allowed: Optional[bool] = None
    special_freight: Optional[Decimal] = Field(default=None, ge=Decimal("0"))
    payment_condition: Optional[str] = None
    source_type: Optional[str] = None
    operator_name: Optional[str] = None
    operator_date: Optional[datetime] = None
    updated_by: Optional[str] = None


class PriceAgreement(PriceAgreementBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InstructionBase(BaseModel):
    instruction_text: str
    instruction_priority: str = Field(default="normal", pattern="^(low|normal|high|critical)$")
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class InstructionCreate(InstructionBase):
    pass


class InstructionUpdate(BaseModel):
    instruction_text: Optional[str] = None
    instruction_priority: Optional[str] = Field(default=None, pattern="^(low|normal|high|critical)$")
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    updated_by: Optional[str] = None


class Instruction(InstructionBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ContactBase(BaseModel):
    priority: int = Field(default=0, ge=0)
    salutation: Optional[str] = None
    brief_salutation: Optional[str] = None
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: str
    position: Optional[str] = None
    department: Optional[str] = None
    phone_1: Optional[str] = None
    phone_2: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    birth_date: Optional[date] = None
    hobbies: Optional[str] = None
    info_1: Optional[str] = None
    info_2: Optional[str] = None
    invoice_email_recipient: bool = False
    reminder_email_recipient: bool = False
    contact_type: str = Field(default="other", pattern="^(main|billing|logistics|sales|other)$")
    cad_system: Optional[str] = None
    software_systems: list[str] = []
    is_data_protection_officer: bool = False
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    priority: Optional[int] = Field(default=None, ge=0)
    salutation: Optional[str] = None
    brief_salutation: Optional[str] = None
    title: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    position: Optional[str] = None
    department: Optional[str] = None
    phone_1: Optional[str] = None
    phone_2: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    street: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    birth_date: Optional[date] = None
    hobbies: Optional[str] = None
    info_1: Optional[str] = None
    info_2: Optional[str] = None
    invoice_email_recipient: Optional[bool] = None
    reminder_email_recipient: Optional[bool] = None
    contact_type: Optional[str] = Field(default=None, pattern="^(main|billing|logistics|sales|other)$")
    cad_system: Optional[str] = None
    software_systems: Optional[list[str]] = None
    is_data_protection_officer: Optional[bool] = None
    updated_by: Optional[str] = None


class Contact(ContactBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AddressBase(BaseModel):
    address_type: str = Field(default="customer", pattern="^(customer|invoice|shipping|postal)$")
    name_1: Optional[str] = None
    name_2: Optional[str] = None
    name_3: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    country: Optional[str] = "DE"
    postal_code: Optional[str] = None
    city: Optional[str] = None
    po_box: Optional[str] = None
    po_box_postal_code: Optional[str] = None
    po_box_city: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    salutation: Optional[str] = None
    brief_salutation: Optional[str] = None
    free_field_1: Optional[str] = None
    free_field_2: Optional[str] = None
    free_field_3: Optional[str] = None
    area_code: Optional[str] = None
    is_default: bool = False
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class AddressCreate(AddressBase):
    pass


class AddressUpdate(BaseModel):
    address_type: Optional[str] = Field(default=None, pattern="^(customer|invoice|shipping|postal)$")
    name_1: Optional[str] = None
    name_2: Optional[str] = None
    name_3: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    po_box: Optional[str] = None
    po_box_postal_code: Optional[str] = None
    po_box_city: Optional[str] = None
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    salutation: Optional[str] = None
    brief_salutation: Optional[str] = None
    free_field_1: Optional[str] = None
    free_field_2: Optional[str] = None
    free_field_3: Optional[str] = None
    area_code: Optional[str] = None
    is_default: Optional[bool] = None
    updated_by: Optional[str] = None


class Address(AddressBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class BillingConfigBase(BaseModel):
    customer_group: Optional[str] = None
    customer_type: Optional[str] = Field(default=None, pattern="^(standard|organ|group_internal)$")
    account_statement_print: bool = False
    account_statement_separate: bool = False
    account_statement_reprint: bool = False
    last_account_statement_number: Optional[int] = Field(default=None, ge=0)
    last_account_statement_date: Optional[date] = None
    account_balance: Optional[Decimal] = None
    print_ad_text: bool = False
    shipping_expenses_enabled: bool = False
    settlement_mode: Optional[str] = Field(default=None, pattern="^(single|collective)$")
    admin_overhead_surcharge_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    invoice_number_range: Optional[str] = None
    bonus_eligible: bool = False
    self_billing_sales: bool = False
    self_billing_purchase: bool = False
    remarkable_claim: bool = False
    vat_optimizer: bool = False
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class BillingConfigCreate(BillingConfigBase):
    pass


class BillingConfigUpdate(BaseModel):
    customer_group: Optional[str] = None
    customer_type: Optional[str] = Field(default=None, pattern="^(standard|organ|group_internal)$")
    account_statement_print: Optional[bool] = None
    account_statement_separate: Optional[bool] = None
    account_statement_reprint: Optional[bool] = None
    last_account_statement_number: Optional[int] = Field(default=None, ge=0)
    last_account_statement_date: Optional[date] = None
    account_balance: Optional[Decimal] = None
    print_ad_text: Optional[bool] = None
    shipping_expenses_enabled: Optional[bool] = None
    settlement_mode: Optional[str] = Field(default=None, pattern="^(single|collective)$")
    admin_overhead_surcharge_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    invoice_number_range: Optional[str] = None
    bonus_eligible: Optional[bool] = None
    self_billing_sales: Optional[bool] = None
    self_billing_purchase: Optional[bool] = None
    remarkable_claim: Optional[bool] = None
    vat_optimizer: Optional[bool] = None
    updated_by: Optional[str] = None


class BillingConfig(BillingConfigBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CpdAccountBase(BaseModel):
    cpd_customer_number: str
    debtor_account: Optional[str] = None
    search_term: Optional[str] = None
    name_1: str
    name_2: Optional[str] = None
    name_3: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    country: Optional[str] = "DE"
    postal_code: Optional[str] = None
    city: Optional[str] = None
    po_box: Optional[str] = None
    po_box_city: Optional[str] = None
    phone_1: Optional[str] = None
    phone_2: Optional[str] = None
    fax: Optional[str] = None
    salutation: Optional[str] = None
    brief_salutation: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    branch_office: Optional[str] = None
    cost_center: Optional[str] = None
    invoice_type: Optional[str] = None
    collective_invoice: bool = False
    invoice_form_template: Optional[str] = None
    sales_representative: Optional[str] = None
    area_code: Optional[str] = None
    cash_discount_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    cash_discount_days: Optional[int] = Field(default=None, ge=0)
    payment_target_days: Optional[int] = Field(default=None, ge=0)
    created_by: Optional[str] = None
    updated_by: Optional[str] = None


class CpdAccountCreate(CpdAccountBase):
    pass


class CpdAccountUpdate(BaseModel):
    cpd_customer_number: Optional[str] = None
    debtor_account: Optional[str] = None
    search_term: Optional[str] = None
    name_1: Optional[str] = None
    name_2: Optional[str] = None
    name_3: Optional[str] = None
    street: Optional[str] = None
    house_number: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None
    po_box: Optional[str] = None
    po_box_city: Optional[str] = None
    phone_1: Optional[str] = None
    phone_2: Optional[str] = None
    fax: Optional[str] = None
    salutation: Optional[str] = None
    brief_salutation: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    branch_office: Optional[str] = None
    cost_center: Optional[str] = None
    invoice_type: Optional[str] = None
    collective_invoice: Optional[bool] = None
    invoice_form_template: Optional[str] = None
    sales_representative: Optional[str] = None
    area_code: Optional[str] = None
    cash_discount_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    cash_discount_days: Optional[int] = Field(default=None, ge=0)
    payment_target_days: Optional[int] = Field(default=None, ge=0)
    updated_by: Optional[str] = None


class CpdAccount(CpdAccountBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PricingRuleBase(BaseModel):
    direct_account: bool = False
    discount_settlement: bool = False
    self_pickup_discount_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    price_determination_mode: Optional[str] = None
    direct_deduction: bool = False
    weekly_price_ec_basis: bool = False
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    notes: Optional[str] = None


class PricingRuleCreate(PricingRuleBase):
    pass


class PricingRuleUpdate(BaseModel):
    direct_account: Optional[bool] = None
    discount_settlement: Optional[bool] = None
    self_pickup_discount_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    price_determination_mode: Optional[str] = None
    direct_deduction: Optional[bool] = None
    weekly_price_ec_basis: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    notes: Optional[str] = None


class PricingRule(PricingRuleBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InterestSettingBase(BaseModel):
    interest_table_debit_code: Optional[str] = None
    interest_table_credit_code: Optional[str] = None
    last_interest_date: Optional[date] = None
    last_interest_balance: Optional[Decimal] = None
    auto_offset_enabled: bool = False
    currency_code: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class InterestSettingCreate(InterestSettingBase):
    pass


class InterestSettingUpdate(BaseModel):
    interest_table_debit_code: Optional[str] = None
    interest_table_credit_code: Optional[str] = None
    last_interest_date: Optional[date] = None
    last_interest_balance: Optional[Decimal] = None
    auto_offset_enabled: Optional[bool] = None
    currency_code: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class InterestSetting(InterestSettingBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DispatchMediumBase(BaseModel):
    document_type: str
    dispatch_channel: str = Field(pattern="^(post|email|portal|edi|fax)$")
    enabled: bool = True
    zugferd_profile: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_name: Optional[str] = None
    notes: Optional[str] = None


class DispatchMediumCreate(DispatchMediumBase):
    pass


class DispatchMediumUpdate(BaseModel):
    document_type: Optional[str] = None
    dispatch_channel: Optional[str] = Field(default=None, pattern="^(post|email|portal|edi|fax)$")
    enabled: Optional[bool] = None
    zugferd_profile: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_name: Optional[str] = None
    notes: Optional[str] = None


class DispatchMedium(DispatchMediumBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CooperativeMembershipBase(BaseModel):
    membership_number: Optional[str] = None
    account_number: Optional[str] = None
    membership_status: str = Field(default="active", pattern="^(active|terminated|exited)$")
    entry_date: Optional[date] = None
    termination_date: Optional[date] = None
    exit_date: Optional[date] = None
    termination_reason: Optional[str] = None
    mandatory_shares: Optional[int] = Field(default=None, ge=0)
    terminated_mandatory_shares: Optional[int] = Field(default=None, ge=0)


class CooperativeMembershipCreate(CooperativeMembershipBase):
    pass


class CooperativeMembershipUpdate(BaseModel):
    membership_number: Optional[str] = None
    account_number: Optional[str] = None
    membership_status: Optional[str] = Field(default=None, pattern="^(active|terminated|exited)$")
    entry_date: Optional[date] = None
    termination_date: Optional[date] = None
    exit_date: Optional[date] = None
    termination_reason: Optional[str] = None
    mandatory_shares: Optional[int] = Field(default=None, ge=0)
    terminated_mandatory_shares: Optional[int] = Field(default=None, ge=0)


class CooperativeMembership(CooperativeMembershipBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class EmailDistributionBase(BaseModel):
    distribution_name: str
    description: Optional[str] = None
    email: str
    is_active: bool = True


class EmailDistributionCreate(EmailDistributionBase):
    pass


class EmailDistributionUpdate(BaseModel):
    distribution_name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class EmailDistribution(EmailDistributionBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CommunityBase(BaseModel):
    community_number: Optional[str] = None
    description: str


class CommunityCreate(CommunityBase):
    pass


class CommunityUpdate(BaseModel):
    community_number: Optional[str] = None
    description: Optional[str] = None


class Community(CommunityBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CommunityMemberBase(BaseModel):
    partner_id: str
    share_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))


class CommunityMemberCreate(CommunityMemberBase):
    pass


class CommunityMemberUpdate(BaseModel):
    partner_id: Optional[str] = None
    share_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))


class CommunityMember(CommunityMemberBase):
    id: str
    community_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ProfileBase(BaseModel):
    company_founded: Optional[date] = None
    annual_revenue: Optional[Decimal] = None
    industry_key: Optional[str] = None
    industry_name: Optional[str] = None
    professional_association: Optional[str] = None
    professional_association_number: Optional[str] = None
    competitors: Optional[str] = None
    bottlenecks: Optional[str] = None
    organization_structure: Optional[str] = None
    employee_count: Optional[int] = Field(default=None, ge=0)
    competitive_differentiation: Optional[str] = None
    works_council: bool = False
    company_philosophy: Optional[str] = None


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(BaseModel):
    company_founded: Optional[date] = None
    annual_revenue: Optional[Decimal] = None
    industry_key: Optional[str] = None
    industry_name: Optional[str] = None
    professional_association: Optional[str] = None
    professional_association_number: Optional[str] = None
    competitors: Optional[str] = None
    bottlenecks: Optional[str] = None
    organization_structure: Optional[str] = None
    employee_count: Optional[int] = Field(default=None, ge=0)
    competitive_differentiation: Optional[str] = None
    works_council: Optional[bool] = None
    company_philosophy: Optional[str] = None


class Profile(ProfileBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class InterfaceProfileBase(BaseModel):
    tank_card_ean: Optional[str] = None
    customer_card_flag: bool = False
    edifact_invoic: bool = False
    edifact_orders: bool = False
    edifact_desadv: bool = False
    webshop_customer_number: Optional[str] = None
    webshop_description: Optional[str] = None


class InterfaceProfileCreate(InterfaceProfileBase):
    pass


class InterfaceProfileUpdate(BaseModel):
    tank_card_ean: Optional[str] = None
    customer_card_flag: Optional[bool] = None
    edifact_invoic: Optional[bool] = None
    edifact_orders: Optional[bool] = None
    edifact_desadv: Optional[bool] = None
    webshop_customer_number: Optional[str] = None
    webshop_description: Optional[str] = None


class InterfaceProfile(InterfaceProfileBase):
    id: str
    partner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


def _to_float(value: Decimal | float | int | None) -> Optional[float]:
    if value is None:
        return None
    return float(value)


def _quantize_2(value: Decimal | float | int | None) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _quantize_4(value: Decimal | float | int | None) -> Optional[Decimal]:
    if value is None:
        return None
    return Decimal(str(value)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


LEGACY_CUSTOMER_FIELD_NAMES = [
    "salutation",
    "first_name",
    "last_name",
    "account_holder",
    "bank_connection_active",
    "payment_method",
    "price_group",
    "discount_percent",
    "customer_group",
    "wants_account_statement",
    "print_balance_on_invoice",
    "invoice_print_blocked",
    "delivery_note_print_blocked",
    "calculate_shipping_flat",
    "settlement_mode",
    "collective_settlement_code",
    "bonus_recipient",
    "invoice_recipient",
    "self_billing_customer",
    "customer_addition",
    "payment_target_days",
    "cash_discount_percent",
    "cash_discount_days",
    "dunning_procedure",
    "currency_code",
    "euro_conversion_rate",
    "interest_table_code",
    "last_interest_date",
    "last_interest_balance",
    "auto_offset_enabled",
    "loading_information",
    "route_information",
    "post_open_items_blocked",
    "insurance_info",
    "statistics_code",
    "agricultural_office",
    "operation_number",
    "market_price_evaluation",
    "threshold_value",
    "webshop_customer",
    "fax_blocked",
    "industry_key",
    "annual_revenue",
    "employee_count",
    "company_philosophy",
    "competitive_differentiation",
    "invoice_dispatch_channel",
    "reminder_dispatch_channel",
    "contact_dispatch_channel",
    "zugferd_profile",
    "delivery_condition",
    "due_date_basis",
    "proforma_invoice",
    "proforma_discount_1",
    "proforma_discount_2",
    "consent_valid_until",
    "consent_note",
    "membership_number",
    "membership_terminated",
    "termination_reason",
    "membership_entry_date",
    "termination_date",
    "exit_date",
    "mandatory_shares",
    "terminated_mandatory_shares",
    "tank_card_ean",
    "customer_card_flag",
    "edifact_invoic",
    "edifact_orders",
    "edifact_desadv",
    "webshop_customer_number",
    "webshop_description",
    "discount_items",
    "price_agreements",
    "tab_23",
]


def _to_out(row: BusinessPartner) -> BusinessPartnerEnvelope:
    legacy_data: dict[str, Any] = {}
    for field_name in LEGACY_CUSTOMER_FIELD_NAMES:
        value = getattr(row, field_name, None)
        if isinstance(value, Decimal):
            value = float(value)
        legacy_data[field_name] = value

    return BusinessPartnerEnvelope(
        business_partner=BusinessPartnerPayload(
            core_identity=CoreIdentity(
                partner_id=row.partner_id,
                partner_number=row.partner_number,
                matchcode=row.matchcode,
                name_1=row.name_1,
                name_2=row.name_2,
                legal_form=row.legal_form,
                street=row.street,
                house_number=row.house_number,
                postal_code=row.postal_code,
                city=row.city,
                country=row.country,
                state=row.state,
                language=row.language,
                status=row.status,
            ),
            roles=Roles(
                is_customer=row.is_customer,
                is_supplier=row.is_supplier,
                is_carrier=row.is_carrier,
                is_employee=row.is_employee,
                is_service_provider=row.is_service_provider,
            ),
            contact_data=ContactData(
                phone=row.phone,
                mobile=row.mobile,
                email=row.email,
                website=row.website,
                fax=row.fax,
            ),
            banking=Banking(
                iban=row.iban,
                bic=row.bic,
                bank_name=row.bank_name,
                sepa_mandate_reference=row.sepa_mandate_reference,
                sepa_mandate_signed_at=row.sepa_mandate_signed_at,
            ),
            finance=Finance(
                debtor_account=row.debtor_account,
                creditor_account=row.creditor_account,
                tax_number=row.tax_number,
                vat_id=row.vat_id,
                tax_type=row.tax_type,
                payment_terms_id=row.payment_terms_id,
                credit_limit=_to_float(row.credit_limit),
                dunning_level=row.dunning_level or 0,
                blocked_for_delivery=row.blocked_for_delivery,
                blocked_for_invoice=row.blocked_for_invoice,
            ),
            agrar_extension=AgrarExtension(
                farm_number=row.farm_number,
                eu_farm_id=row.eu_farm_id,
                harvest_year_default=row.harvest_year_default,
                qs_certificate_number=row.qs_certificate_number,
                qs_valid_until=row.qs_valid_until,
                bio_certified=row.bio_certified,
                bio_certificate_valid_until=row.bio_certificate_valid_until,
                contract_group=row.contract_group,
                default_silo_location=row.default_silo_location,
            ),
            logistics=Logistics(
                default_route_id=row.default_route_id,
                preferred_carrier_id=row.preferred_carrier_id,
                loading_requirements=row.loading_requirements,
            ),
            marketing_consent=MarketingConsent(
                email_opt_in=row.email_opt_in,
                email_opt_in_timestamp=row.email_opt_in_timestamp,
                sms_opt_in=row.sms_opt_in,
                sms_opt_in_timestamp=row.sms_opt_in_timestamp,
                whatsapp_opt_in=row.whatsapp_opt_in,
                whatsapp_opt_in_timestamp=row.whatsapp_opt_in_timestamp,
                newsletter_opt_in=row.newsletter_opt_in,
                newsletter_language=row.newsletter_language,
                flyer_subscription=row.flyer_subscription,
                flyer_delivery_type=row.flyer_delivery_type,
                marketing_segment=row.marketing_segment,
            ),
            gdpr=Gdpr(
                privacy_policy_accepted=row.privacy_policy_accepted,
                privacy_policy_version=row.privacy_policy_version,
                privacy_policy_accepted_at=row.privacy_policy_accepted_at,
                data_processing_agreement_signed=row.data_processing_agreement_signed,
                data_retention_until=row.data_retention_until,
                contact_block_reason=row.contact_block_reason,
                anonymized_at=row.anonymized_at,
            ),
            audit=Audit(
                created_at=row.created_at,
                created_by=row.created_by,
                updated_at=row.updated_at,
                updated_by=row.updated_by,
            ),
            legacy_customer_fields=LegacyCustomerFields(**legacy_data),
        )
    )


def _apply_payload(row: BusinessPartner, payload: BusinessPartnerPayload) -> None:
    ci = payload.core_identity
    row.partner_number = ci.partner_number
    row.matchcode = ci.matchcode
    row.name_1 = ci.name_1
    row.name_2 = ci.name_2
    row.legal_form = ci.legal_form
    row.street = ci.street
    row.house_number = ci.house_number
    row.postal_code = ci.postal_code
    row.city = ci.city
    row.country = ci.country
    row.state = ci.state
    row.language = ci.language
    row.status = ci.status

    roles = payload.roles
    row.is_customer = roles.is_customer
    row.is_supplier = roles.is_supplier
    row.is_carrier = roles.is_carrier
    row.is_employee = roles.is_employee
    row.is_service_provider = roles.is_service_provider

    contact = payload.contact_data
    row.phone = contact.phone
    row.mobile = contact.mobile
    row.email = contact.email
    row.website = contact.website
    row.fax = contact.fax

    bank = payload.banking
    row.iban = bank.iban
    row.bic = bank.bic
    row.bank_name = bank.bank_name
    row.sepa_mandate_reference = bank.sepa_mandate_reference
    row.sepa_mandate_signed_at = bank.sepa_mandate_signed_at

    fin = payload.finance
    row.debtor_account = fin.debtor_account
    row.creditor_account = fin.creditor_account
    row.tax_number = fin.tax_number
    row.vat_id = fin.vat_id
    row.tax_type = fin.tax_type
    row.payment_terms_id = fin.payment_terms_id
    row.credit_limit = fin.credit_limit
    row.dunning_level = fin.dunning_level
    row.blocked_for_delivery = fin.blocked_for_delivery
    row.blocked_for_invoice = fin.blocked_for_invoice

    agr = payload.agrar_extension
    row.farm_number = agr.farm_number
    row.eu_farm_id = agr.eu_farm_id
    row.harvest_year_default = agr.harvest_year_default
    row.qs_certificate_number = agr.qs_certificate_number
    row.qs_valid_until = agr.qs_valid_until
    row.bio_certified = agr.bio_certified
    row.bio_certificate_valid_until = agr.bio_certificate_valid_until
    row.contract_group = agr.contract_group
    row.default_silo_location = agr.default_silo_location

    log = payload.logistics
    row.default_route_id = log.default_route_id
    row.preferred_carrier_id = log.preferred_carrier_id
    row.loading_requirements = log.loading_requirements

    m = payload.marketing_consent
    row.email_opt_in = m.email_opt_in
    row.email_opt_in_timestamp = m.email_opt_in_timestamp
    row.sms_opt_in = m.sms_opt_in
    row.sms_opt_in_timestamp = m.sms_opt_in_timestamp
    row.whatsapp_opt_in = m.whatsapp_opt_in
    row.whatsapp_opt_in_timestamp = m.whatsapp_opt_in_timestamp
    row.newsletter_opt_in = m.newsletter_opt_in
    row.newsletter_language = m.newsletter_language
    row.flyer_subscription = m.flyer_subscription
    row.flyer_delivery_type = m.flyer_delivery_type
    row.marketing_segment = m.marketing_segment

    gdpr = payload.gdpr
    row.privacy_policy_accepted = gdpr.privacy_policy_accepted
    row.privacy_policy_version = gdpr.privacy_policy_version
    row.privacy_policy_accepted_at = gdpr.privacy_policy_accepted_at
    row.data_processing_agreement_signed = gdpr.data_processing_agreement_signed
    row.data_retention_until = gdpr.data_retention_until
    row.contact_block_reason = gdpr.contact_block_reason
    row.anonymized_at = gdpr.anonymized_at

    row.created_by = payload.audit.created_by
    row.updated_by = payload.audit.updated_by

    legacy_values = payload.legacy_customer_fields.model_dump(exclude_none=True)
    for field_name in LEGACY_CUSTOMER_FIELD_NAMES:
        if field_name in legacy_values:
            setattr(row, field_name, legacy_values[field_name])


@router.post("/", response_model=BusinessPartnerEnvelope, status_code=201)
async def create_business_partner(
    payload: BusinessPartnerEnvelope,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    existing = (
        db.query(BusinessPartner)
        .filter(BusinessPartner.tenant_id == tenant_id)
        .filter(BusinessPartner.partner_number == payload.business_partner.core_identity.partner_number)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="partner_number already exists")

    partner_id = payload.business_partner.core_identity.partner_id or uuid7()
    row = BusinessPartner(partner_id=partner_id, tenant_id=tenant_id)
    _apply_payload(row, payload.business_partner)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_out(row)


@router.get("/", response_model=list[BusinessPartnerEnvelope])
async def list_business_partners(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    q = db.query(BusinessPartner).filter(BusinessPartner.tenant_id == tenant_id)
    if status:
        q = q.filter(BusinessPartner.status == status)
    if search:
        s = f"%{search}%"
        q = q.filter((BusinessPartner.partner_number.ilike(s)) | (BusinessPartner.name_1.ilike(s)))
    rows = q.order_by(BusinessPartner.name_1.asc()).limit(500).all()
    return [_to_out(r) for r in rows]


@router.get("/{partner_id}", response_model=BusinessPartnerEnvelope)
async def get_business_partner(
    partner_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    row = db.query(BusinessPartner).filter(
        BusinessPartner.partner_id == partner_id,
        BusinessPartner.tenant_id == tenant_id
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Business partner not found")
    return _to_out(row)


@router.put("/{partner_id}", response_model=BusinessPartnerEnvelope)
async def update_business_partner(
    partner_id: str,
    payload: BusinessPartnerEnvelope,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db)
):
    row = db.query(BusinessPartner).filter(
        BusinessPartner.partner_id == partner_id,
        BusinessPartner.tenant_id == tenant_id
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Business partner not found")

    if payload.business_partner.core_identity.partner_number != row.partner_number:
        duplicate = (
            db.query(BusinessPartner)
            .filter(BusinessPartner.tenant_id == tenant_id)
            .filter(BusinessPartner.partner_number == payload.business_partner.core_identity.partner_number)
            .first()
        )
        if duplicate:
            raise HTTPException(status_code=409, detail="partner_number already exists")

    _apply_payload(row, payload.business_partner)
    db.commit()
    db.refresh(row)
    return _to_out(row)


def _ensure_partner_exists(partner_id: str, db: Session) -> None:
    exists = db.query(BusinessPartner.partner_id).filter(BusinessPartner.partner_id == partner_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Business partner not found")


def _commit_with_validation(db: Session, conflict_detail: str) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail=conflict_detail)


def _to_discount_item(row: BusinessPartnerDiscountItem) -> DiscountItem:
    return DiscountItem(
        id=row.id,
        partner_id=row.partner_id,
        article_number=row.article_number,
        description=row.description,
        discount_percent=_to_float(row.discount_percent) or 0.0,
        valid_from=row.valid_from,
        valid_to=row.valid_to,
        discount_list_number=row.discount_list_number,
        source_type=row.source_type,
        created_by=row.created_by,
        updated_by=row.updated_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_price_agreement(row: BusinessPartnerPriceAgreement) -> PriceAgreement:
    return PriceAgreement(
        id=row.id,
        partner_id=row.partner_id,
        article_number=row.article_number,
        description=row.description,
        valid_from=row.valid_from,
        valid_to=row.valid_to,
        price_net=_to_float(row.price_net),
        price_incl_freight=_to_float(row.price_incl_freight),
        price_unit=row.price_unit,
        discount_allowed=row.discount_allowed,
        special_freight=_to_float(row.special_freight),
        payment_condition=row.payment_condition,
        source_type=row.source_type,
        operator_name=row.operator_name,
        operator_date=row.operator_date,
        created_by=row.created_by,
        updated_by=row.updated_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{partner_id}/discount-items", response_model=list[DiscountItem])
async def list_discount_items(
    partner_id: str,
    article_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    q = db.query(BusinessPartnerDiscountItem).filter(BusinessPartnerDiscountItem.partner_id == partner_id)
    if article_number:
        q = q.filter(BusinessPartnerDiscountItem.article_number.ilike(f"%{article_number}%"))
    rows = q.order_by(BusinessPartnerDiscountItem.article_number.asc(), BusinessPartnerDiscountItem.created_at.desc()).all()
    return [_to_discount_item(r) for r in rows]


@router.post("/{partner_id}/discount-items", response_model=DiscountItem, status_code=201)
async def create_discount_item(
    partner_id: str,
    payload: DiscountItemCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerDiscountItem(
        id=uuid7(),
        partner_id=partner_id,
        article_number=payload.article_number,
        description=payload.description,
        discount_percent=_quantize_2(payload.discount_percent),
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        discount_list_number=payload.discount_list_number,
        source_type=payload.source_type,
        created_by=payload.created_by,
        updated_by=payload.updated_by,
    )
    db.add(row)
    _commit_with_validation(db, "Discount item violates constraints or duplicate period key")
    db.refresh(row)
    return _to_discount_item(row)


@router.get("/{partner_id}/discount-items/{item_id}", response_model=DiscountItem)
async def get_discount_item(partner_id: str, item_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerDiscountItem)
        .filter(
            BusinessPartnerDiscountItem.id == item_id,
            BusinessPartnerDiscountItem.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Discount item not found")
    return _to_discount_item(row)


@router.put("/{partner_id}/discount-items/{item_id}", response_model=DiscountItem)
async def update_discount_item(
    partner_id: str,
    item_id: str,
    payload: DiscountItemCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerDiscountItem)
        .filter(
            BusinessPartnerDiscountItem.id == item_id,
            BusinessPartnerDiscountItem.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Discount item not found")

    # PUT semantics: full replacement of mutable fields.
    row.article_number = payload.article_number
    row.description = payload.description
    row.discount_percent = _quantize_2(payload.discount_percent)
    row.valid_from = payload.valid_from
    row.valid_to = payload.valid_to
    row.discount_list_number = payload.discount_list_number
    row.source_type = payload.source_type
    row.updated_by = payload.updated_by
    _commit_with_validation(db, "Discount item violates constraints or duplicate period key")
    db.refresh(row)
    return _to_discount_item(row)


@router.patch("/{partner_id}/discount-items/{item_id}", response_model=DiscountItem)
async def patch_discount_item(
    partner_id: str,
    item_id: str,
    payload: DiscountItemUpdate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerDiscountItem)
        .filter(
            BusinessPartnerDiscountItem.id == item_id,
            BusinessPartnerDiscountItem.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Discount item not found")

    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        if key == "discount_percent" and value is not None:
            value = _quantize_2(value)
        setattr(row, key, value)
    _commit_with_validation(db, "Discount item violates constraints or duplicate period key")
    db.refresh(row)
    return _to_discount_item(row)


@router.delete("/{partner_id}/discount-items/{item_id}", status_code=204)
async def delete_discount_item(partner_id: str, item_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerDiscountItem)
        .filter(
            BusinessPartnerDiscountItem.id == item_id,
            BusinessPartnerDiscountItem.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Discount item not found")
    db.delete(row)
    db.commit()
    return None


@router.get("/{partner_id}/price-agreements", response_model=list[PriceAgreement])
async def list_price_agreements(
    partner_id: str,
    article_number: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    q = db.query(BusinessPartnerPriceAgreement).filter(BusinessPartnerPriceAgreement.partner_id == partner_id)
    if article_number:
        q = q.filter(BusinessPartnerPriceAgreement.article_number.ilike(f"%{article_number}%"))
    rows = q.order_by(BusinessPartnerPriceAgreement.article_number.asc(), BusinessPartnerPriceAgreement.created_at.desc()).all()
    return [_to_price_agreement(r) for r in rows]


@router.post("/{partner_id}/price-agreements", response_model=PriceAgreement, status_code=201)
async def create_price_agreement(
    partner_id: str,
    payload: PriceAgreementCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerPriceAgreement(
        id=uuid7(),
        partner_id=partner_id,
        article_number=payload.article_number,
        description=payload.description,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        price_net=_quantize_4(payload.price_net),
        price_incl_freight=_quantize_4(payload.price_incl_freight),
        price_unit=payload.price_unit,
        discount_allowed=payload.discount_allowed,
        special_freight=_quantize_4(payload.special_freight),
        payment_condition=payload.payment_condition,
        source_type=payload.source_type,
        operator_name=payload.operator_name,
        operator_date=payload.operator_date,
        created_by=payload.created_by,
        updated_by=payload.updated_by,
    )
    db.add(row)
    _commit_with_validation(db, "Price agreement violates constraints or duplicate period key")
    db.refresh(row)
    return _to_price_agreement(row)


@router.get("/{partner_id}/price-agreements/{agreement_id}", response_model=PriceAgreement)
async def get_price_agreement(partner_id: str, agreement_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerPriceAgreement)
        .filter(
            BusinessPartnerPriceAgreement.id == agreement_id,
            BusinessPartnerPriceAgreement.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Price agreement not found")
    return _to_price_agreement(row)


@router.put("/{partner_id}/price-agreements/{agreement_id}", response_model=PriceAgreement)
async def update_price_agreement(
    partner_id: str,
    agreement_id: str,
    payload: PriceAgreementCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerPriceAgreement)
        .filter(
            BusinessPartnerPriceAgreement.id == agreement_id,
            BusinessPartnerPriceAgreement.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Price agreement not found")

    # PUT semantics: full replacement of mutable fields.
    row.article_number = payload.article_number
    row.description = payload.description
    row.valid_from = payload.valid_from
    row.valid_to = payload.valid_to
    row.price_net = _quantize_4(payload.price_net)
    row.price_incl_freight = _quantize_4(payload.price_incl_freight)
    row.price_unit = payload.price_unit
    row.discount_allowed = payload.discount_allowed
    row.special_freight = _quantize_4(payload.special_freight)
    row.payment_condition = payload.payment_condition
    row.source_type = payload.source_type
    row.operator_name = payload.operator_name
    row.operator_date = payload.operator_date
    row.updated_by = payload.updated_by
    _commit_with_validation(db, "Price agreement violates constraints or duplicate period key")
    db.refresh(row)
    return _to_price_agreement(row)


@router.patch("/{partner_id}/price-agreements/{agreement_id}", response_model=PriceAgreement)
async def patch_price_agreement(
    partner_id: str,
    agreement_id: str,
    payload: PriceAgreementUpdate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerPriceAgreement)
        .filter(
            BusinessPartnerPriceAgreement.id == agreement_id,
            BusinessPartnerPriceAgreement.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Price agreement not found")

    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        if key in {"price_net", "price_incl_freight", "special_freight"} and value is not None:
            value = _quantize_4(value)
        setattr(row, key, value)
    _commit_with_validation(db, "Price agreement violates constraints or duplicate period key")
    db.refresh(row)
    return _to_price_agreement(row)


@router.delete("/{partner_id}/price-agreements/{agreement_id}", status_code=204)
async def delete_price_agreement(partner_id: str, agreement_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerPriceAgreement)
        .filter(
            BusinessPartnerPriceAgreement.id == agreement_id,
            BusinessPartnerPriceAgreement.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Price agreement not found")
    db.delete(row)
    db.commit()
    return None


def _to_instruction(row: BusinessPartnerInstruction) -> Instruction:
    return Instruction(
        id=row.id,
        partner_id=row.partner_id,
        instruction_text=row.instruction_text,
        instruction_priority=row.instruction_priority,
        valid_from=row.valid_from,
        valid_to=row.valid_to,
        created_by=row.created_by,
        updated_by=row.updated_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_contact(row: BusinessPartnerContact) -> Contact:
    return Contact(
        id=row.id,
        partner_id=row.partner_id,
        priority=row.priority,
        salutation=row.salutation,
        brief_salutation=row.brief_salutation,
        title=row.title,
        first_name=row.first_name,
        last_name=row.last_name,
        position=row.position,
        department=row.department,
        phone_1=row.phone_1,
        phone_2=row.phone_2,
        mobile=row.mobile,
        email=row.email,
        street=row.street,
        postal_code=row.postal_code,
        city=row.city,
        birth_date=row.birth_date,
        hobbies=row.hobbies,
        info_1=row.info_1,
        info_2=row.info_2,
        invoice_email_recipient=row.invoice_email_recipient,
        reminder_email_recipient=row.reminder_email_recipient,
        contact_type=row.contact_type,
        cad_system=row.cad_system,
        software_systems=row.software_systems or [],
        is_data_protection_officer=row.is_data_protection_officer,
        created_by=row.created_by,
        updated_by=row.updated_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_address(row: BusinessPartnerAddress) -> Address:
    return Address(
        id=row.id,
        partner_id=row.partner_id,
        address_type=row.address_type,
        name_1=row.name_1,
        name_2=row.name_2,
        name_3=row.name_3,
        street=row.street,
        house_number=row.house_number,
        country=row.country,
        postal_code=row.postal_code,
        city=row.city,
        po_box=row.po_box,
        po_box_postal_code=row.po_box_postal_code,
        po_box_city=row.po_box_city,
        phone=row.phone,
        fax=row.fax,
        email=row.email,
        website=row.website,
        salutation=row.salutation,
        brief_salutation=row.brief_salutation,
        free_field_1=row.free_field_1,
        free_field_2=row.free_field_2,
        free_field_3=row.free_field_3,
        area_code=row.area_code,
        is_default=row.is_default,
        created_by=row.created_by,
        updated_by=row.updated_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_billing_config(row: BusinessPartnerBillingConfig) -> BillingConfig:
    return BillingConfig(
        id=row.id,
        partner_id=row.partner_id,
        customer_group=row.customer_group,
        customer_type=row.customer_type,
        account_statement_print=row.account_statement_print,
        account_statement_separate=row.account_statement_separate,
        account_statement_reprint=row.account_statement_reprint,
        last_account_statement_number=row.last_account_statement_number,
        last_account_statement_date=row.last_account_statement_date,
        account_balance=_to_float(row.account_balance),
        print_ad_text=row.print_ad_text,
        shipping_expenses_enabled=row.shipping_expenses_enabled,
        settlement_mode=row.settlement_mode,
        admin_overhead_surcharge_percent=_to_float(row.admin_overhead_surcharge_percent),
        invoice_number_range=row.invoice_number_range,
        bonus_eligible=row.bonus_eligible,
        self_billing_sales=row.self_billing_sales,
        self_billing_purchase=row.self_billing_purchase,
        remarkable_claim=row.remarkable_claim,
        vat_optimizer=row.vat_optimizer,
        created_by=row.created_by,
        updated_by=row.updated_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_cpd_account(row: BusinessPartnerCpdAccount) -> CpdAccount:
    return CpdAccount(
        id=row.id,
        partner_id=row.partner_id,
        cpd_customer_number=row.cpd_customer_number,
        debtor_account=row.debtor_account,
        search_term=row.search_term,
        name_1=row.name_1,
        name_2=row.name_2,
        name_3=row.name_3,
        street=row.street,
        house_number=row.house_number,
        country=row.country,
        postal_code=row.postal_code,
        city=row.city,
        po_box=row.po_box,
        po_box_city=row.po_box_city,
        phone_1=row.phone_1,
        phone_2=row.phone_2,
        fax=row.fax,
        salutation=row.salutation,
        brief_salutation=row.brief_salutation,
        email=row.email,
        website=row.website,
        branch_office=row.branch_office,
        cost_center=row.cost_center,
        invoice_type=row.invoice_type,
        collective_invoice=row.collective_invoice,
        invoice_form_template=row.invoice_form_template,
        sales_representative=row.sales_representative,
        area_code=row.area_code,
        cash_discount_percent=_to_float(row.cash_discount_percent),
        cash_discount_days=row.cash_discount_days,
        payment_target_days=row.payment_target_days,
        created_by=row.created_by,
        updated_by=row.updated_by,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{partner_id}/instructions", response_model=list[Instruction])
async def list_instructions(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    rows = (
        db.query(BusinessPartnerInstruction)
        .filter(BusinessPartnerInstruction.partner_id == partner_id)
        .order_by(BusinessPartnerInstruction.created_at.desc())
        .all()
    )
    return [_to_instruction(r) for r in rows]


@router.post("/{partner_id}/instructions", response_model=Instruction, status_code=201)
async def create_instruction(partner_id: str, payload: InstructionCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerInstruction(
        id=uuid7(),
        partner_id=partner_id,
        instruction_text=payload.instruction_text,
        instruction_priority=payload.instruction_priority,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        created_by=payload.created_by,
        updated_by=payload.updated_by,
    )
    db.add(row)
    _commit_with_validation(db, "Instruction violates constraints")
    db.refresh(row)
    return _to_instruction(row)


@router.get("/{partner_id}/instructions/{instruction_id}", response_model=Instruction)
async def get_instruction(partner_id: str, instruction_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerInstruction)
        .filter(
            BusinessPartnerInstruction.id == instruction_id,
            BusinessPartnerInstruction.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Instruction not found")
    return _to_instruction(row)


@router.put("/{partner_id}/instructions/{instruction_id}", response_model=Instruction)
async def update_instruction(
    partner_id: str,
    instruction_id: str,
    payload: InstructionCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerInstruction)
        .filter(
            BusinessPartnerInstruction.id == instruction_id,
            BusinessPartnerInstruction.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Instruction not found")
    row.instruction_text = payload.instruction_text
    row.instruction_priority = payload.instruction_priority
    row.valid_from = payload.valid_from
    row.valid_to = payload.valid_to
    row.updated_by = payload.updated_by
    _commit_with_validation(db, "Instruction violates constraints")
    db.refresh(row)
    return _to_instruction(row)


@router.patch("/{partner_id}/instructions/{instruction_id}", response_model=Instruction)
async def patch_instruction(
    partner_id: str,
    instruction_id: str,
    payload: InstructionUpdate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerInstruction)
        .filter(
            BusinessPartnerInstruction.id == instruction_id,
            BusinessPartnerInstruction.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Instruction not found")
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(row, key, value)
    _commit_with_validation(db, "Instruction violates constraints")
    db.refresh(row)
    return _to_instruction(row)


@router.delete("/{partner_id}/instructions/{instruction_id}", status_code=204)
async def delete_instruction(partner_id: str, instruction_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerInstruction)
        .filter(
            BusinessPartnerInstruction.id == instruction_id,
            BusinessPartnerInstruction.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Instruction not found")
    db.delete(row)
    db.commit()
    return None


@router.get("/{partner_id}/contacts", response_model=list[Contact])
async def list_contacts(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    rows = (
        db.query(BusinessPartnerContact)
        .filter(BusinessPartnerContact.partner_id == partner_id)
        .order_by(BusinessPartnerContact.priority.asc(), BusinessPartnerContact.last_name.asc())
        .all()
    )
    return [_to_contact(r) for r in rows]


@router.post("/{partner_id}/contacts", response_model=Contact, status_code=201)
async def create_contact(partner_id: str, payload: ContactCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerContact(
        id=uuid7(),
        partner_id=partner_id,
        priority=payload.priority,
        salutation=payload.salutation,
        brief_salutation=payload.brief_salutation,
        title=payload.title,
        first_name=payload.first_name,
        last_name=payload.last_name,
        position=payload.position,
        department=payload.department,
        phone_1=payload.phone_1,
        phone_2=payload.phone_2,
        mobile=payload.mobile,
        email=payload.email,
        street=payload.street,
        postal_code=payload.postal_code,
        city=payload.city,
        birth_date=payload.birth_date,
        hobbies=payload.hobbies,
        info_1=payload.info_1,
        info_2=payload.info_2,
        invoice_email_recipient=payload.invoice_email_recipient,
        reminder_email_recipient=payload.reminder_email_recipient,
        contact_type=payload.contact_type,
        cad_system=payload.cad_system,
        software_systems=payload.software_systems,
        is_data_protection_officer=payload.is_data_protection_officer,
        created_by=payload.created_by,
        updated_by=payload.updated_by,
    )
    db.add(row)
    _commit_with_validation(db, "Contact violates constraints")
    db.refresh(row)
    return _to_contact(row)


@router.get("/{partner_id}/contacts/{contact_id}", response_model=Contact)
async def get_contact(partner_id: str, contact_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerContact)
        .filter(
            BusinessPartnerContact.id == contact_id,
            BusinessPartnerContact.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Contact not found")
    return _to_contact(row)


@router.put("/{partner_id}/contacts/{contact_id}", response_model=Contact)
async def update_contact(
    partner_id: str,
    contact_id: str,
    payload: ContactCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerContact)
        .filter(
            BusinessPartnerContact.id == contact_id,
            BusinessPartnerContact.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Contact not found")
    row.priority = payload.priority
    row.salutation = payload.salutation
    row.brief_salutation = payload.brief_salutation
    row.title = payload.title
    row.first_name = payload.first_name
    row.last_name = payload.last_name
    row.position = payload.position
    row.department = payload.department
    row.phone_1 = payload.phone_1
    row.phone_2 = payload.phone_2
    row.mobile = payload.mobile
    row.email = payload.email
    row.street = payload.street
    row.postal_code = payload.postal_code
    row.city = payload.city
    row.birth_date = payload.birth_date
    row.hobbies = payload.hobbies
    row.info_1 = payload.info_1
    row.info_2 = payload.info_2
    row.invoice_email_recipient = payload.invoice_email_recipient
    row.reminder_email_recipient = payload.reminder_email_recipient
    row.contact_type = payload.contact_type
    row.cad_system = payload.cad_system
    row.software_systems = payload.software_systems
    row.is_data_protection_officer = payload.is_data_protection_officer
    row.updated_by = payload.updated_by
    _commit_with_validation(db, "Contact violates constraints")
    db.refresh(row)
    return _to_contact(row)


@router.patch("/{partner_id}/contacts/{contact_id}", response_model=Contact)
async def patch_contact(
    partner_id: str,
    contact_id: str,
    payload: ContactUpdate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerContact)
        .filter(
            BusinessPartnerContact.id == contact_id,
            BusinessPartnerContact.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Contact not found")
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(row, key, value)
    _commit_with_validation(db, "Contact violates constraints")
    db.refresh(row)
    return _to_contact(row)


@router.delete("/{partner_id}/contacts/{contact_id}", status_code=204)
async def delete_contact(partner_id: str, contact_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerContact)
        .filter(
            BusinessPartnerContact.id == contact_id,
            BusinessPartnerContact.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(row)
    db.commit()
    return None


@router.get("/{partner_id}/addresses", response_model=list[Address])
async def list_addresses(
    partner_id: str,
    address_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    q = db.query(BusinessPartnerAddress).filter(BusinessPartnerAddress.partner_id == partner_id)
    if address_type:
        q = q.filter(BusinessPartnerAddress.address_type == address_type)
    rows = q.order_by(BusinessPartnerAddress.is_default.desc(), BusinessPartnerAddress.created_at.asc()).all()
    return [_to_address(r) for r in rows]


@router.post("/{partner_id}/addresses", response_model=Address, status_code=201)
async def create_address(
    partner_id: str,
    payload: AddressCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerAddress(
        id=uuid7(),
        partner_id=partner_id,
        address_type=payload.address_type,
        name_1=payload.name_1,
        name_2=payload.name_2,
        name_3=payload.name_3,
        street=payload.street,
        house_number=payload.house_number,
        country=payload.country,
        postal_code=payload.postal_code,
        city=payload.city,
        po_box=payload.po_box,
        po_box_postal_code=payload.po_box_postal_code,
        po_box_city=payload.po_box_city,
        phone=payload.phone,
        fax=payload.fax,
        email=payload.email,
        website=payload.website,
        salutation=payload.salutation,
        brief_salutation=payload.brief_salutation,
        free_field_1=payload.free_field_1,
        free_field_2=payload.free_field_2,
        free_field_3=payload.free_field_3,
        area_code=payload.area_code,
        is_default=payload.is_default,
        created_by=payload.created_by,
        updated_by=payload.updated_by,
    )
    db.add(row)
    _commit_with_validation(db, "Address violates constraints")
    db.refresh(row)
    return _to_address(row)


@router.get("/{partner_id}/addresses/{address_id}", response_model=Address)
async def get_address(partner_id: str, address_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerAddress)
        .filter(
            BusinessPartnerAddress.id == address_id,
            BusinessPartnerAddress.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Address not found")
    return _to_address(row)


@router.put("/{partner_id}/addresses/{address_id}", response_model=Address)
async def update_address(
    partner_id: str,
    address_id: str,
    payload: AddressCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerAddress)
        .filter(
            BusinessPartnerAddress.id == address_id,
            BusinessPartnerAddress.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Address not found")
    row.address_type = payload.address_type
    row.name_1 = payload.name_1
    row.name_2 = payload.name_2
    row.name_3 = payload.name_3
    row.street = payload.street
    row.house_number = payload.house_number
    row.country = payload.country
    row.postal_code = payload.postal_code
    row.city = payload.city
    row.po_box = payload.po_box
    row.po_box_postal_code = payload.po_box_postal_code
    row.po_box_city = payload.po_box_city
    row.phone = payload.phone
    row.fax = payload.fax
    row.email = payload.email
    row.website = payload.website
    row.salutation = payload.salutation
    row.brief_salutation = payload.brief_salutation
    row.free_field_1 = payload.free_field_1
    row.free_field_2 = payload.free_field_2
    row.free_field_3 = payload.free_field_3
    row.area_code = payload.area_code
    row.is_default = payload.is_default
    row.updated_by = payload.updated_by
    _commit_with_validation(db, "Address violates constraints")
    db.refresh(row)
    return _to_address(row)


@router.patch("/{partner_id}/addresses/{address_id}", response_model=Address)
async def patch_address(
    partner_id: str,
    address_id: str,
    payload: AddressUpdate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerAddress)
        .filter(
            BusinessPartnerAddress.id == address_id,
            BusinessPartnerAddress.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Address not found")
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        setattr(row, key, value)
    _commit_with_validation(db, "Address violates constraints")
    db.refresh(row)
    return _to_address(row)


@router.delete("/{partner_id}/addresses/{address_id}", status_code=204)
async def delete_address(partner_id: str, address_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerAddress)
        .filter(
            BusinessPartnerAddress.id == address_id,
            BusinessPartnerAddress.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(row)
    db.commit()
    return None


@router.get("/{partner_id}/billing-config", response_model=BillingConfig)
async def get_billing_config(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerBillingConfig)
        .filter(BusinessPartnerBillingConfig.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Billing config not found")
    return _to_billing_config(row)


@router.put("/{partner_id}/billing-config", response_model=BillingConfig)
async def put_billing_config(
    partner_id: str,
    payload: BillingConfigCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerBillingConfig)
        .filter(BusinessPartnerBillingConfig.partner_id == partner_id)
        .first()
    )
    if row is None:
        row = BusinessPartnerBillingConfig(id=uuid7(), partner_id=partner_id)
        db.add(row)

    row.customer_group = payload.customer_group
    row.customer_type = payload.customer_type
    row.account_statement_print = payload.account_statement_print
    row.account_statement_separate = payload.account_statement_separate
    row.account_statement_reprint = payload.account_statement_reprint
    row.last_account_statement_number = payload.last_account_statement_number
    row.last_account_statement_date = payload.last_account_statement_date
    row.account_balance = _quantize_2(payload.account_balance)
    row.print_ad_text = payload.print_ad_text
    row.shipping_expenses_enabled = payload.shipping_expenses_enabled
    row.settlement_mode = payload.settlement_mode
    row.admin_overhead_surcharge_percent = _quantize_2(payload.admin_overhead_surcharge_percent)
    row.invoice_number_range = payload.invoice_number_range
    row.bonus_eligible = payload.bonus_eligible
    row.self_billing_sales = payload.self_billing_sales
    row.self_billing_purchase = payload.self_billing_purchase
    row.remarkable_claim = payload.remarkable_claim
    row.vat_optimizer = payload.vat_optimizer
    row.created_by = payload.created_by if row.created_by is None else row.created_by
    row.updated_by = payload.updated_by

    _commit_with_validation(db, "Billing config violates constraints")
    db.refresh(row)
    return _to_billing_config(row)


@router.patch("/{partner_id}/billing-config", response_model=BillingConfig)
async def patch_billing_config(
    partner_id: str,
    payload: BillingConfigUpdate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerBillingConfig)
        .filter(BusinessPartnerBillingConfig.partner_id == partner_id)
        .first()
    )
    if row is None:
        row = BusinessPartnerBillingConfig(id=uuid7(), partner_id=partner_id)
        db.add(row)
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        if key in {"account_balance", "admin_overhead_surcharge_percent"} and value is not None:
            value = _quantize_2(value)
        setattr(row, key, value)
    _commit_with_validation(db, "Billing config violates constraints")
    db.refresh(row)
    return _to_billing_config(row)


@router.get("/{partner_id}/cpd-accounts", response_model=list[CpdAccount])
async def list_cpd_accounts(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    rows = (
        db.query(BusinessPartnerCpdAccount)
        .filter(BusinessPartnerCpdAccount.partner_id == partner_id)
        .order_by(BusinessPartnerCpdAccount.cpd_customer_number.asc())
        .all()
    )
    return [_to_cpd_account(r) for r in rows]


@router.post("/{partner_id}/cpd-accounts", response_model=CpdAccount, status_code=201)
async def create_cpd_account(
    partner_id: str,
    payload: CpdAccountCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerCpdAccount(
        id=uuid7(),
        partner_id=partner_id,
        cpd_customer_number=payload.cpd_customer_number,
        debtor_account=payload.debtor_account,
        search_term=payload.search_term,
        name_1=payload.name_1,
        name_2=payload.name_2,
        name_3=payload.name_3,
        street=payload.street,
        house_number=payload.house_number,
        country=payload.country,
        postal_code=payload.postal_code,
        city=payload.city,
        po_box=payload.po_box,
        po_box_city=payload.po_box_city,
        phone_1=payload.phone_1,
        phone_2=payload.phone_2,
        fax=payload.fax,
        salutation=payload.salutation,
        brief_salutation=payload.brief_salutation,
        email=payload.email,
        website=payload.website,
        branch_office=payload.branch_office,
        cost_center=payload.cost_center,
        invoice_type=payload.invoice_type,
        collective_invoice=payload.collective_invoice,
        invoice_form_template=payload.invoice_form_template,
        sales_representative=payload.sales_representative,
        area_code=payload.area_code,
        cash_discount_percent=_quantize_2(payload.cash_discount_percent),
        cash_discount_days=payload.cash_discount_days,
        payment_target_days=payload.payment_target_days,
        created_by=payload.created_by,
        updated_by=payload.updated_by,
    )
    db.add(row)
    _commit_with_validation(db, "CPD account violates constraints")
    db.refresh(row)
    return _to_cpd_account(row)


@router.get("/{partner_id}/cpd-accounts/{account_id}", response_model=CpdAccount)
async def get_cpd_account(partner_id: str, account_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerCpdAccount)
        .filter(
            BusinessPartnerCpdAccount.id == account_id,
            BusinessPartnerCpdAccount.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="CPD account not found")
    return _to_cpd_account(row)


@router.put("/{partner_id}/cpd-accounts/{account_id}", response_model=CpdAccount)
async def update_cpd_account(
    partner_id: str,
    account_id: str,
    payload: CpdAccountCreate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerCpdAccount)
        .filter(
            BusinessPartnerCpdAccount.id == account_id,
            BusinessPartnerCpdAccount.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="CPD account not found")
    row.cpd_customer_number = payload.cpd_customer_number
    row.debtor_account = payload.debtor_account
    row.search_term = payload.search_term
    row.name_1 = payload.name_1
    row.name_2 = payload.name_2
    row.name_3 = payload.name_3
    row.street = payload.street
    row.house_number = payload.house_number
    row.country = payload.country
    row.postal_code = payload.postal_code
    row.city = payload.city
    row.po_box = payload.po_box
    row.po_box_city = payload.po_box_city
    row.phone_1 = payload.phone_1
    row.phone_2 = payload.phone_2
    row.fax = payload.fax
    row.salutation = payload.salutation
    row.brief_salutation = payload.brief_salutation
    row.email = payload.email
    row.website = payload.website
    row.branch_office = payload.branch_office
    row.cost_center = payload.cost_center
    row.invoice_type = payload.invoice_type
    row.collective_invoice = payload.collective_invoice
    row.invoice_form_template = payload.invoice_form_template
    row.sales_representative = payload.sales_representative
    row.area_code = payload.area_code
    row.cash_discount_percent = _quantize_2(payload.cash_discount_percent)
    row.cash_discount_days = payload.cash_discount_days
    row.payment_target_days = payload.payment_target_days
    row.updated_by = payload.updated_by
    _commit_with_validation(db, "CPD account violates constraints")
    db.refresh(row)
    return _to_cpd_account(row)


@router.patch("/{partner_id}/cpd-accounts/{account_id}", response_model=CpdAccount)
async def patch_cpd_account(
    partner_id: str,
    account_id: str,
    payload: CpdAccountUpdate,
    db: Session = Depends(get_db),
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerCpdAccount)
        .filter(
            BusinessPartnerCpdAccount.id == account_id,
            BusinessPartnerCpdAccount.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="CPD account not found")
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        if key == "cash_discount_percent" and value is not None:
            value = _quantize_2(value)
        setattr(row, key, value)
    _commit_with_validation(db, "CPD account violates constraints")
    db.refresh(row)
    return _to_cpd_account(row)


@router.delete("/{partner_id}/cpd-accounts/{account_id}", status_code=204)
async def delete_cpd_account(partner_id: str, account_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerCpdAccount)
        .filter(
            BusinessPartnerCpdAccount.id == account_id,
            BusinessPartnerCpdAccount.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="CPD account not found")
    db.delete(row)
    db.commit()
    return None


def _to_pricing_rule(row: BusinessPartnerPricingRule) -> PricingRule:
    return PricingRule(
        id=row.id,
        partner_id=row.partner_id,
        direct_account=row.direct_account,
        discount_settlement=row.discount_settlement,
        self_pickup_discount_percent=_to_float(row.self_pickup_discount_percent),
        price_determination_mode=row.price_determination_mode,
        direct_deduction=row.direct_deduction,
        weekly_price_ec_basis=row.weekly_price_ec_basis,
        valid_from=row.valid_from,
        valid_to=row.valid_to,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{partner_id}/pricing-rules", response_model=list[PricingRule])
async def list_pricing_rules(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    rows = (
        db.query(BusinessPartnerPricingRule)
        .filter(BusinessPartnerPricingRule.partner_id == partner_id)
        .order_by(BusinessPartnerPricingRule.created_at.desc())
        .all()
    )
    return [_to_pricing_rule(r) for r in rows]


@router.post("/{partner_id}/pricing-rules", response_model=PricingRule, status_code=201)
async def create_pricing_rule(partner_id: str, payload: PricingRuleCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerPricingRule(
        id=uuid7(),
        partner_id=partner_id,
        direct_account=payload.direct_account,
        discount_settlement=payload.discount_settlement,
        self_pickup_discount_percent=_quantize_2(payload.self_pickup_discount_percent),
        price_determination_mode=payload.price_determination_mode,
        direct_deduction=payload.direct_deduction,
        weekly_price_ec_basis=payload.weekly_price_ec_basis,
        valid_from=payload.valid_from,
        valid_to=payload.valid_to,
        notes=payload.notes,
    )
    db.add(row)
    _commit_with_validation(db, "Pricing rule violates constraints")
    db.refresh(row)
    return _to_pricing_rule(row)


@router.get("/{partner_id}/pricing-rules/{rule_id}", response_model=PricingRule)
async def get_pricing_rule(partner_id: str, rule_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerPricingRule)
        .filter(BusinessPartnerPricingRule.id == rule_id, BusinessPartnerPricingRule.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    return _to_pricing_rule(row)


@router.put("/{partner_id}/pricing-rules/{rule_id}", response_model=PricingRule)
async def update_pricing_rule(partner_id: str, rule_id: str, payload: PricingRuleCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerPricingRule)
        .filter(BusinessPartnerPricingRule.id == rule_id, BusinessPartnerPricingRule.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    row.direct_account = payload.direct_account
    row.discount_settlement = payload.discount_settlement
    row.self_pickup_discount_percent = _quantize_2(payload.self_pickup_discount_percent)
    row.price_determination_mode = payload.price_determination_mode
    row.direct_deduction = payload.direct_deduction
    row.weekly_price_ec_basis = payload.weekly_price_ec_basis
    row.valid_from = payload.valid_from
    row.valid_to = payload.valid_to
    row.notes = payload.notes
    _commit_with_validation(db, "Pricing rule violates constraints")
    db.refresh(row)
    return _to_pricing_rule(row)


@router.patch("/{partner_id}/pricing-rules/{rule_id}", response_model=PricingRule)
async def patch_pricing_rule(partner_id: str, rule_id: str, payload: PricingRuleUpdate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerPricingRule)
        .filter(BusinessPartnerPricingRule.id == rule_id, BusinessPartnerPricingRule.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    values = payload.model_dump(exclude_unset=True)
    for key, value in values.items():
        if key == "self_pickup_discount_percent" and value is not None:
            value = _quantize_2(value)
        setattr(row, key, value)
    _commit_with_validation(db, "Pricing rule violates constraints")
    db.refresh(row)
    return _to_pricing_rule(row)


@router.delete("/{partner_id}/pricing-rules/{rule_id}", status_code=204)
async def delete_pricing_rule(partner_id: str, rule_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerPricingRule)
        .filter(BusinessPartnerPricingRule.id == rule_id, BusinessPartnerPricingRule.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Pricing rule not found")
    db.delete(row)
    db.commit()
    return None


def _to_interest_setting(row: BusinessPartnerInterestSetting) -> InterestSetting:
    return InterestSetting(
        id=row.id,
        partner_id=row.partner_id,
        interest_table_debit_code=row.interest_table_debit_code,
        interest_table_credit_code=row.interest_table_credit_code,
        last_interest_date=row.last_interest_date,
        last_interest_balance=row.last_interest_balance,
        auto_offset_enabled=row.auto_offset_enabled,
        currency_code=row.currency_code,
        valid_from=row.valid_from,
        valid_to=row.valid_to,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{partner_id}/interest-settings", response_model=list[InterestSetting])
async def list_interest_settings(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    rows = (
        db.query(BusinessPartnerInterestSetting)
        .filter(BusinessPartnerInterestSetting.partner_id == partner_id)
        .order_by(BusinessPartnerInterestSetting.created_at.desc())
        .all()
    )
    return [_to_interest_setting(r) for r in rows]


@router.post("/{partner_id}/interest-settings", response_model=InterestSetting, status_code=201)
async def create_interest_setting(partner_id: str, payload: InterestSettingCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerInterestSetting(id=uuid7(), partner_id=partner_id, **payload.model_dump())
    db.add(row)
    _commit_with_validation(db, "Interest setting violates constraints")
    db.refresh(row)
    return _to_interest_setting(row)


@router.put("/{partner_id}/interest-settings/{setting_id}", response_model=InterestSetting)
async def update_interest_setting(
    partner_id: str, setting_id: str, payload: InterestSettingCreate, db: Session = Depends(get_db)
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerInterestSetting)
        .filter(BusinessPartnerInterestSetting.id == setting_id, BusinessPartnerInterestSetting.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Interest setting not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    _commit_with_validation(db, "Interest setting violates constraints")
    db.refresh(row)
    return _to_interest_setting(row)


@router.patch("/{partner_id}/interest-settings/{setting_id}", response_model=InterestSetting)
async def patch_interest_setting(
    partner_id: str, setting_id: str, payload: InterestSettingUpdate, db: Session = Depends(get_db)
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerInterestSetting)
        .filter(BusinessPartnerInterestSetting.id == setting_id, BusinessPartnerInterestSetting.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Interest setting not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    _commit_with_validation(db, "Interest setting violates constraints")
    db.refresh(row)
    return _to_interest_setting(row)


@router.delete("/{partner_id}/interest-settings/{setting_id}", status_code=204)
async def delete_interest_setting(partner_id: str, setting_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerInterestSetting)
        .filter(BusinessPartnerInterestSetting.id == setting_id, BusinessPartnerInterestSetting.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Interest setting not found")
    db.delete(row)
    db.commit()
    return None


def _to_dispatch_medium(row: BusinessPartnerDispatchMedium) -> DispatchMedium:
    return DispatchMedium(
        id=row.id,
        partner_id=row.partner_id,
        document_type=row.document_type,
        dispatch_channel=row.dispatch_channel,
        enabled=row.enabled,
        zugferd_profile=row.zugferd_profile,
        recipient_email=row.recipient_email,
        recipient_name=row.recipient_name,
        notes=row.notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{partner_id}/dispatch-media", response_model=list[DispatchMedium])
async def list_dispatch_media(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    rows = (
        db.query(BusinessPartnerDispatchMedium)
        .filter(BusinessPartnerDispatchMedium.partner_id == partner_id)
        .order_by(BusinessPartnerDispatchMedium.document_type.asc(), BusinessPartnerDispatchMedium.dispatch_channel.asc())
        .all()
    )
    return [_to_dispatch_medium(r) for r in rows]


@router.post("/{partner_id}/dispatch-media", response_model=DispatchMedium, status_code=201)
async def create_dispatch_medium(partner_id: str, payload: DispatchMediumCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerDispatchMedium(id=uuid7(), partner_id=partner_id, **payload.model_dump())
    db.add(row)
    _commit_with_validation(db, "Dispatch medium violates constraints or duplicate key")
    db.refresh(row)
    return _to_dispatch_medium(row)


@router.put("/{partner_id}/dispatch-media/{medium_id}", response_model=DispatchMedium)
async def update_dispatch_medium(
    partner_id: str, medium_id: str, payload: DispatchMediumCreate, db: Session = Depends(get_db)
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerDispatchMedium)
        .filter(BusinessPartnerDispatchMedium.id == medium_id, BusinessPartnerDispatchMedium.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Dispatch medium not found")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    _commit_with_validation(db, "Dispatch medium violates constraints or duplicate key")
    db.refresh(row)
    return _to_dispatch_medium(row)


@router.patch("/{partner_id}/dispatch-media/{medium_id}", response_model=DispatchMedium)
async def patch_dispatch_medium(
    partner_id: str, medium_id: str, payload: DispatchMediumUpdate, db: Session = Depends(get_db)
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerDispatchMedium)
        .filter(BusinessPartnerDispatchMedium.id == medium_id, BusinessPartnerDispatchMedium.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Dispatch medium not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    _commit_with_validation(db, "Dispatch medium violates constraints or duplicate key")
    db.refresh(row)
    return _to_dispatch_medium(row)


@router.delete("/{partner_id}/dispatch-media/{medium_id}", status_code=204)
async def delete_dispatch_medium(partner_id: str, medium_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerDispatchMedium)
        .filter(BusinessPartnerDispatchMedium.id == medium_id, BusinessPartnerDispatchMedium.partner_id == partner_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Dispatch medium not found")
    db.delete(row)
    db.commit()
    return None


def _to_coop(row: BusinessPartnerCooperativeMembership) -> CooperativeMembership:
    return CooperativeMembership(
        id=row.id,
        partner_id=row.partner_id,
        membership_number=row.membership_number,
        account_number=row.account_number,
        membership_status=row.membership_status,
        entry_date=row.entry_date,
        termination_date=row.termination_date,
        exit_date=row.exit_date,
        termination_reason=row.termination_reason,
        mandatory_shares=row.mandatory_shares,
        terminated_mandatory_shares=row.terminated_mandatory_shares,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{partner_id}/cooperative-memberships", response_model=list[CooperativeMembership])
async def list_cooperative_memberships(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    rows = (
        db.query(BusinessPartnerCooperativeMembership)
        .filter(BusinessPartnerCooperativeMembership.partner_id == partner_id)
        .order_by(BusinessPartnerCooperativeMembership.created_at.desc())
        .all()
    )
    return [_to_coop(r) for r in rows]


@router.post("/{partner_id}/cooperative-memberships", response_model=CooperativeMembership, status_code=201)
async def create_cooperative_membership(
    partner_id: str, payload: CooperativeMembershipCreate, db: Session = Depends(get_db)
):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerCooperativeMembership(id=uuid7(), partner_id=partner_id, **payload.model_dump())
    db.add(row)
    _commit_with_validation(db, "Cooperative membership violates constraints")
    db.refresh(row)
    return _to_coop(row)


@router.patch("/{partner_id}/cooperative-memberships/{membership_id}", response_model=CooperativeMembership)
async def patch_cooperative_membership(
    partner_id: str, membership_id: str, payload: CooperativeMembershipUpdate, db: Session = Depends(get_db)
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerCooperativeMembership)
        .filter(
            BusinessPartnerCooperativeMembership.id == membership_id,
            BusinessPartnerCooperativeMembership.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Cooperative membership not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    _commit_with_validation(db, "Cooperative membership violates constraints")
    db.refresh(row)
    return _to_coop(row)


@router.delete("/{partner_id}/cooperative-memberships/{membership_id}", status_code=204)
async def delete_cooperative_membership(partner_id: str, membership_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerCooperativeMembership)
        .filter(
            BusinessPartnerCooperativeMembership.id == membership_id,
            BusinessPartnerCooperativeMembership.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Cooperative membership not found")
    db.delete(row)
    db.commit()
    return None


def _to_email_distribution(row: BusinessPartnerEmailDistribution) -> EmailDistribution:
    return EmailDistribution(
        id=row.id,
        partner_id=row.partner_id,
        distribution_name=row.distribution_name,
        description=row.description,
        email=row.email,
        is_active=row.is_active,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{partner_id}/email-distributions", response_model=list[EmailDistribution])
async def list_email_distributions(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    rows = (
        db.query(BusinessPartnerEmailDistribution)
        .filter(BusinessPartnerEmailDistribution.partner_id == partner_id)
        .order_by(BusinessPartnerEmailDistribution.distribution_name.asc(), BusinessPartnerEmailDistribution.email.asc())
        .all()
    )
    return [_to_email_distribution(r) for r in rows]


@router.post("/{partner_id}/email-distributions", response_model=EmailDistribution, status_code=201)
async def create_email_distribution(partner_id: str, payload: EmailDistributionCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = BusinessPartnerEmailDistribution(id=uuid7(), partner_id=partner_id, **payload.model_dump())
    db.add(row)
    _commit_with_validation(db, "Email distribution violates constraints or duplicate key")
    db.refresh(row)
    return _to_email_distribution(row)


@router.patch("/{partner_id}/email-distributions/{distribution_id}", response_model=EmailDistribution)
async def patch_email_distribution(
    partner_id: str, distribution_id: str, payload: EmailDistributionUpdate, db: Session = Depends(get_db)
):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerEmailDistribution)
        .filter(
            BusinessPartnerEmailDistribution.id == distribution_id,
            BusinessPartnerEmailDistribution.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Email distribution not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    _commit_with_validation(db, "Email distribution violates constraints or duplicate key")
    db.refresh(row)
    return _to_email_distribution(row)


@router.delete("/{partner_id}/email-distributions/{distribution_id}", status_code=204)
async def delete_email_distribution(partner_id: str, distribution_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = (
        db.query(BusinessPartnerEmailDistribution)
        .filter(
            BusinessPartnerEmailDistribution.id == distribution_id,
            BusinessPartnerEmailDistribution.partner_id == partner_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Email distribution not found")
    db.delete(row)
    db.commit()
    return None


def _to_community(row: BusinessPartnerCommunity) -> Community:
    return Community(
        id=row.id,
        community_number=row.community_number,
        description=row.description,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _to_community_member(row: BusinessPartnerCommunityMember) -> CommunityMember:
    return CommunityMember(
        id=row.id,
        community_id=row.community_id,
        partner_id=row.partner_id,
        share_percent=row.share_percent,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/catalog/communities", response_model=list[Community])
async def list_communities(db: Session = Depends(get_db)):
    rows = db.query(BusinessPartnerCommunity).order_by(BusinessPartnerCommunity.description.asc()).all()
    return [_to_community(r) for r in rows]


@router.post("/catalog/communities", response_model=Community, status_code=201)
async def create_community(payload: CommunityCreate, db: Session = Depends(get_db)):
    row = BusinessPartnerCommunity(id=uuid7(), **payload.model_dump())
    db.add(row)
    _commit_with_validation(db, "Community violates constraints")
    db.refresh(row)
    return _to_community(row)


@router.patch("/catalog/communities/{community_id}", response_model=Community)
async def patch_community(community_id: str, payload: CommunityUpdate, db: Session = Depends(get_db)):
    row = db.query(BusinessPartnerCommunity).filter(BusinessPartnerCommunity.id == community_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Community not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    _commit_with_validation(db, "Community violates constraints")
    db.refresh(row)
    return _to_community(row)


@router.delete("/catalog/communities/{community_id}", status_code=204)
async def delete_community(community_id: str, db: Session = Depends(get_db)):
    row = db.query(BusinessPartnerCommunity).filter(BusinessPartnerCommunity.id == community_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Community not found")
    db.delete(row)
    db.commit()
    return None


@router.get("/catalog/communities/{community_id}/members", response_model=list[CommunityMember])
async def list_community_members(community_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(BusinessPartnerCommunityMember)
        .filter(BusinessPartnerCommunityMember.community_id == community_id)
        .order_by(BusinessPartnerCommunityMember.created_at.asc())
        .all()
    )
    return [_to_community_member(r) for r in rows]


@router.post("/catalog/communities/{community_id}/members", response_model=CommunityMember, status_code=201)
async def create_community_member(community_id: str, payload: CommunityMemberCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(payload.partner_id, db)
    row = BusinessPartnerCommunityMember(id=uuid7(), community_id=community_id, **payload.model_dump())
    db.add(row)
    _commit_with_validation(db, "Community member violates constraints or duplicate key")
    db.refresh(row)
    return _to_community_member(row)


@router.patch("/catalog/communities/{community_id}/members/{member_id}", response_model=CommunityMember)
async def patch_community_member(
    community_id: str, member_id: str, payload: CommunityMemberUpdate, db: Session = Depends(get_db)
):
    row = (
        db.query(BusinessPartnerCommunityMember)
        .filter(BusinessPartnerCommunityMember.id == member_id, BusinessPartnerCommunityMember.community_id == community_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Community member not found")
    values = payload.model_dump(exclude_unset=True)
    if "partner_id" in values and values["partner_id"] is not None:
        _ensure_partner_exists(values["partner_id"], db)
    for key, value in values.items():
        setattr(row, key, value)
    _commit_with_validation(db, "Community member violates constraints or duplicate key")
    db.refresh(row)
    return _to_community_member(row)


@router.delete("/catalog/communities/{community_id}/members/{member_id}", status_code=204)
async def delete_community_member(community_id: str, member_id: str, db: Session = Depends(get_db)):
    row = (
        db.query(BusinessPartnerCommunityMember)
        .filter(BusinessPartnerCommunityMember.id == member_id, BusinessPartnerCommunityMember.community_id == community_id)
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Community member not found")
    db.delete(row)
    db.commit()
    return None


def _to_profile(row: BusinessPartnerProfile) -> Profile:
    return Profile(
        id=row.id,
        partner_id=row.partner_id,
        company_founded=row.company_founded,
        annual_revenue=row.annual_revenue,
        industry_key=row.industry_key,
        industry_name=row.industry_name,
        professional_association=row.professional_association,
        professional_association_number=row.professional_association_number,
        competitors=row.competitors,
        bottlenecks=row.bottlenecks,
        organization_structure=row.organization_structure,
        employee_count=row.employee_count,
        competitive_differentiation=row.competitive_differentiation,
        works_council=row.works_council,
        company_philosophy=row.company_philosophy,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{partner_id}/profile", response_model=Profile)
async def get_profile(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = db.query(BusinessPartnerProfile).filter(BusinessPartnerProfile.partner_id == partner_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_profile(row)


@router.put("/{partner_id}/profile", response_model=Profile)
async def put_profile(partner_id: str, payload: ProfileCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = db.query(BusinessPartnerProfile).filter(BusinessPartnerProfile.partner_id == partner_id).first()
    if not row:
        row = BusinessPartnerProfile(id=uuid7(), partner_id=partner_id)
        db.add(row)
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    _commit_with_validation(db, "Profile violates constraints")
    db.refresh(row)
    return _to_profile(row)


@router.patch("/{partner_id}/profile", response_model=Profile)
async def patch_profile(partner_id: str, payload: ProfileUpdate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = db.query(BusinessPartnerProfile).filter(BusinessPartnerProfile.partner_id == partner_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    _commit_with_validation(db, "Profile violates constraints")
    db.refresh(row)
    return _to_profile(row)


def _to_interface_profile(row: BusinessPartnerInterfaceProfile) -> InterfaceProfile:
    return InterfaceProfile(
        id=row.id,
        partner_id=row.partner_id,
        tank_card_ean=row.tank_card_ean,
        customer_card_flag=row.customer_card_flag,
        edifact_invoic=row.edifact_invoic,
        edifact_orders=row.edifact_orders,
        edifact_desadv=row.edifact_desadv,
        webshop_customer_number=row.webshop_customer_number,
        webshop_description=row.webshop_description,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.get("/{partner_id}/interface-profile", response_model=InterfaceProfile)
async def get_interface_profile(partner_id: str, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = db.query(BusinessPartnerInterfaceProfile).filter(BusinessPartnerInterfaceProfile.partner_id == partner_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Interface profile not found")
    return _to_interface_profile(row)


@router.put("/{partner_id}/interface-profile", response_model=InterfaceProfile)
async def put_interface_profile(partner_id: str, payload: InterfaceProfileCreate, db: Session = Depends(get_db)):
    _ensure_partner_exists(partner_id, db)
    row = db.query(BusinessPartnerInterfaceProfile).filter(BusinessPartnerInterfaceProfile.partner_id == partner_id).first()
    if not row:
        row = BusinessPartnerInterfaceProfile(id=uuid7(), partner_id=partner_id)
        db.add(row)
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    _commit_with_validation(db, "Interface profile violates constraints")
    db.refresh(row)
    return _to_interface_profile(row)


@router.patch("/{partner_id}/interface-profile", response_model=InterfaceProfile)
async def patch_interface_profile(
    partner_id: str, payload: InterfaceProfileUpdate, db: Session = Depends(get_db)
):
    _ensure_partner_exists(partner_id, db)
    row = db.query(BusinessPartnerInterfaceProfile).filter(BusinessPartnerInterfaceProfile.partner_id == partner_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Interface profile not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    _commit_with_validation(db, "Interface profile violates constraints")
    db.refresh(row)
    return _to_interface_profile(row)
