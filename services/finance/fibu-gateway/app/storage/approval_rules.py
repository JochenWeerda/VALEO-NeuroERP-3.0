"""Persistente Ablage für FiBu-Approval-Rules (pro Tenant)."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Iterable, List

from finance_shared.auth import FiBuRole


@dataclass(frozen=True)
class ApprovalRuleRecord:
    tenant_id: str
    currency: str
    min_amount: Decimal
    required_role: FiBuRole


class ApprovalRuleStore:
    """Sehr leichte SQLite-basierte Ablage – ersetzt später zentrale Config-DB."""

    def __init__(
        self,
        db_path: str,
        *,
        default_min_amount: Decimal = Decimal("1000.00"),
        default_currency: str = "EUR",
        default_role: FiBuRole = FiBuRole.FREIGEBER,
    ) -> None:
        self._path = Path(db_path).expanduser()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._default_min_amount = default_min_amount
        self._default_currency = default_currency.upper()
        self._default_role = default_role
        self._init_db()
        self._ensure_default_rule()

    def list_rules(self, tenant_id: str) -> List[ApprovalRuleRecord]:
        records = self._fetch_rules(tenant_id)
        if not records:
            records = self._fetch_rules("*")
        return records

    def upsert_rule(
        self,
        *,
        tenant_id: str,
        currency: str,
        min_amount: Decimal,
        required_role: FiBuRole,
    ) -> None:
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                """
                INSERT INTO approval_rules (tenant_id, currency, min_amount, required_role)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(tenant_id, currency, min_amount)
                DO UPDATE SET required_role=excluded.required_role
                """,
                (tenant_id, currency.upper(), str(min_amount), required_role.value),
            )

    def _fetch_rules(self, tenant_id: str) -> List[ApprovalRuleRecord]:
        with sqlite3.connect(self._path) as conn:
            cursor = conn.execute(
                """
                SELECT tenant_id, currency, min_amount, required_role
                FROM approval_rules
                WHERE tenant_id = ?
                ORDER BY CAST(min_amount AS REAL)
                """,
                (tenant_id,),
            )
            rows = cursor.fetchall()
        return [
            ApprovalRuleRecord(
                tenant_id=row[0],
                currency=row[1],
                min_amount=Decimal(row[2]),
                required_role=FiBuRole(row[3]),
            )
            for row in rows
        ]

    def _init_db(self) -> None:
        with sqlite3.connect(self._path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS approval_rules (
                    tenant_id TEXT NOT NULL,
                    currency TEXT NOT NULL,
                    min_amount TEXT NOT NULL,
                    required_role TEXT NOT NULL,
                    PRIMARY KEY (tenant_id, currency, min_amount)
                )
                """
            )

    def _ensure_default_rule(self) -> None:
        if self._fetch_rules("*"):
            return
        self.upsert_rule(
            tenant_id="*",
            currency=self._default_currency,
            min_amount=self._default_min_amount,
            required_role=self._default_role,
        )


