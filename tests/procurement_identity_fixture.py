"""Existing probe, real production JWT, own rollback-only procurement data."""
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session
from test_system_tenant_binding import keys, probe

from app.core.database import engine, get_db
from main import app


@pytest.fixture
def procurement_context(require_db, probe):
    tenant, supplier = str(uuid4()), str(uuid4())
    namespace = uuid4().hex[:12]
    previous = app.dependency_overrides.get(get_db)
    with engine.connect() as connection:
        outer = connection.begin()
        db = Session(bind=connection, join_transaction_mode='create_savepoint')
        try:
            db.execute(text('INSERT INTO domain_shared.tenants (id,name,domain,is_active) VALUES (:id,:name,:domain,TRUE)'),
                       {'id': tenant, 'name': 'Procurement integration test', 'domain': namespace+'.test.invalid'})
            db.execute(text('INSERT INTO domain_einkauf.lieferanten (id,tenant_id,lieferantennummer,firmenname) VALUES (:id,:tenant,:number,:name)'),
                       {'id': supplier, 'tenant': tenant, 'number': 'IT-'+namespace, 'name': 'Synthetic procurement supplier'})
            db.commit()
            app.dependency_overrides[get_db] = lambda: db
            headers = {'Authorization': 'Bearer '+probe.token(tenant, changes={'roles': ['admin']}), 'X-Tenant-ID': tenant}
            yield SimpleNamespace(db=db, tenant=tenant, supplier=supplier, namespace=namespace, headers=headers)
        finally:
            if previous is None:
                app.dependency_overrides.pop(get_db, None)
            else:
                app.dependency_overrides[get_db] = previous
            db.close()
            outer.rollback()


def seed_match_cases(context, monkeypatch):
    # Reuse the existing INSERT factories, never seed() or its shared DEMO rows.
    from scripts import seed_demo_procurement as factory
    monkeypatch.setattr(factory, 'TENANT', context.tenant)
    db, ns = context.db, context.namespace
    warehouse, location = str(uuid4()), str(uuid4())
    now = datetime.now(timezone.utc)
    db.execute(text('INSERT INTO public.inventory_warehouses (id,code,name,tenant_id,is_active,created_at,updated_at) VALUES (:id,:code,:name,:tenant,TRUE,:now,:now)'),
               {'id': warehouse, 'code': 'IT-WH-'+ns, 'name': 'Synthetic test warehouse', 'tenant': context.tenant, 'now': now})
    db.execute(text("INSERT INTO public.inventory_locations (id,warehouse_id,code,location_type,created_at) VALUES (:id,:warehouse,:code,'bulk',:now)"),
               {'id': location, 'warehouse': warehouse, 'code': 'IT-LOC-'+ns, 'now': now})
    po_ok, po_over = 'IT-'+ns+'-PO1', 'IT-'+ns+'-PO2'
    first = factory._po(db, context.supplier, po_ok, [
        {'pos': 1, 'artikel_nr': 'WEIZEN-A', 'bezeichnung': 'Test wheat', 'menge': 100, 'einheit': 't', 'einzelpreis': 220},
        {'pos': 2, 'artikel_nr': 'GERSTE-B', 'bezeichnung': 'Test barley', 'menge': 50, 'einheit': 't', 'einzelpreis': 190},
    ])
    factory._gr(db, first, po_ok, context.supplier, 'IT-'+ns+'-GR1', [
        {'pos': 1, 'sku': 'WEIZEN-A', 'bezeichnung': 'Test wheat', 'bestellt': 100, 'geliefert': 100, 'einheit': 't'},
        {'pos': 2, 'sku': 'GERSTE-B', 'bezeichnung': 'Test barley', 'bestellt': 50, 'geliefert': 30, 'einheit': 't'},
    ], warehouse, location)
    factory._invoice(db, po_ok, 'IT-'+ns+'-RE1', 27700)
    second = factory._po(db, context.supplier, po_over, [
        {'pos': 1, 'artikel_nr': 'RAPS-00', 'bezeichnung': 'Test rapeseed', 'menge': 20, 'einheit': 't', 'einzelpreis': 480},
    ])
    factory._gr(db, second, po_over, context.supplier, 'IT-'+ns+'-GR2', [
        {'pos': 1, 'sku': 'RAPS-00', 'bezeichnung': 'Test rapeseed', 'bestellt': 20, 'geliefert': 22, 'einheit': 't'},
    ], warehouse, location)
    db.commit()
    return po_ok, po_over
