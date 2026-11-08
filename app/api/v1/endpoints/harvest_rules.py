"""Transport adapter for versioned harvest domain commands, never direct CRUD."""
from datetime import date, datetime
from typing import Any, Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from decimal import Decimal
from pydantic import BaseModel, computed_field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.finance_roles import beleg_read, beleg_write, finance_admin
from app.core.database import get_db
from app.core.exceptions import DomainError
from app.core.tenant import get_tenant_id
from app.api.v1.schemas.agrar_schemas import HarvestSettlementOut
from modules.agrar.contracts.harvest_control_v1 import (CalculationApproveIn, ContextCommandIn,
    FinancialReleaseIn, MeasurementAttestIn, RuleBindIn, RuleCreateIn, RuleDecisionIn)
from modules.agrar.contracts.harvest_deductions_v1 import HarvestDeductionRuleV1
from modules.agrar.services.harvest_rule_store import HarvestRuleStore, rule_approver

class SafeHarvestRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()
        async def safe(request):
            try:
                return await handler(request)
            except RequestValidationError as exc:
                # Validation diagnostics never echo contract/customer input values.
                return JSONResponse(status_code=422, content={"detail": [
                    {"loc": list(error["loc"]), "type": error["type"], "msg": "Ungueltige Eingabe."}
                    for error in exc.errors()]})
        return safe


router = APIRouter(dependencies=[Depends(beleg_read)], tags=["agrar", "harvest-controls"], route_class=SafeHarvestRoute)


class RuleVersionOut(BaseModel):
    id: str
    definition: HarvestDeductionRuleV1
    content_hash: str
    created_by: str
    status: str
    actor: str | None = None
    recorded_at: datetime | None = None

    # Display projection of the sole immutable definition; never stored or accepted as rule input.
    @computed_field
    @property
    def rule_id(self) -> str:
        return self.definition.rule_id

    @computed_field
    @property
    def rule_version(self) -> int:
        return self.definition.rule_version

    @computed_field
    @property
    def impurities_free_pct(self) -> Decimal:
        return self.definition.impurities_free_pct

    @computed_field
    @property
    def quality_limit_pct(self) -> Decimal | None:
        return self.definition.quality_limit_pct

    @computed_field
    @property
    def measurement_method(self) -> str:
        return self.definition.measurement_method

    @computed_field
    @property
    def measurement_method_version(self) -> str:
        return self.definition.measurement_method_version

    @computed_field
    @property
    def valid_from(self) -> date:
        return self.definition.valid_from

    @computed_field
    @property
    def valid_until(self) -> date:
        return self.definition.valid_until

    @computed_field
    @property
    def source_reference(self) -> str:
        return self.definition.source_reference


class RuleListOut(BaseModel):
    items: list[RuleVersionOut]
    total: int


class ControlEventOut(BaseModel):
    id: str
    rule_version_id: str | None = None
    content_hash: str | None = None
    rule_hash: str | None = None
    calculation_hash: str | None = None
    expires_at: datetime | None = None
    reason: str | None = None
    decision: str | None = None
    protocol_id: str | None = None
    protocol_hash: str | None = None
    snapshot: dict[str, Any] | None = None
    measurement_method: str | None = None
    measurement_method_version: str | None = None
    source_reference: str | None = None
    acknowledge_quality_exception: bool | None = None


class SettlementContextOut(BaseModel):
    context_hash: str
    state: dict[str, Any]
    protocol_hash: str | None = None
    rule_version_id: str | None = None
    calculation_hash: str | None = None
    calculation_id: str | None = None
    calculation_approval: dict[str, Any] | None = None
    release_status: str
    issues: list[str]
    calculation_current: bool
    calculation_result: HarvestSettlementOut | None = None


class ControlledSettlementOut(HarvestSettlementOut):
    calculation_hash: str
    control_event_id: str


class ChoiceOut(BaseModel):
    value: str
    label: str


class ChoicesOut(BaseModel):
    items: list[ChoiceOut]


class PermissionsOut(BaseModel):
    allowed_actions: list[str]


class AuditRowOut(BaseModel):
    id: str
    action: str
    actor: str
    issuer: str
    recorded_at: datetime
    calculation_hash: str | None = None
    rule_version_id: str | None = None


class AuditListOut(BaseModel):
    items: list[AuditRowOut]
    total: int


def verified_principal(request, user):
    claims = getattr(request.state, "token_claims", None) or {}
    subject = claims.get("sub")
    raw = user.get("raw") or {}
    if (getattr(request.state, "tenant_verified", False) is not True
            or not isinstance(subject, str) or not subject.strip() or subject != user.get("sub")
            or not isinstance(claims.get("iss"), str) or not claims["iss"]
            or raw.get("iss") != claims["iss"] or raw.get("sub") != subject):
        raise HTTPException(403, "Gepruefter Mandanten- und Benutzerkontext erforderlich.")
    return user


def controlled_service(db, tenant, user):
    from app.services.harvest_acceptance_service import HarvestAcceptanceService
    store = HarvestRuleStore(db, tenant, user)
    service = HarvestAcceptanceService(db, tenant, rule_resolver=store.resolve, settlement_control=store)
    return service, store


