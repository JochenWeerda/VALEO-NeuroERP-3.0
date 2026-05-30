from __future__ import annotations

from app.api.v1.endpoints import admin_suite


def test_admin_suite_readiness_never_promotes_config_to_live_ready(monkeypatch):
    monkeypatch.setattr(
        admin_suite,
        "build_integration_bootstrap_summary",
        lambda: {
            "ready_count": 5,
            "partial_count": 0,
            "disabled_count": 0,
            "required_blockers": [],
        },
    )

    result = admin_suite.build_admin_suite_readiness()
    items = {item.key: item for item in result.evidence}

    assert result.status == "warning"
    assert result.ready_count == 0
    assert result.score == 0
    assert items["connectors"].status == "warning"
    assert "Live-Evidenz steht noch aus" in items["connectors"].evidence
    assert items["system_status"].status == "unchecked"


def test_admin_suite_readiness_surfaces_required_integration_blockers(monkeypatch):
    monkeypatch.setattr(
        admin_suite,
        "build_integration_bootstrap_summary",
        lambda: {
            "ready_count": 2,
            "partial_count": 1,
            "disabled_count": 2,
            "required_blockers": ["oidc"],
        },
    )

    result = admin_suite.build_admin_suite_readiness()
    items = {item.key: item for item in result.evidence}

    assert result.status == "blocked"
    assert result.blocked_count == 1
    assert items["connectors"].status == "blocked"
    assert "Pflichtblocker: oidc" in items["connectors"].details


def test_admin_suite_readiness_router_is_registered():
    from app.api.v1.api import api_router

    paths = {getattr(route, "path", "") for route in api_router.routes}

    assert "/admin-suite/readiness" in paths
