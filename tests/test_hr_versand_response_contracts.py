"""Response schemas match command results and guarded legacy routes."""
import pytest
from fastapi import FastAPI
from pydantic import ValidationError

from app.api.v1.endpoints import training, versandprofile


@pytest.mark.parametrize("replayed", [False, True])
def test_command_results_preserve_all_fields(replayed):
    hr = {"success": True, "replayed": replayed, "entity_id": "row-1", "auditEntryId": "audit-1", "outboxEventId": "event-1"}
    shipping = {"success": True, "replayed": replayed, "profile_id": "profile-1", "auditEntryId": "audit-1"}
    assert training.HrDeleteResult.model_validate(hr).model_dump() == hr
    assert versandprofile.VersandprofilDeactivateResult.model_validate(shipping).model_dump() == shipping
    with pytest.raises(ValidationError):
        training.HrDeleteResult.model_validate({"success": True})
    with pytest.raises(ValidationError):
        versandprofile.VersandprofilDeactivateResult.model_validate({"success": True})


def test_openapi_documents_actual_command_and_legacy_contracts():
    app = FastAPI()
    app.include_router(training.router)
    app.include_router(versandprofile.router)
    paths = app.openapi()["paths"]
    for collection in ("assignments", "qualifications", "onboarding/runs"):
        path = f"/training/{collection}/{{item_id}}"
        assert "409" in paths[path]["delete"]["responses"]
        assert "200" not in paths[path]["delete"]["responses"]
        schema = paths[path + "/actions/loeschen"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
        assert schema["$ref"].endswith("/HrDeleteResult")
    path = "/logistik/versand/profile/{profil_nr}"
    assert "410" in paths[path]["delete"]["responses"]
    assert "200" not in paths[path]["delete"]["responses"]
    schema = paths["/logistik/versand/profile/{profile_id}/actions/deactivate"]["post"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert schema["$ref"].endswith("/VersandprofilDeactivateResult")
