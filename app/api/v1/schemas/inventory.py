"""
Inventory domain schemas for VALEO-NeuroERP
Schemas for articles, warehouses, stock movements, and inventory management
"""

from datetime import datetime
from typing import Optional
from pydantic import Field
from decimal import Decimal

from .base import BaseSchema, TimestampMixin, SoftDeleteMixin


# Article/Product Schemas
class ArticleBase(BaseSchema):
    """Base article schema"""
    article_number: str = Field(..., min_length=1, max_length=50, description="Unique article number")
    name: str = Field(..., min_length=1, max_length=100, description="Article name")
    description: Optional[str] = Field(None, max_length=500, description="Article description")
    unit: str = Field(..., max_length=10, description="Unit of measure (e.g., kg, pcs, l)")
    category: str = Field(..., max_length=50, description="Article category")
    subcategory: Optional[str] = Field(None, max_length=50, description="Article subcategory")
    barcode: Optional[str] = Field(None, max_length=50, description="Barcode/EAN")
    supplier_number: Optional[str] = Field(None, max_length=50, description="Supplier article number")
    purchase_price: Optional[Decimal] = Field(None, ge=0, description="Purchase price per unit")
    sales_price: Decimal = Field(..., ge=0, description="Sales price per unit")
    currency: str = Field(default="EUR", max_length=3, description="Currency code")
    min_stock: Optional[Decimal] = Field(None, ge=0, description="Minimum stock level")
    max_stock: Optional[Decimal] = Field(None, ge=0, description="Maximum stock level")
    weight: Optional[Decimal] = Field(None, ge=0, description="Weight per unit")
    dimensions: Optional[str] = Field(None, max_length=50, description="Dimensions (LxWxH)")


class ArticleCreate(ArticleBase):
    """Schema for creating an article"""
    tenant_id: str = Field(..., description="Tenant ID")


class ArticleUpdate(BaseSchema):
    """Schema for updating an article"""
    article_number: Optional[str] = Field(None, min_length=1, max_length=50, description="Unique article number")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Article name")
    description: Optional[str] = Field(None, max_length=500, description="Article description")
    unit: Optional[str] = Field(None, max_length=10, description="Unit of measure")
    category: Optional[str] = Field(None, max_length=50, description="Article category")
    subcategory: Optional[str] = Field(None, max_length=50, description="Article subcategory")
    barcode: Optional[str] = Field(None, max_length=50, description="Barcode/EAN")
    supplier_number: Optional[str] = Field(None, max_length=50, description="Supplier article number")
    purchase_price: Optional[Decimal] = Field(None, ge=0, description="Purchase price per unit")
    sales_price: Optional[Decimal] = Field(None, ge=0, description="Sales price per unit")
    currency: Optional[str] = Field(None, max_length=3, description="Currency code")
    min_stock: Optional[Decimal] = Field(None, ge=0, description="Minimum stock level")
    max_stock: Optional[Decimal] = Field(None, ge=0, description="Maximum stock level")
    weight: Optional[Decimal] = Field(None, ge=0, description="Weight per unit")
    dimensions: Optional[str] = Field(None, max_length=50, description="Dimensions")
    is_active: Optional[bool] = Field(None, description="Whether article is active")


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
    address: str = Field(..., max_length=200, description="Warehouse address")
    city: str = Field(..., max_length=50, description="City")
    postal_code: str = Field(..., max_length=10, description="Postal code")
    country: str = Field(default="DE", max_length=2, description="Country code")
    contact_person: Optional[str] = Field(None, max_length=100, description="Contact person")
    phone: Optional[str] = Field(None, max_length=20, description="Contact phone")
    email: Optional[str] = Field(None, max_length=100, description="Contact email")
    warehouse_type: str = Field(default="standard", max_length=20, description="Warehouse type")


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
    used_capacity: Decimal = Field(default=0, ge=0, description="Used storage capacity")


# Stock Movement Schemas
class StockMovementBase(BaseSchema):
    """Base stock movement schema"""
    article_id: str = Field(..., description="Article ID")
    warehouse_id: str = Field(..., description="Warehouse ID")
    movement_type: str = Field(..., pattern="^(in|out|transfer|adjustment)$", description="Movement type")
    quantity: Decimal = Field(..., description="Movement quantity")
    unit_cost: Optional[Decimal] = Field(None, ge=0, description="Unit cost")
    reference_number: Optional[str] = Field(None, max_length=50, description="Reference document number")
    notes: Optional[str] = Field(None, max_length=200, description="Movement notes")


class StockMovementCreate(StockMovementBase):
    """Schema for creating a stock movement"""
    tenant_id: str = Field(..., description="Tenant ID")


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