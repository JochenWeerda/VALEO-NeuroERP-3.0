"""Unit-Tests: Privacy Erasure Evaluate/Execute (In-Memory-Repository)."""

from __future__ import annotations

from uuid import uuid4

import pytest

from app.config.settings import settings
from app.schemas.privacy_erasure import ErasureEvaluateRequest, ErasureExecuteRequest
from app.services.privacy_erasure.constants import ACTION_LEGACY_HTTP_CRM_ERASURE
from app.services.privacy_erasure.service import PrivacyErasureError, PrivacyErasureService
from app.services.privacy_erasure.store import InMemoryPrivacyRepository


@pytest.fixture
def repo() -> InMemoryPrivacyRepository:
    return InMemoryPrivacyRepository()


@pytest.fixture
def svc(repo: InMemoryPrivacyRepository) -> PrivacyErasureService:
    return PrivacyErasureService(repo)


@pytest.mark.asyncio
async def test_evaluate_conservative_insufficient_information(
    svc: PrivacyErasureService, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(settings, "PRIVACY_ERASURE_LEGACY_CRM_EVALUATE", False)

    rid = uuid4()
    sub = uuid4()
    cid = "corr-test-1"

    resp = await svc.evaluate(
        request_id=rid,
        subject_id=sub,
        body=ErasureEvaluateRequest(tenant_id="t1", anonymize_only=False, scope="crm_slice"),
        correlation_id=cid,
        actor_id="actor-1",
    )

    assert resp.decision == "insufficient_information"
    assert ACTION_LEGACY_HTTP_CRM_ERASURE in resp.blocked_actions
    assert resp.requires_manual_review is True


@pytest.mark.asyncio
async def test_execute_idempotent_duplicate(
    svc: PrivacyErasureService, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(settings, "PRIVACY_ERASURE_LEGACY_CRM_EVALUATE", True)

    async def fake_orch(**kwargs):
        return {"steps": ["mock"]}

    monkeypatch.setattr(
        "app.services.privacy_erasure.service.orchestrate_erasure",
        fake_orch,
    )

    rid = uuid4()
    sub = uuid4()

    ev = await svc.evaluate(
        request_id=rid,
        subject_id=sub,
        body=ErasureEvaluateRequest(tenant_id="t1", anonymize_only=False, scope="crm_slice"),
        correlation_id="c1",
        actor_id=None,
    )

    ex1 = ErasureExecuteRequest(
        tenant_id="t1",
        decision_id=ev.decision_id,
        action=ACTION_LEGACY_HTTP_CRM_ERASURE,
        anonymize_only=False,
        actor_id="operator",
    )
    r1 = await svc.execute(request_id=rid, subject_id=sub, body=ex1, correlation_id="e1")
    assert r1.result == "completed"
    assert r1.erasure_log == {"steps": ["mock"]}

    r2 = await svc.execute(request_id=rid, subject_id=sub, body=ex1, correlation_id="e2")
    assert r2.result == "duplicate_idempotent_retry"


@pytest.mark.asyncio
async def test_execute_wrong_anonymize_flag(
    svc: PrivacyErasureService, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setattr(settings, "PRIVACY_ERASURE_LEGACY_CRM_EVALUATE", True)

    async def fake_orch(**kwargs):
        return {}

    monkeypatch.setattr(
        "app.services.privacy_erasure.service.orchestrate_erasure",
        fake_orch,
    )

    rid = uuid4()
    sub = uuid4()
    ev = await svc.evaluate(
        request_id=rid,
        subject_id=sub,
        body=ErasureEvaluateRequest(tenant_id="t1", anonymize_only=True, scope="crm_slice"),
        correlation_id="c1",
        actor_id=None,
    )

    bad = ErasureExecuteRequest(
        tenant_id="t1",
        decision_id=ev.decision_id,
        action=ACTION_LEGACY_HTTP_CRM_ERASURE,
        anonymize_only=False,
        actor_id="x",
    )

    with pytest.raises(PrivacyErasureError):
        await svc.execute(request_id=rid, subject_id=sub, body=bad, correlation_id="e1")
