"""
Tax Profile Service.
Handles supplier tax profile lookup and multi-parameter Self-Billing tax-key resolution.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import and_, or_, text
from sqlalchemy.orm import Session

from app.core.exceptions import ValidationFailedError
from app.infrastructure.models import SupplierTaxProfile


TRANSACTION_TYPE_SELF_BILLING = "self_billing_purchase"


def get_taxation_type_for_supplier(
    db: Session,
    supplier_id: str,
    tenant_id: str,
    effective_date: Optional[date] = None,
    *,
    require_profile: bool = False,
) -> str:
    """
    Ermittelt taxation_type für einen Lieferanten.

    Priorität:
    1. Supplier Tax Profile (gültig zum effective_date)
    2. Fallback: "regular" — nur wenn require_profile=False (Entwurf/Vorschau)

    Bei require_profile=True (endgültige Ausstellung/Buchung): hart ValidationFailedError (HTTP 422).
    """
    if not effective_date:
        effective_date = date.today()

    profile = db.query(SupplierTaxProfile).filter(
        and_(
            SupplierTaxProfile.supplier_id == supplier_id,
            SupplierTaxProfile.tenant_id == tenant_id,
            SupplierTaxProfile.valid_from <= effective_date,
            or_(
                SupplierTaxProfile.valid_to.is_(None),
                SupplierTaxProfile.valid_to >= effective_date,
            ),
        )
    ).order_by(SupplierTaxProfile.valid_from.desc()).first()

    if profile:
        return profile.taxation_type

    if require_profile:
        raise ValidationFailedError(
            "Lieferanten-Steuerprofil fehlt oder ist am Lieferdatum nicht gültig; "
            "endgültige Self-Billing-Ausstellung ohne Profil ist nicht erlaubt."
        )
    return "regular"


def require_self_billing_agreement(
    db: Session,
    tenant_id: str,
    supplier_id: str,
) -> None:
    """Selbstfakturierungsvereinbarung (Einkauf) muss am Partner gesetzt sein."""
    row = db.execute(
        text(
            "SELECT self_billing_purchase FROM domain_crm.business_partners "
            "WHERE tenant_id = :t AND partner_id = :p"
        ),
        {"t": tenant_id, "p": supplier_id},
    ).first()
    if row is None:
        # Fallback: Kundenstamm mit business_partner_id
        row = db.execute(
            text(
                "SELECT bp.self_billing_purchase FROM domain_crm.business_partners bp "
                "JOIN domain_crm.customers c ON c.business_partner_id = bp.partner_id "
                "AND c.tenant_id = bp.tenant_id "
                "WHERE bp.tenant_id = :t AND (c.id::text = :p OR bp.partner_id = :p) "
                "LIMIT 1"
            ),
            {"t": tenant_id, "p": supplier_id},
        ).first()
    if row is None or not bool(row[0]):
        raise ValidationFailedError(
            "Selbstfakturierungsvereinbarung fehlt; endgültige Ausstellung ist nicht erlaubt."
        )


def resolve_self_billing_tax_code(
    db: Session,
    *,
    tenant_id: str,
    supplier_id: str,
    taxation_type: str,
    article_tax_class: Optional[str],
    transaction_type: str,
    delivery_date: date,
) -> dict[str, Any]:
    """
    Multi-Parameter-Steuerauflösung für Self-Billing (kein 1:1 taxation_type→tax_code).

    Parameter: tenant, supplier, taxation_type, article_tax_class, transaction_type, delivery_date.
    §24 (ustg24_flat_rate) nur über Keys mit par_24_ustg und nur wenn taxation_type das verlangt;
    regular/small_business wählen passende Eingangs-Keys ohne §24 bzw. Satz 0.
    """
    if transaction_type != TRANSACTION_TYPE_SELF_BILLING:
        raise ValidationFailedError(f"Unbekannter Self-Billing-Transaktionstyp: {transaction_type}")

    stichtag = delivery_date or date.today()
    # Explizite Property-Overrides (optional, nie alleiniger Tenant-Pauschalschlüssel als Default)
    override_keys = [
        f"agrar.self_billing.tax_code.{taxation_type}.{article_tax_class or '_'}",
        f"agrar.self_billing.tax_code.{taxation_type}",
    ]
    props = {
        r[0]: r[1]
        for r in db.execute(
            text(
                "SELECT property_key, property_value FROM domain_shared.system_properties "
                "WHERE tenant_id = :t AND property_key = ANY(:keys)"
            ),
            {"t": tenant_id, "keys": override_keys},
        ).fetchall()
    }
    preferred = next((props[k].strip() for k in override_keys if props.get(k) and str(props[k]).strip()), None)

    rows = db.execute(
        text(
            "SELECT code, steuersatz, debit_account, expense_account, par_24_ustg, reverse_charge "
            "FROM domain_erp.tax_keys "
            "WHERE tenant_id = :t AND active "
            "AND gueltig_von <= :d AND (gueltig_bis IS NULL OR gueltig_bis >= :d) "
            "AND (debit_account IS NOT NULL OR credit_account IS NULL) "
            "ORDER BY LPAD(code, 2, '0')"
        ),
        {"t": tenant_id, "d": stichtag},
    ).mappings().all()

    def _match(row) -> bool:
        if row["reverse_charge"]:
            return False
        satz = Decimal(str(row["steuersatz"]))
        is_p24 = bool(row["par_24_ustg"])
        if taxation_type == "ustg24_flat_rate":
            return is_p24
        if taxation_type == "small_business":
            return (not is_p24) and satz == 0
        # regular: Eingangskey ohne §24; article_tax_class kann Satz andeuten (reduced/standard)
        if is_p24:
            return False
        if article_tax_class in ("reduced", "7", "ermäßigt") and satz == Decimal("7"):
            return True
        if article_tax_class in ("standard", "19", "voll") and satz == Decimal("19"):
            return True
        if article_tax_class in ("zero", "0", "steuerfrei") and satz == 0:
            return True
        # ohne article_tax_class: reduzierter Eingangskey bevorzugt, sonst erster passender
        return not is_p24

    candidates = [r for r in rows if _match(r)]
    if preferred:
        for r in candidates:
            if str(r["code"]) == preferred:
                return {
                    "tax_code": str(r["code"]),
                    "rate": Decimal(str(r["steuersatz"])),
                    "expense_account": (str(r["expense_account"]).strip() if r["expense_account"] else None),
                    "vorsteuerkonto": (str(r["debit_account"]).strip() if r["debit_account"] else None),
                    "par_24_ustg": bool(r["par_24_ustg"]),
                    "taxation_type": taxation_type,
                    "supplier_id": supplier_id,
                    "article_tax_class": article_tax_class,
                    "delivery_date": stichtag.isoformat(),
                }
        raise ValidationFailedError(
            f"Konfigurierter Self-Billing-Steuerschlüssel {preferred} passt nicht zu "
            f"taxation_type={taxation_type} / article_tax_class={article_tax_class} am {stichtag}."
        )

    if not candidates:
        raise ValidationFailedError(
            f"Kein gültiger Eingangssteuerschlüssel für taxation_type={taxation_type}, "
            f"article_tax_class={article_tax_class}, Stichtag {stichtag}."
        )

    # Prefer reduced (7) for regular when class unset; else first match
    if taxation_type == "regular" and not article_tax_class:
        for r in candidates:
            if Decimal(str(r["steuersatz"])) == Decimal("7"):
                chosen = r
                break
        else:
            chosen = candidates[0]
    else:
        chosen = candidates[0]

    return {
        "tax_code": str(chosen["code"]),
        "rate": Decimal(str(chosen["steuersatz"])),
        "expense_account": (str(chosen["expense_account"]).strip() if chosen["expense_account"] else None),
        "vorsteuerkonto": (str(chosen["debit_account"]).strip() if chosen["debit_account"] else None),
        "par_24_ustg": bool(chosen["par_24_ustg"]),
        "taxation_type": taxation_type,
        "supplier_id": supplier_id,
        "article_tax_class": article_tax_class,
        "delivery_date": stichtag.isoformat(),
    }
