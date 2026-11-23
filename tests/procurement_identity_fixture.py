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
    """Zwei Bestellungen in DocFlow, dem einzigen Belegspeicher (BELEG-052 S3).

    PO1: zwei Positionen, Wareneingang teilweise (100/100 und 30/50), Eingangsrechnung aus dem Wareneingang (27.700).
    PO2: voll geliefert (20 t zu 480), die Rechnung im E-Rechnungs-Postfach lautet auf 22 t - 960 zu viel berechnet.
    Ueberlieferung kennt DocFlow nicht (die Umwandlung uebersteigt die Bestellmenge nie).
    """
    from scripts import seed_demo_procurement as factory
    from stammsaetze import lege_lieferanten_an

    from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest, DocflowCreateRequest, DocflowLineInput
    from app.services.docflow_service import DocflowService

    monkeypatch.setattr(factory, 'TENANT', context.tenant)
    db, ns = context.db, context.namespace
    monkeypatch.setattr(db, 'commit', db.flush)  # Kommandos committen - hier bleibt alles in der Testtransaktion
    lege_lieferanten_an(db, context.tenant, context.supplier)
    svc = DocflowService(db, context.tenant, 'einkauf-1')

    def bestellung(zeilen):
        kennung = svc.create_document(DocflowCreateRequest.model_validate({
            'doc_type': 'purchase_order', 'doc_number': 'ENTWURF-'+uuid4().hex[:6], 'supplier_id': context.supplier,
            'items': [DocflowLineInput(article_number=a, description=b, quantity=m, unit='t', unit_price=p).model_dump()
                      for a, b, m, p in zeilen]}))
        svc.release(kennung, 'rel-'+uuid4().hex, None, None)
        nummer = db.execute(text('SELECT doc_number FROM domain_docflow.document_headers WHERE id = :id'),
                            {'id': kennung}).scalar()
        positionen = db.execute(text('SELECT id FROM domain_docflow.document_items WHERE header_id = :id '
                                     'ORDER BY line_number'), {'id': kennung}).scalars().all()
        return kennung, nummer, [str(p) for p in positionen]

    def wandle(quelle, ziel, mengen=None):
        return str(svc.convert(quelle, DocflowConvertRequest(
            target_doc_type=ziel, idempotency_key='conv-'+uuid4().hex,
            quantities_by_source_item_id=mengen or {}))['target_doc_id'])

    po1, po_ok, (p1, p2) = bestellung([('WEIZEN-A', 'Test wheat', 100, 220), ('GERSTE-B', 'Test barley', 50, 190)])
    wareneingang = wandle(po1, 'goods_receipt', {p1: 100, p2: 30})
    wandle(wareneingang, 'purchase_invoice')
    po2, po_over, (p3,) = bestellung([('RAPS-00', 'Test rapeseed', 20, 480)])
    wandle(po2, 'goods_receipt', {p3: 20})
    factory._invoice(db, po_over, 'IT-'+ns+'-RE2', 10560)
    return po_ok, po_over
