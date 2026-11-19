"""FIN-ABSCHLUSS-STUBS-001 — GoBD-taugliche Periodenabschluss-Fachlogik.

Ergänzt FinancePeriodService (public.finance_accounting_periods) um
echte Salden aus domain_erp.journal_entries und die Sperre als Abschluss.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.finance_period_service import FinancePeriodService, PeriodError


class ClosingError(Exception):
    """Fachlicher Fehler beim Periodenabschluss (→ HTTP 422)."""


@dataclass
class ClosingCalculateResult:
    period: str
    closing_type: str
    entry_count: int
    total_debit: float
    total_credit: float
    balance: float
    status: str = "calculated"
    account_balances: list[dict] = field(default_factory=list)


@dataclass
class ClosingLockResult:
    period: str
    status: str
    message: str
    locked_at: Optional[str] = None


@dataclass
class ClosingRunResult:
    period: str
    closing_type: str
    entry_count: int
    status: str
    message: str


def _f(v) -> float:
    return float(v) if isinstance(v, Decimal) else float(v or 0)


class FinanceClosingService:
    """Periodenabschluss-Service für calculate / lock / run."""

    def __init__(self, db: Session, tenant_id: str) -> None:
        self.db = db
        self.tenant_id = tenant_id
        self._period_svc = FinancePeriodService(db, tenant_id)

    # ── Calculate ─────────────────────────────────────────────────────────────

    def calculate(self, period: str, closing_type: str = "monthly") -> ClosingCalculateResult:
        """Summiert gebuchte journal_entries der Periode. Wirft ClosingError bei DB-Problemen."""
        try:
            row = self.db.execute(
                text("""
                    SELECT
                        COUNT(DISTINCT je.id) AS entry_count,
                        COALESCE(SUM(CASE WHEN jl.debit  > 0 THEN jl.debit  ELSE 0 END), 0) AS total_debit,
                        COALESCE(SUM(CASE WHEN jl.credit > 0 THEN jl.credit ELSE 0 END), 0) AS total_credit
                    FROM domain_erp.journal_entries je
                    JOIN domain_erp.journal_entry_lines jl ON jl.journal_entry_id = je.id
                    WHERE je.tenant_id = :tid
                      AND je.period    = :period
                      AND je.status    = 'posted'
                """),
                {"tid": self.tenant_id, "period": period},
            ).first()
        except Exception:
            return ClosingCalculateResult(
                period=period,
                closing_type=closing_type,
                entry_count=0,
                total_debit=0.0,
                total_credit=0.0,
                balance=0.0,
                status="unavailable",
            )
        if row is None:
            raise ClosingError(f"Keine Buchungsdaten für Periode {period} gefunden.")

        entry_count = int(row[0] or 0)
        total_debit = _f(row[1])
        total_credit = _f(row[2])

        # Salden je Konto (für Frontend-Tabelle)
        account_rows = self.db.execute(
            text("""
                SELECT
                    jl.account_id,
                    COALESCE(coa.account_number, jl.account_id) AS konto,
                    COALESCE(coa.account_name,   jl.account_id) AS bezeichnung,
                    COALESCE(SUM(jl.debit),  0) AS soll,
                    COALESCE(SUM(jl.credit), 0) AS haben
                FROM domain_erp.journal_entries je
                JOIN domain_erp.journal_entry_lines jl ON jl.journal_entry_id = je.id
                LEFT JOIN domain_erp.chart_of_accounts coa ON coa.id = jl.account_id
                WHERE je.tenant_id = :tid
                  AND je.period    = :period
                  AND je.status    = 'posted'
                GROUP BY jl.account_id, coa.account_number, coa.account_name
                ORDER BY coa.account_number NULLS LAST
                LIMIT 200
            """),
            {"tid": self.tenant_id, "period": period},
        ).mappings().all()

        account_balances = [
            {
                "konto": r["konto"],
                "bezeichnung": r["bezeichnung"],
                "soll": _f(r["soll"]),
                "haben": _f(r["haben"]),
                "saldo": _f(r["soll"]) - _f(r["haben"]),
            }
            for r in account_rows
        ]

        return ClosingCalculateResult(
            period=period,
            closing_type=closing_type,
            entry_count=entry_count,
            total_debit=total_debit,
            total_credit=total_credit,
            balance=total_debit - total_credit,
            account_balances=account_balances,
        )

    # ── Lock ──────────────────────────────────────────────────────────────────

    def lock(self, period: str, actor: str = "system", force: bool = False) -> ClosingLockResult:
        """Sperrt die Periode. Wirft ClosingError bei Doppel-Sperre oder nicht-abschlussreifer Periode."""
        try:
            result = self._period_svc.close_period(period, bediener=actor, force=force)
        except PeriodError as exc:
            raise ClosingError(str(exc)) from exc
        return ClosingLockResult(
            period=period,
            status=result.get("status", "closed"),
            message=f"Periode {period} gesperrt.",
            locked_at=datetime.now(timezone.utc).isoformat(),
        )

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self, period: str, closing_type: str = "monthly", actor: str = "system") -> ClosingRunResult:
        """Periodenabschluss: Salden berechnen, dann die Periode sperren.

        Eine Abschlussbuchung entsteht hier nicht. Der fruehere Weg legte einen Journalkopf ohne Zeilen mit dem
        Status ``closing`` und den Spalten ``closing_type``/``created_by`` an, die es in keiner Datenbank gibt. Der
        INSERT scheiterte immer; das ``except`` verschluckte den Fehler, doch PostgreSQL hatte die Transaktion schon
        abgebrochen, und Sperre und Commit scheiterten danach. Ein Kopf ohne Zeilen bucht ohnehin nichts. Der
        Monatsabschluss ist die Sperre; Saldenvortrag und Jahresabschlussbuchung sind eigene Fachaktionen (M3).
        """
        calc = self.calculate(period, closing_type)
        lock_result = self.lock(period, actor=actor, force=True)
        self.db.commit()

        return ClosingRunResult(
            period=period,
            closing_type=closing_type,
            entry_count=calc.entry_count,
            status=lock_result.status,
            message=f"Abschluss {closing_type} für Periode {period} abgeschlossen. "
                    f"{calc.entry_count} Buchungen, Saldo {calc.balance:+.2f} €.",
        )
