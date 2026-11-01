"""Canonical persistent CRM segments; all routes use the verified tenant."""
from __future__ import annotations

import json
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.auth.bereich_roles import SCHREIBEN
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.core.uuid7 import uuid7
from app.services import crm_segment_service as service

router = APIRouter(prefix="/crm/segments", tags=["crm", "segments"])


class Mutation(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    idempotency_key: str = Field(min_length=1, max_length=128, validation_alias=AliasChoices("idempotency_key", "_idempotencyKey"))
    expected_version: int | None = Field(default=None, ge=1)
    audit_reason: str | None = Field(default=None, max_length=1000, validation_alias=AliasChoices("audit_reason", "_auditReason"))


class SegmentInput(Mutation):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    segment_type: Literal["static", "dynamic"] = "static"
    criteria: dict[str, Any] = Field(default_factory=dict)
    criteria_rules: list[dict[str, str]] | None = Field(default=None, max_length=20)

    @model_validator(mode="after")
    def validate_rules(self):
        if not self.name.strip():
            raise ValueError("Segment name must not be blank")
        if self.criteria_rules is not None:
            if self.criteria:
                raise ValueError("Supply criteria or criteria_rules, not both")
            self.criteria = service.criteria_from_rules(self.criteria_rules)
        service.criteria_rules(self.criteria)
        if self.segment_type == "dynamic" and not self.criteria:
            raise ValueError("Dynamic segment requires explicit criteria")
        return self


# Updatable columns and their fixed SET fragments; values are always bound.
_UPDATABLE = {"name": "name=:name", "description": "description=:description",
              "segment_type": "segment_type=:segment_type", "criteria": "criteria=CAST(:criteria AS jsonb)"}


class SegmentUpdate(Mutation):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=10000)
    segment_type: Literal["static", "dynamic"] | None = None
    criteria: dict[str, Any] | None = None
    criteria_rules: list[dict[str, str]] | None = Field(default=None, max_length=20)

    @model_validator(mode="after")
    def validate_rules(self):
        if "name" in self.model_fields_set and (self.name is None or not self.name.strip()):
            raise ValueError("Segment name must not be blank")
        if "segment_type" in self.model_fields_set and self.segment_type is None:
            raise ValueError("Segment type must not be null")
        if self.criteria_rules is not None:
            if self.criteria is not None:
                raise ValueError("Supply criteria or criteria_rules, not both")
            self.criteria = service.criteria_from_rules(self.criteria_rules)
        if self.criteria is not None:
            service.criteria_rules(self.criteria)
        return self


class MemberInput(Mutation):
    partner_id: str = Field(min_length=1, max_length=128)


_find = service.find


def _versioned(db, tenant: str, segment_id: str, body: Mutation) -> dict:
    row = service.find(db, tenant, segment_id, lock=True)
    service.check_version(row, body.expected_version)
    return row


def _touch(db, tenant: str, segment_id: str, count: int | None = None) -> dict:
    db.execute(text("UPDATE domain_crm.crm_segments SET updated_at=clock_timestamp(), member_count=COALESCE(:count,member_count) WHERE tenant_id=:tenant AND id=:id"), {"tenant": tenant, "id": segment_id, "count": count})
    return service.find(db, tenant, segment_id)


