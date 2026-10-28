"""RLS-Domain erp Teil 1: Bankkonten, Kreditoren, Debitoren, Mahnungen, Gutscheine, OP-Sicht und Connector-Positionen
je Mandant; Debitoren-, Export- und Connector-Wege mit Mandant aus dem Token.

Bis 28.10.2026 legte ``POST /debtors`` den Debitor unter dem Mandanten aus dem Rumpf an, Abruf/Aendern/Saldo/Loeschen
lasen ohne Mandantenfilter; der OP-Saldo las Spalten, die es nicht gibt (immer 500); der Export liess den Mandanten
ueber ``filter.tenant_id`` waehlen und lieferte Kreditoren immer leer; der FiBu-Connector band ``:tid``, uebergab aber
``tenant_id`` (Pruefen/Buchen/Abbrechen/Stornieren scheiterten immer), buchte Belege ohne unbekannte Konten und las
Profile fremder Mandanten. Kreditoren- und Debitorennummern waren systemweit eindeutig.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt). Die Fachketten laufen als
Tabelleneigentuemer (ohne RLS): Sie pruefen den Code, nicht die Policies.
"""

from __future__ import annotations

import asyncio
import inspect
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.api.v1.endpoints import creditors as kreditoren
from app.api.v1.endpoints import debtors as debitoren
from app.api.v1.endpoints import export_service as export
from app.api.v1.endpoints import fibu_connectors as connectors
from app.api.v1.schemas.finance import DebtorCreate, DebtorUpdate
from app.core.connectors import workflow
from app.core.tenant import get_tenant_id
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

ERP = "domain_erp"
RUNS, ITEMS = f"{ERP}.fibu_connector_runs", f"{ERP}.fibu_connector_run_items"
DEBITORS, CUSTOMERS = f"{ERP}.debitors", "domain_crm.customers"
ISOLATED = (f"{ERP}.bank_accounts", f"{ERP}.creditors", DEBITORS, f"{ERP}.dunning_notices", f"{ERP}.gift_cards",
            f"{ERP}.open_items", ITEMS)
LINKS = ((ITEMS, "run_id", RUNS), (DEBITORS, "customer_id", CUSTOMERS))


@pytest.fixture(scope="module")
def probe():
    with support.probe(ISOLATED + (RUNS, CUSTOMERS)) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            for parent in (RUNS, CUSTOMERS):
                rows[parent, tenant] = support.insert_row(conn, parent, tenant)
            for table in ISOLATED:
                links = {column: rows[parent, tenant] for child, column, parent in LINKS if child == table}
                rows[table, tenant] = str(support.seed_row(conn, table, tenant, **links)["id"])
        for parent in (RUNS, CUSTOMERS):
            rows["spare", parent] = support.insert_row(conn, parent, B)
        support.as_app(conn)
        yield conn, rows


@pytest.fixture
def db(probe):
    conn, rows = probe
    savepoint = conn.begin_nested()
    yield conn, rows
    if savepoint.is_active:
        savepoint.rollback()


def test_policy_formen(db):
    conn, _ = db
    for table in ISOLATED:
        assert support.shape(conn, table) == ("getrennt", ""), table


@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM])


def test_mandant_pflicht_und_vorgabe_aus_dem_kontext(db):
    conn, _ = db
    for table in ISOLATED:
        notnull, default = conn.execute(sa.text(
            "SELECT a.attnotnull, pg_get_expr(d.adbin, d.adrelid) FROM pg_attribute a LEFT JOIN pg_attrdef d "
            "ON d.adrelid = a.attrelid AND d.adnum = a.attnum WHERE a.attrelid = to_regclass(:t) AND a.attname = 'tenant_id'"),
            {"t": table}).one()
        assert (notnull, default) == (True, "rls_current_tenant()"), table


@pytest.mark.parametrize("child,column,parent", LINKS, ids=[f"{c.split('.')[1]}.{col}" for c, col, _ in LINKS])
def test_kein_verweis_auf_fremden_eltern(db, child, column, parent):
    conn, rows = db
    constraint = f"fk_{child.split('.')[1]}_{column}_tenant"
    with tenant_scope(A, "test"):
        message = support.rejected(conn, f"UPDATE {child} SET {column} = :p WHERE id = :i",
                                   {"p": rows["spare", parent], "i": rows[child, A]})
    assert constraint in message, message


@pytest.mark.parametrize("table,column", ((f"{ERP}.creditors", "creditor_number"), (DEBITORS, "debitor_number")))
def test_nummern_je_mandant_eindeutig(db, table, column):
    conn, rows = db
    nummer = f"N-{uuid4().hex[:8]}"
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text("RESET ROLE"))
        # anderer Mandant: dieselbe Nummer erlaubt (bis 28.10.2026 systemweit eindeutig)
        conn.execute(sa.text(f"UPDATE {table} SET {column} = :n WHERE id IN (:a, :b)"),
                     {"n": nummer, "a": rows[table, A], "b": rows[table, B]})
        with pytest.raises(sa.exc.IntegrityError, match="duplicate key"):
            with conn.begin_nested():
                conn.execute(sa.text(f"INSERT INTO {table} (id, tenant_id, {column}, name) VALUES (:i, :t, :n, 'Doppelt')"),
                             {"i": str(uuid4()), "t": A, "n": nummer})
    finally:
        savepoint.rollback()  # stellt auch SET LOCAL ROLE valeo_app wieder her


