"""Training, qualification and onboarding CRUD endpoints."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import Response, APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.knowledge_core_contracts import KnowledgeChannel
from app.core.onboarding_workspaces import build_onboarding_workspace
from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/training", tags=["training", "hr"])


class Payload(BaseModel):
    data: dict[str, Any] = Field(default_factory=dict)


class OnboardingWorkspaceRequest(BaseModel):
    rolle: str
    employee_ref: str | None = None
    checklist_id: str | None = None
    run_id: str | None = None
    kanal: str = KnowledgeChannel.TEAMS.value
    capability_key: str | None = "onboarding_assistant"
    query: str = ""
    limit: int = 5


def _clean(row: dict[str, Any]) -> dict[str, Any]:
    out = dict(row)
    for k, v in list(out.items()):
        if isinstance(v, UUID):
            out[k] = str(v)
        elif isinstance(v, datetime):
            out[k] = v.isoformat()
    return out


def _list(db: Session, sql: str, params: dict[str, Any]) -> list[dict[str, Any]]:
    return [_clean(dict(r)) for r in db.execute(text(sql), params).mappings().all()]


def _load_optional_row(
    db: Session,
    sql: str,
    params: dict[str, Any],
    *,
    not_found_detail: str,
) -> dict[str, Any] | None:
    row = db.execute(text(sql), params).mappings().first()
    if not row:
        raise HTTPException(status_code=404, detail=not_found_detail)
    return _clean(dict(row))


@router.get("/courses", response_model=list[dict[str, Any]], summary="Courses auflisten")
async def list_courses(
    include_inactive: bool = Query(default=False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = ["tenant_id = :tenant_id"]
    if not include_inactive:
        where.append("is_active = TRUE")
    return _list(
        db,
        f"SELECT * FROM domain_hr.training_courses WHERE {' AND '.join(where)} ORDER BY course_code ASC",
        {"tenant_id": tenant_id},
    )


@router.post("/courses", response_model=dict[str, Any], status_code=201, summary="Course anlegen")
async def create_course(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("course_code", "title"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    item_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_hr.training_courses
                  (id, tenant_id, course_code, title, topic, description, mandatory, validity_months, provider, delivery_mode, metadata, is_active, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :course_code, :title, :topic, :description, :mandatory, :validity_months, :provider, :delivery_mode, CAST(:metadata AS jsonb), :is_active, NOW(), NOW())
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "course_code": d["course_code"],
                "title": d["title"],
                "topic": d.get("topic"),
                "description": d.get("description"),
                "mandatory": bool(d.get("mandatory", False)),
                "validity_months": d.get("validity_months"),
                "provider": d.get("provider"),
                "delivery_mode": d.get("delivery_mode", "classroom"),
                "metadata": json.dumps(d.get("metadata", {})),
                "is_active": bool(d.get("is_active", True)),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Course conflict: {exc}") from exc
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.training_courses WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.put("/courses/{item_id}", response_model=dict[str, Any], summary="Course aktualisieren")
async def update_course(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("course_code", "title"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    updated = db.execute(
        text(
            """
            UPDATE domain_hr.training_courses
            SET course_code=:course_code, title=:title, topic=:topic, description=:description, mandatory=:mandatory,
                validity_months=:validity_months, provider=:provider, delivery_mode=:delivery_mode, metadata=CAST(:metadata AS jsonb),
                is_active=:is_active, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "course_code": d["course_code"],
            "title": d["title"],
            "topic": d.get("topic"),
            "description": d.get("description"),
            "mandatory": bool(d.get("mandatory", False)),
            "validity_months": d.get("validity_months"),
            "provider": d.get("provider"),
            "delivery_mode": d.get("delivery_mode", "classroom"),
            "metadata": json.dumps(d.get("metadata", {})),
            "is_active": bool(d.get("is_active", True)),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Course not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.training_courses WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.delete("/courses/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Course löschen")
