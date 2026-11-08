"""Server-owned closing checks; persisted template text is never executable SQL."""
from datetime import date
import re
from fastapi import HTTPException
from sqlalchemy import text


def verified_closing_actor(user: dict) -> str:
    subject = user.get("sub")
    if not isinstance(subject, str) or not subject.strip():
        raise HTTPException(status_code=401, detail="Verified actor required")
    return subject


def validate_closing_item(db, *, item_code: str, tenant_id: str, period: str) -> tuple[bool, int]:
    if not re.fullmatch(r"[0-9]{4}-(0[1-9]|1[0-2])", period):
        raise ValueError("Invalid closing period")
    year, month = map(int, period.split("-"))
    start = date(year, month, 1)
    end = date(year + (month == 12), month % 12 + 1, 1)
    queries = {
        "GL-001": "SELECT COUNT(*) FROM domain_erp.journal_entries WHERE tenant_id=:tenant_id AND posting_date>=:start AND posting_date<:end AND status='draft'",
        "AR-001": "SELECT COUNT(*) FROM domain_erp.offene_posten WHERE tenant_id=:tenant_id AND debtor_id IS NOT NULL AND offen>0",
        "AP-001": "SELECT COUNT(*) FROM domain_erp.offene_posten WHERE tenant_id=:tenant_id AND creditor_id IS NOT NULL AND offen>0",
        "TAX-001": "SELECT COUNT(*) FROM domain_erp.vat_returns WHERE tenant_id=:tenant_id AND period=:period AND status IN ('calculated', 'validated', 'submitted')",
    }
    if item_code not in queries:
        raise ValueError("Automatic closing check is not registered")
    value = int(db.execute(text(queries[item_code]), {"tenant_id": tenant_id, "period": period, "start": start, "end": end}).scalar_one())
    return (value > 0 if item_code == "TAX-001" else value == 0), value
