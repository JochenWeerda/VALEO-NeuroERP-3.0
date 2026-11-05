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


def test_psm_liest_mandantengefiltert_und_zaehlt_ablauf():
    """SQL-Praedikat, kein Nachweis fuer JWT oder valeo_app-RLS."""
    from datetime import datetime
    from uuid import uuid4
    from sqlalchemy.orm import Session
    from app.domains.agrar.api.psm import list_psm_zulassungen
    from app.infrastructure.models import PSM

    marker = uuid4().hex
    a, b = f"psm-a-{marker[:12]}", f"psm-b-{marker[:12]}"
    with support.probe(("domain_agrar.agrar_psm",)) as conn:
        support.ensure_tenants(conn, a, b)
        with Session(bind=conn, join_transaction_mode="create_savepoint") as db:
            for tenant, suffix, datum in ((a, "a", datetime(2020, 1, 1)), (b, "b", datetime(2099, 1, 1))):
                db.add(PSM(tenant_id=tenant, artikelnummer=f"{marker}-{suffix}", name=f"PSM {marker}",
                           wirkstoff="W", mittel_typ="Fungizid", bvl_nummer=f"BVL-{suffix}", zulassung_ablauf=datum))
            db.flush()
            x = list_psm_zulassungen(tenant_id=a, search=marker, skip=0, limit=1, db=db)
            y = list_psm_zulassungen(tenant_id=b, search=marker, skip=0, limit=1, db=db)
            assert (x.total, x.abgelaufen, x.items[0].artikelnummer) == (1, 1, f"{marker}-a")
            assert (y.total, y.abgelaufen, y.items[0].artikelnummer) == (1, 0, f"{marker}-b")
