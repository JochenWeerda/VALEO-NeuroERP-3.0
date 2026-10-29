"""Batch 11/12 UI fixtures are exact canonical builder output, including permissions."""
import json
from pathlib import Path

from app.core.screen_definitions_listen import build_crm_kunden_liste
from app.core.screen_definitions_kontrolle_batch12 import build_batch12_kontroll_screen


def test_native_batch11_12_mount_fixtures_match_canonical_builders():
    root = Path(__file__).resolve().parents[1]
    fixture = root / "packages/frontend-web/src/__tests__/fixtures/native-batch11-12-builder-contracts.json"
    screens = [build_crm_kunden_liste(), build_batch12_kontroll_screen("admin/integrationen-quarantaene")]
    assert json.loads(fixture.read_text(encoding="utf-8")) == {screen["id"]: screen for screen in screens}
