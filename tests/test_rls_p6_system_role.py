"""RLS-Plan P6: mandantenuebergreifende Arbeit verbindet sich als valeo_system (BYPASSRLS).

``system_session()`` oeffnet nur innerhalb von ``cross_tenant_scope``. Gegen den Pruefstand
(zurueckgerollt) wird gezeigt: dieselbe Abfrage sieht als valeo_app ohne Mandant nichts und als
valeo_system alle Mandanten.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

import pytest
import sqlalchemy as sa

ROOT = Path(__file__).resolve().parents[1]
URL = os.environ.get("TEST_DATABASE_URL")
A, B = "rls-sys-a", "rls-sys-b"


@pytest.mark.unit
def test_system_session_nur_im_uebergreifenden_scope():
    from app.core.database import system_session
    from app.core.tenant_context import TenantContextMissing, tenant_scope
    with pytest.raises(TenantContextMissing):
        system_session()
    with tenant_scope("t-1", "test"), pytest.raises(TenantContextMissing):
        system_session()


@pytest.mark.unit
def test_system_session_wird_nur_in_uebergreifendem_code_geoeffnet():
    call = re.compile(r"\bsystem_session\(\)")
    scoped = re.compile(r"\bcross_tenant_(?:scope|job)\(|\bcross_tenant_reason\(\)")
    offenders = []
    for path in sorted((ROOT / "app").rglob("*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        if call.search(text) and not scoped.search(text):
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == [], offenders


@pytest.mark.integration
def test_systemrolle_sieht_alle_mandanten_anwendung_ohne_mandant_keinen():
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    sys.path.insert(0, str(ROOT / "scripts"))
    import rls_inventory
    engine = sa.create_engine(URL)
    with engine.connect() as conn:
        tx = conn.begin()
        try:
            rls_inventory._pending_upgrade(conn)
            if not conn.execute(sa.text("SELECT 1 FROM pg_roles WHERE rolname = 'valeo_system' AND rolbypassrls")).scalar():
                pytest.skip("Rolle valeo_system fehlt im Cluster (scripts/provision_db_roles.py --anwenden)")
            for tenant in (A, B):
                conn.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true) "
                                     "ON CONFLICT (id) DO NOTHING"), {"t": tenant})
                conn.execute(sa.text("INSERT INTO domain_finance.kostenstellen (id, tenant_id, nummer, bezeichnung) "
                                     "VALUES (:id, :t, :id, 'x')"), {"id": f"ks-{tenant}", "t": tenant})
            for role in ("valeo_app", "valeo_system"):
                conn.execute(sa.text(f"GRANT USAGE ON SCHEMA domain_finance TO {role}"))
                conn.execute(sa.text(f"GRANT SELECT ON domain_finance.kostenstellen TO {role}"))
            query = sa.text("SELECT count(*) FROM domain_finance.kostenstellen WHERE id IN ('ks-rls-sys-a', 'ks-rls-sys-b')")
            conn.execute(sa.text("SELECT set_config('app.tenant_id', '', true)"))
            seen = {}
            for role in ("valeo_app", "valeo_system"):
                nested = conn.begin_nested()
                conn.execute(sa.text(f"SET LOCAL ROLE {role}"))
                seen[role] = conn.execute(query).scalar()
                nested.rollback()
            assert seen == {"valeo_app": 0, "valeo_system": 2}
        finally:
            tx.rollback()
    engine.dispose()


@pytest.mark.unit
def test_kein_dienst_liest_eine_tabelle_mit_rls():
    """Dienste unter services/* setzen kein app.tenant_id (Mandant nicht tokengebunden); eine
    Tabelle mit RLS waere fuer sie still leer. Die Rollout-Analyse haelt solche Tabellen mit
    Grund ``dienst`` zurueck; dieser Vertrag prueft das Ergebnis direkt."""
    import json
    sys.path.insert(0, str(ROOT / "scripts"))
    import rls_rollout
    inventory = json.loads(rls_rollout.INVENTORY.read_text(encoding="utf-8"))
    protected = [t["table"] for t in inventory["tables"] if t["rls"]]
    service_files = [(rel, text) for rel, text in rls_rollout._code_files() if rel.startswith("services/")]
    hits = []
    for table in protected:
        schema, name = table.split(".")
        rx = re.compile(rf"\b{schema}\.\"?{name}\b" if schema != "public"
                        else rf"(?:\bpublic\.{name}\b|(?:FROM|JOIN|INTO|UPDATE)\s+\"?{name}\b)", re.I)
        hits += [(table, rel) for rel, text in service_files if rx.search(text)]
    assert hits == [], hits[:10]