async def delete_course(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_hr.training_courses WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Course not found")
    db.commit()
    return None


@router.get("/assignments", response_model=list[dict[str, Any]], summary="Assignments auflisten")
async def list_assignments(
    employee_ref: str | None = Query(default=None),
    status: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = ["a.tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if employee_ref:
        where.append("a.employee_ref = :employee_ref")
        params["employee_ref"] = employee_ref
    if status:
        where.append("a.status = :status")
        params["status"] = status
    return _list(
        db,
        f"""
        SELECT a.*, c.course_code, c.title AS course_title
        FROM domain_hr.training_assignments a
        JOIN domain_hr.training_courses c ON c.id = a.course_id AND c.tenant_id = a.tenant_id
        WHERE {' AND '.join(where)}
        ORDER BY a.assigned_at DESC
        """,
        params,
    )


@router.post("/assignments", response_model=dict[str, Any], status_code=201, summary="Assignment anlegen")
async def create_assignment(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("course_id", "employee_ref"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    item_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_hr.training_assignments
                  (id, tenant_id, course_id, employee_ref, assigned_by, assigned_at, due_date, status, score_percent, completed_at, evidence_url, notes, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :course_id, :employee_ref, :assigned_by, COALESCE(:assigned_at, NOW()), :due_date, :status, :score_percent, :completed_at, :evidence_url, :notes, NOW(), NOW())
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "course_id": d["course_id"],
                "employee_ref": d["employee_ref"],
                "assigned_by": d.get("assigned_by"),
                "assigned_at": d.get("assigned_at"),
                "due_date": d.get("due_date"),
                "status": d.get("status", "assigned"),
                "score_percent": d.get("score_percent"),
                "completed_at": d.get("completed_at"),
                "evidence_url": d.get("evidence_url"),
                "notes": d.get("notes"),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Assignment conflict: {exc}") from exc
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.training_assignments WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.put("/assignments/{item_id}", response_model=dict[str, Any], summary="Assignment aktualisieren")
async def update_assignment(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("course_id", "employee_ref"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    updated = db.execute(
        text(
            """
            UPDATE domain_hr.training_assignments
            SET course_id=:course_id, employee_ref=:employee_ref, assigned_by=:assigned_by, due_date=:due_date,
                status=:status, score_percent=:score_percent, completed_at=:completed_at, evidence_url=:evidence_url, notes=:notes, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "course_id": d["course_id"],
            "employee_ref": d["employee_ref"],
            "assigned_by": d.get("assigned_by"),
            "due_date": d.get("due_date"),
            "status": d.get("status", "assigned"),
            "score_percent": d.get("score_percent"),
            "completed_at": d.get("completed_at"),
            "evidence_url": d.get("evidence_url"),
            "notes": d.get("notes"),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.training_assignments WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.delete("/assignments/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Assignment löschen")
async def delete_assignment(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_hr.training_assignments WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.commit()
    return None


@router.get("/certificates", response_model=list[dict[str, Any]], summary="Certificates auflisten")
async def list_certificates(
    employee_ref: str | None = Query(default=None),
    status: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = ["tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if employee_ref:
        where.append("employee_ref = :employee_ref")
        params["employee_ref"] = employee_ref
    if status:
        where.append("status = :status")
        params["status"] = status
    return _list(
        db,
        f"SELECT * FROM domain_hr.employee_certificates WHERE {' AND '.join(where)} ORDER BY valid_until ASC NULLS LAST",
        params,
    )


@router.post("/certificates", response_model=dict[str, Any], status_code=201, summary="Certificate anlegen")
async def create_certificate(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("employee_ref", "certificate_type", "certificate_name"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    item_id = str(uuid4())
    db.execute(
        text(
            """
            INSERT INTO domain_hr.employee_certificates
              (id, tenant_id, employee_ref, certificate_type, certificate_name, certificate_number, issuer, issued_at, valid_until, status, document_url, metadata, created_at, updated_at)
            VALUES
              (:id, :tenant_id, :employee_ref, :certificate_type, :certificate_name, :certificate_number, :issuer, :issued_at, :valid_until, :status, :document_url, CAST(:metadata AS jsonb), NOW(), NOW())
            """
        ),
        {
            "id": item_id,
            "tenant_id": tenant_id,
            "employee_ref": d["employee_ref"],
            "certificate_type": d["certificate_type"],
            "certificate_name": d["certificate_name"],
            "certificate_number": d.get("certificate_number"),
            "issuer": d.get("issuer"),
            "issued_at": d.get("issued_at"),
            "valid_until": d.get("valid_until"),
            "status": d.get("status", "valid"),
            "document_url": d.get("document_url"),
            "metadata": json.dumps(d.get("metadata", {})),
        },
    )
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.employee_certificates WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.put("/certificates/{item_id}", response_model=dict[str, Any], summary="Certificate aktualisieren")
async def update_certificate(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("employee_ref", "certificate_type", "certificate_name"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    updated = db.execute(
        text(
            """
            UPDATE domain_hr.employee_certificates
            SET employee_ref=:employee_ref, certificate_type=:certificate_type, certificate_name=:certificate_name,
                certificate_number=:certificate_number, issuer=:issuer, issued_at=:issued_at, valid_until=:valid_until,
                status=:status, document_url=:document_url, metadata=CAST(:metadata AS jsonb), updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "employee_ref": d["employee_ref"],
            "certificate_type": d["certificate_type"],
            "certificate_name": d["certificate_name"],
            "certificate_number": d.get("certificate_number"),
            "issuer": d.get("issuer"),
            "issued_at": d.get("issued_at"),
            "valid_until": d.get("valid_until"),
            "status": d.get("status", "valid"),
            "document_url": d.get("document_url"),
            "metadata": json.dumps(d.get("metadata", {})),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Certificate not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.employee_certificates WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.delete("/certificates/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Certificate löschen")
async def delete_certificate(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_hr.employee_certificates WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Certificate not found")
    db.commit()
    return None


@router.get("/qualifications", response_model=list[dict[str, Any]], summary="Qualifications auflisten")
async def list_qualifications(
    employee_ref: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = ["tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if employee_ref:
        where.append("employee_ref = :employee_ref")
        params["employee_ref"] = employee_ref
    return _list(
        db,
        f"SELECT * FROM domain_hr.qualification_profiles WHERE {' AND '.join(where)} ORDER BY employee_ref ASC, role_code ASC",
        params,
    )


@router.post("/qualifications", response_model=dict[str, Any], status_code=201, summary="Qualification anlegen")
async def create_qualification(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("employee_ref", "role_code"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    item_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_hr.qualification_profiles
                  (id, tenant_id, employee_ref, role_code, qualification_level, skills, notes, valid_until, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :employee_ref, :role_code, :qualification_level, CAST(:skills AS jsonb), :notes, :valid_until, NOW(), NOW())
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "employee_ref": d["employee_ref"],
                "role_code": d["role_code"],
                "qualification_level": d.get("qualification_level", "basic"),
                "skills": json.dumps(d.get("skills", [])),
                "notes": d.get("notes"),
                "valid_until": d.get("valid_until"),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Qualification conflict: {exc}") from exc
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.qualification_profiles WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.put("/qualifications/{item_id}", response_model=dict[str, Any], summary="Qualification aktualisieren")
async def update_qualification(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("employee_ref", "role_code"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    updated = db.execute(
        text(
            """
            UPDATE domain_hr.qualification_profiles
            SET employee_ref=:employee_ref, role_code=:role_code, qualification_level=:qualification_level,
                skills=CAST(:skills AS jsonb), notes=:notes, valid_until=:valid_until, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "employee_ref": d["employee_ref"],
            "role_code": d["role_code"],
            "qualification_level": d.get("qualification_level", "basic"),
            "skills": json.dumps(d.get("skills", [])),
            "notes": d.get("notes"),
            "valid_until": d.get("valid_until"),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Qualification not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.qualification_profiles WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.delete("/qualifications/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Qualification löschen")
async def delete_qualification(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_hr.qualification_profiles WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Qualification not found")
    db.commit()
    return None


@router.get("/onboarding/checklists", response_model=list[dict[str, Any]], summary="Checklists auflisten")
async def list_checklists(
    include_inactive: bool = Query(default=False),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = ["tenant_id = :tenant_id"]
    if not include_inactive:
        where.append("is_active = TRUE")
    return _list(
        db,
        f"SELECT * FROM domain_hr.onboarding_checklists WHERE {' AND '.join(where)} ORDER BY checklist_code ASC",
        {"tenant_id": tenant_id},
    )


@router.post("/onboarding/checklists", response_model=dict[str, Any], status_code=201, summary="Checklist anlegen")
async def create_checklist(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("checklist_code", "title"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    item_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_hr.onboarding_checklists
                  (id, tenant_id, checklist_code, title, description, role_scope, tasks, is_active, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :checklist_code, :title, :description, :role_scope, CAST(:tasks AS jsonb), :is_active, NOW(), NOW())
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "checklist_code": d["checklist_code"],
                "title": d["title"],
                "description": d.get("description"),
                "role_scope": d.get("role_scope"),
                "tasks": json.dumps(d.get("tasks", [])),
                "is_active": bool(d.get("is_active", True)),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Checklist conflict: {exc}") from exc
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.onboarding_checklists WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.put("/onboarding/checklists/{item_id}", response_model=dict[str, Any], summary="Checklist aktualisieren")
async def update_checklist(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("checklist_code", "title"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    updated = db.execute(
        text(
            """
            UPDATE domain_hr.onboarding_checklists
            SET checklist_code=:checklist_code, title=:title, description=:description, role_scope=:role_scope,
                tasks=CAST(:tasks AS jsonb), is_active=:is_active, updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "checklist_code": d["checklist_code"],
            "title": d["title"],
            "description": d.get("description"),
            "role_scope": d.get("role_scope"),
            "tasks": json.dumps(d.get("tasks", [])),
            "is_active": bool(d.get("is_active", True)),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Checklist not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.onboarding_checklists WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.delete("/onboarding/checklists/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Checklist löschen")
async def delete_checklist(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_hr.onboarding_checklists WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Checklist not found")
    db.commit()
    return None


@router.get("/onboarding/runs", response_model=list[dict[str, Any]], summary="Runs auflisten")
async def list_runs(
    employee_ref: str | None = Query(default=None),
    status: str | None = Query(default=None),
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    where = ["r.tenant_id = :tenant_id"]
    params: dict[str, Any] = {"tenant_id": tenant_id}
    if employee_ref:
        where.append("r.employee_ref = :employee_ref")
        params["employee_ref"] = employee_ref
    if status:
        where.append("r.status = :status")
        params["status"] = status
    return _list(
        db,
        f"""
        SELECT r.*, c.checklist_code, c.title AS checklist_title
        FROM domain_hr.onboarding_runs r
        JOIN domain_hr.onboarding_checklists c ON c.id = r.checklist_id AND c.tenant_id = r.tenant_id
        WHERE {' AND '.join(where)}
        ORDER BY r.created_at DESC
        """,
        params,
    )


@router.post("/onboarding/runs", response_model=dict[str, Any], status_code=201, summary="Run anlegen")
async def create_run(payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("checklist_id", "employee_ref"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    item_id = str(uuid4())
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_hr.onboarding_runs
                  (id, tenant_id, checklist_id, employee_ref, assigned_by, started_at, due_date, completed_at, status, progress_percent, state, created_at, updated_at)
                VALUES
                  (:id, :tenant_id, :checklist_id, :employee_ref, :assigned_by, :started_at, :due_date, :completed_at, :status, :progress_percent, CAST(:state AS jsonb), NOW(), NOW())
                """
            ),
            {
                "id": item_id,
                "tenant_id": tenant_id,
                "checklist_id": d["checklist_id"],
                "employee_ref": d["employee_ref"],
                "assigned_by": d.get("assigned_by"),
                "started_at": d.get("started_at"),
                "due_date": d.get("due_date"),
                "completed_at": d.get("completed_at"),
                "status": d.get("status", "not_started"),
                "progress_percent": d.get("progress_percent", 0),
                "state": json.dumps(d.get("state", {})),
            },
        )
    except Exception as exc:
        raise HTTPException(status_code=409, detail=f"Onboarding run conflict: {exc}") from exc
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.onboarding_runs WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.put("/onboarding/runs/{item_id}", response_model=dict[str, Any], summary="Run aktualisieren")
async def update_run(item_id: str, payload: Payload, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    d = payload.data
    for key in ("checklist_id", "employee_ref"):
        if not d.get(key):
            raise HTTPException(status_code=400, detail=f"{key} is required")
    updated = db.execute(
        text(
            """
            UPDATE domain_hr.onboarding_runs
            SET checklist_id=:checklist_id, employee_ref=:employee_ref, assigned_by=:assigned_by, started_at=:started_at, due_date=:due_date,
                completed_at=:completed_at, status=:status, progress_percent=:progress_percent, state=CAST(:state AS jsonb), updated_at=NOW()
            WHERE tenant_id=:tenant_id AND id=:id
            """
        ),
        {
            "tenant_id": tenant_id,
            "id": item_id,
            "checklist_id": d["checklist_id"],
            "employee_ref": d["employee_ref"],
            "assigned_by": d.get("assigned_by"),
            "started_at": d.get("started_at"),
            "due_date": d.get("due_date"),
            "completed_at": d.get("completed_at"),
            "status": d.get("status", "not_started"),
            "progress_percent": d.get("progress_percent", 0),
            "state": json.dumps(d.get("state", {})),
        },
    ).rowcount
    if not updated:
        raise HTTPException(status_code=404, detail="Onboarding run not found")
    db.commit()
    row = db.execute(
        text("SELECT * FROM domain_hr.onboarding_runs WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).mappings().first()
    return _clean(dict(row))


@router.delete("/onboarding/runs/{item_id}", status_code=204, response_class=Response, response_model=None, summary="Run löschen")
async def delete_run(item_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)):
    deleted = db.execute(
        text("DELETE FROM domain_hr.onboarding_runs WHERE tenant_id=:tenant_id AND id=:id"),
        {"tenant_id": tenant_id, "id": item_id},
    ).rowcount
    if not deleted:
        raise HTTPException(status_code=404, detail="Onboarding run not found")
    db.commit()
    return None


@router.post("/onboarding/workspaces", response_model=dict[str, Any], summary="Onboarding workspace anlegen")
async def create_onboarding_workspace(
    payload: OnboardingWorkspaceRequest,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    if not payload.rolle.strip():
        raise HTTPException(status_code=400, detail="rolle is required")

    checklist: dict[str, Any] | None = None
    onboarding_run: dict[str, Any] | None = None

    if payload.checklist_id:
        checklist = _load_optional_row(
            db,
            "SELECT * FROM domain_hr.onboarding_checklists WHERE tenant_id=:tenant_id AND id=:id",
            {"tenant_id": tenant_id, "id": payload.checklist_id},
            not_found_detail="Checklist not found",
        )

    if payload.run_id:
        onboarding_run = _load_optional_row(
            db,
            "SELECT * FROM domain_hr.onboarding_runs WHERE tenant_id=:tenant_id AND id=:id",
            {"tenant_id": tenant_id, "id": payload.run_id},
            not_found_detail="Onboarding run not found",
        )
        if not checklist:
            checklist = _load_optional_row(
                db,
                "SELECT * FROM domain_hr.onboarding_checklists WHERE tenant_id=:tenant_id AND id=:id",
                {"tenant_id": tenant_id, "id": onboarding_run["checklist_id"]},
                not_found_detail="Checklist not found",
            )

    workspace = build_onboarding_workspace(
        db=db,
        rolle=payload.rolle,
        kanal=payload.kanal,
        tenant_id=tenant_id,
        employee_ref=payload.employee_ref,
        capability_key=payload.capability_key,
        query=payload.query,
        limit=payload.limit,
        checklist=checklist,
        onboarding_run=onboarding_run,
    )
    return workspace.as_dict()
