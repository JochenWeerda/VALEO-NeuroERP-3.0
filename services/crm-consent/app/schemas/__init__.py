"""Pydantic schemas for CRM Consent."""

from .consent import (
    ConsentBase,
    ConsentCreate,
    ConsentUpdate,
    Consent,
    ConsentHistory,
    ConsentCheckRequest,
    ConsentCheckResponse,
)

__all__ = [
    "ConsentBase",
    "ConsentCreate",
    "ConsentUpdate",
    "Consent",
    "ConsentHistory",
    "ConsentCheckRequest",
    "ConsentCheckResponse",
]

