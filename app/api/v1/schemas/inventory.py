"""
Inventory domain schemas for VALEO-NeuroERP
Schemas for articles, warehouses, stock movements, and inventory management
"""

from datetime import datetime, date, time
from typing import Any, Optional, Union
from pydantic import Field, field_validator
from decimal import Decimal

from .base import BaseSchema, TimestampMixin, SoftDeleteMixin


# Article/Product Schemas
class ArticleBase(BaseSchema):
    """Base article schema"""
    article_number: str = Field(..., min_length=1, max_length=50, description="Unique article number")
    name: str = Field(..., min_length=1, max_length=100, description="Article name")
    description: Optional[str] = Field(None, max_length=500, description="Article description")
    description2: Optional[str] = Field(None, description="Zweite Bezeichnung (Extended description)")
    short_description: Optional[str] = Field(None, max_length=200, description="Kurzbezeichnung (Short description)")
    suchbegriff: Optional[str] = Field(None, max_length=100, description="Search term/matchcode")
    matchcode2: Optional[str] = Field(None, max_length=100, description="Zweiter Matchcode (Alternative search term)")
    hersteller: Optional[str] = Field(None, max_length=120, description="Manufacturer")
    herkunftsland: Optional[str] = Field(None, max_length=2, description="Country of origin")
    naehrwertangaben: Optional[str] = Field(None, description="Nutrition facts / composition")
    mhd_erforderlich: bool = Field(default=False, description="Best-before date required")
    lagerartikel: bool = Field(default=True, description="Is stock-managed article")
    mehrwertsteuer_prozent: Optional[Decimal] = Field(None, ge=0, le=100, description="VAT percentage")
    warengruppe: Optional[str] = Field(None, max_length=80, description="Product group")
    # Dangerous goods
    gefahrgutklasse: Optional[str] = Field(None, max_length=40, description="Dangerous goods class")
    gefahrgut_un_nummer: Optional[str] = Field(None, max_length=20, description="UN number for dangerous goods")
    gefahrgut_verpackungsgruppe: Optional[str] = Field(None, max_length=5, description="Packing group (I, II, III)")
    gefahrgut_anhaenge: Optional[str] = Field(None, max_length=200, description="Dangerous goods labels")
    lagerorte: list[str] = Field(default_factory=list, description="Default storage locations")
    chargenpflicht: bool = Field(default=False, description="Batch tracking required")
    qs_pruefung_erforderlich: bool = Field(default=False, description="QS check required")
    zolltarifnummer: Optional[str] = Field(None, max_length=30, description="Customs tariff number")
    bio_kennzeichnung: bool = Field(default=False, description="Bio labeling")
    gmp_plus_relevanz: bool = Field(default=False, description="GMP+ relevance")
    # Extended labeling
    kennzeichnung_bio: Optional[str] = Field(None, max_length=50, description="Bio labeling type")
    kennzeichnung_vegan: Optional[str] = Field(None, max_length=10, description="Vegan: Ja/Nein/Unbekannt")
    kennzeichnung_vegetarisch: Optional[str] = Field(None, max_length=10, description="Vegetarian: Ja/Nein/Unbekannt")
    kennzeichnung_allergene: Optional[str] = Field(None, description="Allergen information")
    kennzeichnung_herkunft: Optional[str] = Field(None, max_length=100, description="Origin labeling")
    # Extended storage
    lager_min_temperatur: Optional[Decimal] = Field(None, ge=-50, le=100, description="Min storage temperature")
    lager_max_temperatur: Optional[Decimal] = Field(None, ge=-50, le=100, description="Max storage temperature")
    lager_lagerdauer_tage: Optional[int] = Field(None, ge=0, description="Storage duration in days")
    lager_zentral: bool = Field(default=False, description="Central warehouse")
    lager_silo: bool = Field(default=False, description="Silo storage")
    # Extended analysis
    analyse_protein: Optional[Decimal] = Field(None, ge=0, le=100, description="Protein content %")
    analyse_feuchtigkeit: Optional[Decimal] = Field(None, ge=0, le=100, description="Moisture content %")
    analyse_schadex: Optional[Decimal] = Field(None, ge=0, le=100, description="Schadex (damage index) %")
    analyse_fremdstoffe: Optional[Decimal] = Field(None, ge=0, le=100, description="Foreign substances %")
    analyse_sonstiges: Optional[str] = Field(None, description="Other analysis results")
    # Search filter fields
    ean_code: Optional[str] = Field(None, max_length=50, description="EAN code")
    alt_ean_code: Optional[str] = Field(None, max_length=50, description="Alternative EAN code")
    lieferanten_artikelnummer: Optional[str] = Field(None, max_length=50, description="Supplier article number")
    kunden_artikelnummer: Optional[str] = Field(None, max_length=50, description="Customer article number")
    verwendungszweck: Optional[str] = Field(None, max_length=255, description="Intended use/purpose")
    nachhaltige_biomasse: bool = Field(default=False, description="Sustainable biomass")
    pool_artikel: bool = Field(default=False, description="Pool article")
    # Discount/Surcharge fields
    rabatt_auftrag_rechnung: Optional[Decimal] = Field(None, ge=0, le=100, description="Order/Invoice discount %")
    rabatt_lose: Optional[Decimal] = Field(None, ge=0, le=100, description="Loose discount %")
    rabatt_selbstabholer: Optional[Decimal] = Field(None, ge=0, le=100, description="Self-pickup discount %")
    zu_abschlag_1_code: Optional[str] = Field(None, max_length=50, description="Surcharge/Charge code 1")
    zu_abschlag_1_prozent: Optional[Decimal] = Field(None, ge=-100, le=100, description="Surcharge/Charge percent 1")
    zu_abschlag_2_code: Optional[str] = Field(None, max_length=50, description="Surcharge/Charge code 2")
    zu_abschlag_2_prozent: Optional[Decimal] = Field(None, ge=-100, le=100, description="Surcharge/Charge percent 2")
    berechne_zu_abschlag_auf_netto: bool = Field(default=False, description="Calculate surcharge on net")
    einfuegen_summe_nach_zu_abschlag: bool = Field(default=False, description="Insert total line after surcharge")
    # Discount flags
    skontofaehig: bool = Field(default=True, description="Discountable (skonto)")
    warenrueckverguetung: bool = Field(default=False, description="Goods refund/rebate")
    bonus_faehig: bool = Field(default=False, description="Bonus eligible")
    rabattfaehig: bool = Field(default=True, description="Discount eligible")
    # Basic fields
    lieferantennummer: Optional[str] = Field(None, max_length=50, description="Preferred supplier number")
    unit: str = Field(..., max_length=10, description="Unit of measure (e.g., kg, pcs, l)")
    category: str = Field(..., max_length=50, description="Article category")
    subcategory: Optional[str] = Field(None, max_length=50, description="Article subcategory")
    barcode: Optional[str] = Field(None, max_length=50, description="Barcode/EAN")
    supplier_number: Optional[str] = Field(None, max_length=50, description="Supplier article number")
    customer_article_number: Optional[str] = Field(None, max_length=50, description="Kunden-Artikel-Nummer (Customer-specific article number)")
    purchase_price: Optional[Decimal] = Field(None, ge=0, description="Purchase price per unit")
    sales_price: Decimal = Field(..., ge=0, description="Sales price per unit")
    currency: str = Field(default="EUR", max_length=3, description="Currency code")
    min_stock: Optional[Decimal] = Field(None, ge=0, description="Minimum stock level")
    max_stock: Optional[Decimal] = Field(None, ge=0, description="Maximum stock level")
    weight: Optional[Decimal] = Field(None, ge=0, description="Weight per unit")
    dimensions: Optional[str] = Field(None, max_length=50, description="Dimensions (LxWxH)")
    # Extended Einheiten (Preis-Bezugsgroesse, Gebinde)
    einheit_typ: Optional[str] = Field(None, max_length=20, description="Unit type (weight, volume, etc.)")
    einheit_faktor: Optional[Decimal] = Field(None, description="Conversion factor to base unit")
    einheit_preiseinheit: Optional[str] = Field(None, max_length=20, description="Price reference unit, e.g. '100 kg'")
    gebinde_groesse: Optional[Decimal] = Field(None, ge=0, description="Package/container size")
    gebinde_einheit: Optional[str] = Field(None, max_length=20, description="Package unit code, e.g. 'Sa' (Sack)")


