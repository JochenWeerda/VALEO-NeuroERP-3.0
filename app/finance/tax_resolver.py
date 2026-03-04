from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

EU_COUNTRIES = {
    "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR",
    "DE", "GR", "HU", "IE", "IT", "LV", "LT", "LU", "MT", "NL",
    "PL", "PT", "RO", "SK", "SI", "ES", "SE",
}


def resolve_partner_country(db: Session, partner_id: str | None, default: str = "DE") -> str:
    if not partner_id:
        return default
    try:
        row = db.execute(
            text(
                """
                SELECT country
                FROM domain_shared.business_partners
                WHERE partner_id = :partner_id
                LIMIT 1
                """
            ),
            {"partner_id": partner_id},
        ).fetchone()
        if row and row[0]:
            country = str(row[0]).strip().upper()
            if len(country) == 2:
                return country
    except Exception:
        pass
    return default


def resolve_tax_key_accounts(
    db: Session,
    tenant_id: str,
    rate: Decimal,
    country: str,
    as_of: date | None = None,
) -> dict[str, Any]:
    """
    Resolve tax key with pragmatic fallback order:
    1) exact country + inferred flags (intracom/export)
    2) exact country
    3) DE fallback
    """
    as_of = as_of or date.today()
    country = (country or "DE").strip().upper()
    intracom = country in EU_COUNTRIES and country != "DE"
    export = country not in EU_COUNTRIES

    base_sql = """
        SELECT code, debit_account, credit_account, reverse_charge, intracom, export, country
        FROM domain_erp.tax_keys
        WHERE tenant_id = :tenant_id
          AND active = true
          AND steuersatz = :rate
          AND gueltig_von <= :as_of
          AND (gueltig_bis IS NULL OR gueltig_bis >= :as_of)
          AND country = :country
        ORDER BY
          CASE WHEN intracom = :intracom THEN 0 ELSE 1 END,
          CASE WHEN export = :export THEN 0 ELSE 1 END,
          gueltig_von DESC
        LIMIT 1
    """

    def _fetch(c: str):
        return db.execute(
            text(base_sql),
            {
                "tenant_id": tenant_id,
                "rate": rate,
                "as_of": as_of,
                "country": c,
                "intracom": intracom,
                "export": export,
            },
        ).fetchone()

    row = _fetch(country) or _fetch("DE")
    if not row:
        return {
            "code": None,
            "debit_account": None,
            "credit_account": None,
            "reverse_charge": False,
            "intracom": intracom,
            "export": export,
            "country": country,
        }

    return {
        "code": str(row[0]) if row[0] is not None else None,
        "debit_account": str(row[1]) if row[1] is not None else None,
        "credit_account": str(row[2]) if row[2] is not None else None,
        "reverse_charge": bool(row[3]),
        "intracom": bool(row[4]),
        "export": bool(row[5]),
        "country": str(row[6]) if row[6] is not None else country,
    }

