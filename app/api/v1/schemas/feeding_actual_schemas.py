"""Response-Schemas fuer die Ist-Fuetterung und ihre Abweichungssteuerung.

SPEC-P1-06 Welle 3: ersetzt ``response_model=dict[str, Any]`` bzw.
``list[dict[str, Any]]`` in ``app/api/v1/endpoints/feeding_actual.py``.

Feldlisten aus den Tabellen ``domain_agrar.feeding_actual_records``,
``feeding_actual_components``, ``feeding_deviation_policies``,
``feeding_actual_measures`` und ``feeding_measure_versions`` sowie den
Aufbereitungen in ``feeding_actual_service`` und
``feeding_actual_measure_service``.

Ist-Datensaetze und Komponenten sind per Trigger append-only; die Schemas
bilden sie daher unveraendert ab.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Optional

from pydantic import Field

from app.api.v1.schemas.base import BaseSchema


class ActualComponentOut(BaseSchema):
    """Zeile aus ``domain_agrar.feeding_actual_components``."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    actual_record_id: Optional[str] = None
    instruction_id: Optional[str] = None
    feed_id: Optional[str] = None
    feed_name: Optional[str] = None
    target_kg: Optional[float] = None
    actual_kg: Optional[float] = None
    delta_kg: Optional[float] = None
    delta_pct: Optional[float] = None
    value_consequences: Optional[Any] = Field(
        default=None, description="Kosten-/Naehrstofffolgen der Abweichung (JSONB)"
    )


class ActualRecordOut(BaseSchema):
    """Ist-Fuetterung mit Gruppenkontext und Komponenten.

    ``feeding_actual_records.*`` plus ``group_name`` und ``plan_version_no``
    aus dem Join.
    """

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    plan_version_id: Optional[str] = None
    group_id: Optional[str] = None
    feeding_at: Optional[datetime] = None
    source: Optional[str] = Field(default=None, description="manual | mixing_wagon | import")
    source_ref: Optional[str] = None
    cause_class: Optional[str] = Field(
        default=None,
        description=(
            "normal | stock_substitution | dosing_error | feed_quality | "
            "animal_intake | technical | other"
        ),
    )
    comment: Optional[str] = None
    context: Optional[Any] = Field(default=None, description="Freier Kontext (JSONB)")
    supersedes_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    request_hash: Optional[str] = None
    recorded_by: Optional[str] = None
    recorded_at: Optional[datetime] = None
    group_name: Optional[str] = None
    plan_version_no: Optional[int] = None
    components: list[ActualComponentOut] = Field(default_factory=list)


class ActualComponentRowOut(BaseSchema):
    """``GET /components`` — flache Komponentensicht ueber alle Ist-Datensaetze.

    Bewusst eigene, aufbereitete Form: Kosten- und Naehrstofffolgen sind hier
    zu Textzusammenfassungen verdichtet.
    """

    id: Optional[str] = None
    actual_record_id: Optional[str] = None
    plan_version_id: Optional[str] = None
    plan_version_no: Optional[int] = None
    group_id: Optional[str] = None
    group_name: Optional[str] = None
    feeding_at: Optional[datetime] = None
    cause_class: Optional[str] = None
    comment: Optional[str] = None
    source: Optional[str] = None
    feed_id: Optional[str] = None
    feed_name: Optional[str] = None
    target_kg: Optional[float] = None
    actual_kg: Optional[float] = None
    delta_kg: Optional[float] = None
    delta_pct: Optional[float] = None
    cost_delta_eur: Optional[float] = None
    nutrient_delta_summary: Optional[str] = None
    missing_value_summary: Optional[str] = None


class DeviationPolicyOut(BaseSchema):
    """Zeile aus ``domain_agrar.feeding_deviation_policies`` (append-only)."""

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    feed_class: Optional[str] = None
    version: Optional[int] = None
    warning_pct: Optional[float] = None
    critical_pct: Optional[float] = None
    valid_from: Optional[date] = None
    reason: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None


class DeviationFindingOut(BaseSchema):
    """``GET /findings`` — bewertete Abweichung je Komponente.

    Ohne passende Schwellenkonfiguration liefert der Service
    ``severity="unconfigured"`` und nur den Identitaetsteil; sonst kommen die
    Kennzahlen aus ``evaluate_deviation`` dazu.
    """

    actual_component_id: Optional[str] = None
    actual_record_id: Optional[str] = None
    plan_version_id: Optional[str] = None
    group_id: Optional[str] = None
    feed_id: Optional[str] = None
    feed_name: Optional[str] = None
    policy_id: Optional[str] = None
    severity: Optional[str] = Field(
        default=None, description="unconfigured | warning | critical"
    )
    message: Optional[str] = None
    feed_class: Optional[str] = None
    policy_version: Optional[int] = None
    target_kg: Optional[float] = None
    actual_kg: Optional[float] = None
    delta_kg: Optional[float] = None
    delta_pct: Optional[float] = None
    threshold_pct: Optional[float] = None
    remedy: Optional[str] = None


class ActualMeasureOut(BaseSchema):
    """Massnahme zu einer Abweichung.

    ``feeding_actual_measures.*``; ``list_measures`` ergaenzt die Felder der
    jeweils juengsten Zeile aus ``feeding_measure_versions``.
    """

    id: Optional[str] = None
    tenant_id: Optional[str] = None
    actual_record_id: Optional[str] = None
    actual_component_id: Optional[str] = None
    group_id: Optional[str] = None
    finding: Optional[Any] = Field(default=None, description="Ausloesender Befund (JSONB)")
    title: Optional[str] = None
    owner_subject: Optional[str] = None
    due_date: Optional[date] = None
    version: Optional[int] = None
    status: Optional[str] = Field(
        default=None,
        description="open | in_progress | review_due | completed | cancelled",
    )
    reason: Optional[str] = None
    idempotency_key: Optional[str] = None
    request_hash: Optional[str] = None
    created_by: Optional[str] = None
    created_at: Optional[datetime] = None
    reminder_date: Optional[date] = None
    escalation_status: Optional[str] = Field(
        default=None, description="none | attention | escalated"
    )
    effectiveness: Optional[str] = Field(
        default=None, description="effective | partial | ineffective"
    )
    effectiveness_result: Optional[str] = None
    changed_by: Optional[str] = None
    changed_at: Optional[datetime] = None
