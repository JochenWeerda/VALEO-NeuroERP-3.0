"""FEED-REP-040: Beratungs-, Soll-Ist- und Verlaufsberichte auf der
Report-Entitaet (TDD-Red-Welle 1). Vor der Implementierung geschrieben.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app as main_app

client = TestClient(main_app, raise_server_exceptions=False)
ROOT = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}


def _create_report(report_type: str, profile: str, source_ref: str,
                   expected_status: int = 201) -> dict[str, Any]:
    response = client.post(f"{ROOT}/feeding/reports", headers=HEADERS, json={
        "report_type": report_type, "profile": profile, "source_ref": source_ref})
    assert response.status_code == expected_status, response.text
    return response.json()


# ── consulting: Beratungsbericht aus unveraenderlichem Entwurf ──────────────

def test_consulting_report_is_profiled_and_draft_bound() -> None:
    case = client.post(f"{ROOT}/feeding/consulting-cases", headers=HEADERS, json={
        "title": f"REP040 Fall {uuid4().hex[:8]}", "case_type": "visit",
        "initial_situation": "Verdacht auf Mischfehler soll berichtet werden"})
    assert case.status_code == 201, case.text
    case_id = case.json()["id"]
    observation = client.post(
        f"{ROOT}/feeding/consulting-cases/{case_id}/observations", headers=HEADERS,
        json={"category": "fuetterung",
              "text": "Vorlage und Restfutter kontrolliert",
              "client_ref": f"rep040-obs-{uuid4()}"})
    assert observation.status_code == 201, observation.text
    draft = client.post(
        f"{ROOT}/feeding/consulting-cases/{case_id}/report-drafts", headers=HEADERS,
        json={"reason": "Datenstand fuer Berichtspaket 2 festhalten"})
    assert draft.status_code == 201, draft.text
    draft_id = draft.json()["id"]

    advisor = _create_report("consulting", "advisor", draft_id)
    again = _create_report("consulting", "advisor", draft_id)
    assert again["id"] == advisor["id"], "idempotent bei identischem Entwurf"
    assert advisor["content"]["case"]["id"] == case_id
    assert advisor["content"]["observations"], "advisor sieht Beobachtungen"

    farmer = _create_report("consulting", "farmer", draft_id)
    assert farmer["content_hash"] != advisor["content_hash"]
    for measure in farmer["content"]["measures"]:
        assert "owner_subject" not in measure, "farmer ohne interne Steuerfelder"
        assert "escalation_status" not in measure

    # feeder-Profil ist fuer Beratungsberichte nicht anwendbar
    _create_report("consulting", "feeder", draft_id, expected_status=422)
    # kein CSV fuer narrative Berichte
    csv = client.get(f"{ROOT}/feeding/reports/{advisor['id']}/csv", headers=HEADERS)
    assert csv.status_code == 422, csv.text
    # unbekannter Entwurf
    _create_report("consulting", "advisor", str(uuid4()), expected_status=404)


# ── target_actual: Soll-Ist-Auswertung je Planversion ───────────────────────

def _actual_plan() -> tuple[str, str]:
    suffix = uuid4().hex[:8]
    feed = client.post(f"{ROOT}/feed-catalog/feeds", headers=HEADERS, json={
        "artikel_nummer": f"REP040-{suffix}", "name": f"Berichtsfutter {suffix}",
        "art": "Grundfutter", "feed_kind": "forage", "approval_status": "approved"})
    assert feed.status_code == 201, feed.text
    feed_id = feed.json()["id"]
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"REP040 Gruppe {suffix}", "animal_count": 20, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    ration = client.post(f"{ROOT}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group.json()["id"], "name": f"REP040 Ration {suffix}",
        "snapshot": {"components": [
            {"feed_id": feed_id, "name": f"Berichtsfutter {suffix}", "kg_fm": 10.0}]}})
    assert ration.status_code == 201, ration.text
    version_id = ration.json()["latest_version_id"]
    for target, expected in (("in_review", "draft"), ("approved", "in_review")):
        assert client.post(f"{ROOT}/lifecycle/versions/{version_id}/transitions",
                           headers=HEADERS, json={"target_status": target,
                                                  "expected_status": expected}).status_code == 200
    plan = client.post(f"{ROOT}/feeding/plans/publish", headers=HEADERS, json={
        "source_ration_version_id": version_id, "animal_count": 20,
        "dosing_step_kg": "0.1", "rounding_mode": "nearest",
        "valid_from": str(date.today()), "reason": "Soll-Ist-Berichtsplan",
        "idempotency_key": f"rep040-{suffix}"})
    assert plan.status_code == 201, plan.text
    return plan.json()["id"], feed_id


def test_target_actual_report_aggregates_components_and_exports_csv() -> None:
    plan_version_id, feed_id = _actual_plan()
    actual = client.post(f"{ROOT}/feeding/actuals", headers=HEADERS, json={
        "plan_version_id": plan_version_id,
        "feeding_at": datetime.now(timezone.utc).isoformat(),
        "source": "manual", "source_ref": f"rep040-{uuid4()}",
        "cause_class": "dosing_error", "comment": "Nachdosiert",
        "idempotency_key": f"rep040-act-{uuid4()}",
        "components": [{"feed_id": feed_id, "actual_kg": "208"}]})
    assert actual.status_code == 201, actual.text

    farmer = _create_report("target_actual", "farmer", plan_version_id)
    content = farmer["content"]
    assert content["record_count"] == 1
    line = content["components"][0]
    assert line["feed_id"] == feed_id
    assert line["target_kg_sum"] == 200.0
    assert line["actual_kg_sum"] == 208.0
    assert line["delta_kg_sum"] == 8.0
    assert "cause_breakdown" not in content, "Ursachenverteilung nur im advisor-Profil"

    advisor = _create_report("target_actual", "advisor", plan_version_id)
    assert advisor["content"]["cause_breakdown"] == {"dosing_error": 1}
    assert advisor["content"]["source"]["plan_version_id"] == plan_version_id

    # Datenstand-Aenderung erzeugt neuen Bericht statt stiller Ueberschreibung
    more = client.post(f"{ROOT}/feeding/actuals", headers=HEADERS, json={
        "plan_version_id": plan_version_id,
        "feeding_at": datetime.now(timezone.utc).isoformat(),
        "source": "manual", "source_ref": f"rep040-{uuid4()}",
        "cause_class": "normal",
        "idempotency_key": f"rep040-act2-{uuid4()}",
        "components": [{"feed_id": feed_id, "actual_kg": "200"}]})
    assert more.status_code == 201, more.text
    fresh = _create_report("target_actual", "farmer", plan_version_id)
    assert fresh["id"] != farmer["id"]
    assert fresh["content"]["record_count"] == 2

    csv = client.get(f"{ROOT}/feeding/reports/{fresh['id']}/csv", headers=HEADERS)
    assert csv.status_code == 200, csv.text
    assert csv.text.splitlines()[0].startswith("feed_id;feed_name;n;target_kg_sum")
    _create_report("target_actual", "feeder", plan_version_id, expected_status=422)
    _create_report("target_actual", "farmer", str(uuid4()), expected_status=404)


# ── trend: Verlaufsbericht je Gruppe ────────────────────────────────────────

def test_trend_report_builds_deterministic_series_with_csv() -> None:
    suffix = uuid4().hex[:8]
    group = client.post(f"{ROOT}/lifecycle/groups", headers=HEADERS, json={
        "name": f"REP040 Trend {suffix}", "animal_count": 30, "feeding_system": "TMR",
        "profile_code": "fresh_cow", "pregnancy_status": "unknown"})
    assert group.status_code == 201, group.text
    group_id = group.json()["id"]
    for day, milk in (("2026-07-10", 31.0), ("2026-07-11", 32.5)):
        observation = client.post(f"{ROOT}/controlling/observations", headers=HEADERS, json={
            "group_id": group_id, "observation_date": day,
            "source": "manual", "source_ref": f"rep040-trend-{day}",
            "cow_count": 30, "actual_milk_kg_cow": milk,
            "actual_dmi_kg_cow": 22.0, "actual_fat_pct": 4.1,
            "actual_protein_pct": 3.4})
        assert observation.status_code == 201, observation.text

    farmer = _create_report("trend", "farmer", group_id)
    days = farmer["content"]["days"]
    assert [item["observation_date"] for item in days] == ["2026-07-10", "2026-07-11"]
    assert days[1]["actual_milk_kg_cow"] == 32.5
    again = _create_report("trend", "farmer", group_id)
    assert again["id"] == farmer["id"], "gleicher Datenstand => derselbe Bericht"

    advisor = _create_report("trend", "advisor", group_id)
    assert advisor["content_hash"] != farmer["content_hash"]
    assert "ration_version_no" in advisor["content"]["days"][0], \
        "advisor sieht Versionsmarker"

    csv = client.get(f"{ROOT}/feeding/reports/{farmer['id']}/csv", headers=HEADERS)
    assert csv.status_code == 200, csv.text
    assert csv.text.splitlines()[0].startswith("observation_date;")
    assert "2026-07-11" in csv.text
    _create_report("trend", "feeder", group_id, expected_status=422)
    _create_report("trend", "farmer", str(uuid4()), expected_status=404)
