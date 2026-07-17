"""Deterministic assist proposals API (FEED-AI-046, contract 11-agenten.md)."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.agrar.rations.authz import READ_ROLES, require_roles
from app.auth.deps import User, get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.services.feeding_assist_service import FeedingAssistService

router = APIRouter(prefix="/feeding/assist", tags=["feeding-assist"])


class ExplainFindingsIn(BaseModel):
    group_id: str = Field(min_length=1, max_length=80)
    components: list[dict[str, Any]] = Field(min_length=1)


class ProposalOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    proposal_id: str
    agent: str
    objective: str
    scope: dict[str, Any]
    facts: list[dict[str, Any]]
    assumptions: list[str]
    recommendations: list[dict[str, Any]]
    evidence_refs: list[str]
    ruleset: str
    confidence: str
    risks: list[Any]
    proposed_commands: list[dict[str, Any]]
    requires_human_approval: bool


class StoredProposalOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    agent: str
    objective: str
    group_id: str | None = None
    content: dict[str, Any]
    created_by: str
    created_at: datetime


class SubstituteCandidateOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    feed_id: str
    name: str
    feed_kind: str
    price_eur_t: float | None = None
    price_provenance: str | None = None
    analysis_complete: bool
    uncertainty: str | None = None


class SubstitutesOut(BaseModel):
    model_config = ConfigDict(extra="ignore")

    feed_id: str
    feed_name: str
    feed_kind: str
    restriction: str
    candidates: list[SubstituteCandidateOut]
    requires_human_approval: bool


def _service(db: Session, tenant_id: str, user: User) -> FeedingAssistService:
    return FeedingAssistService(db, tenant_id, str(user.get("sub") or "unknown"))


@router.post("/explain-findings", response_model=ProposalOut, status_code=201,
             summary="Befunde deterministisch erklaeren (Proposal mit Evidenz und Unsicherheit)")
async def explain_findings(body: ExplainFindingsIn, db: Session = Depends(get_db),
                           tenant_id: str = Depends(get_tenant_id),
                           user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer die Assistenz.")
    try:
        return _service(db, tenant_id, user).explain_findings(
            group_id=body.group_id, components=body.components)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/propose-measures", response_model=ProposalOut, status_code=201,
             summary="Bestaetigungspflichtige Massnahmenvorschlaege aus offenen Abweichungsbefunden")
async def propose_measures(db: Session = Depends(get_db),
                           tenant_id: str = Depends(get_tenant_id),
                           user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer die Assistenz.")
    # Grant-gefilterte Befunde ueber den bestehenden Vertrag (kein zweiter Datenpfad).
    from app.api.v1.endpoints.feeding_actual import _actor, _groups
    from app.services.feeding_actual_measure_service import FeedingActualMeasureService
    findings = FeedingActualMeasureService(db, tenant_id, _actor(user)).findings(
        group_ids=_groups(db, tenant_id, user))
    return _service(db, tenant_id, user).propose_measures(findings=findings)


@router.get("/substitutes", response_model=SubstitutesOut,
            summary="Ersatzfuttermittel gleicher Klasse nach Preis mit Provenienz und Unsicherheit")
async def substitutes(feed_id: str, db: Session = Depends(get_db),
                      tenant_id: str = Depends(get_tenant_id),
                      user: User = Depends(get_current_user)) -> dict[str, Any]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer die Assistenz.")
    try:
        return _service(db, tenant_id, user).substitutes(feed_id=feed_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/proposals", response_model=list[StoredProposalOut],
            summary="Auditierte Assistenz-Proposals (neueste zuerst)")
async def list_proposals(group_id: str | None = None, db: Session = Depends(get_db),
                         tenant_id: str = Depends(get_tenant_id),
                         user: User = Depends(get_current_user)) -> list[dict[str, Any]]:
    require_roles(user, READ_ROLES, detail="Keine Berechtigung fuer die Assistenz.")
    return _service(db, tenant_id, user).list_proposals(group_id=group_id)
