"""
Base API schemas for VALEO-NeuroERP
Common Pydantic models used across all API endpoints.

Import convention:
    from app.api.v1.schemas.base import (
        BaseSchema, TimestampMixin, TenantMixin, AuditMixin,
        StatusResponse, IDResponse, ListResponse, OffsetPaginatedResponse,
        PaginatedResponse, ErrorResponse,
    )

Anti-patterns verboten:
    response_model=dict          → StatusResponse / IDResponse / eigenes Schema
    response_model=list          → ListResponse[T] oder eigenes Schema
    response_model=Any           → eigenes Schema
"""

from datetime import datetime
from typing import Optional, Any, Dict, TypeVar, Generic
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

T = TypeVar('T')


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseSchema):
    """Mixin for timestamp fields"""
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")


class SoftDeleteMixin(BaseSchema):
    """Mixin for soft delete functionality"""
    is_active: bool = Field(default=True, description="Whether the record is active")
    deleted_at: Optional[datetime] = Field(default=None, description="Deletion timestamp")


class PaginationParams(BaseModel):
    """Parameters for pagination"""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=50, ge=1, le=1000, description="Items per page")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Response wrapper for paginated results"""
    items: list[T] = Field(description="List of items")
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page")
    size: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there is a next page")
    has_prev: bool = Field(description="Whether there is a previous page")


class APIResponse(BaseSchema):
    """Standard API response wrapper"""
    success: bool = Field(description="Whether the operation was successful")
    message: Optional[str] = Field(default=None, description="Response message")
    data: Optional[Any] = Field(default=None, description="Response data")
    errors: Optional[list[str]] = Field(default=None, description="List of errors")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")


class ErrorResponse(BaseSchema):
    """Error response model"""
    detail: str = Field(description="Error detail")
    type: str = Field(description="Error type")
    code: Optional[str] = Field(default=None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")


class HealthResponse(BaseSchema):
    """Health check response"""
    status: str = Field(description="Service status")
    service: str = Field(description="Service name")
    version: str = Field(description="Service version")
    timestamp: float = Field(description="Unix timestamp")


class DatabaseHealthResponse(BaseSchema):
    """Database health check response"""
    status: str = Field(description="Database status")
    database_type: str = Field(description="Database type")
    total_tables: int = Field(description="Total number of tables")
    record_counts: Dict[str, int] = Field(description="Record counts per table")
    timestamp: float = Field(description="Unix timestamp")


# ---------------------------------------------------------------------------
# Tenant / Audit Mixins
# ---------------------------------------------------------------------------

class TenantMixin(BaseSchema):
    """Mixin: Mandanten-Feld für mandantenfähige Entitäten."""
    tenant_id: str = Field(description="Mandanten-ID (X-Tenant-ID)")


class AuditMixin(BaseSchema):
    """Mixin: Audit-Felder (erstellt/geändert von)."""
    created_by: Optional[str] = Field(default=None, description="Erstellt von (User-ID)")
    updated_by: Optional[str] = Field(default=None, description="Geändert von (User-ID)")


# ---------------------------------------------------------------------------
# Einheitliche Response-Typen
# ---------------------------------------------------------------------------

class StatusResponse(BaseSchema):
    """Antwort für Operationen ohne Nutzlast (z. B. DELETE, Trigger, Status-Update).

    Verwendung:
        response_model=StatusResponse
        return StatusResponse(success=True, message="Deleted")
    """
    success: bool = Field(description="Ob die Operation erfolgreich war")
    message: Optional[str] = Field(default=None, description="Optionale Nachricht")


class IDResponse(BaseSchema):
    """Antwort für Create-Operationen, die eine neue ID zurückgeben.

    Verwendung:
        response_model=IDResponse
        return IDResponse(id=str(new_obj.id))
    """
    id: str = Field(description="ID des erstellten Objekts")
    message: Optional[str] = Field(default=None)


class CountResponse(BaseSchema):
    """Antwort für Operationen, die eine Anzahl zurückgeben."""
    count: int = Field(description="Anzahl der betroffenen/gefundenen Datensätze")
    message: Optional[str] = Field(default=None)


class ListResponse(BaseSchema, Generic[T]):
    """Einfache Listen-Antwort ohne Pagination.

    Verwendung:
        response_model=ListResponse[MySchema]
        return ListResponse(items=rows, total=len(rows))
    """
    items: list[T] = Field(description="Listenelemente")
    total: int = Field(description="Gesamtanzahl der Elemente")


class OffsetPaginatedResponse(BaseSchema, Generic[T]):
    """Paginierte Antwort mit Offset/Limit (häufiger ERP-Standard).

    Verwendung:
        response_model=OffsetPaginatedResponse[MySchema]
        return OffsetPaginatedResponse(items=rows, total=n, limit=limit, offset=offset)
    """
    items: list[T] = Field(description="Listenelemente")
    total: int = Field(description="Gesamtanzahl")
    limit: int = Field(description="Max. Elemente pro Seite")
    offset: int = Field(default=0, description="Startposition")


class ValidationErrorItem(BaseSchema):
    """Ein einzelner Validierungsfehler."""
    field: str = Field(description="Feldname")
    message: str = Field(description="Fehlermeldung")
    code: Optional[str] = Field(default=None, description="Fehlercode")


class BulkOperationResponse(BaseSchema):
    """Antwort für Bulk-Operationen (Import, Massenaktualisierung)."""
    success_count: int = Field(description="Erfolgreich verarbeitete Einträge")
    error_count: int = Field(description="Fehlerhafte Einträge")
    errors: list[ValidationErrorItem] = Field(default_factory=list, description="Fehlerdetails")
    message: Optional[str] = Field(default=None)


class CompatFlexOut(BaseSchema):
    """Transitional open schema — allows arbitrary extra fields.

    DEPRECATED: Replace with a proper typed schema for each endpoint.
    Only use this when migrating legacy endpoints; do not use for new code.
    Import from here instead of defining locally in each endpoint file.
    """
    model_config = ConfigDict(extra="allow")
