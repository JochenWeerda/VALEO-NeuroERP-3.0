"""Studio audit views open their registered workspace before selecting a draft."""
from pathlib import Path
import pytest

from app.core.screen_definitions import (
    SCREEN_DEFINITION_BUILDERS,
    get_screen_list_route,
)


@pytest.fixture(autouse=True)
def _enable_dev_token():
    """Registry-only checks need neither an HTTP app nor an auth double."""
    yield


@pytest.fixture(scope="session", autouse=True)
def _seed_contract_test_tenants():
    """These navigation checks do not use a database."""
    yield


def test_studio_audit_views_use_registered_workspace():
    for screen in ("platform/studio-history", "platform/studio-history-diff"):
        assert get_screen_list_route(screen) == "/admin/screen-studio"
    route_tree = Path("packages/frontend-web/src/app/routing/route-tree.gen.tsx").read_text(encoding="utf-8")
    assert 'path: "admin/screen-studio"' in route_tree


def test_every_native_screen_retains_an_omnibox_destination():
    missing = [screen for screen in SCREEN_DEFINITION_BUILDERS
               if not get_screen_list_route(screen)]
    assert missing == []