# --- Fachwege (als Eigentuemer, ohne RLS) ------------------------------------------------------------------------


@pytest.fixture
def fach(db):
    conn, rows = db
    conn.execute(sa.text("RESET ROLE"))
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        yield session, rows
    finally:
        session.close()


def _status(aufruf) -> int:
    with pytest.raises(HTTPException) as info:
        asyncio.run(aufruf) if inspect.iscoroutine(aufruf) else aufruf()
    return info.value.status_code


def test_debitoren_nur_im_eigenen_mandanten(fach):
    db, _ = fach
    nummer = f"D-{uuid4().hex[:6]}"
    roh = dict(debtor_number=nummer, company_name="Hof Janssen", street="Dorfstr. 1", postal_code="26789",
               city="Leer", country="DE", email="hof@example.org")
    assert _status(debitoren.create_debtor(DebtorCreate(tenant_id=B, **roh), tenant_id=A, db=db)) == 403
    angelegt = asyncio.run(debitoren.create_debtor(DebtorCreate(tenant_id=A, **roh), tenant_id=A, db=db))
    assert angelegt.tenant_id == A
    did = angelegt.id
    assert asyncio.run(debitoren.get_debtor(did, tenant_id=A, db=db)).id == did
    assert _status(debitoren.get_debtor(did, tenant_id=B, db=db)) == 404
    assert _status(debitoren.update_debtor(did, DebtorUpdate(company_name="Fremd"), tenant_id=B, db=db)) == 404
    assert _status(debitoren.get_debtor_balance(did, tenant_id=B, db=db)) == 404
    assert _status(debitoren.delete_debtor(did, tenant_id=B, db=db)) == 404
    assert db.execute(sa.text("SELECT name, is_active FROM domain_erp.debitors WHERE id = :i"), {"i": did}).one() == ("Hof Janssen", True)
    # dieselbe Nummer im anderen Mandanten ist erlaubt
    assert asyncio.run(debitoren.create_debtor(DebtorCreate(tenant_id=B, **roh), tenant_id=B, db=db)).tenant_id == B


def _op(db, tenant, konto_typ, offen, **verweis):
    db.execute(sa.text(
        "INSERT INTO domain_erp.offene_posten (id, tenant_id, rechnungsnr, konto_typ, betrag, offen, op_status, due_date, "
        f"{', '.join(verweis)}) VALUES (:id, :t, :nr, :k, :o, :o, 'offen', DATE '2026-11-30', {', '.join(':' + v for v in verweis)})"),
        {"id": str(uuid4()), "t": tenant, "nr": f"R-{uuid4().hex[:6]}", "k": konto_typ, "o": offen, **verweis})


def test_op_saldo_liest_die_offenen_posten(fach):
    db, rows = fach
    kunde = rows[CUSTOMERS, A]
    nummer = f"D-{uuid4().hex[:6]}"
    deb = asyncio.run(debitoren.create_debtor(DebtorCreate(tenant_id=A, debtor_number=nummer, company_name="Hof Saldo", street="Weg 2", postal_code="26789", city="Leer",
                                                           country="DE"), tenant_id=A, db=db))
    db.execute(sa.text("UPDATE domain_erp.debitors SET customer_id = :k WHERE id = :i"), {"k": kunde, "i": deb.id})
    _op(db, A, "debitoren", 120, kunde_id=kunde)
    _op(db, A, "debitoren", 30, debtor_id=deb.id)
    _op(db, B, "debitoren", 999, kunde_id=kunde)  # fremder Mandant zaehlt nicht
    saldo = asyncio.run(debitoren.get_debtor_balance(deb.id, tenant_id=A, db=db))
    assert (saldo["open_balance"], saldo["open_item_count"], saldo["oldest_due_date"]) == (150.0, 2, "2026-11-30")

    kred = rows[f"{ERP}.creditors", A]
    _op(db, A, "kreditoren", 75, creditor_id=kred)
    saldo = asyncio.run(kreditoren.get_creditor_balance(kred, tenant_id=A, db=db))
    assert (saldo["open_balance"], saldo["open_item_count"]) == (75.0, 1)


def test_export_nur_eigener_mandant(fach):
    db, rows = fach
    fremd = export.ExportListRequest(entity="debtors", filter=export.ExportListFilter(tenant_id=B))
    assert _status(export.export_list(fremd, tenant_id=A, db=db)) == 403
    namen = {r["id"] for r in export._export_creditors(db, A, None)}
    assert rows[f"{ERP}.creditors", A] in namen and rows[f"{ERP}.creditors", B] not in namen
    eigen = export.ExportListRequest(entity="debtors", filter=export.ExportListFilter(tenant_id=A))
    assert asyncio.run(export.export_list(eigen, tenant_id=A, db=db)).status_code == 200


