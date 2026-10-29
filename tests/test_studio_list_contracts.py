import json
from copy import deepcopy
from pathlib import Path

import pytest

from app.core.screen_definitions_listen import build_qualitaet_reklamationen_liste
from app.services.studio_list_contracts import validate_list_experience
from app.services.studio_validation import load_studio_catalog, validate_studio_draft


def definition():
    return deepcopy(build_qualitaet_reklamationen_liste())


def test_real_definition_and_frontend_fixture_match():
    source = definition()
    fixture = Path(__file__).resolve().parents[1] / "packages/frontend-web/src/__tests__/fixtures/complaint-studio.json"
    assert json.loads(fixture.read_text(encoding="utf-8")) == source
    assert validate_list_experience(source) == []


def mutate(d, case):
    x = d["listExperience"]
    if case == "malformed": x["searchFields"] = "nummer"
    elif case == "duplicate_search": x["searchFields"].append(x["searchFields"][0])
    elif case == "duplicate_export": x["export"]["columns"].append(deepcopy(x["export"]["columns"][0]))
    elif case == "duplicate_aggregate": x["aggregates"].append(deepcopy(x["aggregates"][0]))
    elif case == "reserved_search": x["searchFields"][0] = "__proto__"
    elif case == "reserved_export": x["export"]["columns"][0]["key"] = "Constructor"
    elif case == "reserved_aggregate": x["aggregates"][0]["key"] = "prototype"
    elif case == "workflow_missing": del x["workflowResume"]["detailScreen"]
    elif case == "unknown_notice": x["notice"]["aggregate"] = "missing"
    elif case == "unknown_insight": x["insightLines"][0]["variants"][0]["when"]["aggregate"] = "missing"
    elif case == "undeclared_search": x["searchFields"][0] = "missing"
    elif case == "undeclared_export": x["export"]["columns"][0]["key"] = "missing"
    elif case == "undeclared_aggregate": x["aggregates"][1]["conditions"][0]["field"] = "missing"
    elif case == "too_many_search": x["searchFields"] = [f"x{i}" for i in range(101)]
    elif case == "too_many_aggregates": x["aggregates"] = [{"key": f"x{i}", "label": "X", "conditions": []} for i in range(101)]
    elif case == "too_many_export": x["export"]["columns"] = [{"key": f"x{i}", "label": "X"} for i in range(101)]
    elif case == "too_many_conditions": x["aggregates"][0]["conditions"] = [{"field": "status", "op": "eq", "value": "neu"}] * 101
    elif case == "too_many_insights": x["insightLines"] = [{"label": "X", "variants": []}] * 101
    elif case == "too_many_variants": x["insightLines"][0]["variants"] = [{"text": "X"}] * 101
    elif case == "non_list": d["mode"] = "detail"
    elif case == "missing_table": d["tables"] = []
    elif case == "command_injection": x["commandEndpoint"] = "/danger"
    else: raise AssertionError(case)


CASES = ["malformed", "duplicate_search", "duplicate_export", "duplicate_aggregate", "reserved_search", "reserved_export", "reserved_aggregate", "workflow_missing", "unknown_notice", "unknown_insight", "undeclared_search", "undeclared_export", "undeclared_aggregate", "too_many_search", "too_many_aggregates", "too_many_export", "too_many_conditions", "too_many_insights", "too_many_variants", "non_list", "missing_table", "command_injection"]


@pytest.mark.parametrize("case", CASES)
def test_invalid_metadata_rejected_by_contract_and_studio_draft(case):
    source = definition()
    mutate(source, case)
    violations = validate_list_experience(source)
    assert violations
    draft_violations = validate_studio_draft(source, native_screen_ids=set(), catalog=load_studio_catalog())
    assert set(violations) <= set(draft_violations)
