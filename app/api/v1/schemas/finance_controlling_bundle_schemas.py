"""Response-Schemas fuer Finance/Controlling (SPEC-P1-06 Welle 12).

Ersetzt schwache ``response_model`` in:
- ``controlling_actions.py``
- ``finance_period.py``
- ``bank_import.py``
"""

from __future__ import annotations

from typing import Any, Optional

from pydantic import ConfigDict, Field

from app.api.v1.schemas.base import BaseSchema


# ── Controlling ─────────────────────────────────────────────────────────────


class ControllingBudgetCreatedOut(BaseSchema):
    id: Optional[str] = None
    kostenstelle_id: Optional[str] = None
    periode: Optional[str] = None
    plan_eur: Optional[float] = None
    bezeichnung: Optional[str] = None
    status: Optional[str] = None


class ControllingBudgetTransitionOut(BaseSchema):
    """Kann Idempotenz- oder Statuswechsel-Felder aus dem DB-Row tragen."""

    model_config = ConfigDict(from_attributes=True, extra="allow")

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    kostenstelle_id: Optional[str] = None
    periode: Optional[str] = None
    plan_eur: Optional[float] = None
    bezeichnung: Optional[str] = None
    status: Optional[str] = None
    previous_status: Optional[str] = None
    idempotent: Optional[bool] = None
    freigabe_operator: Optional[str] = None


class ControllingAbweichungOut(BaseSchema):
    kostenstelle_id: Optional[str] = None
    periode: Optional[str] = None
    plan_eur: Optional[float] = None
    ist_eur: Optional[float] = None
    abweichung_eur: Optional[float] = None
    abweichung_pct: Optional[float] = None
    ampel: Optional[str] = None


class ControllingIstWertOut(BaseSchema):
    id: Optional[str] = None
    kostenstelle_id: Optional[str] = None
    periode: Optional[str] = None
    ist_eur: Optional[float] = None
    buchungsref: Optional[str] = None


class ControllingKstAbschlussOut(BaseSchema):
    model_config = ConfigDict(from_attributes=True, extra="allow")

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    kostenstelle_id: Optional[str] = None
    periode: Optional[str] = None
    status: Optional[str] = None
    operator: Optional[str] = None
    previous_status: Optional[str] = None
    idempotent: Optional[bool] = None
    abgeschlossen_am: Optional[Any] = None
    created_at: Optional[Any] = None


# ── Periodenabschluss ───────────────────────────────────────────────────────


class FinancePeriodItemOut(BaseSchema):
    period: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    status: Optional[str] = None
    closed_at: Optional[str] = None
    closed_by: Optional[str] = None
    offen_count: Optional[int] = None
    storno_inkonsistent: Optional[int] = None
    abschlussreif: Optional[bool] = None


class FinancePeriodListOut(BaseSchema):
    items: list[FinancePeriodItemOut] = Field(default_factory=list)


class FinancePeriodReadinessOut(BaseSchema):
    period: Optional[str] = None
    offen_count: Optional[int] = None
    storno_inkonsistent: Optional[int] = None
    ready: Optional[bool] = None
    blocker: list[str] = Field(default_factory=list)


class FinancePeriodActionOut(BaseSchema):
    ok: Optional[bool] = None
    period: Optional[str] = None
    status: Optional[str] = None
    erzwungen: Optional[bool] = None


# ── Bank-Import ─────────────────────────────────────────────────────────────


class BankStatementImportOut(BaseSchema):
    statement_id: Optional[str] = None
    lines: Optional[int] = None
    iban: Optional[str] = None
    format: Optional[str] = None


class BankMatchOut(BaseSchema):
    statement_id: Optional[str] = None
    matched: Optional[int] = None
    unmatched: Optional[int] = None
    info: Optional[str] = None


class BankStatementItemOut(BaseSchema):
    id: Optional[str] = None
    iban: Optional[str] = None
    format: Optional[str] = None
    filename: Optional[str] = None
    line_count: Optional[int] = None
    imported_at: Optional[str] = None


class BankStatementListOut(BaseSchema):
    items: list[BankStatementItemOut] = Field(default_factory=list)
    count: Optional[int] = None
