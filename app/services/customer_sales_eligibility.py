"""
CRM-Kunde ↔ Business-Partner: Sperr- und Lieferfähigkeit für Verkaufsbelege.

Verwendet domain_crm.customers + business_partners; Auflösung des BP über
business_partner_id oder Kundennummer (partner_number / debtor_account).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session


@dataclass(frozen=True)
class PartnerSalesFlags:
    partner_id: Optional[str]
    status: Optional[str]
    blocked_for_delivery: bool
    blocked_for_invoice: bool


def _resolve_partner_flags(db: Session, tenant_id: str, crm_customer_id: str) -> Optional[PartnerSalesFlags]:
    row = db.execute(
        text(
            """
            SELECT c.customer_number, c.business_partner_id,
                   bp.partner_id AS bp_id, bp.status AS bp_status,
                   bp.blocked_for_delivery, bp.blocked_for_invoice
            FROM domain_crm.customers c
            LEFT JOIN domain_crm.business_partners bp
              ON bp.partner_id = c.business_partner_id AND bp.tenant_id = c.tenant_id
            WHERE c.id = :cid AND c.tenant_id = :tid
            """
        ),
        {"cid": crm_customer_id, "tid": tenant_id},
    ).fetchone()
    if not row:
        return None
    pid = row.bp_id
    st = row.bp_status
    bfd = bool(row.blocked_for_delivery) if row.blocked_for_delivery is not None else False
    bfi = bool(row.blocked_for_invoice) if row.blocked_for_invoice is not None else False
    cn = (row.customer_number or "").strip()
    if not pid and cn:
        r2 = db.execute(
            text(
                """
                SELECT partner_id, status, blocked_for_delivery, blocked_for_invoice
                FROM domain_crm.business_partners
                WHERE tenant_id = :tid
                  AND (partner_number = :cn OR debtor_account = :cn)
                LIMIT 1
                """
            ),
            {"tid": tenant_id, "cn": cn},
        ).fetchone()
        if r2:
            pid = r2.partner_id
            st = r2.status
            bfd = bool(r2.blocked_for_delivery)
            bfi = bool(r2.blocked_for_invoice)
    if not pid:
        return PartnerSalesFlags(
            partner_id=None,
            status=None,
            blocked_for_delivery=False,
            blocked_for_invoice=False,
        )
    return PartnerSalesFlags(
        partner_id=str(pid),
        status=str(st or "active"),
        blocked_for_delivery=bfd,
        blocked_for_invoice=bfi,
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
