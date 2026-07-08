"""UIX-090: SD-Studio Draft-Validierung — harte Sicherheitsregeln.

Reine Unit-Tests (kein DB): fuehre mit
`pytest tests/test_uix090_studio_validation.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""`.
"""
from __future__ import annotations

import pytest

from app.services.studio_validation import load_studio_catalog, validate_studio_draft

pytestmark = pytest.mark.unit

NATIVE = {"crm/customer-360", "finance/ar-open-item", "sales/sales-order"}


def _draft(**overrides):
    base = {
        "schemaVersion": 1,
        "id": "tenant/lieferanten-bewertung",
        "domain": "einkauf",
        "mode": "list",
        "title": "Lieferanten-Bewertung",
        "adapter": {"type": "native", "sourceId": "tenant/lieferanten-bewertung", "temporary": True},
        "actions": [],
    }
    base.update(overrides)
    return base


def _v(draft):
    return validate_studio_draft(draft, native_screen_ids=NATIVE)


def test_catalog_loads():
    cat = load_studio_catalog()
    assert cat["version"] == "2026-07"
    assert "create_activity" in cat["actions"]
    assert cat["actions"]["stornieren"]["forbiddenForAgents"] is True


def test_valider_draft_ohne_verletzung():
    draft = _draft(actions=[{"key": "create_activity", "dangerLevel": "safe"}])
    assert _v(draft) == []


def test_namensraum_ohne_tenant_prefix_verboten():
    assert any(x.startswith("namensraum:") for x in _v(_draft(id="lieferanten-bewertung")))


def test_native_kollision_verboten():
    assert any("kollision" in x for x in _v(_draft(id="crm/customer-360")))


def test_temporary_false_verboten():
    draft = _draft(adapter={"type": "native", "temporary": False})
    assert "adapter_temporary_false_verboten" in _v(draft)


def test_action_nicht_im_katalog_verboten():
    draft = _draft(actions=[{"key": "eigene_gefahr", "dangerLevel": "safe"}])
    assert any(x.startswith("action_nicht_im_katalog") for x in _v(draft))


def test_fremder_command_endpoint_verboten():
    draft = _draft(actions=[{"key": "mahnen", "commandEndpoint": "/api/v1/evil/backdoor"}])
    assert any(x.startswith("action_fremder_commandEndpoint") for x in _v(draft))


def test_danger_level_senken_verboten():
    # stornieren ist im Katalog high — auf safe senken ist verboten
    draft = _draft(actions=[{"key": "stornieren", "dangerLevel": "safe", "forbiddenForAgents": True}])
    assert any(x.startswith("action_dangerLevel_gesenkt") for x in _v(draft))


def test_danger_level_erhoehen_erlaubt():
    # create_activity safe -> moderate erhoehen ist ok
    draft = _draft(actions=[{"key": "create_activity", "dangerLevel": "moderate"}])
    assert not any(x.startswith("action_dangerLevel") for x in _v(draft))


def test_forbidden_for_agents_aufheben_verboten():
    draft = _draft(actions=[{"key": "stornieren", "dangerLevel": "high", "forbiddenForAgents": False}])
    assert any(x.startswith("action_forbiddenForAgents_aufgehoben") for x in _v(draft))


def test_pflichtfeld_fehlt_verboten():
    draft = _draft()
    del draft["title"]
    assert any(x == "pflichtfeld_fehlt:title" for x in _v(draft))


def test_ungueltiger_danger_level_gemeldet():
    draft = _draft(actions=[{"key": "create_activity", "dangerLevel": "apokalyptisch"}])
    assert any(x.startswith("action_ungueltiger_dangerLevel") for x in _v(draft))


def test_mehrere_verletzungen_werden_alle_gemeldet():
    draft = _draft(
        id="crm/customer-360",  # namensraum + kollision
        adapter={"temporary": False},  # temporary
        actions=[{"key": "stornieren", "dangerLevel": "safe", "forbiddenForAgents": False}],  # danger + forbidden
    )
    violations = _v(draft)
    assert len(violations) >= 4
