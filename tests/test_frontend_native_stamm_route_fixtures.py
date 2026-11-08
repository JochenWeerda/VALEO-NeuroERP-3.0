"""Routed Stamm list/detail fixtures mirror their canonical Python builders."""
import json
from pathlib import Path

from app.core.screen_definitions import build_agrar_saatgut_screen_definition
from app.core.screen_definitions_listen import (
    build_agrar_duenger_liste,
    build_agrar_saatgut_liste,
    build_banken_konten_liste,
    build_einkauf_lieferanten_liste,
)


def test_native_stamm_route_mount_fixtures_match_builders():
    root = Path(__file__).resolve().parents[1]
    fixture = root / "packages/frontend-web/src/__tests__/fixtures/native-stamm-route-builder-contracts.json"
    screens = [builder() for builder in (
        build_agrar_saatgut_liste,
        build_agrar_duenger_liste,
        build_einkauf_lieferanten_liste,
        build_banken_konten_liste,
        build_agrar_saatgut_screen_definition,
    )]
    assert json.loads(fixture.read_text(encoding="utf-8")) == {screen["id"]: screen for screen in screens}
    assert all(screen["mode"] == "list" for screen in screens[:4])
    assert screens[-1]["mode"] == "detail"
