"""Auto-generated domain schemas for gobd archiv.

These are named open schemas (extra="allow") that provide semantic names
in the OpenAPI documentation while maintaining backwards compatibility.
Replace with fully typed schemas as the domain stabilizes.
"""
from __future__ import annotations

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict


class GobdArchivOut(BaseSchema):
    """Response schema for gobd archiv endpoints."""
    model_config = ConfigDict(extra="allow")


# --- Extracted from endpoint file ---
class DocumentArtifactCreate(BaseModel):
    header_id: str = Field(..., min_length=1, max_length=36)
    artifact_type: str = Field(..., pattern="^(pdf|xml|html|other)$")
    content_hash_sha256: str = Field(..., min_length=64, max_length=64)
    storage_key: str = Field(..., min_length=1, max_length=500)
    file_name: Optional[str] = Field(default=None, max_length=255)
    created_by: Optional[str] = Field(default=None, max_length=100)


class DocumentArtifactOut(BaseModel):
    id: str
    tenant_id: str
    header_id: str
    artifact_type: str
    content_hash_sha256: str
    storage_key: str
    file_name: Optional[str]
    created_at: datetime
    created_by: Optional[str]


class ArtifactVeri4Out(BaseModel):
    """Integritätsprüfung: Artifact-ID, Content-Hash und Speicherreferenz für Verifikation."""

    id: str
    header_id: str
    artifact_type: str
    content_hash_sha256: str
    storage_key: str
    file_name: Optional[str]


class InvoiceXmlCreate(BaseModel):
    header_id: str = Field(..., min_length=1, max_length=36)
    content_hash_sha256: str = Field(..., min_length=64, max_length=64)
    storage_key: str = Field(..., min_length=1, max_length=500)
    format_type: str = Field(default="XRechnung", max_length=40)
    created_by: Optional[str] = Field(default=None, max_length=100)


class InvoiceXmlOut(BaseModel):
    id: str
    tenant_id: str
    header_id: str
    content_hash_sha256: str
    storage_key: str
    format_type: str
    validation_status: str
    validation_errors: Optional[dict[str, Any]]
    created_at: datetime
    created_by: Optional[str]


class ArtifactVerifyOut(BaseModel):
    id: str
    stored_hash: str
    provided_hash: Optional[str] = None
    match: Optional[bool] = None
    integrity_status: str  # "verified" | "mismatch" | "unchecked"


class InvoiceXmlValidateIn(BaseModel):
    validation_status: str = Field(..., pattern="^(valid|invalid|pending)$")
    validation_errors: Optional[dict[str, Any]] = None

