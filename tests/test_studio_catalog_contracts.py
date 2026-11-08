import pytest
from app.core.screen_definitions_domain_batch15 import build_workflow_flow_spine_studio_screen_definition
from app.services.studio_catalog_contracts import validate_flow_spine_catalog
from app.services.studio_validation import validate_studio_draft


def test_registered_definition_is_catalog_cockpit():
    d = build_workflow_flow_spine_studio_screen_definition()
    assert d["id"] == "workflow/flow-spine-studio" and d["mode"] == "cockpit"
    assert d["flowSpineCatalog"] == {"enabled": True, "warmWorkspaces": True}
    assert not d.get("tables") and not d.get("actions") and "dead-letter" not in repr(d)
    assert validate_flow_spine_catalog(d) == []


@pytest.mark.parametrize("metadata", [None, {}, {"enabled": False, "warmWorkspaces": True}, {"enabled": 1, "warmWorkspaces": True}, {"enabled": True, "warmWorkspaces": 1}, {"enabled": True, "warmWorkspaces": True, "url": "/evil"}, {"enabled": True, "warmWorkspaces": True, "custom": "x"}])
def test_invalid_metadata_rejected_by_draft_validator(metadata):
    d = build_workflow_flow_spine_studio_screen_definition()
    d["flowSpineCatalog"] = metadata
    assert "flow_spine_katalog_ungueltig" in validate_studio_draft(d, native_screen_ids=set())


@pytest.mark.parametrize("field,value", [("id", "tenant/other"), ("mode", "list")])
def test_catalog_restricted_to_registered_cockpit(field, value):
    d = build_workflow_flow_spine_studio_screen_definition()
    d[field] = value
    assert "flow_spine_katalog_maske_ungueltig" in validate_studio_draft(d, native_screen_ids=set())


def test_optional_contract_and_false_warmup():
    d = build_workflow_flow_spine_studio_screen_definition()
    d["flowSpineCatalog"]["warmWorkspaces"] = False
    assert validate_flow_spine_catalog(d) == []
    del d["flowSpineCatalog"]
    assert validate_flow_spine_catalog(d) == []
