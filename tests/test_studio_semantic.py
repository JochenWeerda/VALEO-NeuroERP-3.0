"""Catalog resolution, exact Domain-Service calculation and fail-closed preview."""
from copy import deepcopy
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.core.studio_release import profile_errors
from app.services.studio_semantic import (
    CONTRACT, DialogueTurn, HarvestPreviewIn, StudioDialogueIn, dialogue,
    preview, reference_definition, semantic_catalog,
)
from app.services.studio_validation import validate_studio_draft
from test_meridian_screen_studio_persistence import studio_db, _client, _HEADERS_A


def sample(**changes):
    return HarvestPreviewIn(**dict({"delivered_quantity_kg": 25000,
                                   "unit_price_eur_per_ton": 220, "vat_rate_percent": 7,
                                   "impurities_free_pct": 2, "impurities_pct": 3,
                                   "freight_costs": 100, "weighing_fees": 15, "windage_pct": 0, "moisture_pct": 0,
                                   "hl_weight_kg_per_hl": 76, "storage_shrinkage_pct": 0,
                                   "storage_fee_per_month": 0, "storage_months": 0}, **changes))


def test_fachgespraech_requires_explicit_manual_scope_and_preserves_decisions():
    turns = [DialogueTurn(role="user", content="Getreideannahme mit Feuchte und Abrechnungspreis")]
    first = dialogue(StudioDialogueIn(turns=turns))
    assert not first.ready and "Waage" in first.message
    turns.extend([DialogueTurn(role="assistant", content=first.message), DialogueTurn(role="user", content="Manuell reicht fuer die Testmaske.")])
    second = dialogue(StudioDialogueIn(turns=turns, weighing="manual"))
    assert not second.ready and "bestaetigen" in second.message
    ready = dialogue(StudioDialogueIn(turns=turns, weighing="manual", accept_preview_limits=True))
    assert ready.ready and ready.mode == "catalog_guided"
    assert ready.definition["studioSemantic"]["dialogue"] == [turn.model_dump() for turn in turns]
    assert validate_studio_draft(ready.definition, native_screen_ids=set()) == []
    assert "semantic_preview_not_a_release_profile" in profile_errors(ready.definition)


@pytest.mark.parametrize("text,weighing", [("Ich will ein unbekanntes Fachmodul", "manual"), ("Getreideannahme", "automatic")])
def test_unknown_or_unavailable_contract_cannot_generate_bindings(text, weighing):
    result = dialogue(StudioDialogueIn(turns=[DialogueTurn(role="user", content=text)], weighing=weighing, accept_preview_limits=True))
    assert not result.ready and result.definition is None


def test_every_catalog_field_is_an_actual_versioned_domain_input():
    from modules.agrar.services.harvest_calculator import HarvestCalculationInput
    fields = semantic_catalog()["fields"]
    assert {field["key"] for field in fields} == set(HarvestPreviewIn.model_fields)
    assert all(field["contract"].startswith(CONTRACT + "#") for field in fields)
    assert set(HarvestPreviewIn.model_fields) - {"vat_rate_percent"} <= set(HarvestCalculationInput.__dataclass_fields__)


def test_real_domain_calculation_has_conditional_positions_and_exact_money():
    result = preview(sample())
    assert len(result["positions"]) == 12
    assert 15 not in {row["position_number"] for row in result["positions"]}
    full = preview(sample(windage_pct=1, storage_shrinkage_pct=0.5))
    assert len(full["positions"]) == 14
    assert result["total_net_amount_eur"] == Decimal("5330.00")
    assert result["total_vat_amount_eur"] == Decimal("373.10")
    assert result["total_gross_amount_eur"] == Decimal("5703.10")
    assert result["business_effect"] == result["external_effect"] == "none"
    assert preview(sample()) == result


@pytest.mark.parametrize("changes", [{"delivered_quantity_kg": 0}, {"moisture_pct": 101}, {"windage_pct": -1},
                                   {"vat_rate_percent": "NaN"}, {"unit_price_eur_per_ton": "Infinity"},
                                   {"storage_months": 1.5}, {"tenant_id": "foreign"}, {"endpoint": "https://evil.invalid"}])
def test_invalid_values_and_adapter_injections_are_rejected(changes):
    with pytest.raises(ValidationError):
        sample(**changes)


