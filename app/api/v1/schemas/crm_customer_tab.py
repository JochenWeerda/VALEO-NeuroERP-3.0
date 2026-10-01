"""Zeilenformen der Register in der Kundenakte."""

from __future__ import annotations

from typing import Optional

from pydantic import ConfigDict, Field

from app.api.v1.schemas.base import BaseSchema

class CustomerTabOut(BaseSchema):
    """Die Huelle jeder Register-Antwort der Kunden-360-Maske."""

    model_config = ConfigDict(extra="allow")

    tab_key: str
    table_key: str
    total: int = 0
    page: int = 1
    limit: int = 25


class CustomerContactRowOut(BaseSchema):
    """Eine Zeile im Register Ansprechpartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str = ""
    firstName: str = ""
    position: str = ""
    email: str = ""
    phone1: str = ""


class CustomerOrderRowOut(BaseSchema):
    """Eine Zeile im Register Auftraege."""

    model_config = ConfigDict(extra="allow")

    id: str
    order_number: Optional[str] = None
    status: Optional[str] = None
    total_amount: float = 0.0
    created_at: Optional[str] = None


class CustomerActivityRowOut(BaseSchema):
    """Eine Zeile im Register Aktivitaeten."""

    model_config = ConfigDict(extra="allow")

    id: str
    activity_type: Optional[str] = None
    subject: Optional[str] = None
    status: str = ""
    assigned_to: str = ""
    created_at: Optional[str] = None


class CustomerDocumentRowOut(BaseSchema):
    """Eine Zeile im Register Dokumente — offene Posten des Kunden."""

    model_config = ConfigDict(extra="allow")

    id: str
    rechnungsnr: Optional[str] = None
    faelligkeit: Optional[str] = None
    amount: float = 0.0
    days_overdue: int = 0
    op_status: Optional[str] = None


class CustomerContactsTabOut(CustomerTabOut):
    items: list[CustomerContactRowOut] = Field(default_factory=list)


class CustomerOrdersTabOut(CustomerTabOut):
    items: list[CustomerOrderRowOut] = Field(default_factory=list)


class CustomerActivitiesTabOut(CustomerTabOut):
    items: list[CustomerActivityRowOut] = Field(default_factory=list)


class CustomerDocumentsTabOut(CustomerTabOut):
    items: list[CustomerDocumentRowOut] = Field(default_factory=list)


class CustomerTaskRowOut(BaseSchema):
    """Eine Zeile im Register Aufgaben."""

    model_config = ConfigDict(extra="allow")

    id: str
    titel: str = ""
    art: str = ""
    prioritaet: str = ""
    status: str = ""
    faellig: Optional[str] = None


class CustomerContractRowOut(BaseSchema):
    """Eine Zeile im Register Kontrakte."""

    model_config = ConfigDict(extra="allow")

    id: str
    contract_no: Optional[str] = None
    contract_type: Optional[str] = None
    status: Optional[str] = None
    contract_date: Optional[str] = None
    total_quantity: float = 0.0


class CustomerTasksTabOut(CustomerTabOut):
    items: list[CustomerTaskRowOut] = Field(default_factory=list)


class CustomerContractsTabOut(CustomerTabOut):
    items: list[CustomerContractRowOut] = Field(default_factory=list)


class CustomerOfferRowOut(BaseSchema):
    """Eine Zeile im Register Angebote — Verkaufschance aus der Pipeline."""

    model_config = ConfigDict(extra="allow")

    id: str
    title: str = ""
    stage: str = ""
    estimated_value: float = 0.0
    expected_close_date: Optional[str] = None
    probability: Optional[float] = None


class CustomerOffersTabOut(CustomerTabOut):
    items: list[CustomerOfferRowOut] = Field(default_factory=list)


class CustomerHistoryTabOut(CustomerTabOut):
    items: list[CustomerActivityRowOut] = Field(default_factory=list)


class CustomerInstructionRowOut(BaseSchema):
    """Eine Chef-Anweisung am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    instruction_priority: str = ""
    instruction_text: str = ""
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class CustomerInstructionsTabOut(CustomerTabOut):
    items: list[CustomerInstructionRowOut] = Field(default_factory=list)


class CustomerAddressRowOut(BaseSchema):
    """Eine normalisierte Anschrift am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    address_type: str = ""
    name_1: str = ""
    street: str = ""
    postal_code: str = ""
    city: str = ""
    email: str = ""
    is_default: Optional[bool] = None


class CustomerAddressesTabOut(CustomerTabOut):
    items: list[CustomerAddressRowOut] = Field(default_factory=list)


class CustomerCpdRowOut(BaseSchema):
    """Ein CPD-Konto am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    cpd_customer_number: str = ""
    debtor_account: str = ""
    name_1: str = ""
    city: str = ""
    email: str = ""


class CustomerCpdTabOut(CustomerTabOut):
    items: list[CustomerCpdRowOut] = Field(default_factory=list)


class CustomerDiscountRowOut(BaseSchema):
    """Eine Rabattzeile am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    article_number: str = ""
    description: str = ""
    discount_percent: float = 0.0
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class CustomerDiscountsTabOut(CustomerTabOut):
    items: list[CustomerDiscountRowOut] = Field(default_factory=list)


class CustomerPriceRowOut(BaseSchema):
    """Eine Preisvereinbarung am Geschaeftspartner."""

    model_config = ConfigDict(extra="allow")

    id: str
    article_number: str = ""
    description: str = ""
    price_net: Optional[float] = None
    price_unit: str = ""
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class CustomerPricesTabOut(CustomerTabOut):
    items: list[CustomerPriceRowOut] = Field(default_factory=list)