CSV = (b"buchungsdatum;konto;betrag;soll_haben;buchungstext\n"
       b"2026-10-15;6000;100,50;S;Lohn Oktober\n"
       b"2026-10-15;1200;100,50;H;Lohn Oktober\n")


def _konten(db, tenant, *nummern):
    for nummer in nummern:
        db.execute(sa.text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type) "
            "VALUES (:i, :t, :n, :n, 'expense')"), {"i": str(uuid4()), "t": tenant, "n": nummer})


def _lauf(db, tenant, csv=CSV) -> str:
    run_id = workflow.create_run(db, tenant, "PAYROLL", None, None, "test")
    workflow.parse_run(db, run_id, tenant, csv)
    return run_id


def test_connector_lauf_buchen_und_stornieren(fach):
    db, _ = fach
    _konten(db, A, "6000", "1200")
    run_id = _lauf(db, A)
    assert db.execute(sa.text("SELECT DISTINCT tenant_id FROM domain_erp.fibu_connector_run_items WHERE run_id = :r"),
                      {"r": run_id}).scalars().all() == [A]
    with pytest.raises(ValueError):
        workflow.validate_run(db, run_id, B)
    workflow.validate_run(db, run_id, A)
    workflow.post_run(db, run_id, A)
    buchung = db.execute(sa.text(
        "SELECT id, period, total_debit, total_credit FROM domain_erp.journal_entries WHERE reference = :r AND tenant_id = :t"),
        {"r": run_id, "t": A}).one()
    assert (buchung.period, float(buchung.total_debit), float(buchung.total_credit)) == ("2026-10", 100.5, 100.5)
    assert db.execute(sa.text("SELECT count(*) FROM domain_erp.journal_entry_lines WHERE journal_entry_id = :e"),
                      {"e": buchung.id}).scalar() == 2
    with pytest.raises(ValueError):
        workflow.post_run(db, run_id, A)  # gebucht ist gebucht
    workflow.reverse_run(db, run_id, A)
    storno = db.execute(sa.text(
        "SELECT entry_number, reversed_entry_id FROM domain_erp.journal_entries WHERE reference = :r AND id <> :e"),
        {"r": run_id, "e": buchung.id}).one()
    assert storno.reversed_entry_id == buchung.id and storno.entry_number.startswith("STORNO-")


def test_connector_bucht_nichts_bei_fehlendem_konto(fach):
    db, _ = fach
    _konten(db, A, "6000")  # 1200 fehlt
    run_id = _lauf(db, A)
    workflow.validate_run(db, run_id, A)
    with pytest.raises(ValueError, match="Konto 1200 fehlt"):
        workflow.post_run(db, run_id, A)
    assert db.execute(sa.text("SELECT count(*) FROM domain_erp.journal_entries WHERE reference = :r"),
                      {"r": run_id}).scalar() == 0


def test_connector_wiederholter_upload_liest_nicht_neu_ein(fach):
    db, _ = fach
    schluessel = f"idem-{uuid4().hex[:6]}"
    run_id = workflow.create_run(db, A, "PAYROLL", None, schluessel, "test")
    workflow.parse_run(db, run_id, A, CSV)
    assert workflow.find_run(db, A, "PAYROLL", schluessel) == (run_id, "PARSED")
    assert workflow.find_run(db, B, "PAYROLL", schluessel) is None


def test_connector_profil_nur_eigener_mandant(fach):
    db, _ = fach
    profil = str(uuid4())
    db.execute(sa.text(
        "INSERT INTO domain_erp.fibu_connector_profiles (id, tenant_id, connector_type, name, settings, mapping) "
        "VALUES (:i, :t, 'PAYROLL', 'fremd', CAST(:s AS jsonb), '{}'::jsonb)"),
        {"i": profil, "t": B, "s": '{"delimiter": ","}'})
    run_id = workflow.create_run(db, A, "PAYROLL", profil, None, "test")
    workflow.parse_run(db, run_id, A, CSV)  # fremdes Profil (Komma) greift nicht, Standard-Semikolon schon
    assert db.execute(sa.text("SELECT counts->>'lines_total' FROM domain_erp.fibu_connector_runs WHERE id = :r"),
                      {"r": run_id}).scalar() == "1"


def test_jeder_weg_nimmt_den_mandanten_aus_dem_token():
    funde = []
    for modul in (debitoren, kreditoren, export, connectors):
        for route in modul.router.routes:
            parameter = inspect.signature(route.endpoint).parameters
            if "db" not in parameter:
                continue
            if "tenant_id" not in parameter:
                funde.append(f"{modul.__name__}:{route.path}:ohne Mandant")
            elif getattr(parameter["tenant_id"].default, "dependency", None) is not get_tenant_id:
                funde.append(f"{modul.__name__}:{route.path}:tenant_id")
    assert funde == []