def test_negative_settlement_cannot_be_presented_as_successful_preview():
    with pytest.raises(ValueError, match="Kosten"):
        preview(sample(unit_price_eur_per_ton=0))


def test_optional_catalog_fields_can_be_removed_but_required_inputs_cannot():
    definition = reference_definition([])
    definition["fields"] = [field for field in definition["fields"] if field["required"]]
    assert validate_studio_draft(definition, native_screen_ids=set()) == []
    definition["fields"].pop()
    assert "semantic_fields_not_in_contract" in validate_studio_draft(definition, native_screen_ids=set())


@pytest.mark.parametrize("free", [0, 2, 3])
def test_position_label_matches_the_explicit_impurities_allowance(free):
    result = preview(sample(impurities_free_pct=free))
    row = next(row for row in result["positions"] if row["position_number"] == 20)
    assert row["description"] == f"Besatz {free}% frei"
    assert f"- {free}%" in row["calculation_formula"]


@pytest.mark.parametrize("mutation", ["field", "type", "required", "contract", "source", "action", "output", "decision"])
def test_semantic_contract_cannot_be_forged_by_direct_definition_edit(mutation):
    definition = deepcopy(reference_definition([]))
    if mutation == "field": definition["fields"].append({"key": "invented", "type": "text"})
    elif mutation == "type": definition["fields"][0]["type"] = "text"
    elif mutation == "required": definition["fields"][0]["required"] = False
    elif mutation == "contract": definition["studioSemantic"]["contract"] = "unknown.v1"
    elif mutation == "source": definition["fields"][0]["optionsSource"] = {"endpoint": "/api/v1/einkauf/lieferanten"}
    elif mutation == "action": definition["actions"] = [{"key": "create_activity", "dangerLevel": "safe"}]
    elif mutation == "output": definition["tables"][0]["columns"][0]["key"] = "invented"
    elif mutation == "decision": definition["studioSemantic"]["decisions"]["weighing"] = "automatic"
    assert any(error.startswith("semantic_") for error in validate_studio_draft(definition, native_screen_ids=set()))


@pytest.mark.parametrize("roles,expected", [([], 403), (["EINKAUF_LESEN"], 403), (["EINKAUF_BEARBEITEN"], 200)])
def test_existing_roles_protect_dialogue_and_calculation(roles, expected):
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from app.auth.deps import get_current_user
    from app.core.tenant import get_tenant_id
    from app.api.v1.endpoints.studio_drafts import router
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "synthetic-editor", "roles": roles}
    app.dependency_overrides[get_tenant_id] = lambda: "own"
    client = TestClient(app)
    assert client.post("/studio/dialogue", json={"turns": [{"role": "user", "content": "Getreideannahme"}]}).status_code == expected
    assert client.post("/studio/harvest-preview", json=sample().model_dump(mode="json")).status_code == expected


@pytest.mark.integration
def test_sql_semantic_draft_preserves_dialogue_and_idempotency_but_blocks_release(studio_db):
    from uuid import uuid4
    from app.services.studio_draft_store import get_draft, count_history
    client = _client()
    definition = reference_definition([DialogueTurn(role="user", content="Manuelle Getreideprobe vereinbart.")])
    payload = {"definition": definition, "idempotency_key": str(uuid4())}
    path = "/api/v1/studio/drafts"
    saved = client.post(path, headers=_HEADERS_A, json=payload)
    assert saved.status_code == 200, saved.text
    record = saved.json()
    assert client.post(path, headers=_HEADERS_A, json=payload).json() == record
    assert count_history(record["tenant_id"], record["id"]) == 1
    loaded = get_draft(record["tenant_id"], record["id"])
    assert loaded["definition"]["studioSemantic"]["dialogue"] == definition["studioSemantic"]["dialogue"]
    definition["title"] += " – ueberarbeitet"
    changed = client.put(path + "/" + record["id"], headers=_HEADERS_A, json={
        "definition": definition, "expected_revision": record["revision"], "idempotency_key": str(uuid4())})
    assert changed.status_code == 200, changed.text
    assert changed.json()["revision"] != record["revision"]
    assert count_history(record["tenant_id"], record["id"]) == 2
    assert "semantic_preview_not_a_release_profile" in profile_errors(changed.json()["definition"])
