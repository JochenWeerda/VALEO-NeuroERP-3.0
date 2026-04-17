"""Configurable number range service for Debitor/Kreditor accounts and partner numbers."""
from __future__ import annotations

from sqlalchemy.orm import Session

from app.infrastructure.models import NumberRange


class NumberRangeService:
    def __init__(self, db: Session):
        self.db = db

    def next_number(self, range_type: str, tenant_id: str) -> str:
        nr = self.db.query(NumberRange).filter(
            NumberRange.range_type == range_type,
            NumberRange.tenant_id == tenant_id,
            NumberRange.is_active.is_(True),
        ).with_for_update().first()

        if not nr:
            raise ValueError(f"Kein aktiver Nummernkreis fuer '{range_type}' in Mandant '{tenant_id}'")

        value = nr.current_value
        formatted = f"{nr.prefix}{value:0{nr.digit_count}d}"
        nr.current_value = value + 1
        self.db.flush()
        return formatted

    def peek_next(self, range_type: str, tenant_id: str) -> str | None:
        nr = self.db.query(NumberRange).filter(
            NumberRange.range_type == range_type,
            NumberRange.tenant_id == tenant_id,
            NumberRange.is_active.is_(True),
        ).first()
        if not nr:
            return None
        return f"{nr.prefix}{nr.current_value:0{nr.digit_count}d}"

    def configure(
        self,
        tenant_id: str,
        range_type: str,
        prefix: str,
        start_number: int,
        digit_count: int,
        reserved_prefix_digits: int = 1,
    ) -> NumberRange:
        existing = self.db.query(NumberRange).filter(
            NumberRange.range_type == range_type,
            NumberRange.tenant_id == tenant_id,
        ).first()

        if existing:
            if digit_count < existing.digit_count:
                raise ValueError("Stellenanzahl darf nicht verkleinert werden")
            existing.prefix = prefix
            existing.digit_count = digit_count
            existing.reserved_prefix_digits = reserved_prefix_digits
            if existing.current_value == existing.start_number:
                existing.start_number = start_number
                existing.current_value = start_number
            self.db.flush()
            return existing

        nr = NumberRange(
            tenant_id=tenant_id,
            range_type=range_type,
            prefix=prefix,
            start_number=start_number,
            current_value=start_number,
            digit_count=digit_count,
            reserved_prefix_digits=reserved_prefix_digits,
        )
        self.db.add(nr)
        self.db.flush()
        return nr

    def list_ranges(self, tenant_id: str) -> list[NumberRange]:
        return self.db.query(NumberRange).filter(
            NumberRange.tenant_id == tenant_id,
        ).order_by(NumberRange.range_type).all()
