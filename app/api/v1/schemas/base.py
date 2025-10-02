"""
Base API schemas for VALEO-NeuroERP
Common Pydantic models used across all API endpoints
"""

from datetime import datetime
from typing import Optional, Any, Dict, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

T = TypeVar('T')


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: str
        }
    )


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