"""
API schemas for shared domain (tenants, users)
Pydantic models for request/response validation
"""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from uuid import UUID

from .base import BaseSchema, PaginatedResponse


# Tenant Schemas
class Tenant(BaseSchema):
    """Tenant schema"""
    id: str
    name: str = Field(..., max_length=100, description="Tenant name")
    domain: str = Field(..., max_length=100, description="Tenant domain")
    settings: Optional[str] = Field("{}", description="Tenant settings as JSON string")
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TenantCreate(BaseSchema):
    """Tenant creation schema"""
    name: str = Field(..., max_length=100, description="Tenant name")
    domain: str = Field(..., max_length=100, description="Tenant domain")
    settings: Optional[str] = Field("{}", description="Tenant settings as JSON string")


class TenantUpdate(BaseSchema):
    """Tenant update schema"""
    name: Optional[str] = Field(None, max_length=100)
    domain: Optional[str] = Field(None, max_length=100)
    settings: Optional[str] = None


# User Schemas
class User(BaseSchema):
    """User schema"""
    id: str
    username: str = Field(..., max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., max_length=50, description="First name")
    last_name: str = Field(..., max_length=50, description="Last name")
    roles: Optional[str] = Field("[]", description="User roles as JSON array")
    tenant_id: str
    keycloak_id: Optional[str]
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserCreate(BaseSchema):
    """User creation schema"""
    username: str = Field(..., max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., max_length=50, description="First name")
    last_name: str = Field(..., max_length=50, description="Last name")
    roles: Optional[str] = Field("[]", description="User roles as JSON array")
    tenant_id: str = Field(..., description="Tenant ID")
    password: str = Field(..., min_length=8, description="User password")


class UserUpdate(BaseSchema):
    """User update schema"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    roles: Optional[str] = None


class UserLogin(BaseSchema):
    """User login schema"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


# Authentication Schemas
class LoginRequest(BaseSchema):
    """Login request schema"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="User password")


class TokenResponse(BaseSchema):
    """Token response schema"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: User


class ChangePasswordRequest(BaseSchema):
    """Change password request schema"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")


class PasswordResetRequest(BaseSchema):
    """Password reset request schema"""
    email: EmailStr = Field(..., description="User email address")


class PasswordReset(BaseSchema):
    """Password reset schema"""
    token: str = Field(..., description="Reset token")
    new_password: str = Field(..., min_length=8, description="New password")


class PasswordChange(BaseSchema):
    """Password change schema (alias for ChangePasswordRequest)"""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password")