@router.get("")
@router.get("/", include_in_schema=False)
async def list_segments(search: str | None = Query(default=None, max_length=255), limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    params = {"tenant": tenant_id,"search": f"%{search}%" if search else None,"limit": limit,"offset": offset}
    total = db.execute(text("SELECT count(*) FROM domain_crm.crm_segments WHERE tenant_id=:tenant AND (CAST(:search AS text) IS NULL OR name ILIKE :search)"), params).scalar_one()
    ids = db.execute(text("SELECT id FROM domain_crm.crm_segments WHERE tenant_id=:tenant AND (CAST(:search AS text) IS NULL OR name ILIKE :search) ORDER BY name,id LIMIT :limit OFFSET :offset"), params).scalars().fetchmany(limit)
    return {"items": [service.find(db, tenant_id, sid) for sid in ids], "total": total}


@router.post("", status_code=201, dependencies=SCHREIBEN["CRM"])
@router.post("/", status_code=201, include_in_schema=False, dependencies=SCHREIBEN["CRM"])
async def create_segment(body: SegmentInput, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    def mutate():
        sid = str(uuid7())
        db.execute(text("INSERT INTO domain_crm.crm_segments (id,tenant_id,name,description,segment_type,criteria,member_count,created_at,updated_at) VALUES (:id,:tenant,:name,:description,:segment_type,CAST(:criteria AS jsonb),0,clock_timestamp(),clock_timestamp())"), {"id": sid,"tenant": tenant_id,"name": body.name.strip(),"description": body.description,"segment_type": body.segment_type,"criteria": json.dumps(body.criteria)})
        return service.find(db, tenant_id, sid)
    return service.command(db, tenant_id, "create", body.idempotency_key, body.model_dump(), mutate)


@router.get("/{segment_id}")
async def get_segment(segment_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    return service.find(db, tenant_id, segment_id)


@router.put("/{segment_id}", dependencies=SCHREIBEN["CRM"])
async def update_segment(segment_id: str, body: SegmentUpdate, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    def mutate():
        row = _versioned(db, tenant_id, segment_id, body)
        updates = body.model_dump(exclude_unset=True, exclude={"idempotency_key","expected_version","audit_reason","criteria_rules"})
        if body.criteria_rules is not None:
            updates["criteria"] = body.criteria
        if (updates.get("segment_type") or row["segment_type"]) == "dynamic" and not (updates.get("criteria", row["criteria"])):
            raise HTTPException(422, "Dynamic segment requires explicit criteria")
        if "criteria" in updates and updates["criteria"] is None:
            raise HTTPException(422, "Criteria must not be null")
        if updates:
            if not set(updates) <= _UPDATABLE:
                raise HTTPException(422, "Unsupported segment field")
            keys = [_UPDATABLE[key] for key in updates]
            if "criteria" in updates:
                updates["criteria"] = json.dumps(updates["criteria"])
            db.execute(text("UPDATE domain_crm.crm_segments SET " + ",".join(keys) + " WHERE tenant_id=:tenant AND id=:id"), {**updates,"tenant": tenant_id,"id": segment_id})  # nosec B608  # SET-Teile nur aus der festen _UPDATABLE-Zuordnung, Werte gebunden
        return _touch(db, tenant_id, segment_id)
    return service.command(db, tenant_id, "update", body.idempotency_key, {"id": segment_id,**body.model_dump()}, mutate)


@router.get("/{segment_id}/members")
async def segment_members(segment_id: str, limit: int = Query(100, ge=1, le=5000), offset: int = Query(0, ge=0), tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    service.find(db, tenant_id, segment_id)
    params={"tenant": tenant_id,"id": segment_id,"limit": limit,"offset": offset}
    total=db.execute(text("SELECT count(*) FROM domain_crm.crm_segment_members m JOIN domain_crm.business_partners p ON p.partner_id=m.partner_id WHERE m.tenant_id=:tenant AND m.segment_id=:id AND p.tenant_id=:tenant"),params).scalar_one()
    rows=db.execute(text("SELECT m.id,m.partner_id,m.partner_id AS contact_id,m.added_at,p.name_1 AS name FROM domain_crm.crm_segment_members m JOIN domain_crm.business_partners p ON p.partner_id=m.partner_id WHERE m.tenant_id=:tenant AND m.segment_id=:id AND p.tenant_id=:tenant ORDER BY m.added_at,m.id LIMIT :limit OFFSET :offset"),params).mappings().fetchmany(limit)
    return {"items":[dict(row) for row in rows],"total":total}


@router.post("/{segment_id}/members", dependencies=SCHREIBEN["CRM"])
async def add_segment_member(segment_id: str, body: MemberInput, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    def mutate():
        row=_versioned(db,tenant_id,segment_id,body)
        if row["segment_type"] != "static":
            raise HTTPException(409,"Manual members belong to static segments")
        partner=db.execute(text("SELECT partner_id FROM domain_crm.business_partners WHERE tenant_id=:tenant AND partner_id=:partner FOR SHARE"),{"tenant":tenant_id,"partner":body.partner_id}).scalar()
        if partner is None:
            raise HTTPException(404,"Partner not found")
        db.execute(text("INSERT INTO domain_crm.crm_segment_members (id,tenant_id,segment_id,partner_id,added_at) VALUES (:mid,:tenant,:id,:partner,clock_timestamp()) ON CONFLICT (segment_id,partner_id) DO NOTHING"),{"mid":str(uuid7()),"tenant":tenant_id,"id":segment_id,"partner":body.partner_id})
        return _touch(db,tenant_id,segment_id,service.evaluate(db,tenant_id,row))
    return service.command(db,tenant_id,"member.add",body.idempotency_key,{"id":segment_id,**body.model_dump()},mutate)


@router.post("/{segment_id}/members/remove", dependencies=SCHREIBEN["CRM"])
async def remove_segment_member(segment_id: str, body: MemberInput, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    def mutate():
        row=_versioned(db,tenant_id,segment_id,body)
        if row["segment_type"] != "static":
            raise HTTPException(409,"Manual members belong to static segments")
        db.execute(text("DELETE FROM domain_crm.crm_segment_members WHERE tenant_id=:tenant AND segment_id=:id AND partner_id=:partner"),{"tenant":tenant_id,"id":segment_id,"partner":body.partner_id})
        return _touch(db,tenant_id,segment_id,service.evaluate(db,tenant_id,row))
    return service.command(db,tenant_id,"member.remove",body.idempotency_key,{"id":segment_id,**body.model_dump()},mutate)


@router.post("/{segment_id}/calculate", dependencies=SCHREIBEN["CRM"])
@router.post("/{segment_id}/recalculate", include_in_schema=False, dependencies=SCHREIBEN["CRM"])
async def recalculate_segment(segment_id: str, body: Mutation, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    def mutate():
        row=_versioned(db,tenant_id,segment_id,body)
        return _touch(db,tenant_id,segment_id,service.evaluate(db,tenant_id,row))
    return service.command(db,tenant_id,"calculate",body.idempotency_key,{"id":segment_id,**body.model_dump()},mutate)


@router.get("/{segment_id}/performance")
async def segment_performance(segment_id: str, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    row=service.find(db,tenant_id,segment_id)
    return {"segment_id":segment_id,"member_count":row["member_count"],"updated_at":row["updated_at"],"criteria_supported":row["criteria_supported"]}


@router.delete("/{segment_id}", dependencies=SCHREIBEN["CRM"])
async def delete_segment(segment_id: str, body: Mutation, tenant_id: str = Depends(get_tenant_id), db: Session = Depends(get_db)) -> dict:
    def mutate():
        row=_versioned(db,tenant_id,segment_id,body)
        db.execute(text("DELETE FROM domain_crm.crm_segment_members WHERE tenant_id=:tenant AND segment_id=:id"),{"tenant":tenant_id,"id":segment_id})
        db.execute(text("DELETE FROM domain_crm.crm_segments WHERE tenant_id=:tenant AND id=:id"),{"tenant":tenant_id,"id":segment_id})
        return {"id":segment_id,"version":row["version"],"deleted":True}
    return service.command(db,tenant_id,"delete",body.idempotency_key,{"id":segment_id,**body.model_dump()},mutate)
