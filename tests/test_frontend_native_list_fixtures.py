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

def test_native_final_list_mount_fixtures_match_canonical_builders():
    from app.core.screen_definitions_cluster_futter import build_futter_einzel_liste
    from app.core.screen_definitions_listen import (
        build_agrar_biostimulanzien_liste, build_agrar_psm_sachkunde_register_liste,
        build_agrar_saatgut_sortenregister_liste, build_agrar_feldbuch_schlagkartei_liste,
        build_futtermittel_mischfuttermittel_liste, build_zertifikate_liste,
    )
    builders = (build_agrar_biostimulanzien_liste, build_agrar_psm_sachkunde_register_liste,
                build_agrar_saatgut_sortenregister_liste, build_agrar_feldbuch_schlagkartei_liste,
                build_futtermittel_mischfuttermittel_liste, build_zertifikate_liste, build_futter_einzel_liste)
    screens = [builder() for builder in builders]
    fixture = Path(__file__).resolve().parents[1] / 'packages/frontend-web/src/__tests__/fixtures/native-final-list-builder-contracts.json'
    assert json.loads(fixture.read_text(encoding='utf-8')) == {screen['id']: screen for screen in screens}
