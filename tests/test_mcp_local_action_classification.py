"""Local reset/navigation is not a missing business mutation endpoint."""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RESET_PAGES = {
    "personal/bewerbungen": "personal/bewerbungen.tsx",
    "personal/einwilligungserklaerungen": "personal/einwilligungserklaerungen.tsx",
    "personal/onboarding": "personal/onboarding.tsx",
    "personal/qualifikationen": "personal/qualifikationen.tsx",
    "personal/schulungen": "personal/schulungen.tsx",
    "fuhrpark/ausgehende-dokumente": "fuhrpark/ausgehende-belege-dokumente.tsx",
    "fuhrpark/rechnungen": "fuhrpark/fuhrpark-rechnungen.tsx",
    "fuhrpark/terminarten": "fuhrpark/fuhrpark-stammdaten.tsx",
}
NAV_PAGES = {
    "fuhrpark/fahrzeuge": ("fuhrpark/fahrzeuge.tsx", "/fuhrpark/fahrzeug/neu"),
    "transporte/fahrer": ("transporte/fahrer-liste.tsx", "/transporte/fahrer/neu"),
}


def generator():
    spec = importlib.util.spec_from_file_location("tested_mask_map", ROOT / "scripts/generate_mcp_mask_action_map.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("screen", [*RESET_PAGES, *NAV_PAGES])
def test_verified_local_action_is_not_reported_as_missing_http_mutation(screen):
    by_id = {entry["mask_action_id"]: entry for entry in generator().build_map()["mappings"]}
    entry = by_id[f"mask:{screen}:neu"]
    assert entry["coverage"] == "local_ui"
    assert entry["mcp_tool_id"] is None
    assert entry["command_endpoint"] is None
    assert entry["local_effect"] == ("form_reset" if screen in RESET_PAGES else "navigation")


@pytest.mark.parametrize("screen,page", list(RESET_PAGES.items()))
def test_local_reset_evidence_has_no_business_operation(screen, page):
    source = (ROOT / "packages/frontend-web/src/pages" / page).read_text(encoding="utf-8")
    branch = re.search(r"if \(key === 'neu'\) \{(.*?)\}", source, re.S)
    assert branch, screen
    assert re.sub(r"\s+", "", branch.group(1)) == "leeren()return", screen


@pytest.mark.parametrize("screen,evidence", list(NAV_PAGES.items()))
def test_local_navigation_evidence_opens_the_create_form(screen, evidence):
    page, route = evidence
    source = (ROOT / "packages/frontend-web/src/pages" / page).read_text(encoding="utf-8")
    if screen == "fuhrpark/fahrzeuge":
        assert f"'vehicle.create': () => navigate('{route}')" in source
    else:
        branch = re.search(r"if \(key === 'neu'\) \{(.*?)\}", source, re.S)
        assert branch
        assert re.sub(r"\s+", "", branch.group(1)) == f"navigate('{route}')return"


def test_unknown_new_action_stays_an_open_business_contract(monkeypatch):
    module = generator()
    load = module._load_json
    def catalog_with_unknown(path):
        catalog = load(path)
        catalog["actions"].append({"id": "mask:personal/unknown:neu", "domain": "personal", "source": {"actionKey": "neu"}})
        return catalog
    monkeypatch.setattr(module, "_load_json", catalog_with_unknown)
    entry = next(m for m in module.build_map()["mappings"] if m["mask_action_id"] == "mask:personal/unknown:neu")
    assert entry["coverage"] == "open_medium"
    assert entry["mcp_tool_id"] is None


def test_actual_writes_and_finance_gaps_remain_visible():
    data = generator().build_map()
    by_id = {m["mask_action_id"]: m for m in data["mappings"]}
    for screen in RESET_PAGES:
        key = "anlegen" if screen == "personal/einwilligungserklaerungen" else "speichern"
        assert by_id[f"mask:{screen}:{key}"]["coverage"] == "blocked_no_endpoint"
    assert by_id["mask:finance/payment-run:freigeben"]["coverage"] == "open_high"
    assert data["fin_close"]["status"] == "blocked_adr_076"
    assert data["stats"]["by_coverage"]["blocked_no_endpoint"] == 21
    assert data["stats"]["by_coverage"]["local_ui"] == 10
    assert data["stats"]["mask_actions_considered"] == len(by_id)
    assert data["stats"]["mask_mutations_considered"] == len(by_id) - 10
    assert "blocked_no_endpoint 21" in data["classification_notes"]


def test_new_http_binding_cannot_silently_remain_classified_local(monkeypatch):
    module = generator()
    load = module._load_json
    def changed_catalog(path):
        catalog = load(path)
        action = next(a for a in catalog["actions"] if a["id"] == "mask:personal/bewerbungen:neu")
        action["source"]["commandEndpoint"] = "/api/v1/new-business-command"
        return catalog
    monkeypatch.setattr(module, "_load_json", changed_catalog)
    with pytest.raises(ValueError, match="gained a commandEndpoint"):
        module.build_map()
