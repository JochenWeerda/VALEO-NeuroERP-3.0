"""
Sanctions Compliance API — Verbotsliste / Sanktionsprüfung
Agrar-Spezialsoftware Feature: EU/UN/US/HM_TREASURY sanctions list management.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Literal, Optional
from uuid import uuid4

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.api.v1.schemas.base import IDResponse
from app.api.v1.schemas.sanctions_compliance_schemas import SanctionsComplianceOut
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/compliance/sanctions", tags=["Compliance", "Sanctions"])

MIGRATION_HINT = (
    "Tabelle domain_compliance.sanctions_list fehlt — "
    "bitte Alembic-Migration ausführen: alembic upgrade head"
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class SanktionsEintragCreate(BaseModel):
    name: str
    alias_namen: list[str] = Field(default_factory=list)
    land_code: str = Field(
        ..., min_length=2, max_length=2, description="ISO 3166-1 alpha-2"
    )
    liste: str = Field(..., description="EU | UN | OFAC | HM_TREASURY")
    eintragstyp: str = Field(
        ..., description="PERSON | ORGANISATION | SCHIFF | ANDERES"
    )
    eintrags_nr: str
    is_active: bool = True


class SanktionsPruefungInput(BaseModel):
    name: str
    land_code: Optional[str] = None
    adresse: Optional[str] = None
    scope: Literal["manual", "personal", "customers"] = "manual"
    entity_ref: Optional[str] = Field(default=None, max_length=120)


class SanktionsTreffer(BaseModel):
    name: str
    liste: str
    eintrags_nr: str
    aehnlichkeit: float


class SanktionsPruefungResult(BaseModel):
    geprueft_am: str
    treffer: list[SanktionsTreffer]
    status: str  # KEIN_TREFFER | VERDAECHTIG | TREFFER
    empfehlung: str
    scope: Literal["manual", "personal", "customers"]
    entity_ref: Optional[str] = None


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _row_to_dict(row: Any) -> dict:
    return dict(row._mapping)


def _fuzzy_match(input_name: str, eintraege: list[dict]) -> list[SanktionsTreffer]:
    """Simple case-insensitive match + alias check + 5-char prefix partial match."""
    input_lower = input_name.lower().strip()
    input_prefix = input_lower[:5]
    treffer: list[SanktionsTreffer] = []

    for e in eintraege:
        candidate = e.get("name", "")
        aliases: list[str] = e.get("alias_namen") or []
        if isinstance(aliases, str):
            # stored as comma-separated string fallback
            aliases = [a.strip() for a in aliases.split(",") if a.strip()]

        all_names = [candidate] + aliases

        for n in all_names:
            n_lower = n.lower().strip()
            if input_lower == n_lower:
                aehnlichkeit = 1.0
            elif input_lower in n_lower or n_lower in input_lower:
                aehnlichkeit = 0.8
            elif input_prefix and n_lower[:5] == input_prefix:
                aehnlichkeit = 0.5
            else:
                continue

            treffer.append(
                SanktionsTreffer(
                    name=candidate,
                    liste=e.get("liste", ""),
                    eintrags_nr=e.get("eintrags_nr", ""),
                    aehnlichkeit=aehnlichkeit,
                )
            )
            break  # one hit per entry is enough

    return treffer


def _status_from_treffer(treffer: list[SanktionsTreffer]) -> str:
    if not treffer:
        return "KEIN_TREFFER"
    max_sim = max(t.aehnlichkeit for t in treffer)
    if max_sim >= 1.0:
        return "TREFFER"
    return "VERDAECHTIG"


_EMPFEHLUNGEN = {
    "TREFFER": (
        "Geschäftsbeziehung NICHT eingehen — Sanktionstreffer vorhanden. "
        "Compliance-Beauftragten informieren."
    ),
    "VERDAECHTIG": (
        "Verdächtiger Treffer — manuelle Prüfung durch Compliance-Beauftragten erforderlich."
    ),
    "KEIN_TREFFER": (
        "Kein Sanktionstreffer — Freigabe unter Vorbehalt periodischer Neuprüfung."
    ),
}


def load_active_sanctions_list(db: Session) -> list[dict]:
    """Fail-closed: fehlende Liste ist kein KEIN_TREFFER."""
    try:
        rows = db.execute(
            text(
                "SELECT name, alias_namen, liste, eintrags_nr "
                "FROM domain_compliance.sanctions_list "
                "WHERE is_active = TRUE"
            )
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.error("sanctions_list not accessible during pruefen: %s", exc)
        raise HTTPException(
            status_code=503,
            detail=(
                "Sanktionspruefung nicht moeglich: Sanktionsliste ist nicht "
                f"verfuegbar. Keine Freigabe erteilt. {MIGRATION_HINT}"
            ),
        ) from exc


def match_sanctions_name(db: Session, name: str) -> tuple[list[SanktionsTreffer], str, str]:
    """Nur Lesen: Treffer + Status + Empfehlung ohne Protokollzeile."""
    treffer = _fuzzy_match(name, load_active_sanctions_list(db))
    status = _status_from_treffer(treffer)
    return treffer, status, _EMPFEHLUNGEN[status]


def persist_sanctions_check(
    db: Session,
    *,
    tenant_id: str,
    name: str,
    status: str,
    scope: str,
    entity_ref: str | None,
    checked_by: str,
    commit: bool = True,
) -> str:
    """Schreibt mandantengebundenes Pruefprotokoll; liefert check-id."""
    check_id = str(uuid4())
    db.execute(
        text(
            "INSERT INTO domain_compliance.sanctions_checks "
            "(id, tenant_id, geprueft_name, status, scope, entity_ref, checked_by, geprueft_am) "
            "VALUES (:id, :tenant_id, :name, :status, :scope, :entity_ref, :checked_by, NOW())"
        ),
        {
            "id": check_id,
            "tenant_id": tenant_id,
            "name": name,
            "status": status,
            "scope": scope,
            "entity_ref": entity_ref,
            "checked_by": checked_by,
        },
    )
    if commit:
        db.commit()
    return check_id


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.get(
    "/eintraege",
    summary="Sanktionsliste abfragen",
    response_model=list[SanctionsComplianceOut],
)
def list_eintraege(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        rows = db.execute(
            text(
                "SELECT id, name, alias_namen, land_code, liste, eintragstyp, "
                "eintrags_nr, is_active, created_at "
                "FROM domain_compliance.sanctions_list "
                "WHERE is_active = TRUE "
                "ORDER BY name"
            )
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.warning("sanctions_list table not accessible: %s", exc)
        return []


@router.post(
    "/eintraege",
    status_code=201,
    summary="Sanktionseintrag anlegen",
    response_model=IDResponse,
)
def create_eintrag(
    payload: SanktionsEintragCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict:
    entry_id = str(uuid4())
    aliases_str = ",".join(payload.alias_namen)
    try:
        db.execute(
            text(
                "INSERT INTO domain_compliance.sanctions_list "
                "(id, name, alias_namen, land_code, liste, eintragstyp, eintrags_nr, is_active, created_at) "
                "VALUES (:id, :name, :alias_namen, :land_code, :liste, :eintragstyp, :eintrags_nr, :is_active, NOW())"
            ),
            {
                "id": entry_id,
                "name": payload.name,
                "alias_namen": aliases_str,
                "land_code": payload.land_code,
                "liste": payload.liste,
                "eintragstyp": payload.eintragstyp,
                "eintrags_nr": payload.eintrags_nr,
                "is_active": payload.is_active,
            },
        )
        db.commit()
        return {
            "id": entry_id,
            "eintrags_nr": payload.eintrags_nr,
            "status": "angelegt",
        }
    except Exception as exc:
        db.rollback()
        logger.error("Fehler beim Anlegen des Sanktionseintrags: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={"error": str(exc), "migration_hint": MIGRATION_HINT},
        )


@router.post(
    "/pruefen",
    summary="Name gegen Sanktionsliste prüfen",
    response_model=SanktionsPruefungResult,
)
def pruefen(
    payload: SanktionsPruefungInput,
    request: Request,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> SanktionsPruefungResult:
    geprueft_am = datetime.now(timezone.utc).isoformat()
    treffer, status, empfehlung = match_sanctions_name(db, payload.name)

    # Log check to protocol table (best-effort — Legacy-REST bleibt kompatibel)
    try:
        persist_sanctions_check(
            db,
            tenant_id=tenant_id,
            name=payload.name,
            status=status,
            scope=payload.scope,
            entity_ref=payload.entity_ref,
            checked_by=request.headers.get("X-User-ID") or "sanctions-operator",
            commit=True,
        )
    except Exception:
        db.rollback()

    return SanktionsPruefungResult(
        geprueft_am=geprueft_am,
        treffer=treffer,
        status=status,
        empfehlung=empfehlung,
        scope=payload.scope,
        entity_ref=payload.entity_ref,
    )


@router.post(
    "/actions/pruefen/{scope}",
    response_model=MaskActionResult,
    summary="Sanktionspruefung als Masken-CommandEndpoint (validate/dryRun/propose/execute)",
)
def action_pruefen(
    scope: Literal["manual", "personal", "customers"],
    request: Request,
    body: dict[str, Any] = Body(default_factory=dict),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> MaskActionResult:
    """Kanonischer CE fuer auswertungen/sanktionspruefung-*:check.

    Scope kommt aus dem Pfad (Maskenvertrag), nicht aus Client-Ueberschreibung.
    dryRun/validate/propose: Treffer berechnen, kein Protokoll-INSERT.
    execute: Treffer + mandantengebundenes Protokoll (kein Auto-Freigeben).
    """
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="check",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )

    name = str(payload.get("name") or "").strip()
    # Pfad-Scope ist kanonisch; abweichender Body-Scope wird abgelehnt (kein Silent-Override).
    body_scope = payload.get("scope")
    if body_scope is not None and str(body_scope).strip() and str(body_scope).strip() != scope:
        return MaskActionResult(
            actionKey="check",
            mode=mode,
            success=False,
            error="Scope im Body widerspricht dem Masken-CommandEndpoint.",
            validationErrors=[
                {"field": "scope", "message": f"Erwartet {scope}", "severity": "blocking"}
            ],
        )
    scope_raw = scope
    entity_ref = payload.get("entity_ref")
    entity_ref_s = str(entity_ref).strip() if entity_ref is not None else None
    if entity_ref_s == "":
        entity_ref_s = None

    if not name:
        return MaskActionResult(
            actionKey="check",
            mode=mode,
            success=False,
            error="Name ist erforderlich.",
            validationErrors=[
                {"field": "name", "message": "Pflichtfeld", "severity": "blocking"}
            ],
        )

    try:
        treffer, status, empfehlung = match_sanctions_name(db, name)
    except HTTPException as exc:
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        db.rollback()
        return MaskActionResult(
            actionKey="check",
            mode=mode,
            success=False,
            error=detail,
            validationErrors=[
                {"field": "_entity", "message": detail, "severity": "blocking"}
            ],
        )

    preview = {
        "name": name,
        "scope": scope_raw,
        "entity_ref": entity_ref_s,
        "status": status,
        "empfehlung": empfehlung,
        "treffer": [t.model_dump() for t in treffer],
    }
    db.rollback()

    if mode != "execute":
        return MaskActionResult(
            actionKey="check",
            mode=mode,
            success=True,
            summary=f"Pruefung ohne Speichern: {status}.",
            proposedChanges=[preview],
        )

    checked_by = request.headers.get("X-User-ID") or "sanctions-operator"
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        check_id = persist_sanctions_check(
            db,
            tenant_id=tenant_id,
            name=name,
            status=status,
            scope=scope_raw,
            entity_ref=entity_ref_s,
            checked_by=checked_by,
            commit=False,
        )
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="check",
            entity_type="sanctions_check",
            entity_id=check_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Sanktionspruefung {scope_raw}: {status} fuer {name}",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="compliance.sanctions.checked",
            aggregate_id=check_id,
            payload={
                "check_id": check_id,
                "status": status,
                "scope": scope_raw,
                "name": name,
                "tenant_id": tenant_id,
            },
        )
        db.commit()
    except Exception as exc:  # noqa: BLE001 — Maskenantwort, kein 500
        db.rollback()
        logger.warning("Sanctions action execute failed: %s", exc)
        return MaskActionResult(
            actionKey="check",
            mode=mode,
            success=False,
            error="Sanktionspruefung konnte nicht protokolliert werden.",
        )

    return MaskActionResult(
        actionKey="check",
        mode=mode,
        success=True,
        summary=f"Pruefung protokolliert: {status}.",
        proposedChanges=[preview],
        affectedIds=[check_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
    )


@router.get(
    "/pruefprotokoll",
    summary="Sanktionsprüf-Protokoll abrufen",
    response_model=list[SanctionsComplianceOut],
)
def pruefprotokoll(
    scope: Literal["manual", "personal", "customers"] | None = Query(default=None),
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict]:
    try:
        where_scope = " AND scope = :scope" if scope else ""
        rows = db.execute(
            text(
                "SELECT id, geprueft_name, status, scope, entity_ref, checked_by, geprueft_am "
                "FROM domain_compliance.sanctions_checks "
                "WHERE tenant_id = :tenant_id"
                f"{where_scope} "  # nosec B608  # fixed allow-listed clause
                "ORDER BY geprueft_am DESC LIMIT 500"
            ),
            {"tenant_id": tenant_id, "scope": scope},
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    except Exception as exc:
        logger.warning("sanctions_checks table not accessible: %s", exc)
        return []
