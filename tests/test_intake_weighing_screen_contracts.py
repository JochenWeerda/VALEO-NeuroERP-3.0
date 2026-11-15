import json
from pathlib import Path

from app.core.screen_definitions_intake_weighing import (
    build_intake_registration, build_intake_quality, build_intake_queue,
    build_scale_list, build_scale_create, build_weighing_tickets,
)


def test_frontend_behavior_fixtures_match_current_studio_definitions():
    """UI tests must not stay green by rendering an obsolete schema snapshot."""
    path = Path(__file__).resolve().parents[1] / "packages/frontend-web/src/__tests__/fixtures/intake-weighing-screens.json"
    fixtures = json.loads(path.read_text(encoding="utf-8"))
    builders = (build_intake_registration, build_intake_quality, build_intake_queue,
                build_scale_list, build_scale_create, build_weighing_tickets)
    current = {definition["id"]: definition for definition in (builder() for builder in builders)}
    assert fixtures == current, "Regenerate UI fixtures from the current Studio builders and review behavior changes"


def test_eight_ids_use_fixed_domain_specialists_and_no_generic_table_substitution():
    screens = [build_intake_registration(), build_intake_quality(), build_intake_queue(),
               build_scale_list(), build_scale_list("waage/waagen-liste"), build_scale_create(),
               build_weighing_tickets(), build_weighing_tickets("waage/wiegungen-liste")]
    assert len({screen["id"] for screen in screens}) == 8
    for screen in screens:
        assert screen["adapter"]["temporary"] is False
        assert screen["specialized"] == {"type": "intake" if screen["id"].startswith("annahme/") else "weighing", "id": screen["id"]}
        assert not screen.get("tables")
        assert screen["layout"]["density"] == "expertDense"
        assert screen["layout"]["contextRail"] == "combined"
        assert screen["dataSources"] and screen["fields"] and screen["actions"]


def test_registration_preserves_upload_and_real_article_identity():
    screen = build_intake_registration()
    assert {"kennzeichen", "lieferant", "lieferscheinNr", "articleId", "artikel", "ankunftszeit", "prioritaet", "attachmentIds"} == {field["key"] for field in screen["fields"]}
    actions = {action["key"]: action for action in screen["actions"]}
    assert actions["register"]["inputFlow"]["submitEndpoint"] == "/api/v1/annahme/lkw-registrierung"
    assert actions["upload"]["inputFlow"]["submitEndpoint"] == "/api/v1/annahme/upload"
    assert all(action["forbiddenForAgents"] for action in screen["actions"])


def test_scale_creation_is_not_a_list_and_does_not_invent_required_values():
    screen = build_scale_create()
    assert screen["id"] == "waage/neu"
    assert screen["layout"]["floorplan"] == "wizard"
    assert {field["key"] for field in screen["fields"]} == {"standort", "typ", "max_kapazitaet"}
    assert all(field["required"] and "default" not in field for field in screen["fields"])
    assert screen["actions"][0]["inputFlow"]["submitEndpoint"] == "/api/v1/waage/waagen"


def test_tickets_use_canonical_weighing_and_calibration_uses_own_scale():
    tickets = build_weighing_tickets()
    assert tickets["dataSources"][0]["endpoint"] == "/api/v1/weighing-tickets?limit=100"
    actions = {action["key"]: action for action in tickets["actions"]}
    assert actions["close"]["inputFlow"] == {"kind": "humanForm", "submitEndpoint": "/api/v1/weighing-tickets/{entity_id}", "method": "PUT"}
    assert actions["allocate"]["inputFlow"]["submitEndpoint"].endswith("/allocate-contract")
    calibrate = next(action for action in build_scale_list()["actions"] if action["key"] == "calibrate")
    assert calibrate["inputFlow"] == {"kind": "humanForm", "submitEndpoint": "/api/v1/waage/waagen/{entity_id}/kalibrierung", "method": "PATCH"}


def test_surface_only_cannot_hide_unrelated_generic_actions():
    from app.services.studio_runtime_surface_contracts import validate_runtime_surface
    screen = build_intake_queue()
    assert validate_runtime_surface(screen) == []
    assert next(action for action in screen["actions"] if action["key"] == "repair")["surfaceOnly"] is True
    screen.pop("specialized")
    assert "fachaktion_bindung_ungueltig" in validate_runtime_surface(screen)
