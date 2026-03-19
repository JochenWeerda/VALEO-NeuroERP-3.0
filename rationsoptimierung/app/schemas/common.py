from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class BaseResponse(BaseModel):
    """Base response model for all API endpoints"""
    success: bool = Field(True, description="Whether the request was successful")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    message: Optional[str] = Field(None, description="Optional message")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "timestamp": "2026-03-18T05:00:00Z",
                "message": "Operation completed successfully"
            }
        }

class ErrorResponse(BaseResponse):
    """Error response model"""
    success: bool = Field(False, description="Whether the request was successful")
    error_code: str = Field(..., description="Error code identifier")
    details: Optional[Any] = Field(None, description="Additional error details")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "timestamp": "2026-03-18T05:00:00Z",
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": {"field": "feed_id", "issue": "required field missing"}
            }
        }

class PaginatedResponse(BaseResponse):
    """Paginated response model"""
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    pages: int = Field(..., ge=0, description="Total number of pages")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "timestamp": "2026-03-18T05:00:00Z",
                "message": "Retrieved paginated feeds",
                "total": 25,
                "page": 1,
                "page_size": 10,
                "pages": 3
            }
        }

class HealthCheckResponse(BaseResponse):
    """Health check response model"""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    services: dict = Field(default_factory=dict, description="Status of dependent services")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "timestamp": "2026-03-18T05:00:00Z",
                "message": "Service is healthy",
                "status": "healthy",
                "version": "1.0.0",
                "services": {
                    "database": "connected",
                    "solver": "available"
                }
            }
        }