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
SD_NAV_ONLY = {
    "logistik/verladung": "/verladung/lkw-beladung",
}


def generator():
    spec = importlib.util.spec_from_file_location("tested_mask_map", ROOT / "scripts/generate_mcp_mask_action_map.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("screen", [*RESET_PAGES, *NAV_PAGES, *SD_NAV_ONLY])
def test_verified_local_action_is_not_reported_as_missing_http_mutation(screen):
    by_id = {entry["mask_action_id"]: entry for entry in generator().build_map()["mappings"]}
    entry = by_id[f"mask:{screen}:neu"]
    assert entry["coverage"] == "local_ui"
    assert entry["mcp_tool_id"] is None
    assert entry["command_endpoint"] is None
    assert entry["local_effect"] == ("form_reset" if screen in RESET_PAGES else "navigation")


def test_verladung_neu_is_screen_definition_navigation_only():
    from app.core.screen_definitions_capture import build_logistik_verladung_screen_definition

    action = next(a for a in build_logistik_verladung_screen_definition()["actions"] if a["key"] == "neu")
    assert action.get("navigationRoute") == SD_NAV_ONLY["logistik/verladung"]
    assert not action.get("commandEndpoint")
    assert not action.get("command")


def test_supplier_neue_bestellung_is_navigation_only_local_ui():
    from app.core.screen_definitions import get_screen_definition

    by_id = {entry["mask_action_id"]: entry for entry in generator().build_map()["mappings"]}
    entry = by_id["mask:einkauf/supplier:neue_bestellung"]
    assert entry["coverage"] == "local_ui"
    assert entry["local_effect"] == "navigation"
    assert entry["mcp_tool_id"] is None
    assert entry["command_endpoint"] is None
    action = next(
        a for a in get_screen_definition("einkauf/supplier")["actions"] if a["key"] == "neue_bestellung"
    )
    assert action.get("navigationRoute") == "/einkauf/bestellungen/neu"
    assert not action.get("commandEndpoint")


def test_postfaecher_neu_is_form_reset_local_ui():
    from app.core.screen_definitions_capture import build_admin_postfaecher_screen_definition

    by_id = {entry["mask_action_id"]: entry for entry in generator().build_map()["mappings"]}
    entry = by_id["mask:admin/postfaecher:neu"]
    assert entry["coverage"] == "local_ui"
    assert entry["local_effect"] == "form_reset"
    assert entry["mcp_tool_id"] is None
    assert entry["command_endpoint"] is None
    action = next(
        a for a in build_admin_postfaecher_screen_definition()["actions"] if a["key"] == "neu"
    )
    assert not action.get("commandEndpoint")
    assert "leert" in (action.get("stubReason") or "").lower()


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
    missing_tenant = (
        "fuhrpark/ausgehende-dokumente:speichern",
        "fuhrpark/rechnungen:speichern",
        "fuhrpark/terminarten:speichern",
        "fuhrpark/fahrzeug-stamm:speichern",
        "fuhrpark/fahrzeug-stamm:loeschen",
    )
    for mask_action in missing_tenant:
        assert by_id[f"mask:{mask_action}"]["coverage"] == "blocked_missing_tenant"
    assert by_id["mask:personal/onboarding:speichern"]["coverage"] == "mapped"
    assert by_id["mask:personal/qualifikationen:speichern"]["coverage"] == "mapped"
    assert by_id["mask:personal/schulungen:speichern"]["coverage"] == "mapped"
    assert by_id["mask:personal/bewerbungen:speichern"]["coverage"] == "mapped"
    assert by_id["mask:personal/einwilligungserklaerungen:anlegen"]["coverage"] == "mapped"
    assert by_id["mask:admin/postfaecher:speichern"]["coverage"] == "mapped"
    assert by_id["mask:finance/payment-run:freigeben"]["coverage"] == "open_high"
    assert data["fin_close"]["status"] == "blocked_adr_076"
    assert by_id["mask:auswertungen/sanktionspruefung-kunden:check"]["coverage"] == "mapped"
    assert by_id["mask:logistik/frachttabellen:anlegen"]["coverage"] == "mapped"
    assert by_id["mask:auswertungen/bonus-berechnung:calculate"]["coverage"] == "mapped"
    assert by_id["mask:auswertungen/abfrage-center:import"]["coverage"] == "mapped"
    assert by_id["mask:logistik/verladung:neu"]["coverage"] == "local_ui"
    assert by_id["mask:einkauf/supplier:neue_bestellung"]["coverage"] == "local_ui"
    assert by_id["mask:admin/postfaecher:neu"]["coverage"] == "local_ui"
    assert by_id["mask:logistik/tourenplanung:anlegen"]["coverage"] == "mapped"
    assert by_id["mask:einkauf/purchase-order:speichern"]["coverage"] == "mapped"
    assert data["stats"]["by_coverage"].get("blocked_no_endpoint", 0) == 0
    assert data["stats"]["by_coverage"]["blocked_missing_tenant"] == 5
    assert data["stats"]["by_coverage"]["local_ui"] == 13
    assert data["stats"]["mask_actions_considered"] == len(by_id)
    assert data["stats"]["mask_mutations_considered"] == len(by_id) - 13
    assert "blocked_missing_tenant 5" in data["classification_notes"]


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
