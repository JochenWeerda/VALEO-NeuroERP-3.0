"""UIX mounts consume exact canonical schemas, never independently invented masks."""
import json
from pathlib import Path

from app.core.screen_definitions import get_screen_definition


def test_multi_domain_uix_fixtures_match_registered_builders():
    fixture = Path(__file__).resolve().parents[1] / (
        "packages/frontend-web/src/__tests__/fixtures/multi-domain-uix-builder-contracts.json"
    )
    schemas = json.loads(fixture.read_text(encoding="utf-8"))
    assert len(schemas) == 48
    for screen_id, schema in schemas.items():
        assert schema == get_screen_definition(screen_id), screen_id
