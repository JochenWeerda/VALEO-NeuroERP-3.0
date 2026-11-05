"""Vertrag der lokalen PSM-Zulassungsliste ohne Datenbank."""
import inspect
from datetime import date, datetime, timezone
from types import SimpleNamespace

from app.domains.agrar.api import psm
from app.core.screen_definitions_listen import build_compliance_zulassungen_liste


def test_projektion_laesst_unbekannten_aktivstatus_stehen():
    row = SimpleNamespace(id="1", artikelnummer="A1", name="Mittel", wirkstoff="W", mittel_typ="Fungizid",
                          bvl_nummer="123", zulassung_ablauf=datetime(2026, 1, 1, tzinfo=timezone.utc), ist_aktiv=None)
    assert psm.PSMZulassung.model_validate(row).ist_aktiv is None


def test_mandant_kommt_aus_anmeldung():
    from app.core.tenant import get_tenant_id
    tenant = inspect.signature(psm.list_psm_zulassungen).parameters["tenant_id"]
    assert tenant.default.dependency is get_tenant_id


def test_route_vor_dynamischem_psm_id():
    paths = [route.path for route in psm.router.routes]
    assert paths.index("/zulassungen") < paths.index("/{psm_id}")


def test_listenvertrag_und_mandantenfilter(monkeypatch):
    filters = []
    calls = []
    monkeypatch.setattr(psm, "business_today", lambda: date(2026, 11, 4))
    monkeypatch.setattr(psm, "business_timezone", lambda: SimpleNamespace(key="Europe/Berlin"))

    class Query:
        def __init__(self, expired=False):
            self.expired = expired
        def filter(self, condition):
            filters.append(condition)
            return Query(expired=self.expired or "timezone" in str(condition))
        def count(self):
            return 4 if self.expired else 51
        def order_by(self, *args):
            return self
        def offset(self, value):
            calls.append(("offset", value))
            return self
        def limit(self, value):
            calls.append(("limit", value))
            return self
        def all(self):
            return []
    db = SimpleNamespace(query=lambda model: Query())
    result = psm.list_psm_zulassungen(tenant_id="tenant-a", search="Mittel", skip=25, limit=25, db=db)
    assert any("tenant-a" in condition.compile().params.values() for condition in filters)
    assert any("%Mittel%" in condition.compile().params.values() for condition in filters)
    assert (result.total, result.abgelaufen, result.page, result.pages) == (51, 4, 2, 3)
    assert result.has_next and result.has_prev and ("offset", 25) in calls and ("limit", 25) in calls
    assert "/api/v1/agrar/psm/zulassungen" in str(build_compliance_zulassungen_liste())


def test_migration_entfernt_ersetzte_tabelle_ohne_cascade(monkeypatch):
    import importlib.util
    from pathlib import Path
    path = Path(__file__).resolve().parents[1] / "alembic/versions/psm_zulassungen_register_entfernen_20261104.py"
    spec = importlib.util.spec_from_file_location("psm_register_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    executed = []
    class Result:
        def __init__(self, value): self.value = value
        def scalar(self): return self.value
    class Bind:
        def execute(self, statement):
            return Result("domain_ops.ops_zulassungen_register" if "to_regclass" in str(statement) else 1)
    monkeypatch.setattr(migration.op, "get_bind", lambda: Bind())
    monkeypatch.setattr(migration.op, "execute", executed.append)
    migration.upgrade()
    assert executed == ["LOCK TABLE domain_ops.ops_zulassungen_register IN ACCESS EXCLUSIVE MODE",
                        "DROP TABLE domain_ops.ops_zulassungen_register"]
