"""Training commands; the existing router supplies the canonical business delegates."""
from typing import Any, Callable
from fastapi import HTTPException, Request
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services.mask_action_runtime_service import MaskActionResult, parse_action_body


def action_onboarding_speichern(request: Request, body: dict[str, Any], db: Session, tenant_id: str, *, insert_onboarding_run: Callable, _require_tenant_row: Callable) -> MaskActionResult:
    """CE fuer personal/onboarding:speichern — dryRun ohne INSERT; Token-Mandant."""
    del request
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="speichern",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    preview = {
        "employee_ref": data.get("employee_ref"),
        "checklist_id": data.get("checklist_id"),
        "assigned_by": data.get("assigned_by"),
        "due_date": data.get("due_date"),
        "tenant_id": tenant_id,
    }
    if mode != "execute":
        try:
            if data.get("checklist_id"):
                _require_tenant_row(
                    db,
                    "SELECT id FROM domain_hr.onboarding_checklists WHERE tenant_id=:tenant_id AND id=:id",
                    {"tenant_id": tenant_id, "id": data["checklist_id"]},
                    not_found_detail="Checklist not found",
                )
        except HTTPException:
            db.rollback()
            return MaskActionResult(
                actionKey="speichern",
                mode=mode,
                success=False,
                error="Checklist nicht im Authentifizierungs-Mandanten.",
                validationErrors=[
                    {"field": "checklist_id", "message": "Nicht im Authentifizierungs-Mandanten", "severity": "blocking"}
                ],
            )
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Onboarding-Lauf wuerde angelegt — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = insert_onboarding_run(db, tenant_id, dict(data))
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="hr_onboarding_run",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Onboarding-Lauf {created.get('employee_ref')} erfasst",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="personal.onboarding.created",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=detail)
    except Exception:  # noqa: BLE001
        db.rollback()
        return MaskActionResult(
            actionKey="speichern", mode=mode, success=False, error="Onboarding-Lauf konnte nicht gespeichert werden."
        )
    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Onboarding-Lauf {created.get('employee_ref')} angelegt.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


def action_qualification_speichern(request: Request, body: dict[str, Any], db: Session, tenant_id: str, *, insert_qualification: Callable) -> MaskActionResult:
    """CE fuer personal/qualifikationen:speichern — dryRun ohne INSERT; Token-Mandant."""
    del request
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="speichern",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    preview = {
        "employee_ref": data.get("employee_ref"),
        "role_code": data.get("role_code"),
        "qualification_level": data.get("qualification_level", "basic"),
        "tenant_id": tenant_id,
    }
    if mode != "execute":
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Qualifikation wuerde angelegt — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = insert_qualification(db, tenant_id, dict(data))
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="hr_qualification",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Qualifikation {created.get('employee_ref')}/{created.get('role_code')} erfasst",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="personal.qualifikation.created",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=detail)
    except Exception:  # noqa: BLE001
        db.rollback()
        return MaskActionResult(
            actionKey="speichern", mode=mode, success=False, error="Qualifikation konnte nicht gespeichert werden."
        )
    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Qualifikation {created.get('employee_ref')} angelegt.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


def action_assignment_speichern(request: Request, body: dict[str, Any], db: Session, tenant_id: str, *, insert_assignment: Callable, _require_tenant_row: Callable) -> MaskActionResult:
    """CE fuer personal/schulungen:speichern — dryRun ohne INSERT; Token-Mandant."""
    del request
    try:
        mode, audit_reason, idempotency_key, payload = parse_action_body(body)
    except ValueError:
        return MaskActionResult(
            actionKey="speichern",
            mode="invalid",
            success=False,
            error="Unbekannter Aktionsmodus.",
            validationErrors=[
                {"field": "_mode", "message": "Ungueltiger Aktionsmodus", "severity": "blocking"}
            ],
        )
    data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    preview = {
        "employee_ref": data.get("employee_ref"),
        "course_id": data.get("course_id"),
        "assigned_by": data.get("assigned_by"),
        "due_date": data.get("due_date"),
        "tenant_id": tenant_id,
    }
    if mode != "execute":
        try:
            if data.get("course_id"):
                _require_tenant_row(
                    db,
                    "SELECT id FROM domain_hr.training_courses WHERE tenant_id=:tenant_id AND id=:id",
                    {"tenant_id": tenant_id, "id": data["course_id"]},
                    not_found_detail="Course not found",
                )
        except HTTPException:
            db.rollback()
            return MaskActionResult(
                actionKey="speichern",
                mode=mode,
                success=False,
                error="Kurs nicht im Authentifizierungs-Mandanten.",
                validationErrors=[
                    {"field": "course_id", "message": "Nicht im Authentifizierungs-Mandanten", "severity": "blocking"}
                ],
            )
        db.rollback()
        return MaskActionResult(
            actionKey="speichern",
            mode=mode,
            success=True,
            summary="Schulungszuweisung wuerde angelegt — keine Aenderung geschrieben.",
            proposedChanges=[preview],
        )
    try:
        from app.services.mask_action_runtime_service import _write_audit, _write_outbox

        created = insert_assignment(db, tenant_id, dict(data))
        entity_id = str(created["id"])
        audit_id = _write_audit(
            db,
            tenant_id=tenant_id,
            action_key="speichern",
            entity_type="hr_training_assignment",
            entity_id=entity_id,
            audit_reason=audit_reason,
            idempotency_key=idempotency_key,
            summary=f"Schulung {created.get('employee_ref')} erfasst",
        )
        outbox_id = _write_outbox(
            db,
            tenant_id=tenant_id,
            event_type="personal.schulung.created",
            aggregate_id=entity_id,
            payload={"id": entity_id, "tenant_id": tenant_id},
        )
        db.commit()
    except HTTPException as exc:
        db.rollback()
        detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return MaskActionResult(actionKey="speichern", mode=mode, success=False, error=detail)
    except Exception:  # noqa: BLE001
        db.rollback()
        return MaskActionResult(
            actionKey="speichern", mode=mode, success=False, error="Schulung konnte nicht gespeichert werden."
        )
    return MaskActionResult(
        actionKey="speichern",
        mode=mode,
        success=True,
        summary=f"Schulung {created.get('employee_ref')} angelegt.",
        affectedIds=[entity_id],
        auditEntryId=audit_id,
        outboxEventId=outbox_id,
        proposedChanges=[preview],
    )


