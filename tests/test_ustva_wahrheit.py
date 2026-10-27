"""UStVA: Zahlen aus dem Hauptbuch, Uebermittlung nur mit ELSTER-Transferticket.

Bis 27.10.2026 erkannten Vorberechnung und Berechnung Erloes- und Aufwandskonten am ersten Zeichen der Konto-UUID,
rechneten pauschal 19 %, filterten auf eine nie geschriebene Spalte und meldeten Fehler als null. ``submit`` setzte
``submitted`` mit erfundener ELSTER-Referenz, ``/compliance/ustva`` meldete ``EINGEREICHT`` ohne Uebermittlung.

Pruefstand ``valeo_probe``: ausstehende Migrationen und eigene Zeilen in einer Transaktion, die zurueckgerollt wird.
"""
from __future__ import annotations

import asyncio
import inspect
import os
import sys
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from pydantic import ValidationError
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm import Session

from app.api.v1.endpoints import compliance, vat_return_export as ustva_api
from app.elster.ustva_xml import build_ustva_elster_xml
from app.finance import ustva

pytestmark = pytest.mark.integration
ROOT = Path(__file__).resolve().parents[1]

KONTEN = ("1000", "1200", "1400", "1576", "1600", "1771", "1776", "3400", "8300", "8400", "8500", "1577")


def _anfrage(sub: str = "pruefer-ustva"):
    return SimpleNamespace(state=SimpleNamespace(token_claims={"sub": sub}))


@pytest.fixture
def hauptbuch():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL (valeo_probe) erforderlich")
    assert make_url(url).database == "valeo_probe" or os.environ.get("GITHUB_ACTIONS") == "true"
    sys.path.insert(0, str(ROOT / "scripts"))
    import rls_inventory

    engine = sa.create_engine(url)
    with engine.connect() as conn:
        tx = conn.begin()
        rls_inventory._pending_upgrade(conn)
        a, b = f"ustva-a-{uuid4().hex[:8]}", f"ustva-b-{uuid4().hex[:8]}"
        konto: dict[tuple[str, str], str] = {}

        def sql(statement, **params):
            return conn.execute(sa.text(statement), params)

        for t in (a, b):
            sql("INSERT INTO domain_shared.tenants(id, name) VALUES (:t, :n)", t=t, n=f"Firma {t}")
            for nr in KONTEN:
                konto[(t, nr)] = str(uuid4())
                sql("""INSERT INTO domain_erp.chart_of_accounts(id, tenant_id, account_number, account_name, account_type, is_active)
                       VALUES (:id, :t, :nr, :nr, 'asset', true)""", id=konto[(t, nr)], t=t, nr=nr)
            for code, satz, kz, ust, vst, erl in (("2", 7, "86", "1771", None, "8300"), ("3", 19, "81", "1776", None, "8400"),
                                                  ("9", 19, "66", None, "1576", None)):
                sql("""INSERT INTO domain_erp.tax_keys(id, tenant_id, code, bezeichnung, steuersatz, ustva_position,
                           credit_account, debit_account, revenue_account, gueltig_von)
                       VALUES (:id, :t, :code, 'UStVA-Pruefung', :satz, :kz, :ust, :vst, :erl, DATE '2020-01-01')""",
                    id=str(uuid4()), t=t, code=code, satz=satz, kz=kz, ust=ust, vst=vst, erl=erl)

        def buche(t: str, periode: str, zeilen, status: str = "posted") -> str:
            je = str(uuid4())
            sql("""INSERT INTO domain_erp.journal_entries(id, tenant_id, entry_number, entry_date, posting_date, period, status)
                   VALUES (:id, :t, :nr, CAST(:tag AS date), CAST(:tag AS date), :p, :s)""",
                id=je, t=t, nr=f"U-{je[:12]}", tag=f"{periode}-15", p=periode, s=status)
            for i, (nr, soll, haben) in enumerate(zeilen, 1):
                sql("""INSERT INTO domain_erp.journal_entry_lines(id, journal_entry_id, account_id, line_number, debit, credit)
                       VALUES (:id, :je, :k, :i, :d, :c)""",
                    id=str(uuid4()), je=je, k=konto[(t, nr)], i=i, d=Decimal(str(soll)), c=Decimal(str(haben)))
            return je

        # Maerz, Mandant a: Verkauf 19 %, Verkauf 7 %, Gutschrift 19 %, Einkauf 19 %
        buche(a, "2026-03", [("1400", 119, 0), ("8400", 0, 100), ("1776", 0, 19)])
        buche(a, "2026-03", [("1400", 107, 0), ("8300", 0, 100), ("1771", 0, 7)])
        buche(a, "2026-03", [("8400", 10, 0), ("1776", 1.90, 0), ("1400", 0, 11.90)])
        buche(a, "2026-03", [("3400", 200, 0), ("1576", 38, 0), ("1600", 0, 238)])
        # nicht in der Anmeldung: anderer Monat, anderer Mandant, Entwurf
        buche(a, "2026-04", [("1400", 1190, 0), ("8400", 0, 1000), ("1776", 0, 190)])
        buche(b, "2026-03", [("1400", 595, 0), ("8400", 0, 500), ("1776", 0, 95)])
        entwurf = buche(a, "2026-03", [("1000", 50, 0), ("1200", 0, 50)], status="draft")

        session = Session(bind=conn, join_transaction_mode="create_savepoint")
        try:
            yield SimpleNamespace(db=session, sql=sql, buche=buche, a=a, b=b, entwurf=entwurf, konto=konto)
        finally:
            session.close()
            tx.rollback()
    engine.dispose()


