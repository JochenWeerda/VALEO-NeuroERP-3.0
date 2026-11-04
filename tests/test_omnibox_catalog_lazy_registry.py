"""Omnibox must enumerate lazy native screens before tenant-specific publications."""
from app.api.v1.endpoints.mask_registry import _build_omnibox_catalog
from app.core import screen_definitions as screens
from app.core import stamm_object_page_parent as stamm
from app.core.screen_definitions_kontrolle import KONTROLLE_SCREEN_BUILDERS
from app.core.screen_definitions_stamm import STAMM_SCREEN_BUILDERS
from app.services import studio_draft_store as store


def test_lazy_native_catalog_is_complete_stable_and_tenant_isolated(monkeypatch):
    lazy_ids = set(STAMM_SCREEN_BUILDERS) - set(KONTROLLE_SCREEN_BUILDERS)
    assert lazy_ids
    registry = {key: value for key, value in screens._SCREEN_DEFINITIONS.items() if key not in lazy_ids}
    monkeypatch.setattr(screens, "_SCREEN_DEFINITIONS", registry)
    monkeypatch.setattr(screens, "_SCREEN_LIST_ROUTE", dict(screens._SCREEN_LIST_ROUTE))
    monkeypatch.setattr(screens, "_AGENT_SYNONYMS", {key: list(value) for key, value in screens._AGENT_SYNONYMS.items()})
    monkeypatch.setattr(stamm, "_STAMM_REGISTRY_DONE", False)
    publications = {
        "tenant-a": [{"id": "tenant/a", "title": "A"}],
        "tenant-b": [{"id": "tenant/b", "title": "B"}],
    }
    monkeypatch.setattr(store, "list_published_definitions", lambda tenant: publications[tenant])
    monkeypatch.setattr(store, "get_published_definition", lambda tenant, screen_id: next(
        (item for item in publications[tenant] if item["id"] == screen_id), None
    ))

    first = _build_omnibox_catalog("tenant-a")
    second = _build_omnibox_catalog("tenant-a")
    other = _build_omnibox_catalog("tenant-b")
    first_ids = [entry["screen_id"] for entry in first]
    assert set(first_ids) == set(registry) | {"tenant/a"}
    assert lazy_ids <= set(first_ids)
    assert len(first_ids) == len(set(first_ids))
    assert first == second
    other_ids = {entry["screen_id"] for entry in other}
    assert other_ids == set(registry) | {"tenant/b"}
    assert "tenant/b" not in first_ids
    assert "tenant/a" not in other_ids
