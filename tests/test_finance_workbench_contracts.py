import json
from pathlib import Path

from app.core.screen_definitions import get_screen_definition
from app.core.screen_governance import validate_screen_definition
from app.services.studio_runtime_surface_contracts import validate_runtime_surface


def test_finance_workbenches_are_fixed_native_contracts_and_fixture_matches():
    ids = ("finance/bank-abgleich", "mahnwesen/mahnlauf")
    fixtures = json.loads(Path("packages/frontend-web/src/__tests__/fixtures/finance-workbenches.json").read_text(encoding="utf-8"))
    for screen_id, fixture in zip(ids, fixtures, strict=True):
        screen = get_screen_definition(screen_id)
        assert screen == fixture
        assert screen["specialized"] == {"type": "finance_workbench", "id": screen_id}
        assert not validate_runtime_surface(screen)
        assert not validate_screen_definition(screen)
        forged = {**screen, "specialized": {"type": "finance_workbench", "id": ids[1] if screen_id == ids[0] else ids[0]}}
        assert "fachoberflaechen_bindung_ungueltig" in validate_runtime_surface(forged)
