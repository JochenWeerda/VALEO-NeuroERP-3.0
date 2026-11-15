"""PostgreSQL acceptance against the shared test stand; never creates a database."""
from uuid import uuid4
import pytest
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from app.services import rohware_schema_service as schemas

TABLES = ('domain_shared.rohwarengruppen', 'domain_shared.rohware_abrechnungsschemata',
          'domain_shared.rohware_schema_lines')


def test_canonical_schema_lifecycle_foreign_keys_and_rls(require_db):
    marker = uuid4().hex
    a, b = 'rwa-' + marker[:12], 'rwb-' + marker[:12]
    ga, gb = 'ga-' + marker, 'gb-' + marker
    with support.probe(TABLES) as conn:
        support.ensure_tenants(conn, a, b)
        conn.execute(sa.text('''INSERT INTO domain_shared.rohwarengruppen
            (id, tenant_id, gruppe_nr, bezeichnung) VALUES
            (:ga, :a, :na, 'A'), (:gb, :b, :nb, 'B')'''),
            {'ga': ga, 'gb': gb, 'a': a, 'b': b, 'na': 'a-' + marker, 'nb': 'b-' + marker})
        with Session(bind=conn, join_transaction_mode='create_savepoint') as db:
            legacy_id = 'legacy-' + marker
            db.execute(sa.text("""INSERT INTO domain_shared.rohware_abrechnungsschemata
                (id, tenant_id, schema_nr, bezeichnung, gruppe_id)
                VALUES (:id, :tenant, :nr, 'Altvertrag', :gruppe)"""),
                {'id': legacy_id, 'tenant': a, 'nr': 'legacy-' + marker, 'gruppe': ga})
            legacy = db.execute(sa.text("""SELECT status, aktiv, gueltig_ab = CURRENT_DATE
                FROM domain_shared.rohware_abrechnungsschemata WHERE id=:id"""), {'id': legacy_id}).one()
            assert tuple(legacy) == ('AKTIV', True, True)
            group = schemas.group_id(db, a, group_id=ga)
            schema_id = schemas.create(db, a, schema_code='s-' + marker, name='Prüfung',
                                       group=group, valid_from='2026-01-01')
            draft = db.execute(sa.text('SELECT status, aktiv FROM domain_shared.rohware_abrechnungsschemata WHERE id=:id'), {'id':schema_id}).one()
            assert tuple(draft) == ('ENTWURF', False)
            schemas.transition(db, a, schema_id, 'AKTIV')
            row = db.execute(sa.text('SELECT status, aktiv FROM domain_shared.rohware_abrechnungsschemata WHERE id=:id'), {'id':schema_id}).one()
            assert tuple(row) == ('AKTIV', True)
            schemas.transition(db, a, schema_id, 'ARCHIV')
            assert db.execute(sa.text('SELECT aktiv FROM domain_shared.rohware_abrechnungsschemata WHERE id=:id'), {'id':schema_id}).scalar() is False
            db.execute(sa.text("""INSERT INTO domain_shared.rohware_schema_lines
                (id, tenant_id, schema_id, positions_typ, bezeichnung, berechnungsformel, einheit)
                VALUES (:id, :tenant, :schema, 'GRUNDPREIS', 'Preis', 'basis_preis', 'EUR/t')"""),
                {'id': 'line-' + marker, 'tenant': a, 'schema': schema_id})
            db.flush()
            with pytest.raises(IntegrityError) as line_error, db.begin_nested():
                db.execute(sa.text('''INSERT INTO domain_shared.rohware_schema_lines
                    (id, tenant_id, schema_id, positions_typ, bezeichnung, berechnungsformel, einheit)
                    VALUES (:id, :tenant, :schema, 'GRUNDPREIS', 'x', 'basis_preis', 'EUR/t')'''),
                    {'id': marker, 'tenant': b, 'schema': schema_id})
            assert (getattr(line_error.value.orig, 'sqlstate', None) or getattr(line_error.value.orig, 'pgcode', None)) == '23503'
            assert line_error.value.orig.diag.constraint_name == 'fk_rohware_schema_line_tenant'
            with pytest.raises(IntegrityError) as group_error, db.begin_nested():
                db.execute(sa.text('''INSERT INTO domain_shared.rohware_abrechnungsschemata
                    (id, tenant_id, schema_nr, bezeichnung, gruppe_id, status, aktiv)
                    VALUES (:id, :tenant, :nr, 'x', :gruppe, 'ENTWURF', false)'''),
                    {'id':'bad-' + marker, 'tenant':a, 'nr':'bad-' + marker, 'gruppe':gb})
            assert (getattr(group_error.value.orig, 'sqlstate', None) or getattr(group_error.value.orig, 'pgcode', None)) == '23503'
            assert group_error.value.orig.diag.constraint_name == 'fk_rohware_schema_gruppe_tenant'
            db.commit()  # releases only the session savepoint; probe rolls back outer transaction
        with tenant_scope(b, "Rohware-Mandantenprobe"):
            support.as_app(conn)
            role = conn.execute(sa.text("SELECT current_user, rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")).one()
            assert tuple(role) == ('valeo_app', False, False)
            assert conn.execute(sa.text("UPDATE domain_shared.rohware_abrechnungsschemata SET bezeichnung='foreign' WHERE id=:id"), {'id':schema_id}).rowcount == 0
            assert conn.execute(sa.text("UPDATE domain_shared.rohware_abrechnungsschemata SET tenant_id=:tenant, gruppe_id=:gruppe WHERE id=:id"), {'id':schema_id, 'tenant':b, 'gruppe':gb}).rowcount == 0
            assert conn.execute(sa.text("DELETE FROM domain_shared.rohware_abrechnungsschemata WHERE id=:id"), {'id':schema_id}).rowcount == 0
            assert conn.execute(sa.text("UPDATE domain_shared.rohware_schema_lines SET bezeichnung='foreign' WHERE schema_id=:id"), {'id':schema_id}).rowcount == 0
            assert conn.execute(sa.text("DELETE FROM domain_shared.rohware_schema_lines WHERE schema_id=:id"), {'id':schema_id}).rowcount == 0
            assert conn.execute(sa.text("SELECT count(*) FROM domain_shared.rohware_abrechnungsschemata WHERE id=:id"), {"id":schema_id}).scalar() == 0
            assert conn.execute(sa.text("SELECT count(*) FROM domain_shared.rohware_schema_lines WHERE schema_id=:id"), {"id":schema_id}).scalar() == 0
        with tenant_scope(a, "Rohware-Eigentümerprobe"):
            support.as_app(conn)
            assert conn.execute(sa.text('SELECT count(*) FROM domain_shared.rohware_abrechnungsschemata WHERE id=:id'), {'id':schema_id}).scalar() == 1
            assert conn.execute(sa.text('SELECT count(*) FROM domain_shared.rohware_schema_lines WHERE schema_id=:id'), {'id':schema_id}).scalar() == 1
            assert conn.execute(sa.text('SELECT bezeichnung FROM domain_shared.rohware_abrechnungsschemata WHERE id=:id'), {'id':schema_id}).scalar() == 'Prüfung'
            assert conn.execute(sa.text('SELECT bezeichnung FROM domain_shared.rohware_schema_lines WHERE schema_id=:id'), {'id':schema_id}).scalar() == 'Preis'
            with Session(bind=conn, join_transaction_mode='create_savepoint') as app_db:
                own_group = schemas.group_id(app_db, a, group_id=ga)
                own_id = schemas.create(app_db, a, schema_code='app-' + marker, name='App', group=own_group, valid_from='2026-01-01')
                schemas.transition(app_db, a, own_id, 'AKTIV')
                app_db.execute(sa.text('''INSERT INTO domain_shared.rohware_schema_lines
                    (id, tenant_id, schema_id, positions_typ, bezeichnung, berechnungsformel, einheit)
                    VALUES (:id, :tenant, :schema, 'GRUNDPREIS', 'App', 'basis_preis', 'EUR/t')'''),
                    {'id': 'app-line-' + marker, 'tenant': a, 'schema': own_id})
                assert app_db.execute(sa.text('SELECT status FROM domain_shared.rohware_abrechnungsschemata WHERE id=:id'), {'id':own_id}).scalar() == 'AKTIV'
                assert app_db.execute(sa.text('SELECT count(*) FROM domain_shared.rohware_schema_lines WHERE schema_id=:id'), {'id':own_id}).scalar() == 1
                app_db.commit()  # outer probe transaction still rolls back