def _kz(stand) -> dict[str, tuple]:
    return {k.kennzahl: (k.bemessungsgrundlage, k.steuer) for k in stand.kennzahlen}


def test_kennzahlen_aus_den_konten_der_steuerschluessel(hauptbuch):
    stand = ustva.berechne(hauptbuch.db, hauptbuch.a, "2026-03")
    assert _kz(stand) == {
        "81": (Decimal("90.00"), Decimal("17.10")),   # Gutschrift mindert Bemessungsgrundlage und Steuer
        "86": (Decimal("100.00"), Decimal("7.00")),
        "66": (None, Decimal("38.00")),
    }
    assert (stand.umsatz_netto, stand.umsatzsteuer, stand.vorsteuer, stand.zahllast) == (
        Decimal("190.00"), Decimal("24.10"), Decimal("38.00"), Decimal("-13.90"))
    assert stand.klaerungen == [] and stand.offene_entwuerfe == 1 and stand.gebuchte_buchungen == 4


def test_quartal_und_ungueltiger_zeitraum(hauptbuch):
    assert ustva.perioden("2026-Q1") == ["2026-01", "2026-02", "2026-03"]
    assert _kz(ustva.berechne(hauptbuch.db, hauptbuch.a, "2026-Q2"))["81"] == (Decimal("1000.00"), Decimal("190.00"))
    for falsch in ("2026-13", "2026-Q5", "03/2026", ""):
        with pytest.raises(ValueError):
            ustva.perioden(falsch)
    with pytest.raises(HTTPException) as info:
        asyncio.run(ustva_api.vorberechnung_ustva(zeitraum="2026-3", tenant_id=hauptbuch.a, db=hauptbuch.db))
    assert info.value.status_code == 422


