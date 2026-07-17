"""FEED-AI-046 (TDD-Red-Welle 1): deterministische Assistenz nach dem
Agentenvertrag (11-agenten.md) — Proposal-Schema, Evidenz, Unsicherheit,
Human Gate, keine erfundenen Werte. Vor der Implementierung geschrieben.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.main import app as main_app

ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(main_app, raise_server_exceptions=False)


@pytest.mark.parametrize(("method", "path", "body"), [
    ("post", "/feeding/assist/explain-findings",
     {"group_id": "g-1", "components": [{"feed_id": "f-1", "kg_fm": 10}]}),
    ("post", "/feeding/assist/propose-measures", {}),
    ("get", "/feeding/assist/substitutes?feed_id=f-1", None),
    ("get", "/feeding/assist/proposals", None),
])
def test_assist_endpoints_reject_user_without_role(method: str, path: str, body: dict | None) -> None:
    from app.api.v1.endpoints import feeding_assist
    app = FastAPI()
    app.include_router(feeding_assist.router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "role-test", "roles": []}
    app.dependency_overrides[get_tenant_id] = lambda: "tenant-role-test"
    app.dependency_overrides[get_db] = lambda: object()
    with TestClient(app) as role_client:
        response = getattr(role_client, method)(path, **({"json": body} if body is not None else {}))
    assert response.status_code == 403, (method, path, response.text)


# ── Journey (Dev-DB) ────────────────────────────────────────────────────────

def _feed(suffix: str, *, kind: str = "forage", price: float | None = 60.0,
          with_energy: bool = True) -> str:
    payload: dict[str, Any] = {
        "artikel_nummer": f"AI-{suffix}", "name": f"Assistfutter {suffix}",
        "art": "Grundfutter", "feed_kind": kind, "approval_status": "approved"}
    if price is not None:
        payload["preis_pro_t"] = price
    feed = client.post(f"{ROOT}/feed-catalog/feeds", headers=HEADERS, json=payload)
    assert feed.status_code == 201, feed.text
    feed_id = feed.json()["id"]
    values = [("dry_matter", "35", "percent")]
    if with_energy:
        values.append(("metabolizable_energy", "10.5", "MJ_per_kg"))
    for code, value, unit in values:
        response = client.post(f"{ROOT}/feed-catalog/feeds/{feed_id}/reference-values",
                               headers=HEADERS, json={
                                   "nutrient_code": code, "value": value, "unit_code": unit,
                                   "basis": "dry_matter", "source_type": "analysis",
                                   "source_ref": f"assist {suffix}"})
        assert response.status_code == 201, response.text
    return feed_id


def test_explain_findings_returns_audited_proposal_with_evidence() -> None:
    suffix = uuid4().hex[:8]
    feed_id = _feed(suffix)
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Assist {suffix}", "animal_count": 20, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]
    profile = client.post(f"{ROOT}/feeding/requirement-profiles", headers=HEADERS,
                          json={"group_id": group_id, "inputs": {"milk_kg_day": 30}})
    assert profile.status_code == 201, profile.text

    # bewusst knappe Ration -> deterministische Befunde (Energie/DMI)
    explained = client.post(f"{ROOT}/feeding/assist/explain-findings", headers=HEADERS,
                            json={"group_id": group_id,
                                  "components": [{"feed_id": feed_id, "kg_fm": 10.0}]})
    assert explained.status_code == 201, explained.text
    proposal = explained.json()

    assert proposal["agent"] == "ration_advisor"
    assert proposal["requires_human_approval"] is True
    assert proposal["facts"], "Befunde als Fakten mit Evidenz"
    fact = proposal["facts"][0]
    assert fact["kind"] == "finding" and fact["code"] and fact["message"]
    assert any(ref.startswith("requirement-profile:") for ref in proposal["evidence_refs"]), \
        "Evidenz referenziert das Bedarfsprofil"
    assert proposal["recommendations"], "Empfehlungen aus Befund-Abhilfen/Historie"
    assert proposal["confidence"] in {"low", "medium"}
    assert any("Historie" in a or "Beobachtung" in a for a in proposal["assumptions"]), \
        "fehlende Historie wird als Annahme benannt, nicht verschwiegen (FEED-AI-009)"

    # auditiert: Proposal ist gespeichert und abrufbar (FEED-AI-010)
    listed = client.get(f"{ROOT}/feeding/assist/proposals?group_id={group_id}", headers=HEADERS)
    assert listed.status_code == 200
    assert any(item["id"] == proposal["proposal_id"] for item in listed.json())


def test_propose_measures_creates_confirmable_commands_without_commit() -> None:
    # Abweichungslage aus dem bestehenden Ist-Fuetterungs-Vertrag aufbauen
    suffix = uuid4().hex[:8]
    feed_id = _feed(suffix)
    assert client.post(f"{ROOT}/feed-catalog/feeds/{feed_id}/products", headers=HEADERS, json={
        "sku": f"AI-P-{suffix}", "display_name": "Lose Ware", "price_eur_t": "50",
        "freight_eur_t": "5", "packaging_unit": "t", "package_size": 1}).status_code == 201
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"AssistM {suffix}", "animal_count": 10, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group.json()["id"], "name": f"AssistRation {suffix}",
        "snapshot": {"components": [{"feed_id": feed_id, "name": "Assist", "kg_fm": 10.0}]}})
    version_id = ration.json()["latest_version_id"]
    for target, expected in (("in_review", "draft"), ("approved", "in_review")):
        assert client.post(f"{ROOT}/lifecycle/versions/{version_id}/transitions",
                           headers=HEADERS, json={"target_status": target,
                                                  "expected_status": expected}).status_code == 200
    plan = client.post(f"{ROOT}/feeding/plans/publish", headers=HEADERS, json={
        "source_ration_version_id": version_id, "animal_count": 10,
        "dosing_step_kg": "0.1", "rounding_mode": "nearest",
        "valid_from": str(date.today()), "reason": "Assist-Testplan",
        "idempotency_key": f"assist-{suffix}"})
    assert plan.status_code == 201, plan.text
    policy = client.post(f"{ROOT}/feeding/actuals/deviation-policies", headers=HEADERS, json={
        "feed_class": "forage", "warning_pct": "5", "critical_pct": "10",
        "valid_from": date.today().isoformat(),
        "reason": "Assist-Toleranz fuer Grundfutter"})
    assert policy.status_code == 201, policy.text
    actual = client.post(f"{ROOT}/feeding/actuals", headers=HEADERS, json={
        "plan_version_id": plan.json()["id"],
        "feeding_at": datetime.now(timezone.utc).isoformat(),
        "source": "manual", "source_ref": f"assist-{uuid4()}",
        "cause_class": "dosing_error", "comment": "Deutliche Ueberdosierung",
        "idempotency_key": f"assist-act-{uuid4()}",
        "components": [{"feed_id": feed_id, "actual_kg": "115"}]})
    assert actual.status_code == 201, actual.text
    component_id = actual.json()["components"][0]["id"]

    proposed = client.post(f"{ROOT}/feeding/assist/propose-measures", headers=HEADERS, json={})
    assert proposed.status_code == 201, proposed.text
    proposal = proposed.json()
    assert proposal["requires_human_approval"] is True
    commands = proposal["proposed_commands"]
    mine = next(item for item in commands
                if item["payload"]["actual_component_id"] == component_id)
    assert mine["command"] == "create_actual_measure"
    assert mine["endpoint"].endswith("/feeding/actuals/measures")
    assert mine["payload"]["title"]
    assert mine["payload"]["idempotency_key"]
    assert mine["payload"]["reason"]

    # Human Gate: NICHTS wurde committed — keine Massnahme existiert
    measures = client.get(f"{ROOT}/feeding/actuals/measures", headers=HEADERS)
    assert measures.status_code == 200
    assert not any(item["actual_component_id"] == component_id for item in measures.json())


def test_substitutes_rank_by_price_with_provenance_and_uncertainty() -> None:
    suffix = uuid4().hex[:8]
    source = _feed(f"src-{suffix}", price=80.0)
    cheap = _feed(f"cheap-{suffix}", price=55.0)
    no_analysis = _feed(f"noana-{suffix}", price=50.0, with_energy=False)
    _feed(f"otherkind-{suffix}", kind="mineral", price=10.0)

    response = client.get(f"{ROOT}/feeding/assist/substitutes?feed_id={source}",
                          headers=HEADERS)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["feed_id"] == source
    ids = [item["feed_id"] for item in payload["candidates"]]
    assert cheap in ids and no_analysis in ids
    assert source not in ids, "Ausgangsfutter ist kein Ersatzkandidat"
    assert all(item["feed_kind"] == "forage" for item in payload["candidates"]), \
        "Restriktion: gleiche Futterklasse"
    prices = [item["price_eur_t"] for item in payload["candidates"] if item["price_eur_t"] is not None]
    assert prices == sorted(prices), "nach Preis sortiert"
    incomplete = next(item for item in payload["candidates"] if item["feed_id"] == no_analysis)
    assert incomplete["analysis_complete"] is False
    assert incomplete["uncertainty"], "fehlende Analyse wird benannt, nicht geschaetzt"

    missing = client.get(f"{ROOT}/feeding/assist/substitutes?feed_id={uuid4()}",
                         headers=HEADERS)
    assert missing.status_code == 404
