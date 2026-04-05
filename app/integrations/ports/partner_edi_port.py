"""Canonical partner EDI preview port contract."""

from .partner_adapter_port import PartnerAdapterPort, PartnerPreview

PartnerEdiPort = PartnerAdapterPort

__all__ = [
    "PartnerAdapterPort",
    "PartnerEdiPort",
    "PartnerPreview",
]
