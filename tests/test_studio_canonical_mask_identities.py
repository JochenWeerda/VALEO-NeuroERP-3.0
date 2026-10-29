from pathlib import Path

import pytest

from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(("old_id", "canonical_id", "page"), [
    ("finance/bankkonten-stamm", "finance/bankkonto", "finance/bankkonten-stamm.tsx"),
    ("finance/kreditoren-stamm", "finance/kreditor", "finance/kreditoren-stamm.tsx"),
    ("qualitaet/reklamation-detail", "qualitaet/reklamation", "qualitaet/reklamation-detail.tsx"),
])
def test_route_uses_one_canonical_screen_definition(old_id, canonical_id, page):
    assert old_id not in SCREEN_DEFINITION_BUILDERS
    assert get_screen_definition(old_id) is None
    assert canonical_id in SCREEN_DEFINITION_BUILDERS
    assert get_screen_definition(canonical_id)["id"] == canonical_id
    source = (ROOT / "packages/frontend-web/src/pages" / page).read_text(encoding="utf-8")
    assert "createStammNativeDetailPage" in source
    assert f"'{canonical_id}'" in source
    assert "-legacy" in source


def test_complaint_list_uses_its_functional_studio_definition():
    assert "qualitaet/reklamationen" not in SCREEN_DEFINITION_BUILDERS
    assert get_screen_definition("qualitaet/reklamationen") is None
    definition = get_screen_definition("qualitaet/reklamationen-liste")
    assert definition["id"] == "qualitaet/reklamationen-liste"
    assert definition["dataSources"][0]["endpoint"] == "/api/v1/qualitaet/reklamationen"
    assert definition["listExperience"]["workflowResume"]["resumeNodeId"] == "complaint"
    source = (ROOT / "packages/frontend-web/src/pages/qualitaet/reklamationen.tsx").read_text(encoding="utf-8")
    assert 'screenId="qualitaet/reklamationen-liste"' in source
    assert "NativeListPage" in source
