from app.core.native_screen_aliases import build_native_alias, NATIVE_SCREEN_ALIASES
from app.core.screen_definitions import get_screen_definition
from app.services.made_by_studio_gates import _gate_e_runtime_candidates


def test_existing_replacements_share_actual_canonical_sources_and_runtime():
    for old, target in NATIVE_SCREEN_ALIASES.items():
        original = get_screen_definition(target)
        alias = build_native_alias(old)
        assert alias["id"] == old and alias["adapter"]["sourceId"] == old
        assert alias["dataSources"] == original["dataSources"]
        assert alias["actions"] == original["actions"]
        assert target in _gate_e_runtime_candidates(old)
    assert all("/api/v1/verkauf/kunden" not in source["endpoint"]
               for source in build_native_alias("verkauf/rechnungen")["dataSources"])
