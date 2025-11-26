"""FastAPI Dependencies für Gateway."""

from __future__ import annotations

from decimal import Decimal
from functools import lru_cache
from typing import List

from fastapi import Depends, Request
from finance_shared.auth import ApprovalPolicyConfig, ApprovalRule, FiBuAccessPolicy, FiBuRole, RoleAssignment
from finance_shared.gobd import GoBDAuditTrail

from app.clients import FibuCoreClient, FibuMasterDataClient, FibuOpClient
from app.config import settings
from app.integration.event_publisher import FiBuEventPublisher
from app.storage.approval_rules import ApprovalRuleStore


@lru_cache
def get_core_client() -> FibuCoreClient:
    return FibuCoreClient(settings.FIBU_CORE_URL)


@lru_cache
def get_master_data_client() -> FibuMasterDataClient:
    return FibuMasterDataClient(settings.FIBU_MASTER_DATA_URL)


@lru_cache
def get_op_client() -> FibuOpClient:
    return FibuOpClient(settings.FIBU_OP_URL)


def get_tenant(request: Request) -> str:
    return getattr(request.state, "tenant_id", settings.DEFAULT_TENANT)


def get_approval_rule_store() -> ApprovalRuleStore:
    return _get_cached_rule_store()


@lru_cache
def _get_cached_rule_store() -> ApprovalRuleStore:
    return ApprovalRuleStore(
        settings.APPROVAL_RULES_DB_PATH,
        default_min_amount=Decimal(str(settings.JOURNAL_APPROVAL_THRESHOLD_EUR)),
        default_currency=settings.DEFAULT_CURRENCY,
    )


def get_access_policy(
    request: Request,
    tenant: str = Depends(get_tenant),
    store: ApprovalRuleStore = Depends(get_approval_rule_store),
) -> FiBuAccessPolicy:
    roles = _resolve_roles(request)
    assignment = RoleAssignment(
        tenant_id=tenant,
        user_id=_resolve_user_id(request),
        roles=roles or [FiBuRole.SACHBEARBEITER],
    )
    rule_records = store.list_rules(tenant)
    rules = [
        ApprovalRule(min_amount=record.min_amount, currency=record.currency, required_role=record.required_role)
        for record in rule_records
    ]
    config = ApprovalPolicyConfig(rules=rules, default_currency=settings.DEFAULT_CURRENCY)
    return FiBuAccessPolicy(assignment, config)


def get_audit_trail(tenant: str = Depends(get_tenant)) -> GoBDAuditTrail:
    return GoBDAuditTrail(tenant_id=tenant)


@lru_cache
def get_event_publisher() -> FiBuEventPublisher:
    return FiBuEventPublisher(
        enabled=settings.EVENT_BUS_ENABLED,
        url=settings.EVENT_BUS_URL,
        subject_booking_created=settings.EVENT_BUS_SUBJECT_BOOKING_CREATED,
    )


def _resolve_roles(request: Request) -> List[FiBuRole]:
    header = request.headers.get("X-FIBU-ROLES") or ""
    roles: List[FiBuRole] = []
    for raw in header.split(","):
        value = raw.strip().lower()
        if not value:
            continue
        try:
            roles.append(FiBuRole(value))
        except ValueError:
            continue
    return roles


def _resolve_user_id(request: Request) -> str:
    return getattr(request.state, "user_id", request.headers.get("X-User-ID") or "system")

