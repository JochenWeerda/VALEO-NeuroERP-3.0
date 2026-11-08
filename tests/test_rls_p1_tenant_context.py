"""RLS-Plan P1: Mandantenkontext ist fail-closed, Hintergrundarbeit nennt ihren Kontext.

Ohne Mandant gibt es keinen stillen Rueckfall auf DEFAULT_TENANT_ID mehr. Worker arbeiten je
Mandant in ``tenant_scope`` (Mandanten aus ``domain_shared.tenants``) oder markieren bewusst
mandantenuebergreifende Arbeit mit ``cross_tenant_scope``.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.core import tenant_context as tc

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]


def test_ohne_kontext_kein_standardmandant():
    assert tc.current_tenant_or_none() is None
    with pytest.raises(tc.TenantContextMissing):
        tc.get_current_tenant_id()


def test_leerer_mandant_wird_nicht_gesetzt():
    with pytest.raises(tc.TenantContextMissing):
        tc.set_current_tenant_id("  ")


def test_tenant_scope_setzt_und_stellt_wieder_her():
    with tc.tenant_scope("t-1", "test"):
        assert tc.get_current_tenant_id() == "t-1"
        with tc.tenant_scope("t-2", "test"):
            assert tc.get_current_tenant_id() == "t-2"
        assert tc.get_current_tenant_id() == "t-1"
    assert tc.current_tenant_or_none() is None


def test_scope_braucht_grund():
    with pytest.raises(ValueError):
        with tc.tenant_scope("t-1", ""):
            pass
    with pytest.raises(ValueError):
        with tc.cross_tenant_scope(""):
            pass


def test_cross_tenant_scope_loescht_den_mandanten():
    with tc.tenant_scope("t-1", "test"):
        with tc.cross_tenant_scope("outbox"):
            assert tc.current_tenant_or_none() is None
            assert tc.cross_tenant_reason() == "outbox"
            with pytest.raises(tc.TenantContextMissing):
                tc.get_current_tenant_id()
        assert tc.get_current_tenant_id() == "t-1"
        assert tc.cross_tenant_reason() is None


def test_tenant_scope_beendet_einen_cross_tenant_scope():
    with tc.cross_tenant_scope("liste"):
        with tc.tenant_scope("t-1", "test"):
            assert tc.cross_tenant_reason() is None
        assert tc.cross_tenant_reason() == "liste"


def test_for_each_tenant_isoliert_fehler(monkeypatch):
    from app.core import tenant_registry

    class _Session:
        def close(self):
            pass

    monkeypatch.setattr("app.core.database.SessionLocal", lambda: _Session())
    monkeypatch.setattr(tenant_registry, "active_tenant_ids", lambda db: ["a", "b", "c"])
    seen = []

    def work(tenant_id):
        seen.append(tc.get_current_tenant_id())
        if tenant_id == "b":
            raise RuntimeError("kaputt")
        return tenant_id.upper()

    result = tenant_registry.for_each_tenant("test", work)
    assert seen == ["a", "b", "c"]
    assert result["a"] == "A" and result["c"] == "C"
    assert isinstance(result["b"], RuntimeError)
    assert tc.current_tenant_or_none() is None


# --- Vertrag: Worker ---------------------------------------------------------------------

WORKER_FILES = sorted((ROOT / "app" / "workers").glob("*.py")) + [ROOT / "app" / "services" / "scheduler_service.py"]
OPENS_DB = re.compile(r"\bSessionLocal\(\)|\bnext\(get_db\(\)\)|\bsystem_session\(\)")
SCOPED = re.compile(r"\b(?:tenant_scope|cross_tenant_scope|for_each_tenant|cross_tenant_job)\(")
FALLBACK = re.compile(r"\bDEFAULT_TENANT_ID\b|tenant_id[\"']?\s*,\s*[\"']default[\"']|tenant_id:\s*str\s*=\s*[\"']default[\"']")


def test_base_worker_verweigert_start_ohne_kontext():
    import asyncio
    from app.workers.base_worker import BaseWorker

    class _Probe(BaseWorker):
        async def run(self):
            return {}

    with pytest.raises(tc.TenantContextMissing):
        asyncio.run(_Probe().initialize())


def test_muster_selbsttest():
    assert OPENS_DB.search("db = SessionLocal()") and OPENS_DB.search("db = next(get_db())")
    assert SCOPED.search('with tenant_scope(t, "x"):') and not SCOPED.search("tenant_scope_x = 1")
    assert FALLBACK.search('payload.get("tenant_id", "default")')
    assert FALLBACK.search('def f(tenant_id: str = "default"):')
    assert FALLBACK.search("settings.DEFAULT_TENANT_ID")


@pytest.mark.parametrize("path", WORKER_FILES, ids=lambda p: p.name)
def test_worker_oeffnen_die_datenbank_nur_mit_ausdruecklichem_kontext(path: Path):
    source = path.read_text(encoding="utf-8")
    if OPENS_DB.search(source):
        assert SCOPED.search(source), f"{path.name} oeffnet die Datenbank ohne tenant_scope/cross_tenant_scope"
    assert not FALLBACK.search(source), f"{path.name} faellt auf einen Standardmandanten zurueck"