def execute(operation):
    try:
        return operation()
    except DomainError as exc:
        raise HTTPException(exc.http_status, exc.detail) from exc
    except SQLAlchemyError as exc:
        raise HTTPException(503, "Regel- oder Nachweisspeicher nicht verfuegbar.") from exc


def get_store(request: Request, tenant=Depends(get_tenant_id), db: Session=Depends(get_db),
              user=Depends(get_current_user)):
    return controlled_service(db, tenant, verified_principal(request, user))[1]


@router.get("/permissions", response_model=PermissionsOut, summary="Wirksame Bedienaktionen aus vorhandenen Bereichsrollen ableiten")
def permissions(store=Depends(get_store)):
    allowed = ["refresh"]
    for dependency, actions in [(beleg_write, ["create_rule", "bind_rule", "attest", "calculate", "release"]),
                                (rule_approver, ["approve_rule", "revoke_rule"]),
                                (finance_admin, ["approve_calculation"])]:
        try:
            dependency(user=store.principal)
            if dependency in (rule_approver, finance_admin):
                store._human_approver()
            allowed.extend(actions)
        except (HTTPException, DomainError):
            pass
    return {"allowed_actions": allowed}


@router.get("/choices/{kind}", response_model=ChoicesOut, summary="Mandantengebundene fachliche Auswahl suchen")
def choices(kind: Literal["acceptance", "customer", "article", "contract"], q: str=Query(min_length=2, max_length=100),
            limit: int=Query(25, ge=1, le=25), store=Depends(get_store)):
    return execute(lambda: store.choices(kind, q, limit))


@router.get("/acceptances/{acceptance_id}/history", response_model=AuditListOut, summary="Unveraenderliche Abrechnungsnachweise lesen")
def history(acceptance_id: str, offset: int | None=Query(None, ge=0), page: int=Query(1, ge=1),
            limit: int=Query(25, ge=1, le=100), store=Depends(get_store)):
    return execute(lambda: store.history(acceptance_id, offset=offset if offset is not None else (page-1)*limit, limit=limit))


@router.get("/rules", response_model=RuleListOut, summary="Versionierte Vertragsregeln lesen")
def list_rules(offset: int | None=Query(None, ge=0), page: int=Query(1, ge=1),
               limit: int=Query(25, ge=1, le=100), store=Depends(get_store)):
    return execute(lambda: store.list_rules(offset=offset if offset is not None else (page-1)*limit, limit=limit))


@router.post("/rules", response_model=RuleVersionOut, status_code=201,
             dependencies=[Depends(beleg_write)], summary="Neue unveraenderliche Vertragsregelversion erstellen")
def create_rule(body: RuleCreateIn, store=Depends(get_store)):
    return execute(lambda: store.create_rule(body))


@router.post("/rules/{version_id}/approve", response_model=ControlEventOut,
             dependencies=[Depends(rule_approver)], summary="Konkrete Vertragsregel im Vier-Augen-Prinzip genehmigen")
def approve_rule(version_id: str, body: RuleDecisionIn, store=Depends(get_store)):
    return execute(lambda: store.decide_rule(version_id, body))


@router.post("/rules/{version_id}/revoke", response_model=ControlEventOut,
             dependencies=[Depends(rule_approver)], summary="Vertragsregelgenehmigung widerrufen")
def revoke_rule(version_id: str, body: RuleDecisionIn, store=Depends(get_store)):
    return execute(lambda: store.decide_rule(version_id, body, revoke=True))


@router.get("/acceptances/{acceptance_id}/context", response_model=SettlementContextOut,
            summary="Aktuellen Eingabe- und Nachweisstand der Abrechnung lesen")
def context(acceptance_id: str, store=Depends(get_store)):
    return execute(lambda: store.context(acceptance_id))


@router.post("/acceptances/{acceptance_id}/bind-rule", response_model=ControlEventOut,
             dependencies=[Depends(beleg_write)], summary="Genehmigte Regelversion an Annahme binden")
def bind_rule(acceptance_id: str, body: RuleBindIn, store=Depends(get_store)):
    return execute(lambda: store.bind_rule(acceptance_id, body))


@router.post("/acceptances/{acceptance_id}/attest-measurement", response_model=ControlEventOut,
             dependencies=[Depends(beleg_write)], summary="Messprovenienz fuer den konkreten Protokollstand bestaetigen")
def attest(acceptance_id: str, body: MeasurementAttestIn, store=Depends(get_store)):
    return execute(lambda: store.attest(acceptance_id, body))


@router.post("/acceptances/{acceptance_id}/approve-calculation", response_model=ControlEventOut,
             dependencies=[Depends(finance_admin)], summary="Gepruefte Berechnungsfassung finanziell genehmigen")
def approve_calculation(acceptance_id: str, body: CalculationApproveIn, store=Depends(get_store)):
    service, _ = controlled_service(store.db, store.tenant_id, store.principal)
    return execute(lambda: store.approve_calculation(service, acceptance_id, body))
