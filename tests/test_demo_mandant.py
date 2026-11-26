"""Demo-Mandant anlegen und wieder löschen gegen valeo_probe (M7)."""
from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


def _demo_url() -> str | None:
    return os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")


@pytest.fixture()
def demo_db_url():
    url = _demo_url()
    if not url:
        pytest.skip("TEST_DATABASE_URL/DATABASE_URL fehlt — Demo-Mandant braucht valeo_probe")
    if "valeo_probe" not in url and os.environ.get("ALLOW_DEMO_MANDANT_ANY_DB") != "1":
        pytest.skip("Demo-Mandant-Test nur gegen valeo_probe (oder ALLOW_DEMO_MANDANT_ANY_DB=1)")
    return url


def test_demo_mandant_anlegen_und_loeschen(demo_db_url, monkeypatch):
    monkeypatch.setenv("DATABASE_URL", demo_db_url)
    monkeypatch.setenv("PGAPPNAME", "agent:test-demo-mandant")

    import scripts.demo_mandant as demo

    assert demo.main(["--loeschen"]) == 0
    assert demo.main(["--anlegen"]) == 0
    assert demo.main(["--status"]) == 0
    with demo._session() as db:
        assert demo.vorhanden(db) is True
    assert demo.main(["--loeschen"]) == 0
    with demo._session() as db:
        assert demo.vorhanden(db) is False