@pytest.mark.parametrize("fall", ["ohne_kennzahl", "geteiltes_konto", "steuer_passt_nicht", "reverse_charge"])
def test_was_sich_nicht_zuordnen_laesst_ist_eine_klaerung(hauptbuch, fall):
    h, a = hauptbuch, hauptbuch.a
    if fall == "ohne_kennzahl":
        h.sql("""INSERT INTO domain_erp.tax_keys(id, tenant_id, code, bezeichnung, steuersatz, credit_account, revenue_account, gueltig_von)
                 VALUES (:id, :t, '4', 'ohne', 19, '1577', '8500', DATE '2020-01-01')""", id=str(uuid4()), t=a)
        h.buche(a, "2026-03", [("1400", 119, 0), ("8500", 0, 100), ("1577", 0, 19)])
    elif fall == "geteiltes_konto":
        h.sql("""INSERT INTO domain_erp.tax_keys(id, tenant_id, code, bezeichnung, steuersatz, ustva_position, credit_account,
                     revenue_account, gueltig_von)
                 VALUES (:id, :t, '5', 'geteilt', 7, '86', '1577', '8400', DATE '2020-01-01')""", id=str(uuid4()), t=a)
    elif fall == "steuer_passt_nicht":
        h.buche(a, "2026-03", [("1400", 105, 0), ("8400", 0, 100), ("1776", 0, 5)])
    else:
        h.sql("UPDATE domain_erp.tax_keys SET reverse_charge = true WHERE tenant_id = :t AND code = '9'", t=a)
    stand = ustva.berechne(h.db, a, "2026-03")
    assert len(stand.klaerungen) >= 1, stand
    with pytest.raises(HTTPException) as info:
        asyncio.run(ustva_api.calculate_vat_return(
            ustva_api.VATReturnCalculationRequest(period="2026-03"), _anfrage(), tenant_id=a, db=h.db))
    assert info.value.status_code == 422
    assert h.sql("SELECT COUNT(*) FROM domain_erp.vat_returns WHERE tenant_id = :t", t=a).scalar() == 0


def _ablauf_bis_geprueft(h):
    angelegt = asyncio.run(ustva_api.calculate_vat_return(
        ustva_api.VATReturnCalculationRequest(period="2026-03"), _anfrage("rechner"), tenant_id=h.a, db=h.db))
    assert (angelegt.status, angelegt.calculated_by, angelegt.taxpayer_name) == ("calculated", "rechner", f"Firma {h.a}")
    assert angelegt.vat_payable == Decimal("-13.90")
    pruefung = asyncio.run(ustva_api.validate_vat_return(angelegt.id, _anfrage("pruefer"), tenant_id=h.a, db=h.db))
    assert pruefung["valid"] is False and "Buchungsentwürfe" in pruefung["hindernisse"][0]
    h.sql("UPDATE domain_erp.journal_entries SET status = 'posted' WHERE id = :id", id=h.entwurf)
    pruefung = asyncio.run(ustva_api.validate_vat_return(angelegt.id, _anfrage("pruefer"), tenant_id=h.a, db=h.db))
    assert pruefung["valid"] is True, pruefung
    return angelegt.id


def test_ablauf_speichert_bearbeiter_und_transferticket(hauptbuch):
    h = hauptbuch
    rid = _ablauf_bis_geprueft(h)
    with pytest.raises(HTTPException) as info:  # nicht freigegeben: keine Uebermittlung
        asyncio.run(ustva_api.submit_vat_return(rid, ustva_api.VATReturnSubmitRequest(transferticket="et1234567"),
                                                _anfrage(), tenant_id=h.a, db=h.db))
    assert info.value.status_code == 409
    frei = asyncio.run(ustva_api.approve_vat_return(rid, _anfrage("chefin"), tenant_id=h.a, db=h.db))
    assert (frei.status, frei.approved_by, frei.approval_can_submit) == ("approved", "chefin", True)
    assert frei.approved_at is not None and frei.elster_reference is None
    with pytest.raises(ValidationError):
        ustva_api.VATReturnSubmitRequest()
    fertig = asyncio.run(ustva_api.submit_vat_return(
        rid, ustva_api.VATReturnSubmitRequest(transferticket="et1234567890"), _anfrage("chefin"), tenant_id=h.a, db=h.db))
    assert (fertig.status, fertig.submitted_by, fertig.elster_reference) == ("submitted", "chefin", "et1234567890")
    zeile = h.sql("SELECT status, approved_by, submitted_by, elster_transferticket, validated_by, calculated_by "
                  "FROM domain_erp.vat_returns WHERE id = :id", id=rid).one()
    assert tuple(zeile) == ("submitted", "chefin", "chefin", "et1234567890", "pruefer", "rechner")
    with pytest.raises(HTTPException) as info:
        asyncio.run(ustva_api.submit_vat_return(rid, ustva_api.VATReturnSubmitRequest(transferticket="et999999"),
                                                _anfrage(), tenant_id=h.a, db=h.db))
    assert info.value.status_code == 409
    # Fremder Mandant sieht die Anmeldung nicht.
    with pytest.raises(HTTPException) as info:
        asyncio.run(ustva_api.get_vat_return(rid, tenant_id=h.b, db=h.db))
    assert info.value.status_code == 404


