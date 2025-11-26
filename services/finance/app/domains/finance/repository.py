"""Persistence helpers for Finance models."""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Iterable, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Account, JournalEntry, OpenItem

DEFAULT_ACCOUNTS: tuple[dict[str, str], ...] = (
    {"account_number": "1000", "name": "Kasse", "category": "assets"},
    {"account_number": "1200", "name": "Bank", "category": "assets"},
    {"account_number": "8000", "name": "Umsatzerlöse", "category": "revenue"},
)


class AccountRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self, tenant_id: str) -> list[Account]:
        stmt = (
            select(Account)
            .where(Account.tenant_id == tenant_id, Account.is_active.is_(True))
            .order_by(Account.account_number)
        )
        return list(self.db.scalars(stmt))

    def ensure_seed_data(self, tenant_id: str) -> None:
        if self.list_active(tenant_id):
            return

        for definition in DEFAULT_ACCOUNTS:
            self.db.add(
                Account(
                    tenant_id=tenant_id,
                    account_number=definition["account_number"],
                    name=definition["name"],
                    category=definition["category"],
                )
            )
        self.db.commit()


class JournalEntryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_entries(self, tenant_id: str) -> list[JournalEntry]:
        stmt = (
            select(JournalEntry)
            .where(JournalEntry.tenant_id == tenant_id)
            .order_by(JournalEntry.posted_at.desc())
        )
        return list(self.db.scalars(stmt))

    def create_entry(
        self,
        *,
        tenant_id: str,
        account_id: str,
        description: str,
        amount: Decimal,
        currency: str,
        period: str,
        document_id: str | None,
        user_id: str,
    ) -> JournalEntry:
        entry = JournalEntry(
            tenant_id=tenant_id,
            account_id=account_id,
            description=description,
            amount=amount,
            currency=currency,
            period=period,
            document_id=document_id,
            created_by=user_id,
            posted_at=datetime.utcnow(),
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry


class OpenItemRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_items(self, tenant_id: str) -> list[OpenItem]:
        stmt = select(OpenItem).where(OpenItem.tenant_id == tenant_id)
        return list(self.db.scalars(stmt))

    def seed_demo_items(
        self,
        *,
        tenant_id: str,
        items: Iterable[dict[str, str | Decimal | date]],
    ) -> None:
        existing = self.list_items(tenant_id)
        if existing:
            return
        for item in items:
            self.db.add(OpenItem(tenant_id=tenant_id, **item))
        self.db.commit()

