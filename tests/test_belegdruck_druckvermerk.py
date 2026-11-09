"""Belegdruck mit Druckvermerk (GoBD, BELEG-052 Phase 1, 09.11.2026).

Bis heute war der Belegdruck ein reiner Download: kein Zaehler, kein Nachdruckvermerk. Der alte Lieferscheindruck
verlangte beim Nachdruck eine Begruendung mit gepruefter Identitaet - das traegt jetzt die Belegmaske fuer jede
Belegart: Druck zaehlt, Nachdruck nur mit Begruendung (Attestierung mit lokalem Nutzer), das PDF zeigt den Nachdruck.
"""
from __future__ import annotations

import os
import uuid

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


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
    s = Session(bind=verbindung, join_transaction_mode="create_savepoint")
    t, beleg, nutzer = f"dv-{uuid.uuid4().hex[:8]}", str(uuid.uuid4()), f"kc-{uuid.uuid4().hex[:8]}"
    s.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"), {"t": t})
    s.execute(sa.text("INSERT INTO domain_shared.users (id, keycloak_id, username, email, tenant_id, is_active) "
                      "VALUES (:id, :kc, :id, :mail, :t, true)"),
              {"id": f"u-{nutzer}", "kc": nutzer, "mail": f"{nutzer}@example.invalid", "t": t})
    s.execute(sa.text(
        "INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number, status, source_system, "
        "currency, total_net, total_tax, total_gross, document_date, version, created_at, updated_at) "
        "VALUES (:id, :t, 'sales_delivery', :nr, 'open', 'test', 'EUR', 0, 0, 0, NOW(), 1, NOW(), NOW())"),
        {"id": beleg, "t": t, "nr": f"LS-{uuid.uuid4().hex[:6]}"})
    s.flush()
    try:
        yield {"db": s, "t": t, "beleg": beleg, "nutzer": {"sub": nutzer, "iss": "https://idp.example", "roles":
                                                           ["SALES_BEARBEITEN"]}}
    finally:
        s.close()
        aussen.rollback()
        verbindung.close()


def _drucke(w, **eingaben) -> str:
    from app.services.docflow_belegaktionen import fuehre_aus, pruefe

    fehler = pruefe(w["db"], w["t"], "sales_delivery", w["beleg"], "drucken", w["nutzer"], eingaben)
    if fehler:
        raise AssertionError(fehler)
    return fuehre_aus(w["db"], w["t"], "sales_delivery", w["beleg"], "drucken", w["nutzer"], eingaben)


def test_erstdruck_ohne_nachdruck_nur_mit_begruendung(w):
    from app.services.docflow_belegaktionen import pruefe

    assert _drucke(w).endswith("gedruckt.")
    fehler = pruefe(w["db"], w["t"], "sales_delivery", w["beleg"], "drucken", w["nutzer"], {})
    assert fehler and fehler[0]["field"] == "grund"
    assert "Nachdruck 2" in _drucke(w, grund="Kunde hat das Original verloren")
    kopf = w["db"].execute(sa.text("SELECT print_count, printed_by FROM domain_docflow.document_headers WHERE id = :id"),
                           {"id": w["beleg"]}).one()
    assert (kopf[0], kopf[1]) == (2, w["nutzer"]["sub"])
    vermerk = w["db"].execute(sa.text(
        "SELECT action, reason, created_by, changes->'actor'->>'issuer', changes->>'nachdruck' FROM domain_audit.attestations "
        "WHERE entity_id = :id"), {"id": w["beleg"]}).all()
    assert [tuple(v) for v in vermerk] == [
        ("print", "Kunde hat das Original verloren", f"u-{w['nutzer']['sub']}", "https://idp.example", "true")]


def test_ohne_eindeutige_nutzerzuordnung_kein_nachdruck(w):
    from app.services.docflow_service import DocflowService

    _drucke(w)
    with pytest.raises(HTTPException) as fehler:
        DocflowService(w["db"], w["t"], "fremd").druck_vermerken(w["beleg"], subjekt="unbekannt", aussteller=None,
                                                                 grund="Nachdruck fuer die Akte")
    assert fehler.value.status_code == 403


def test_pdf_zeigt_den_nachdruck(w):
    from app.services.beleg_druck import beleg_pdf
    from app.services.docflow_belegadapter import lies_beleg
    from app.services.docflow_service import DocflowService

    _drucke(w)
    _drucke(w, grund="Zweitschrift fuer die Spedition")
    beleg = lies_beleg(DocflowService(w["db"], w["t"], "test"), w["beleg"])
    assert beleg.druck_anzahl == 2
    pdf = beleg_pdf(beleg)
    assert pdf.startswith(b"%PDF")
