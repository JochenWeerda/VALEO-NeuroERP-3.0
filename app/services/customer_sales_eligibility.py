"""
CRM-Kunde ↔ Business-Partner: Sperr- und Lieferfähigkeit für Verkaufsbelege.

Verwendet domain_crm.customers + business_partners; Auflösung des BP über
business_partner_id oder Kundennummer (partner_number / debtor_account).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class PartnerSalesFlags:
    partner_id: Optional[str]
    status: Optional[str]
    blocked_for_delivery: bool
    blocked_for_invoice: bool


def _resolve_partner_flags(db: Session, tenant_id: str, crm_customer_id: str) -> Optional[PartnerSalesFlags]:
    # Phase 2B: Auflösung läuft über die kanonische Zugriffsschicht statt Roh-SQL.
    from app.services.business_partner_service import BusinessPartnerService

    flags = BusinessPartnerService(db, tenant_id).resolve_partner_sales_flags(crm_customer_id)
    if flags is None:
        return None
    return PartnerSalesFlags(
        partner_id=flags["partner_id"],
        status=flags["status"],
        blocked_for_delivery=flags["blocked_for_delivery"],
        blocked_for_invoice=flags["blocked_for_invoice"],
    )


def assert_customer_allowed_for_sales_order(db: Session, tenant_id: str, crm_customer_id: str) -> None:
    """Auftrag: hart gesperrte Kunden / Lieferstopp."""
    flags = _resolve_partner_flags(db, tenant_id, crm_customer_id)
    if flags is None:
        return
    if flags.status == "blocked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kunde ist im Stammdatensatz gesperrt — Auftrag nicht möglich.",
        )
    if flags.blocked_for_delivery:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kunde ist für Lieferungen gesperrt — Auftrag mit Lieferbezug nicht möglich.",
        )


def assert_customer_allowed_for_delivery(db: Session, tenant_id: str, crm_customer_id: str) -> None:
    """Lieferschein / LS aus Auftrag."""
    flags = _resolve_partner_flags(db, tenant_id, crm_customer_id)
    if flags is None:
        return
    if flags.status == "blocked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kunde ist gesperrt — Lieferschein nicht möglich.",
        )
    if flags.blocked_for_delivery:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kunde ist für Lieferungen gesperrt.",
        )


def describe_sales_eligibility(db: Session, tenant_id: str, crm_customer_id: str) -> dict:
    """Für UI: Freigaben und Hinweistexte ohne Exception."""
    flags = _resolve_partner_flags(db, tenant_id, crm_customer_id)
    if flags is None:
        return {
            "linked": False,
            "allowed_order": True,
            "allowed_delivery": True,
            "allowed_invoice": True,
            "reasons": [],
        }
    if not flags.partner_id:
        return {
            "linked": False,
            "allowed_order": True,
            "allowed_delivery": True,
            "allowed_invoice": True,
            "reasons": [],
        }
    reasons: list[str] = []
    allowed_order = True
    allowed_delivery = True
    allowed_invoice = True
    if flags.status == "blocked":
        reasons.append("Kunde im Stammdatensatz gesperrt (status=blocked).")
        allowed_order = False
        allowed_delivery = False
        allowed_invoice = False
    if flags.blocked_for_delivery:
        reasons.append("Lieferungen für diesen Kunden gesperrt.")
        allowed_delivery = False
        allowed_order = False
    if flags.blocked_for_invoice:
        reasons.append("Rechnungsstellung für diesen Kunden gesperrt.")
        allowed_invoice = False
    return {
        "linked": True,
        "partner_id": flags.partner_id,
        "allowed_order": allowed_order,
        "allowed_delivery": allowed_delivery,
        "allowed_invoice": allowed_invoice,
        "reasons": reasons,
    }


def assert_customer_allowed_for_invoice(db: Session, tenant_id: str, crm_customer_id: str) -> None:
    """Rechnungsstellung (falls separater Pfad)."""
    flags = _resolve_partner_flags(db, tenant_id, crm_customer_id)
    if flags is None:
        return
    if flags.status == "blocked":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kunde ist gesperrt — Rechnung nicht möglich.",
        )
    if flags.blocked_for_invoice:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Kunde ist für Rechnungsstellung gesperrt.",
        )