class ArticleCreate(ArticleBase):
    """Schema for creating an article"""
    tenant_id: str = Field(..., description="Tenant ID")


class ArticleUpdate(BaseSchema):
    """Schema for updating an article"""
    article_number: Optional[str] = Field(None, min_length=1, max_length=50, description="Unique article number")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Article name")
    description: Optional[str] = Field(None, max_length=500, description="Article description")
    description2: Optional[str] = Field(None, description="Zweite Bezeichnung (Extended description)")
    short_description: Optional[str] = Field(None, max_length=200, description="Kurzbezeichnung (Short description)")
    suchbegriff: Optional[str] = Field(None, max_length=100, description="Search term/matchcode")
    matchcode2: Optional[str] = Field(None, max_length=100, description="Zweiter Matchcode (Alternative search term)")
    hersteller: Optional[str] = Field(None, max_length=120, description="Manufacturer")
    herkunftsland: Optional[str] = Field(None, max_length=2, description="Country of origin")
    naehrwertangaben: Optional[str] = Field(None, description="Nutrition facts / composition")
    mhd_erforderlich: Optional[bool] = Field(None, description="Best-before date required")
    lagerartikel: Optional[bool] = Field(None, description="Is stock-managed article")
    mehrwertsteuer_prozent: Optional[Decimal] = Field(None, ge=0, le=100, description="VAT percentage")
    warengruppe: Optional[str] = Field(None, max_length=80, description="Product group")
    # Dangerous goods
    gefahrgutklasse: Optional[str] = Field(None, max_length=40, description="Dangerous goods class")
    gefahrgut_un_nummer: Optional[str] = Field(None, max_length=20, description="UN number for dangerous goods")
    gefahrgut_verpackungsgruppe: Optional[str] = Field(None, max_length=5, description="Packing group (I, II, III)")
    gefahrgut_anhaenge: Optional[str] = Field(None, max_length=200, description="Dangerous goods labels")
    lagerorte: Optional[list[str]] = Field(None, description="Default storage locations")
    chargenpflicht: Optional[bool] = Field(None, description="Batch tracking required")
    qs_pruefung_erforderlich: Optional[bool] = Field(None, description="QS check required")
    zolltarifnummer: Optional[str] = Field(None, max_length=30, description="Customs tariff number")
    bio_kennzeichnung: Optional[bool] = Field(None, description="Bio labeling")
    gmp_plus_relevanz: Optional[bool] = Field(None, description="GMP+ relevance")
    # Extended labeling
    kennzeichnung_bio: Optional[str] = Field(None, max_length=50, description="Bio labeling type")
    kennzeichnung_vegan: Optional[str] = Field(None, max_length=10, description="Vegan: Ja/Nein/Unbekannt")
    kennzeichnung_vegetarisch: Optional[str] = Field(None, max_length=10, description="Vegetarian: Ja/Nein/Unbekannt")
    kennzeichnung_allergene: Optional[str] = Field(None, description="Allergen information")
    kennzeichnung_herkunft: Optional[str] = Field(None, max_length=100, description="Origin labeling")
    # Extended storage
    lager_min_temperatur: Optional[Decimal] = Field(None, ge=-50, le=100, description="Min storage temperature")
    lager_max_temperatur: Optional[Decimal] = Field(None, ge=-50, le=100, description="Max storage temperature")
    lager_lagerdauer_tage: Optional[int] = Field(None, ge=0, description="Storage duration in days")
    lager_zentral: Optional[bool] = Field(None, description="Central warehouse")
    lager_silo: Optional[bool] = Field(None, description="Silo storage")
    # Extended analysis
    analyse_protein: Optional[Decimal] = Field(None, ge=0, le=100, description="Protein content %")
    analyse_feuchtigkeit: Optional[Decimal] = Field(None, ge=0, le=100, description="Moisture content %")
    analyse_schadex: Optional[Decimal] = Field(None, ge=0, le=100, description="Schadex (damage index) %")
    analyse_fremdstoffe: Optional[Decimal] = Field(None, ge=0, le=100, description="Foreign substances %")
    analyse_sonstiges: Optional[str] = Field(None, description="Other analysis results")
    lieferantennummer: Optional[str] = Field(None, max_length=50, description="Preferred supplier number")
    unit: Optional[str] = Field(None, max_length=10, description="Unit of measure")
    category: Optional[str] = Field(None, max_length=50, description="Article category")
    subcategory: Optional[str] = Field(None, max_length=50, description="Article subcategory")
    barcode: Optional[str] = Field(None, max_length=50, description="Barcode/EAN")
    supplier_number: Optional[str] = Field(None, max_length=50, description="Supplier article number")
    customer_article_number: Optional[str] = Field(None, max_length=50, description="Kunden-Artikel-Nummer (Customer-specific article number)")
    purchase_price: Optional[Decimal] = Field(None, ge=0, description="Purchase price per unit")
    sales_price: Optional[Decimal] = Field(None, ge=0, description="Sales price per unit")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    min_stock: Optional[Decimal] = Field(None, ge=0, description="Minimum stock level")
    max_stock: Optional[Decimal] = Field(None, ge=0, description="Maximum stock level")
    weight: Optional[Decimal] = Field(None, ge=0, description="Weight per unit")
    dimensions: Optional[str] = Field(None, max_length=50, description="Dimensions")
    einheit_typ: Optional[str] = Field(None, max_length=20, description="Unit type (weight, volume, etc.)")
    einheit_faktor: Optional[Decimal] = Field(None, description="Conversion factor to base unit")
    einheit_preiseinheit: Optional[str] = Field(None, max_length=20, description="Price reference unit, e.g. '100 kg'")
    gebinde_groesse: Optional[Decimal] = Field(None, ge=0, description="Package/container size")
    gebinde_einheit: Optional[str] = Field(None, max_length=20, description="Package unit code, e.g. 'Sa' (Sack)")
    is_active: Optional[bool] = Field(None, description="Whether article is active")
    image_url: Optional[str] = Field(None, max_length=500, description="Product image URL (auto-fetched or manually set)")


