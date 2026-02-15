"""
SQLAlchemy models for VALEO-NeuroERP
Database entities following domain-driven design
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Date, Time, Text, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func
import uuid

from ...core.database import Base


# Shared Models
class Tenant(Base):
    """Tenant model for multi-tenancy"""
    __tablename__ = "tenants"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    domain = Column(String(100), nullable=False)
    settings = Column(Text, default="{}")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class User(Base):
    """User model"""
    __tablename__ = "users"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    keycloak_id = Column(String, nullable=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    roles = Column(Text, default="[]")  # JSON array of roles
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


# CRM Models
class Customer(Base):
    """Customer model"""
    __tablename__ = "customers"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    customer_number = Column(String(50), nullable=False)
    company_name = Column(String(255), nullable=False)
    contact_person = Column(String(100), nullable=True)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    postal_code = Column(String(10), nullable=True)
    country = Column(String(50), nullable=True)
    industry = Column(String(50), nullable=True)
    website = Column(String(100), nullable=True)
    customer_type = Column(String(50), nullable=True)
    credit_limit = Column(DECIMAL(15, 2), nullable=True)
    payment_terms = Column(Integer, nullable=True)
    tax_id = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Lead(Base):
    """Lead model"""
    __tablename__ = "leads"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    priority = Column(String(10), default="medium")
    estimated_value = Column(DECIMAL(15, 2), nullable=True)
    company_name = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    assigned_to = Column(String, ForeignKey("domain_shared.users.id"), nullable=True)
    converted_at = Column(DateTime(timezone=True), nullable=True)
    converted_to_customer_id = Column(String, ForeignKey("domain_crm.customers.id"), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Contact(Base):
    """Contact model"""
    __tablename__ = "contacts"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    position = Column(String(50), nullable=True)
    department = Column(String(50), nullable=True)
    customer_id = Column(String, ForeignKey("domain_crm.customers.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Activity(Base):
    """CRM Activity model"""
    __tablename__ = "activities"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    type = Column(String(20), nullable=False)  # meeting, call, email, note
    title = Column(String(200), nullable=False)
    customer = Column(String(100), nullable=False)
    contact_person = Column(String(100), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), nullable=False)  # planned, completed, overdue
    assigned_to = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FarmProfile(Base):
    """Farm Profile model for agricultural operations"""
    __tablename__ = "farm_profiles"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    farm_name = Column(String(200), nullable=False)
    owner = Column(String(100), nullable=False)
    total_area = Column(Float, nullable=False)  # in hectares
    crops = Column(postgresql.JSONB(astext_type=Text()), nullable=True, default="[]")  # JSON array of {crop, area}
    livestock = Column(postgresql.JSONB(astext_type=Text()), nullable=True, default="[]")  # JSON array of {type, count}
    location = Column(postgresql.JSONB(astext_type=Text()), nullable=True)  # {latitude, longitude, address}
    certifications = Column(postgresql.JSONB(astext_type=Text()), nullable=True, default="[]")  # JSON array of strings
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartner(Base):
    """Unified business partner master data."""
    __tablename__ = "business_partners"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    # core_identity
    partner_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_number = Column(String(64), nullable=False, unique=True)
    matchcode = Column(String(120), nullable=True)
    name_1 = Column(String(255), nullable=False)
    name_2 = Column(String(255), nullable=True)
    legal_form = Column(String(80), nullable=True)
    street = Column(String(120), nullable=True)
    house_number = Column(String(40), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(120), nullable=True)
    country = Column(String(2), nullable=True, default="DE")
    state = Column(String(80), nullable=True)
    language = Column(String(10), nullable=True, default="de")
    status = Column(String(20), nullable=False, default="active")

    # roles
    is_customer = Column(Boolean, nullable=False, default=False)
    is_supplier = Column(Boolean, nullable=False, default=False)
    is_carrier = Column(Boolean, nullable=False, default=False)
    is_employee = Column(Boolean, nullable=False, default=False)
    is_service_provider = Column(Boolean, nullable=False, default=False)

    # contact_data
    phone = Column(String(60), nullable=True)
    mobile = Column(String(60), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    fax = Column(String(60), nullable=True)

    # banking
    iban = Column(String(34), nullable=True)
    bic = Column(String(20), nullable=True)
    bank_name = Column(String(120), nullable=True)
    sepa_mandate_reference = Column(String(120), nullable=True)
    sepa_mandate_signed_at = Column(DateTime(timezone=True), nullable=True)

    # finance
    debtor_account = Column(String(40), nullable=True)
    creditor_account = Column(String(40), nullable=True)
    tax_number = Column(String(60), nullable=True)
    vat_id = Column(String(60), nullable=True)
    tax_type = Column(String(40), nullable=True, default="standard")
    payment_terms_id = Column(String(36), nullable=True)
    credit_limit = Column(DECIMAL(14, 2), nullable=True)
    dunning_level = Column(Integer, nullable=True, default=0)
    blocked_for_delivery = Column(Boolean, nullable=False, default=False)
    blocked_for_invoice = Column(Boolean, nullable=False, default=False)

    # agrar_extension
    farm_number = Column(String(80), nullable=True)
    eu_farm_id = Column(String(80), nullable=True)
    harvest_year_default = Column(Integer, nullable=True)
    qs_certificate_number = Column(String(80), nullable=True)
    qs_valid_until = Column(DateTime(timezone=True), nullable=True)
    bio_certified = Column(Boolean, nullable=False, default=False)
    bio_certificate_valid_until = Column(DateTime(timezone=True), nullable=True)
    contract_group = Column(String(80), nullable=True)
    default_silo_location = Column(String(120), nullable=True)

    # logistics
    default_route_id = Column(String(36), nullable=True)
    preferred_carrier_id = Column(String(36), nullable=True)
    loading_requirements = Column(Text, nullable=True)

    # marketing_consent
    email_opt_in = Column(Boolean, nullable=False, default=False)
    email_opt_in_timestamp = Column(DateTime(timezone=True), nullable=True)
    sms_opt_in = Column(Boolean, nullable=False, default=False)
    sms_opt_in_timestamp = Column(DateTime(timezone=True), nullable=True)
    whatsapp_opt_in = Column(Boolean, nullable=False, default=False)
    whatsapp_opt_in_timestamp = Column(DateTime(timezone=True), nullable=True)
    newsletter_opt_in = Column(Boolean, nullable=False, default=False)
    newsletter_language = Column(String(10), nullable=True)
    flyer_subscription = Column(Boolean, nullable=False, default=False)
    flyer_delivery_type = Column(String(20), nullable=True)
    marketing_segment = Column(String(80), nullable=True)

    # gdpr
    privacy_policy_accepted = Column(Boolean, nullable=False, default=False)
    privacy_policy_version = Column(String(40), nullable=True)
    privacy_policy_accepted_at = Column(DateTime(timezone=True), nullable=True)
    data_processing_agreement_signed = Column(Boolean, nullable=False, default=False)
    data_retention_until = Column(DateTime(timezone=True), nullable=True)
    contact_block_reason = Column(String(255), nullable=True)
    anonymized_at = Column(DateTime(timezone=True), nullable=True)

    # audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(36), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(36), nullable=True)

    # legacy customer master extensions (tabs/screens mapping)
    salutation = Column(String(40), nullable=True)
    first_name = Column(String(120), nullable=True)
    last_name = Column(String(120), nullable=True)
    account_holder = Column(String(255), nullable=True)
    bank_connection_active = Column(Boolean, nullable=False, default=True)
    payment_method = Column(String(40), nullable=True)
    price_group = Column(String(80), nullable=True)
    discount_percent = Column(DECIMAL(7, 2), nullable=True)
    customer_group = Column(String(80), nullable=True)

    wants_account_statement = Column(Boolean, nullable=False, default=False)
    print_balance_on_invoice = Column(Boolean, nullable=False, default=False)
    invoice_print_blocked = Column(Boolean, nullable=False, default=False)
    delivery_note_print_blocked = Column(Boolean, nullable=False, default=False)
    calculate_shipping_flat = Column(Boolean, nullable=False, default=False)
    settlement_mode = Column(String(20), nullable=True)  # single|collective
    collective_settlement_code = Column(String(80), nullable=True)
    bonus_recipient = Column(String(255), nullable=True)
    invoice_recipient = Column(String(255), nullable=True)
    self_billing_customer = Column(Boolean, nullable=False, default=False)
    customer_addition = Column(String(255), nullable=True)

    payment_target_days = Column(Integer, nullable=True)
    cash_discount_percent = Column(DECIMAL(7, 2), nullable=True)
    cash_discount_days = Column(Integer, nullable=True)
    dunning_procedure = Column(String(120), nullable=True)
    currency_code = Column(String(3), nullable=True)
    euro_conversion_rate = Column(DECIMAL(14, 6), nullable=True)
    interest_table_code = Column(String(80), nullable=True)
    last_interest_date = Column(Date, nullable=True)
    last_interest_balance = Column(DECIMAL(14, 2), nullable=True)
    auto_offset_enabled = Column(Boolean, nullable=False, default=False)

    loading_information = Column(Text, nullable=True)
    route_information = Column(Text, nullable=True)

    post_open_items_blocked = Column(Boolean, nullable=False, default=False)
    insurance_info = Column(String(255), nullable=True)
    statistics_code = Column(String(80), nullable=True)
    agricultural_office = Column(String(120), nullable=True)
    operation_number = Column(String(80), nullable=True)
    market_price_evaluation = Column(Boolean, nullable=False, default=False)
    threshold_value = Column(DECIMAL(14, 2), nullable=True)
    webshop_customer = Column(Boolean, nullable=False, default=False)
    fax_blocked = Column(Boolean, nullable=False, default=False)

    industry_key = Column(String(80), nullable=True)
    annual_revenue = Column(DECIMAL(14, 2), nullable=True)
    employee_count = Column(Integer, nullable=True)
    company_philosophy = Column(Text, nullable=True)
    competitive_differentiation = Column(Text, nullable=True)

    invoice_dispatch_channel = Column(String(40), nullable=True)  # post|email
    reminder_dispatch_channel = Column(String(40), nullable=True)
    contact_dispatch_channel = Column(String(40), nullable=True)
    zugferd_profile = Column(String(40), nullable=True)

    delivery_condition = Column(String(120), nullable=True)
    due_date_basis = Column(String(40), nullable=True)  # invoice_date|delivery_date|valuta
    proforma_invoice = Column(Boolean, nullable=False, default=False)
    proforma_discount_1 = Column(DECIMAL(7, 2), nullable=True)
    proforma_discount_2 = Column(DECIMAL(7, 2), nullable=True)

    consent_valid_until = Column(Date, nullable=True)
    consent_note = Column(Text, nullable=True)

    membership_number = Column(String(80), nullable=True)
    membership_terminated = Column(Boolean, nullable=False, default=False)
    termination_reason = Column(String(255), nullable=True)
    membership_entry_date = Column(Date, nullable=True)
    termination_date = Column(Date, nullable=True)
    exit_date = Column(Date, nullable=True)
    mandatory_shares = Column(Integer, nullable=True)
    terminated_mandatory_shares = Column(Integer, nullable=True)

    tank_card_ean = Column(String(80), nullable=True)
    customer_card_flag = Column(Boolean, nullable=False, default=False)
    edifact_invoic = Column(Boolean, nullable=False, default=False)
    edifact_orders = Column(Boolean, nullable=False, default=False)
    edifact_desadv = Column(Boolean, nullable=False, default=False)
    webshop_customer_number = Column(String(80), nullable=True)
    webshop_description = Column(String(255), nullable=True)

    discount_items = Column(postgresql.JSONB(astext_type=Text()), nullable=True, default="[]")
    price_agreements = Column(postgresql.JSONB(astext_type=Text()), nullable=True, default="[]")


class BusinessPartnerDiscountItem(Base):
    """Normalized customer discount items per business partner."""
    __tablename__ = "business_partner_discount_items"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    article_number = Column(String(64), nullable=False)
    description = Column(String(255), nullable=True)
    discount_percent = Column(DECIMAL(7, 2), nullable=False, default=0)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    discount_list_number = Column(String(64), nullable=True)
    source_type = Column(String(20), nullable=True)  # import|batch|internal
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerPriceAgreement(Base):
    """Normalized customer price agreements per business partner."""
    __tablename__ = "business_partner_price_agreements"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    article_number = Column(String(64), nullable=False)
    description = Column(String(255), nullable=True)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    price_net = Column(DECIMAL(14, 4), nullable=True)
    price_incl_freight = Column(DECIMAL(14, 4), nullable=True)
    price_unit = Column(String(20), nullable=True)
    discount_allowed = Column(Boolean, nullable=False, default=True)
    special_freight = Column(DECIMAL(14, 4), nullable=True)
    payment_condition = Column(String(120), nullable=True)
    source_type = Column(String(20), nullable=True)  # import|batch|internal
    operator_name = Column(String(120), nullable=True)
    operator_date = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerInstruction(Base):
    """Internal instructions (Chef-Anweisung) per business partner."""
    __tablename__ = "business_partner_instructions"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    instruction_text = Column(Text, nullable=False)
    instruction_priority = Column(String(20), nullable=False, default="normal")
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerContact(Base):
    """Contacts (Ansprechpartner) per business partner."""
    __tablename__ = "business_partner_contacts"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    priority = Column(Integer, nullable=False, default=0)
    salutation = Column(String(40), nullable=True)
    brief_salutation = Column(String(120), nullable=True)
    title = Column(String(60), nullable=True)
    first_name = Column(String(120), nullable=True)
    last_name = Column(String(120), nullable=False)
    position = Column(String(120), nullable=True)
    department = Column(String(120), nullable=True)
    phone_1 = Column(String(60), nullable=True)
    phone_2 = Column(String(60), nullable=True)
    mobile = Column(String(60), nullable=True)
    email = Column(String(255), nullable=True)
    street = Column(String(120), nullable=True)
    postal_code = Column(String(20), nullable=True)
    city = Column(String(120), nullable=True)
    birth_date = Column(Date, nullable=True)
    hobbies = Column(Text, nullable=True)
    info_1 = Column(String(255), nullable=True)
    info_2 = Column(String(255), nullable=True)
    invoice_email_recipient = Column(Boolean, nullable=False, default=False)
    reminder_email_recipient = Column(Boolean, nullable=False, default=False)
    contact_type = Column(String(20), nullable=False, default="other")
    cad_system = Column(String(120), nullable=True)
    software_systems = Column(postgresql.JSONB(astext_type=Text()), nullable=True, default="[]")
    is_data_protection_officer = Column(Boolean, nullable=False, default=False)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerAddress(Base):
    """Normalized business partner addresses (Tab 23)."""
    __tablename__ = "business_partner_addresses"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    address_type = Column(String(20), nullable=False, default="customer")  # customer|invoice|shipping|postal
    name_1 = Column(String(255), nullable=True)
    name_2 = Column(String(255), nullable=True)
    name_3 = Column(String(255), nullable=True)
    street = Column(String(120), nullable=True)
    house_number = Column(String(40), nullable=True)
    country = Column(String(2), nullable=True, default="DE")
    postal_code = Column(String(20), nullable=True)
    city = Column(String(120), nullable=True)
    po_box = Column(String(40), nullable=True)
    po_box_postal_code = Column(String(20), nullable=True)
    po_box_city = Column(String(120), nullable=True)
    phone = Column(String(60), nullable=True)
    fax = Column(String(60), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    salutation = Column(String(40), nullable=True)
    brief_salutation = Column(String(120), nullable=True)
    free_field_1 = Column(String(255), nullable=True)
    free_field_2 = Column(String(255), nullable=True)
    free_field_3 = Column(String(255), nullable=True)
    area_code = Column(String(80), nullable=True)
    is_default = Column(Boolean, nullable=False, default=False)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerBillingConfig(Base):
    """Normalized billing/account statement settings (Tab 24)."""
    __tablename__ = "business_partner_billing_configs"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, unique=True, index=True)
    customer_group = Column(String(80), nullable=True)
    customer_type = Column(String(40), nullable=True)  # standard|organ|group_internal
    account_statement_print = Column(Boolean, nullable=False, default=False)
    account_statement_separate = Column(Boolean, nullable=False, default=False)
    account_statement_reprint = Column(Boolean, nullable=False, default=False)
    last_account_statement_number = Column(Integer, nullable=True)
    last_account_statement_date = Column(Date, nullable=True)
    account_balance = Column(DECIMAL(14, 2), nullable=True)
    print_ad_text = Column(Boolean, nullable=False, default=False)
    shipping_expenses_enabled = Column(Boolean, nullable=False, default=False)
    settlement_mode = Column(String(20), nullable=True)  # single|collective
    admin_overhead_surcharge_percent = Column(DECIMAL(7, 2), nullable=True)
    invoice_number_range = Column(String(80), nullable=True)
    bonus_eligible = Column(Boolean, nullable=False, default=False)
    self_billing_sales = Column(Boolean, nullable=False, default=False)
    self_billing_purchase = Column(Boolean, nullable=False, default=False)
    remarkable_claim = Column(Boolean, nullable=False, default=False)
    vat_optimizer = Column(Boolean, nullable=False, default=False)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerCpdAccount(Base):
    """Normalized CPD account records (Tab 25)."""
    __tablename__ = "business_partner_cpd_accounts"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    cpd_customer_number = Column(String(64), nullable=False, unique=True)
    debtor_account = Column(String(40), nullable=True)
    search_term = Column(String(120), nullable=True)
    name_1 = Column(String(255), nullable=False)
    name_2 = Column(String(255), nullable=True)
    name_3 = Column(String(255), nullable=True)
    street = Column(String(120), nullable=True)
    house_number = Column(String(40), nullable=True)
    country = Column(String(2), nullable=True, default="DE")
    postal_code = Column(String(20), nullable=True)
    city = Column(String(120), nullable=True)
    po_box = Column(String(40), nullable=True)
    po_box_city = Column(String(120), nullable=True)
    phone_1 = Column(String(60), nullable=True)
    phone_2 = Column(String(60), nullable=True)
    fax = Column(String(60), nullable=True)
    salutation = Column(String(40), nullable=True)
    brief_salutation = Column(String(120), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    branch_office = Column(String(120), nullable=True)
    cost_center = Column(String(120), nullable=True)
    invoice_type = Column(String(40), nullable=True)
    collective_invoice = Column(Boolean, nullable=False, default=False)
    invoice_form_template = Column(String(80), nullable=True)
    sales_representative = Column(String(120), nullable=True)
    area_code = Column(String(80), nullable=True)
    cash_discount_percent = Column(DECIMAL(7, 2), nullable=True)
    cash_discount_days = Column(Integer, nullable=True)
    payment_target_days = Column(Integer, nullable=True)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerPricingRule(Base):
    """Global pricing/discount rule set per business partner."""
    __tablename__ = "business_partner_pricing_rules"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    direct_account = Column(Boolean, nullable=False, default=False)
    discount_settlement = Column(Boolean, nullable=False, default=False)
    self_pickup_discount_percent = Column(DECIMAL(7, 2), nullable=True)
    price_determination_mode = Column(String(80), nullable=True)
    direct_deduction = Column(Boolean, nullable=False, default=False)
    weekly_price_ec_basis = Column(Boolean, nullable=False, default=False)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerInterestSetting(Base):
    """Extended payment/interest settings per business partner."""
    __tablename__ = "business_partner_interest_settings"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    interest_table_debit_code = Column(String(80), nullable=True)
    interest_table_credit_code = Column(String(80), nullable=True)
    last_interest_date = Column(Date, nullable=True)
    last_interest_balance = Column(DECIMAL(14, 2), nullable=True)
    auto_offset_enabled = Column(Boolean, nullable=False, default=False)
    currency_code = Column(String(3), nullable=True)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerDispatchMedium(Base):
    """Dispatch channel configuration per document type including ZUGFeRD."""
    __tablename__ = "business_partner_dispatch_media"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    document_type = Column(String(80), nullable=False)
    dispatch_channel = Column(String(20), nullable=False)
    enabled = Column(Boolean, nullable=False, default=True)
    zugferd_profile = Column(String(40), nullable=True)
    recipient_email = Column(String(255), nullable=True)
    recipient_name = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerCooperativeMembership(Base):
    """Cooperative membership/share model."""
    __tablename__ = "business_partner_cooperative_memberships"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    membership_number = Column(String(80), nullable=True)
    account_number = Column(String(80), nullable=True)
    membership_status = Column(String(20), nullable=False, default="active")
    entry_date = Column(Date, nullable=True)
    termination_date = Column(Date, nullable=True)
    exit_date = Column(Date, nullable=True)
    termination_reason = Column(String(255), nullable=True)
    mandatory_shares = Column(Integer, nullable=True)
    terminated_mandatory_shares = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerEmailDistribution(Base):
    """Email distribution lists per business partner."""
    __tablename__ = "business_partner_email_distributions"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    distribution_name = Column(String(120), nullable=False)
    description = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerCommunity(Base):
    """Betriebsgemeinschaft header."""
    __tablename__ = "business_partner_communities"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    community_number = Column(String(80), nullable=True, unique=True)
    description = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerCommunityMember(Base):
    """Members of a Betriebsgemeinschaft."""
    __tablename__ = "business_partner_community_members"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    community_id = Column(String(36), ForeignKey("domain_crm.business_partner_communities.id"), nullable=False, index=True)
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, index=True)
    share_percent = Column(DECIMAL(7, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerProfile(Base):
    """Customer profile/analytics related master data."""
    __tablename__ = "business_partner_profiles"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, unique=True, index=True)
    company_founded = Column(Date, nullable=True)
    annual_revenue = Column(DECIMAL(14, 2), nullable=True)
    industry_key = Column(String(80), nullable=True)
    industry_name = Column(String(120), nullable=True)
    professional_association = Column(String(120), nullable=True)
    professional_association_number = Column(String(80), nullable=True)
    competitors = Column(Text, nullable=True)
    bottlenecks = Column(Text, nullable=True)
    organization_structure = Column(Text, nullable=True)
    employee_count = Column(Integer, nullable=True)
    competitive_differentiation = Column(Text, nullable=True)
    works_council = Column(Boolean, nullable=False, default=False)
    company_philosophy = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BusinessPartnerInterfaceProfile(Base):
    """Interface profile (Tankkarte/EAN, EDIFACT, Webshop)."""
    __tablename__ = "business_partner_interface_profiles"
    __table_args__ = {"schema": "domain_crm", "extend_existing": True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    partner_id = Column(String(36), ForeignKey("domain_crm.business_partners.partner_id"), nullable=False, unique=True, index=True)
    tank_card_ean = Column(String(80), nullable=True)
    customer_card_flag = Column(Boolean, nullable=False, default=False)
    edifact_invoic = Column(Boolean, nullable=False, default=False)
    edifact_orders = Column(Boolean, nullable=False, default=False)
    edifact_desadv = Column(Boolean, nullable=False, default=False)
    webshop_customer_number = Column(String(80), nullable=True)
    webshop_description = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Inventory Models
class Article(Base):
    """Article/Product model"""
    __tablename__ = "articles"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_number = Column(String(50), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    suchbegriff = Column(String(100), nullable=True)
    hersteller = Column(String(120), nullable=True)
    herkunftsland = Column(String(2), nullable=True)
    naehrwertangaben = Column(Text, nullable=True)
    mhd_erforderlich = Column(Boolean, nullable=False, default=False)
    lagerartikel = Column(Boolean, nullable=False, default=True)
    mehrwertsteuer_prozent = Column(DECIMAL(5, 2), nullable=True)
    warengruppe = Column(String(80), nullable=True)
    gefahrgutklasse = Column(String(40), nullable=True)
    lagerorte = Column(postgresql.JSONB(astext_type=Text()), nullable=False, default=list)
    chargenpflicht = Column(Boolean, nullable=False, default=False)
    qs_pruefung_erforderlich = Column(Boolean, nullable=False, default=False)
    zolltarifnummer = Column(String(30), nullable=True)
    bio_kennzeichnung = Column(Boolean, nullable=False, default=False)
    gmp_plus_relevanz = Column(Boolean, nullable=False, default=False)
    lieferantennummer = Column(String(50), nullable=True)
    unit = Column(String(10), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    barcode = Column(String(50), nullable=True)
    supplier_number = Column(String(50), nullable=True)
    purchase_price = Column(DECIMAL(10, 2), nullable=True)
    sales_price = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default="EUR")
    min_stock = Column(DECIMAL(10, 2), nullable=True)
    max_stock = Column(DECIMAL(10, 2), nullable=True)
    weight = Column(DECIMAL(8, 2), nullable=True)
    dimensions = Column(String(50), nullable=True)
    current_stock = Column(DECIMAL(10, 2), default=0)
    reserved_stock = Column(DECIMAL(10, 2), default=0)
    available_stock = Column(DECIMAL(10, 2), default=0)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class Warehouse(Base):
    """Warehouse model"""
    __tablename__ = "warehouses"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    warehouse_code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    address = Column(String(200), nullable=False)
    city = Column(String(50), nullable=False)
    postal_code = Column(String(10), nullable=False)
    country = Column(String(2), default="DE")
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    warehouse_type = Column(String(20), default="standard")
    total_capacity = Column(DECIMAL(12, 2), nullable=True)
    used_capacity = Column(DECIMAL(12, 2), default=0)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class StockMovement(Base):
    """Stock movement model"""
    __tablename__ = "inventory_stock_movements"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    movement_type = Column(String(20), nullable=False)  # in, out, transfer, adjustment
    quantity = Column(DECIMAL(10, 2), nullable=False)
    unit_cost = Column(DECIMAL(10, 2), nullable=True)
    unit = Column(String(10), nullable=True)
    reference_number = Column(String(50), nullable=True)
    movement_number = Column(String(64), nullable=True)
    movement_date = Column(Date, nullable=True)
    movement_time = Column(Time, nullable=True)
    notes = Column(Text, nullable=True)
    warehouse_location = Column(String(120), nullable=True)
    charge = Column(String(64), nullable=True)
    booking_user = Column(String(100), nullable=True)
    auto_created = Column(Boolean, nullable=False, default=False)
    linked_order_id = Column(PGUUID(as_uuid=True), nullable=True)
    ownership_type = Column(String(20), nullable=False, default="owned")  # owned, consigned
    owner_partner_id = Column(String(64), nullable=True)
    agrar_contract_id = Column(String(64), nullable=True)
    weighing_ticket_id = Column(String(64), nullable=True)
    storage_fee_relevant = Column(Boolean, nullable=False, default=False)
    storage_fee_start_date = Column(Date, nullable=True)
    storage_fee_monthly_rate = Column(DECIMAL(12, 4), nullable=True)
    storage_fee_last_charged_until = Column(Date, nullable=True)
    previous_stock = Column(DECIMAL(10, 2), nullable=False)
    new_stock = Column(DECIMAL(10, 2), nullable=False)
    total_cost = Column(DECIMAL(12, 2), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InventoryCount(Base):
    """Inventory count model"""
    __tablename__ = "inventory_counts"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    count_date = Column(DateTime(timezone=True), server_default=func.now())
    counted_by = Column(String, ForeignKey("domain_shared.users.id"), nullable=False)
    status = Column(String(20), default="draft")  # draft, completed, approved
    total_items = Column(Integer, default=0)
    discrepancies_found = Column(Integer, default=0)
    approved_by = Column(String, ForeignKey("domain_shared.users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Finance Models
class Account(Base):
    """Chart of accounts model"""
    __tablename__ = "finance_accounts"
    __table_args__ = {"schema": "domain_erp", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    account_number = Column(String(20), nullable=False)
    account_name = Column(String(100), nullable=False)
    account_type = Column(String(20), nullable=False)  # asset, liability, equity, revenue, expense
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    is_summary = Column(Boolean, default=False)
    balance = Column(DECIMAL(15, 2), default=0)
    last_transaction_date = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    parent_account_id = Column(String, ForeignKey("domain_erp.finance_accounts.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class JournalEntry(Base):
    """Journal entry model"""
    __tablename__ = "finance_journal_entries"
    __table_args__ = {"schema": "domain_erp", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entry_number = Column(String(20), nullable=False)
    entry_date = Column(DateTime(timezone=True), nullable=False)
    posting_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String(200), nullable=False)
    reference = Column(String(50), nullable=True)
    source = Column(String(50), nullable=False)
    status = Column(String(20), default="draft")  # draft, posted, reversed
    total_debit = Column(DECIMAL(15, 2), default=0)
    total_credit = Column(DECIMAL(15, 2), default=0)
    posted_by = Column(String, ForeignKey("domain_shared.users.id"), nullable=True)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    reversed_entry_id = Column(String, ForeignKey("domain_erp.finance_journal_entries.id"), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class JournalEntryLine(Base):
    """Journal entry line model"""
    __tablename__ = "finance_journal_entry_lines"
    __table_args__ = {"schema": "domain_erp", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    journal_entry_id = Column(String, ForeignKey("domain_erp.finance_journal_entries.id"), nullable=False)
    account_id = Column(String, ForeignKey("domain_erp.finance_accounts.id"), nullable=False)
    debit = Column(DECIMAL(15, 2), default=0)
    credit = Column(DECIMAL(15, 2), default=0)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# Policy Engine Models
class PolicyRule(Base):
    """MCP policy rule model"""
    __tablename__ = "policy_rules"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=True)
    when_kpi_id = Column(String, nullable=False)
    when_severity = Column(postgresql.JSONB(astext_type=Text()), nullable=False)
    action = Column(String, nullable=False)
    params = Column(postgresql.JSONB(astext_type=Text()), nullable=True)
    limits = Column(postgresql.JSONB(astext_type=Text()), nullable=True)
    window = Column(postgresql.JSONB(astext_type=Text()), nullable=True)
    approval = Column(postgresql.JSONB(astext_type=Text()), nullable=True)
    auto_execute = Column(Boolean, default=False)
    auto_suggest = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Audit & Compliance Models
class AuditLog(Base):
    """Audit log for compliance tracking"""
    __tablename__ = "audit_logs"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    user_id = Column(String, ForeignKey("domain_shared.users.id"), nullable=False)
    user_email = Column(String(100), nullable=False)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String, nullable=False)
    changes = Column(postgresql.JSONB(astext_type=Text()), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(200), nullable=True)
    correlation_id = Column(String(50), nullable=True)


# Import Agrar models
from .agrar_models import (
    Saatgut,
    SaatgutLizenz,
    Duenger,
    DuengerMischung,
    PSM,
    Sachkunde,
    Biostimulanz
)

# Import L3-Connect gap closure models
from .l3c_models import (
    InventoryCountLine,
    WeighingTicket,
    WeighingTicketLine,
    WeighingMeasurement,
    AgrarContract,
    AgrarContractAllocation,
    AgrarSettlement,
    AgrarSettlementDeduction,
    NawaroPrintNotification,
    NawaroContractSheet,
    NawaroContractSheetRow,
    NawaroAreaSheet,
    NawaroAreaSheetRow,
    NawaroRapsProfile,
    NawaroRapsCertificate,
    NawaroRapsBalance,
    Silo,
    SiloLot,
    SiloLotMovement,
    SiloQualitySnapshot,
    WarehouseTransfer,
    WarehouseTransferLine,
    StockCorrection,
    StockCorrectionLine,
    BinLocation,
    PreparationList,
    PreparationListLine,
    PickList,
    PickListLine,
    ShippingUnit,
    WebhookRegistration,
    ArticleBatch,
    InternalMessage,
    MasterDataEntry,
    Dispatcher,
    ArticleSelection,
)
