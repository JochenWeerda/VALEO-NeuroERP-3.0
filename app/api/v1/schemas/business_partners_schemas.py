from __future__ import annotations

from typing import Any, List, Optional
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.api.v1.schemas.base import BaseSchema


class DiscountItemUpdate(BaseModel):
    article_number: Optional[str] = None
    description: Optional[str] = None
    discount_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    discount_list_number: Optional[str] = None
    source_type: Optional[str] = None
    updated_by: Optional[str] = None



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



class InstructionUpdate(BaseModel):
    instruction_text: Optional[str] = None
    instruction_priority: Optional[str] = Field(default=None, pattern="^(low|normal|high|critical)$")
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    updated_by: Optional[str] = None



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



class InterestSettingUpdate(BaseModel):
    interest_table_debit_code: Optional[str] = None
    interest_table_credit_code: Optional[str] = None
    last_interest_date: Optional[date] = None
    last_interest_balance: Optional[Decimal] = None
    auto_offset_enabled: Optional[bool] = None
    currency_code: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None



class DispatchMediumUpdate(BaseModel):
    document_type: Optional[str] = None
    dispatch_channel: Optional[str] = Field(default=None, pattern="^(post|email|portal|edi|fax)$")
    enabled: Optional[bool] = None
    zugferd_profile: Optional[str] = None
    recipient_email: Optional[str] = None
    recipient_name: Optional[str] = None
    notes: Optional[str] = None



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



class EmailDistributionUpdate(BaseModel):
    distribution_name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None



class CommunityUpdate(BaseModel):
    community_number: Optional[str] = None
    description: Optional[str] = None



class CommunityMemberUpdate(BaseModel):
    partner_id: Optional[str] = None
    share_percent: Optional[Decimal] = Field(default=None, ge=Decimal("0"), le=Decimal("100"))



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



class InterfaceProfileUpdate(BaseModel):
    tank_card_ean: Optional[str] = None
    customer_card_flag: Optional[bool] = None
    edifact_invoic: Optional[bool] = None
    edifact_orders: Optional[bool] = None
    edifact_desadv: Optional[bool] = None
    webshop_customer_number: Optional[str] = None
    webshop_description: Optional[str] = None