class Article(ArticleBase, TimestampMixin, SoftDeleteMixin):
    """Full article schema"""
    id: str = Field(..., description="Article ID")
    tenant_id: str = Field(..., description="Tenant ID")
    current_stock: Decimal = Field(default=0, ge=0, description="Current stock quantity")
    reserved_stock: Decimal = Field(default=0, ge=0, description="Reserved stock quantity")
    available_stock: Decimal = Field(default=0, ge=0, description="Available stock quantity")


# Warehouse Schemas
class WarehouseBase(BaseSchema):
    """Base warehouse schema"""
    warehouse_code: str = Field(..., min_length=1, max_length=20, description="Unique warehouse code")
    name: str = Field(..., min_length=1, max_length=100, description="Warehouse name")
    address: Optional[str] = Field(None, max_length=200, description="Warehouse address")
    city: Optional[str] = Field(None, max_length=50, description="City")

    @field_validator("address", mode="before")
    @classmethod
    def coerce_address(cls, v: Any) -> Optional[str]:
        # 001_initial_schema.py created address as JSONB; coerce to str for backwards compat
        if isinstance(v, dict):
            return str(v)
        return v
    postal_code: Optional[str] = Field(None, max_length=10, description="Postal code")
    country: Optional[str] = Field(default="DE", max_length=2, description="Country code")
    contact_person: Optional[str] = Field(None, max_length=100, description="Contact person")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    email: Optional[str] = Field(None, max_length=100, description="Contact email")
    warehouse_type: Optional[str] = Field(default="standard", max_length=20, description="Warehouse type")