def test_freigabe_nach_geaendertem_hauptbuch_wird_abgewiesen(hauptbuch):
    h = hauptbuch
    rid = _ablauf_bis_geprueft(h)
    h.buche(h.a, "2026-03", [("1400", 119, 0), ("8400", 0, 100), ("1776", 0, 19)])
    with pytest.raises(HTTPException) as info:
        asyncio.run(ustva_api.approve_vat_return(rid, _anfrage("chefin"), tenant_id=h.a, db=h.db))
    assert info.value.status_code == 409
    assert h.sql("SELECT status FROM domain_erp.vat_returns WHERE id = :id", id=rid).scalar() == "validated"


def test_ohne_gepruefte_identitaet_kein_schritt(hauptbuch):
    h = hauptbuch
    with pytest.raises(HTTPException) as info:
        asyncio.run(ustva_api.calculate_vat_return(
            ustva_api.VATReturnCalculationRequest(period="2026-03"), SimpleNamespace(state=SimpleNamespace()),
            tenant_id=h.a, db=h.db))
    assert info.value.status_code == 403


def test_datenbank_haelt_den_ablauf_fest(hauptbuch):
    h = hauptbuch
    rid = str(uuid4())
    h.sql("INSERT INTO domain_erp.vat_returns(id, tenant_id, period) VALUES (:id, :t, '2026-03')", id=rid, t=h.a)
    assert h.sql("SELECT status FROM domain_erp.vat_returns WHERE id = :id", id=rid).scalar() == "calculated"
    for setzen in ("status = 'submitted', submitted_at = NOW(), submitted_by = 'x', approved_by = 'x', approved_at = NOW()",
                   "status = 'approved'", "status = 'draft'"):
        with pytest.raises(IntegrityError):
            with h.db.begin_nested():
                h.db.execute(sa.text(f"UPDATE domain_erp.vat_returns SET {setzen} WHERE id = :id"), {"id": rid})  # nosec B608


def test_compliance_status_meldet_uebermittlung_nur_mit_transferticket(hauptbuch):
    h = hauptbuch
    vorher = asyncio.run(compliance.get_ustva_status(periode="2026-03", tenant_id=h.a, db=h.db))
    assert vorher["elster_uebermittlung"] == "NICHT_UEBERMITTELT" and vorher["status"] == "IN_VORBEREITUNG"
    assert (vorher["zahllast"], vorher["offene_positionen"], vorher["deadline"]) == (-13.9, 1, "2026-04-10")
    rid = _ablauf_bis_geprueft(h)
    asyncio.run(ustva_api.approve_vat_return(rid, _anfrage("chefin"), tenant_id=h.a, db=h.db))
    bereit = asyncio.run(compliance.get_ustva_status(periode="2026-03", tenant_id=h.a, db=h.db))
    assert (bereit["status"], bereit["elster_uebermittlung"], bereit["readiness_pct"]) == ("BEREIT", "NICHT_UEBERMITTELT", 100)
    asyncio.run(ustva_api.submit_vat_return(
        rid, ustva_api.VATReturnSubmitRequest(transferticket="et1234567890"), _anfrage("chefin"), tenant_id=h.a, db=h.db))
    danach = asyncio.run(compliance.get_ustva_status(periode="2026-03", tenant_id=h.a, db=h.db))
    assert (danach["status"], danach["elster_uebermittlung"], danach["elster_transferticket"]) == (
        "UEBERMITTELT", "UEBERMITTELT", "et1234567890")
    fremd = asyncio.run(compliance.get_ustva_status(periode="2026-03", tenant_id=h.b, db=h.db))
    assert fremd["elster_uebermittlung"] == "NICHT_UEBERMITTELT" and fremd["zahllast"] == 95.0


