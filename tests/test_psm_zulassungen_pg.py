"""Belegtes Altregister in derselben PostgreSQL-Transaktion entfernen und zurueckrollen."""
import importlib.util
from pathlib import Path

import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

import rls_domain_support as support


def test_belegtes_psm_altregister_drop_und_rollback():
    path = Path(__file__).resolve().parents[1] / "alembic/versions/psm_zulassungen_register_entfernen_20261104.py"
    spec = importlib.util.spec_from_file_location("psm_register_pg_migration", path)
    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)
    with support.probe(("domain_agrar.agrar_psm",)) as conn:
        assert not support.exists(conn, "domain_ops.ops_zulassungen_register")
        with Operations.context(MigrationContext.configure(conn)):
            migration.downgrade()
            conn.execute(sa.text("""INSERT INTO domain_ops.ops_zulassungen_register
                (id, tenant_id, produkt, typ, nummer, behoerde)
                VALUES ('psm-rollback-test', 'test-tenant', 'Test', 'PSM', 'test', 'BVL')"""))
            savepoint = conn.begin_nested()
            try:
                migration.upgrade()
                assert not support.exists(conn, "domain_ops.ops_zulassungen_register")
            finally:
                savepoint.rollback()
            assert support.exists(conn, "domain_ops.ops_zulassungen_register")
            assert conn.execute(sa.text("SELECT count(*) FROM domain_ops.ops_zulassungen_register WHERE id = 'psm-rollback-test'" )).scalar() == 1
