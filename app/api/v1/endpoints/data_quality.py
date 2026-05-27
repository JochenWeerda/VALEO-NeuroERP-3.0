"""
Datenqualitäts-API (Gap 040): Validierung von Dubletten, Pflichtfeldern und Referenzen.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.data_quality_rules import (
    DUPLICATE_RULES,
    REQUIRED_FIELD_RULES,
    REFERENCE_RULES,
    get_all_entity_types,
    get_dq_catalog,
    get_dq_ruleset_for_entity,
    get_dq_ruleset_summary,
    DuplicateRule,
    RequiredFieldRule,
    ReferenceRule,
)

router = APIRouter(prefix="/data-quality", tags=["admin", "data-quality"])


class RuleOut(BaseModel):
    id: str
    entity_type: str
    label: str
    rule_type: str


class ViolationOut(BaseModel):
    rule_id: str
    entity_type: str
    entity_id: str | None
    detail: str
    severity: str = "error"


class ValidationResultOut(BaseModel):
    entity_type: str
    violations: list[ViolationOut]
    total_count: int


@router.get("/rules", response_model=list[RuleOut], summary="Data quality rules auflisten")
async def list_data_quality_rules(
    entity_type: str | None = Query(None, description="Filter nach Entity-Typ"),
):
    """Liste aller definierten Datenqualitätsregeln."""
    rules: list[RuleOut] = []
    for r in DUPLICATE_RULES:
        if entity_type and r.entity_type != entity_type:
            continue
        rules.append(
            RuleOut(id=r.id, entity_type=r.entity_type, label=r.label, rule_type="duplicate")
        )
    for r in REQUIRED_FIELD_RULES:
        if entity_type and r.entity_type != entity_type:
            continue
        rules.append(
            RuleOut(id=r.id, entity_type=r.entity_type, label=r.label, rule_type="required")
        )
    for r in REFERENCE_RULES:
        if entity_type and r.entity_type != entity_type:
            continue
        rules.append(
            RuleOut(id=r.id, entity_type=r.entity_type, label=r.label, rule_type="reference")
        )
    return rules


@router.get("/catalog", response_model=dict, summary="Data quality catalog abrufen")
async def get_data_quality_catalog(
    entity_type: str | None = Query(None, description="Optionaler Filter nach Entity-Typ"),
):
    """Katalogsicht ueber alle produktiven DQ-Regelsets."""
    return get_dq_catalog(entity_typ=entity_type).as_dict()


@router.get("/entity-types", response_model=list[str], summary="Entity types auflisten")
async def list_entity_types():
    """Liste aller Entity-Typen mit definierten Regeln."""
    return get_all_entity_types()


@router.get("/rulesets/{entity_type}", response_model=dict, summary="Data quality ruleset abrufen")
async def get_data_quality_ruleset(entity_type: str):
    """Gibt das vollstaendige DQ-Regelset fuer einen Entity-Typ zurueck."""
    ruleset = get_dq_ruleset_for_entity(entity_type)
    if ruleset is None:
        raise HTTPException(status_code=404, detail=f"Kein Regelset fuer entity_typ '{entity_type}' gefunden")
    return ruleset.as_dict()


@router.get("/rulesets/{entity_type}/summary", response_model=dict, summary="Data quality ruleset summary abrufen")
async def get_data_quality_ruleset_summary(entity_type: str):
    """Verdichtete Sicht auf ein einzelnes DQ-Regelset."""
    ruleset = get_dq_ruleset_for_entity(entity_type)
    if ruleset is None:
        raise HTTPException(status_code=404, detail=f"Kein Regelset fuer entity_typ '{entity_type}' gefunden")
    return get_dq_ruleset_summary(ruleset).as_dict()


def _run_duplicate_check(db: Session, rule: DuplicateRule, tenant_id: str) -> list[ViolationOut]:
    violations: list[ViolationOut] = []
    cols = ", ".join(rule.unique_columns)
    full_table = f'"{rule.schema}"."{rule.table}"'
    q = text(
        f"""
        SELECT {cols}, COUNT(*) as cnt, array_agg({rule.id_column}) as ids
        FROM {full_table}
        WHERE tenant_id = :tenant_id OR (:tenant_id = 'system' AND tenant_id IS NULL)
        GROUP BY {cols}
        HAVING COUNT(*) > 1
        """
    )
    try:
        rows = db.execute(q, {"tenant_id": tenant_id}).fetchall()
        for row in rows:
            vals = [str(row[i]) for i in range(len(rule.unique_columns))]
            key_str = " / ".join(f"{c}={v}" for c, v in zip(rule.unique_columns, vals))
            ids = row[-1] if hasattr(row[-1], "__iter__") and not isinstance(row[-1], str) else [row[-1]]
            for eid in (ids or [])[:5]:  # max 5 IDs pro Dublette
                violations.append(
                    ViolationOut(
                        rule_id=rule.id,
                        entity_type=rule.entity_type,
                        entity_id=str(eid),
                        detail=f"Dublette: {key_str} (insg. {row[-2]} Einträge)",
                        severity="error",
                    )
                )
            if len(ids or []) > 5:
                violations.append(
                    ViolationOut(
                        rule_id=rule.id,
                        entity_type=rule.entity_type,
                        entity_id=None,
                        detail=f"… und {len(ids) - 5} weitere Dubletten für {key_str}",
                        severity="error",
                    )
                )
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass  # Tabelle/Schema fehlt evtl.
    return violations


def _run_required_check(db: Session, rule: RequiredFieldRule, tenant_id: str) -> list[ViolationOut]:
    violations: list[ViolationOut] = []
    full_table = f'"{rule.schema}"."{rule.table}"'
    cond = f'"{rule.field}" IS NULL'
    if rule.check_empty_string:
        cond += f' OR TRIM(COALESCE("{rule.field}"::text, \'\')) = \'\''
    q = text(
        f"""
        SELECT id
        FROM {full_table}
        WHERE (tenant_id = :tenant_id OR (:tenant_id = 'system' AND tenant_id IS NULL))
          AND ({cond})
        LIMIT 100
        """
    )
    try:
        rows = db.execute(q, {"tenant_id": tenant_id}).fetchall()
        for row in rows:
            violations.append(
                ViolationOut(
                    rule_id=rule.id,
                    entity_type=rule.entity_type,
                    entity_id=str(row[0]),
                    detail=f"Pflichtfeld '{rule.field}' fehlt oder ist leer",
                    severity="error",
                )
            )
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass
    return violations


def _run_reference_check(db: Session, rule: ReferenceRule, tenant_id: str) -> list[ViolationOut]:
    violations: list[ViolationOut] = []
    src = f'"{rule.schema}"."{rule.table}"'
    tgt = f'"{rule.target_schema}"."{rule.target_table}"'
    q = text(
        f"""
        SELECT s.id
        FROM {src} s
        LEFT JOIN {tgt} t ON s."{rule.fk_column}" = t."{rule.target_pk}"
        WHERE s."{rule.fk_column}" IS NOT NULL
          AND t."{rule.target_pk}" IS NULL
          AND (s.tenant_id = :tenant_id OR (:tenant_id = 'system' AND s.tenant_id IS NULL))
        LIMIT 100
        """
    )
    try:
        rows = db.execute(q, {"tenant_id": tenant_id}).fetchall()
        for row in rows:
            violations.append(
                ViolationOut(
                    rule_id=rule.id,
                    entity_type=rule.entity_type,
                    entity_id=str(row[0]),
                    detail=f"Ungültige Referenz: {rule.fk_column} verweist auf nicht existierenden Datensatz",
                    severity="error",
                )
            )
    except Exception:  # noqa: BLE001 — optionale DB-Abfrage; Fallback greift
        pass
    return violations


class ValidateRequest(BaseModel):
    entity_types: list[str] | None = Field(default=None, description="Entity-Typen zu prüfen; leer = alle")


@router.post("/validate", response_model=list[ValidationResultOut], summary="Data quality validieren")
async def validate_data_quality(
    body: ValidateRequest | None = None,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """
    Führt Datenqualitätsprüfungen für die angegebenen Entity-Typen durch.
    Ohne entity_types werden alle Typen geprüft.
    """
    types_to_check = (body.entity_types if body else None) or get_all_entity_types()
    results: list[ValidationResultOut] = []

    for et in types_to_check:
        violations: list[ViolationOut] = []
        for r in DUPLICATE_RULES:
            if r.entity_type == et:
                violations.extend(_run_duplicate_check(db, r, tenant_id))
        for r in REQUIRED_FIELD_RULES:
            if r.entity_type == et:
                violations.extend(_run_required_check(db, r, tenant_id))
        for r in REFERENCE_RULES:
            if r.entity_type == et:
                violations.extend(_run_reference_check(db, r, tenant_id))

        results.append(
            ValidationResultOut(
                entity_type=et,
                violations=violations,
                total_count=len(violations),
            )
        )

    return results