def test_frist_am_wochenende_verschoben():
    assert ustva.abgabefrist("2026-09") == ustva.abgabefrist("2026-Q3")
    assert ustva.abgabefrist("2026-09").isoformat() == "2026-10-12"  # 10.10.2026 ist ein Samstag
    assert ustva.abgabefrist("2026-12").isoformat() == "2027-01-11"


def test_xml_kennzahlen_wie_im_formular():
    positionen = [
        {"kennzahl": "81", "seite": "umsatz", "bemessungsgrundlage": "90.99", "steuer": "17.29"},
        {"kennzahl": "35", "seite": "umsatz", "bemessungsgrundlage": "10.50", "steuer": "1.11"},
        {"kennzahl": "66", "seite": "vorsteuer", "bemessungsgrundlage": None, "steuer": "38"},
    ]
    werte = {}
    for quelle, code in (("2026-03", "03"), ("2026-Q1", "41")):
        baum = ET.fromstring(build_ustva_elster_xml(period=quelle, taxpayer_name="Firma", positions=positionen,
                                                    vat_payable=Decimal("-19.60")))
        werte = {e.tag.split("}")[-1]: e.text for e in baum.iter()}
        assert werte["Zeitraum"] == code
    assert (werte["Kz81"], werte["Kz35"], werte["Kz36"], werte["Kz66"], werte["Kz83"]) == ("90", "10", "1.11", "38.00", "-19.60")
    with pytest.raises(ValueError):
        build_ustva_elster_xml(period="2026-03", taxpayer_name="x", positions=[{"seite": "umsatz"}])


class _Kaputt:
    def execute(self, *_a, **_k):
        raise OperationalError("SELECT", {}, Exception("verbindung weg"))

    def rollback(self):
        return None


def test_lesefehler_ist_503_keine_null():
    for aufruf in (
        lambda: ustva_api.vorberechnung_ustva(zeitraum="2026-03", tenant_id="t", db=_Kaputt()),
        lambda: ustva_api.list_vat_returns(period=None, tenant_id="t", db=_Kaputt()),
        lambda: compliance.get_ustva_status(periode="2026-03", tenant_id="t", db=_Kaputt()),
    ):
        with pytest.raises(HTTPException) as info:
            asyncio.run(aufruf())
        assert info.value.status_code == 503


def test_mandant_und_bearbeiter_aus_dem_token():
    from app.core.tenant import get_tenant_id

    assert inspect.signature(compliance.get_ustva_status).parameters["tenant_id"].default.dependency is get_tenant_id
    for weg in (ustva_api.calculate_vat_return, ustva_api.validate_vat_return, ustva_api.approve_vat_return,
                ustva_api.submit_vat_return):
        assert "http_request" in inspect.signature(weg).parameters
    assert "approved_by" not in ustva_api.VATReturnSubmitRequest.model_fields
    assert not hasattr(ustva_api, "VATReturnApprovalRequest")
    quelle = Path(ustva_api.__file__).read_text(encoding="utf-8")
    assert "except Exception" not in quelle and 'startswith("8")' not in quelle and "Company Name" not in quelle