class WarehouseCreate(WarehouseBase):
    """Schema for creating a warehouse"""
    tenant_id: str = Field(..., description="Tenant ID")


class WarehouseUpdate(BaseSchema):
    """Schema for updating a warehouse"""
    warehouse_code: Optional[str] = Field(None, min_length=1, max_length=20, description="Unique warehouse code")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Warehouse name")
    address: Optional[str] = Field(None, max_length=200, description="Warehouse address")
    city: Optional[str] = Field(None, max_length=50, description="City")
    postal_code: Optional[str] = Field(None, max_length=10, description="Postal code")
    country: Optional[str] = Field(None, max_length=2, description="Country code")
    contact_person: Optional[str] = Field(None, max_length=100, description="Contact person")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    email: Optional[str] = Field(None, max_length=100, description="Contact email")
    warehouse_type: Optional[str] = Field(None, max_length=20, description="Warehouse type")
    is_active: Optional[bool] = Field(None, description="Whether warehouse is active")


class Warehouse(WarehouseBase, TimestampMixin, SoftDeleteMixin):
    """Full warehouse schema"""
    id: str = Field(..., description="Warehouse ID")
    tenant_id: str = Field(..., description="Tenant ID")
    total_capacity: Optional[Decimal] = Field(None, ge=0, description="Total storage capacity")
    used_capacity: Optional[Decimal] = Field(default=0, ge=0, description="Used storage capacity")


