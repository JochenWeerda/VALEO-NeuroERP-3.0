import json
from pathlib import Path

from app.core.mask_family_versions import family_definition


def test_bestellvorschlag_frontend_fixture_entspricht_familienregister():
    path = Path(__file__).resolve().parents[1] / 'packages/frontend-web/src/__tests__/fixtures/bestellvorschlag-family.json'
    fixture = json.loads(path.read_text(encoding='utf-8'))
    assert fixture == {name: family_definition('bestellvorschlag', name) for name in ('lager', 'rohware', 'verkauf')}
