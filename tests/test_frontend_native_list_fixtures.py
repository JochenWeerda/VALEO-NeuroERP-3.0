"""The UI mount fixtures must remain exact projections of the real builders."""
import json
from pathlib import Path

from app.core.screen_definitions_listen import (
    build_agrar_duenger_liste,
    build_agrar_bodenproben_liste,
    build_agrar_ernte_liste,
    build_einkauf_angebote_liste,
    build_einkauf_lieferanten_liste,
)


def test_native_list_mount_fixtures_match_canonical_builders():
    root = Path(__file__).resolve().parents[1]
    fixture = root / "packages/frontend-web/src/__tests__/fixtures/native-list-builder-contracts.json"
    expected = [builder() for builder in (
        build_einkauf_angebote_liste, build_einkauf_lieferanten_liste, build_agrar_duenger_liste,
    )]
    assert json.loads(fixture.read_text(encoding="utf-8")) == {screen["id"]: screen for screen in expected}


def test_native_agrar_list_mount_fixtures_match_canonical_builders():
    root = Path(__file__).resolve().parents[1]
    fixture = root / "packages/frontend-web/src/__tests__/fixtures/native-agrar-list-builder-contracts.json"
    expected = [build_agrar_bodenproben_liste(), build_agrar_ernte_liste()]
    assert json.loads(fixture.read_text(encoding="utf-8")) == {screen["id"]: screen for screen in expected}