# Stock Movement Schemas
class StockMovementBase(BaseSchema):
    """Base stock movement schema"""
    article_id: str = Field(..., description="Article ID")
    warehouse_id: str = Field(..., description="Warehouse ID")
    movement_type: str = Field(..., pattern="^(in|out|transfer|adjustment)$", description="Movement type")
    quantity: Decimal = Field(..., description="Movement quantity")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Unit cost")
    unit: Optional[str] = Field(None, max_length=10, description="Unit of measure for booking")
    movement_number: Optional[str] = Field(None, max_length=64, description="Movement number")
    movement_date: Optional[date] = Field(None, description="Booking date")
    movement_time: Optional[time] = Field(None, description="Booking time")
    reference_number: Optional[str] = Field(None, max_length=50, description="Reference document number")
    notes: Optional[str] = Field(None, max_length=200, description="Movement notes")
    warehouse_location: Optional[str] = Field(None, max_length=120, description="Location text")
    charge: Optional[str] = Field(None, max_length=64, description="Batch/charge")
    booking_user: Optional[str] = Field(None, max_length=100, description="Booking user")
    auto_created: bool = Field(default=False, description="Automatically created movement")
    linked_order_id: Optional[str] = Field(None, description="Linked order ID")
    ownership_type: str = Field(default="owned", pattern="^(owned|consigned)$", description="Stock ownership type")
    owner_partner_id: Optional[str] = Field(None, max_length=64, description="Owner partner for consigned stock")
    agrar_contract_id: Optional[str] = Field(None, max_length=64, description="Linked agrar contract")
    weighing_ticket_id: Optional[str] = Field(None, max_length=64, description="Linked weighing ticket")
    storage_fee_relevant: bool = Field(default=False, description="Whether storage fee applies")
    storage_fee_start_date: Optional[date] = Field(None, description="Storage fee start date")
    storage_fee_monthly_rate: Optional[Decimal] = Field(None, ge=0, description="Monthly storage fee rate")
    storage_fee_last_charged_until: Optional[date] = Field(None, description="Last storage-fee run covered until")
    process_type: Optional[str] = Field(
        default=None,
        pattern="^(mix|withdrawal|split|transfer)$",
        description="Process type for charge lineage",
    )


