"""
L3-Connect Gap Closure Models
Database models for inventory extensions, logistics, messaging, webhooks,
and master-data tables required for L3-Connect API parity.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
import uuid

from ...core.database import Base


# ── Inventory Count Lines ────────────────────────────────────────

class InventoryCountLine(Base):
    """Individual line item within an inventory count."""
    __tablename__ = "inventory_count_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    inventory_count_id = Column(String, ForeignKey("domain_inventory.inventory_counts.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    expected_qty = Column(DECIMAL(12, 3), default=0)
    counted_qty = Column(DECIMAL(12, 3), default=0)
    difference = Column(DECIMAL(12, 3), default=0)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=True)
    bin_location_id = Column(String, nullable=True)
    batch_number = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── Weighing Tickets ─────────────────────────────────────────────

class WeighingTicket(Base):
    """Wiegeschein header."""
    __tablename__ = "weighing_tickets"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_number = Column(String(50), nullable=False)
    scale_id = Column(String(50), nullable=True)
    vehicle_plate = Column(String(20), nullable=True)
    gross_weight = Column(DECIMAL(12, 3), nullable=True)
    tare_weight = Column(DECIMAL(12, 3), nullable=True)
    net_weight = Column(DECIMAL(12, 3), nullable=True)
    first_weighing_at = Column(DateTime(timezone=True), nullable=True)
    second_weighing_at = Column(DateTime(timezone=True), nullable=True)
    moisture_pct = Column(DECIMAL(5, 2), nullable=True)
    protein_pct = Column(DECIMAL(5, 2), nullable=True)
    impurities_pct = Column(DECIMAL(5, 2), nullable=True)
    hl_weight = Column(DECIMAL(6, 2), nullable=True)
    billing_weight = Column(DECIMAL(12, 3), nullable=True)
    quality_data = Column(JSONB, nullable=True)
    contract_id = Column(String, ForeignKey("domain_inventory.agrar_contracts.id"), nullable=True)
    allocated_quantity_kg = Column(DECIMAL(12, 3), nullable=True)
    allocation_status = Column(String(20), nullable=False, default="unallocated")  # unallocated / allocated / posted
    weighing_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="open")
    direction = Column(String(10), default="in")  # in / out
    reference_doc = Column(String(100), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WeighingTicketLine(Base):
    """Wiegeschein position."""
    __tablename__ = "weighing_ticket_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String, ForeignKey("domain_inventory.weighing_tickets.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    quantity = Column(DECIMAL(12, 3), nullable=False)
    unit = Column(String(10), default="kg")
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WeighingMeasurement(Base):
    """Wiegeschein quality measurement entries."""
    __tablename__ = "weighing_measurements"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String, ForeignKey("domain_inventory.weighing_tickets.id"), nullable=False)
    metric_key = Column(String(50), nullable=False)
    metric_value = Column(DECIMAL(10, 3), nullable=False)
    unit = Column(String(20), nullable=True)
    measured_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AgrarContract(Base):
    """Agrar contract (buy/sell) with quantity tracking."""
    __tablename__ = "agrar_contracts"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_number = Column(String(50), nullable=False)
    contract_type = Column(String(10), nullable=False)  # buy / sell
    harvest_year = Column(Integer, nullable=False)
    partner_id = Column(String(64), nullable=False)
    article_id = Column(String(64), nullable=False)
    pricing_model = Column(String(10), nullable=False)  # fixed / follow / pool
    pool_group_id = Column(String(64), nullable=True)
    fixed_price = Column(DECIMAL(12, 2), nullable=True)
    currency = Column(String(3), nullable=False, default="EUR")
    total_quantity_kg = Column(DECIMAL(12, 3), nullable=False)
    remaining_quantity_kg = Column(DECIMAL(12, 3), nullable=False)
    status = Column(String(20), nullable=False, default="open")  # open / partially_allocated / fulfilled / cancelled
    valid_from = Column(DateTime(timezone=True), nullable=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AgrarContractAllocation(Base):
    """Allocation entries against an agrar contract."""
    __tablename__ = "agrar_contract_allocations"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = Column(String, ForeignKey("domain_inventory.agrar_contracts.id"), nullable=False)
    ticket_id = Column(String, ForeignKey("domain_inventory.weighing_tickets.id"), nullable=True)
    allocation_quantity_kg = Column(DECIMAL(12, 3), nullable=False)
    allocated_at = Column(DateTime(timezone=True), server_default=func.now())
    note = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Warehouse Transfers ──────────────────────────────────────────

class WarehouseTransfer(Base):
    """Lager-zu-Lager Buchung header."""
    __tablename__ = "warehouse_transfers"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transfer_number = Column(String(50), nullable=False)
    from_warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    to_warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    status = Column(String(20), default="draft")
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WarehouseTransferLine(Base):
    """Lager-zu-Lager Buchung position."""
    __tablename__ = "warehouse_transfer_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    transfer_id = Column(String, ForeignKey("domain_inventory.warehouse_transfers.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    quantity = Column(DECIMAL(12, 3), nullable=False)
    batch_number = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Stock Corrections ────────────────────────────────────────────

class StockCorrection(Base):
    """Bestandskorrektur header."""
    __tablename__ = "stock_corrections"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    correction_number = Column(String(50), nullable=False)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    reason = Column(String(100), nullable=True)
    status = Column(String(20), default="draft")
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StockCorrectionLine(Base):
    """Bestandskorrektur position."""
    __tablename__ = "stock_correction_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    correction_id = Column(String, ForeignKey("domain_inventory.stock_corrections.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    old_quantity = Column(DECIMAL(12, 3), nullable=False)
    new_quantity = Column(DECIMAL(12, 3), nullable=False)
    difference = Column(DECIMAL(12, 3), nullable=False)
    batch_number = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Bin Locations ────────────────────────────────────────────────

class BinLocation(Base):
    """Lagerfach."""
    __tablename__ = "bin_locations"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), nullable=False)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    zone = Column(String(20), nullable=True)
    rack = Column(String(20), nullable=True)
    shelf = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Preparation Lists ───────────────────────────────────────────

class PreparationList(Base):
    """Rüstliste header."""
    __tablename__ = "preparation_lists"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    list_number = Column(String(50), nullable=False)
    status = Column(String(20), default="open")
    notes = Column(Text, nullable=True)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PreparationListLine(Base):
    """Rüstliste position."""
    __tablename__ = "preparation_list_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    list_id = Column(String, ForeignKey("domain_inventory.preparation_lists.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    required_qty = Column(DECIMAL(12, 3), nullable=False)
    picked_qty = Column(DECIMAL(12, 3), default=0)
    bin_location_id = Column(String, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Pick Lists ───────────────────────────────────────────────────

class PickList(Base):
    """Pickliste header."""
    __tablename__ = "pick_lists"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pick_list_number = Column(Integer, nullable=False)
    status = Column(String(20), default="open")
    tour_id = Column(String, nullable=True)
    order_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PickListLine(Base):
    """Pickliste position."""
    __tablename__ = "pick_list_lines"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pick_list_id = Column(String, ForeignKey("domain_inventory.pick_lists.id"), nullable=False)
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    required_qty = Column(DECIMAL(12, 3), nullable=False)
    picked_qty = Column(DECIMAL(12, 3), default=0)
    bin_location_id = Column(String, nullable=True)
    batch_number = Column(String(50), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Shipping Units (NVE/SSCC) ────────────────────────────────────

class ShippingUnit(Base):
    """NVE / SSCC Versandeinheit."""
    __tablename__ = "shipping_units"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sscc = Column(String(18), nullable=False, unique=True)
    status = Column(String(20), default="created")
    order_id = Column(String, nullable=True)
    delivery_note_id = Column(String, nullable=True)
    weight = Column(DECIMAL(12, 3), nullable=True)
    contents = Column(JSONB, nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── Webhook Registrations ────────────────────────────────────────

class WebhookRegistration(Base):
    """Webhook-Registrierung."""
    __tablename__ = "webhook_registrations"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String(500), nullable=False)
    event_area = Column(String(50), nullable=False)
    secret = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── Article Batches ──────────────────────────────────────────────

class ArticleBatch(Base):
    """Chargen-Bestand für Artikel."""
    __tablename__ = "article_batches"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    batch_number = Column(String(50), nullable=False)
    warehouse_id = Column(String, ForeignKey("domain_inventory.warehouses.id"), nullable=False)
    quantity = Column(DECIMAL(12, 3), default=0)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Internal Messages ────────────────────────────────────────────

class InternalMessage(Base):
    """Interne Nachricht."""
    __tablename__ = "internal_messages"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String, ForeignKey("domain_shared.users.id"), nullable=False)
    recipient_id = Column(String, ForeignKey("domain_shared.users.id"), nullable=False)
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=True)
    is_read = Column(Boolean, default=False)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


# ── Master Data Entries ──────────────────────────────────────────

class MasterDataEntry(Base):
    """Generic lookup / master-data table."""
    __tablename__ = "master_data_entries"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    category = Column(String(50), nullable=False)  # e.g. 'branch', 'country', 'shipping_method'
    code = Column(String(50), nullable=False)
    label = Column(String(200), nullable=False)
    extra = Column(JSONB, nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── Dispatchers ──────────────────────────────────────────────────

class Dispatcher(Base):
    """Disponent."""
    __tablename__ = "dispatchers"
    __table_args__ = {"schema": "domain_shared", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    code = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(30), nullable=True)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ── Article Selections ───────────────────────────────────────────

class ArticleSelection(Base):
    """Artikel-Selektion (Zuordnung)."""
    __tablename__ = "article_selections"
    __table_args__ = {"schema": "domain_inventory", "extend_existing": True}

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey("domain_inventory.articles.id"), nullable=False)
    selection_code = Column(String(50), nullable=False)
    label = Column(String(200), nullable=True)
    tenant_id = Column(String, ForeignKey("domain_shared.tenants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

