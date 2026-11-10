"""Positionsbaustein Kontrakt und Kontrakt-Abruf bei Lieferscheinfreigabe (BELEG-052 Phase 1, 10.11.2026).

Der alte Lieferschein buchte je Position mit Kontraktnummer einen Abruf; die DocFlow-Belegmaske kannte keinen Kontrakt.
Jetzt: Kontraktbezug je Position (offener Kontrakt des Mandanten, sonst Pruefgrund), geht beim Umwandeln mit (dazu
Charge und Batch), die Freigabe des Lieferscheins bucht den Abruf in der Kontrakteinheit - ueber die Restmenge nur mit
erlaubter Mehrlieferung -, das Storno kennzeichnet ihn (nicht loeschen).
"""
from __future__ import annotations

import importlib.util
import os
import uuid
from decimal import Decimal
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

WURZEL = Path(__file__).resolve().parents[1]
DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


def _migriere(verbindung, name: str) -> None:
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"alembic/versions/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    with Operations.context(MigrationContext.configure(verbindung)):
        modul.upgrade()


def _spalte(verbindung, schema: str, tabelle: str, spalte: str) -> bool:
    return bool(verbindung.execute(sa.text(
        "SELECT 1 FROM information_schema.columns WHERE table_schema = :s AND table_name = :t AND column_name = :c"),
        {"s": schema, "t": tabelle, "c": spalte}).scalar())


@pytest.fixture
def w():
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    if not _spalte(verbindung, "domain_docflow", "document_headers", "bausteine"):
        _migriere(verbindung, "docflow_kopfbausteine_20261109")
    if not _spalte(verbindung, "domain_docflow", "document_items", "contract_ref"):
        _migriere(verbindung, "docflow_position_kontrakt_20261110")
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    t, kunde, kontrakt = f"kp-{uuid.uuid4().hex[:8]}", str(uuid.uuid4()), f"VK-{uuid.uuid4().hex[:8]}"
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    from app.finance.steuerschluessel import richte_skr03_ein

    richte_skr03_ein(s, t)
    s.execute(sa.text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                      "VALUES (:id, :t, 'K-KP', 'Muehle Nord')"), {"id": kunde, "t": t})
    s.execute(sa.text(
        "INSERT INTO domain_ops.kon_contract (contract_id, contract_no, contract_type, party_id, quantity_type, "
        "total_quantity, unit, allow_overdelivery, status, tenant_id) "
        "VALUES (:id, :nr, 'VERKAUF', :kunde, 'GESAMTKONTRAKT', 1000, 'kg', false, 'OFFEN', :t)"),
        {"id": str(uuid.uuid4()), "nr": kontrakt, "kunde": kunde, "t": t})
    s.flush()
    try:
        yield {"db": s, "t": t, "kunde": kunde, "kontrakt": kontrakt}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _svc(w):
    from app.services.docflow_service import DocflowService

    return DocflowService(w["db"], w["t"], "verkauf-1")


def _beleg(w, art: str, menge: float, kontrakt: str | None, **zeile) -> str:
    from app.api.v1.schemas.docflow_schemas import DocflowCreateRequest, DocflowLineInput

    return _svc(w).create_document(DocflowCreateRequest.model_validate({
        "doc_type": art, "doc_number": f"E-{uuid.uuid4().hex[:6]}", "customer_id": w["kunde"],
        "items": [DocflowLineInput(article_number="W", quantity=menge, unit="dt", unit_price=21.5, tax_code="3",
                                   contract_ref=kontrakt, **zeile).model_dump()]}))


def _abrufe(w) -> list[tuple]:
    return [tuple(z) for z in w["db"].execute(sa.text(
        "SELECT m.quantity, m.is_storniert FROM domain_ops.kon_contract_movement m "
        "JOIN domain_ops.kon_contract k ON k.contract_id = m.contract_id WHERE k.contract_no = :nr "
        "ORDER BY m.created_at"), {"nr": w["kontrakt"]}).all()]


def test_freigabe_bucht_den_abruf_in_der_kontrakteinheit_und_storno_kennzeichnet_ihn(w):
    from app.api.v1.schemas.docflow_schemas import DocflowReverseRequest
    from app.services.docflow_belegadapter import lies_beleg

    ls = _beleg(w, "sales_delivery", 3, w["kontrakt"])
    assert lies_beleg(_svc(w), ls).positionen[0].kontrakt == w["kontrakt"]
    assert _abrufe(w) == []  # Entwurf bucht nichts
    _svc(w).release(ls, f"rel-{uuid.uuid4().hex}", 1, None)
    assert [(float(m), s) for m, s in _abrufe(w)] == [(300.0, False)]  # 3 dt = 300 kg
    _svc(w).reverse_document(ls, DocflowReverseRequest(idempotency_key=f"st-{uuid.uuid4().hex}",
                                                       reason="Falsche Ware geladen"))
    assert [(float(m), s) for m, s in _abrufe(w)] == [(300.0, True)]


def test_abruf_ueber_die_restmenge_haelt_die_freigabe_an(w):
    from app.core.exceptions import ValidationFailedError

    erster = _beleg(w, "sales_delivery", 8, w["kontrakt"])
    _svc(w).release(erster, f"rel-{uuid.uuid4().hex}", 1, None)  # 800 von 1000 kg
    zweiter = _beleg(w, "sales_delivery", 3, w["kontrakt"])  # 300 kg > Rest 200 kg
    with pytest.raises(ValidationFailedError, match="Restmenge"):
        _svc(w).release(zweiter, f"rel-{uuid.uuid4().hex}", 1, None)


def test_unbekannter_oder_fremder_kontrakt_wird_abgelehnt(w):
    from app.core.exceptions import ValidationFailedError

    with pytest.raises(ValidationFailedError, match="nicht bekannt"):
        _beleg(w, "sales_delivery", 1, "GIBT-ES-NICHT")


def test_umwandeln_nimmt_kontrakt_charge_und_batch_mit(w):
    from app.api.v1.schemas.docflow_schemas import DocflowConvertRequest

    auftrag = _beleg(w, "sales_order", 2, w["kontrakt"], charge="CH-17", batch_id="B-3")
    _svc(w).release(auftrag, f"rel-{uuid.uuid4().hex}", 1, None)
    ziel = _svc(w).convert(auftrag, DocflowConvertRequest(target_doc_type="sales_delivery",
                                                         idempotency_key=f"cv-{uuid.uuid4().hex}"))
    position = _svc(w).fetch_items(ziel["target_doc_id"])[0]
    assert (position["contract_ref"], position["charge"], position["batch_id"]) == (w["kontrakt"], "CH-17", "B-3")
    assert Decimal(str(position["quantity"])) == Decimal("2")