class ChargeLineageSource(BaseSchema):
    from_charge: str = Field(..., min_length=1, max_length=64, description="Source charge")
    quantity_share: Decimal = Field(..., gt=0, description="Quantity share from source charge")
    share_percent: Optional[Decimal] = Field(None, ge=0, le=100, description="Optional percentage share")
    source_movement_id: Optional[str] = Field(None, description="Optional source movement reference")
    notes: Optional[str] = Field(None, max_length=500, description="Lineage note")


class StockMovementCreate(StockMovementBase):
    """Schema for creating a stock movement"""
    tenant_id: Optional[str] = Field(None, description="Tenant ID")
    lineage_sources: list[ChargeLineageSource] = Field(default_factory=list, description="Source charges for lineage linking")


class StockMovementUpdate(BaseSchema):
    """Schema for updating stock movement metadata."""
    movement_number: Optional[str] = Field(None, max_length=64)
    movement_date: Optional[date] = None
    movement_time: Optional[time] = None
    unit: Optional[str] = Field(None, max_length=10)
    reference_number: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=200)
    warehouse_location: Optional[str] = Field(None, max_length=120)
    charge: Optional[str] = Field(None, max_length=64)
    booking_user: Optional[str] = Field(None, max_length=100)
    auto_created: Optional[bool] = None
    linked_order_id: Optional[str] = None
    ownership_type: Optional[str] = Field(None, pattern="^(owned|consigned)$")
    owner_partner_id: Optional[str] = Field(None, max_length=64)
    agrar_contract_id: Optional[str] = Field(None, max_length=64)
    weighing_ticket_id: Optional[str] = Field(None, max_length=64)
    storage_fee_relevant: Optional[bool] = None
    storage_fee_start_date: Optional[date] = None
    storage_fee_monthly_rate: Optional[Decimal] = Field(None, ge=0)
    storage_fee_last_charged_until: Optional[date] = None


class StockMovement(StockMovementBase, TimestampMixin):
    """Full stock movement schema"""
    id: str = Field(..., description="Movement ID")
    tenant_id: str = Field(..., description="Tenant ID")
    previous_stock: Decimal = Field(..., ge=0, description="Stock before movement")
    new_stock: Decimal = Field(..., ge=0, description="Stock after movement")
    total_cost: Optional[Decimal] = Field(None, ge=0, description="Total movement cost")


# Inventory Count Schemas
class InventoryCountBase(BaseSchema):
    """Base inventory count schema"""
    warehouse_id: str = Field(..., description="Warehouse ID")
    count_date: datetime = Field(default_factory=datetime.now, description="Count date")
    counted_by: str = Field(..., description="User who performed the count")
    status: str = Field(default="draft", pattern="^(draft|completed|approved)$", description="Count status")


class InventoryCountCreate(InventoryCountBase):
    """Schema for creating an inventory count"""
    tenant_id: str = Field(..., description="Tenant ID")


class InventoryCount(InventoryCountBase, TimestampMixin):
    """Full inventory count schema"""
    id: str = Field(..., description="Count ID")
    tenant_id: str = Field(..., description="Tenant ID")
    total_items: int = Field(default=0, ge=0, description="Total items counted")
    discrepancies_found: int = Field(default=0, ge=0, description="Number of discrepancies")
    approved_by: Optional[str] = Field(None, description="User who approved the count")
    approved_at: Optional[datetime] = Field(None, description="Approval timestamp")
