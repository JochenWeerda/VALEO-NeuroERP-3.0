"""RLS-Domain ops, Teil 1: Kontrakte und PCN-Meldungen getrennt, Vorgaben aus dem Kontext, Eindeutigkeit je Mandant,
Kinder ueber Verbundschluessel.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt).
"""

from __future__ import annotations

import pytest
import sqlalchemy as sa

import rls_domain_support as support
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

OPS = "domain_ops"
CONTRACT, LINE, PROJECT, PLANT, SPINE, VEHICLE = (
    f"{OPS}.kon_contract", f"{OPS}.kon_contract_line", f"{OPS}.ops_projekte", f"{OPS}.ops_wartung_anlagen",
    f"{OPS}.ops_flow_spine_instances", f"{OPS}.ops_fahrzeuge",
)
ISOLATED = (CONTRACT, f"{OPS}.ops_pcn_meldungen")
LINKS = (
    (LINE, "contract_id", CONTRACT),
    (f"{OPS}.kon_contract_movement", "contract_id", CONTRACT),
    (f"{OPS}.kon_contract_movement", "line_id", LINE),
    (f"{OPS}.ops_projekt_aufgaben", "projekt_id", PROJECT),
    (f"{OPS}.ops_wartungs_protokolle", "anlage_id", PLANT),
    (f"{OPS}.ops_flow_spine_instance_documents", "instance_id", SPINE),
    (f"{OPS}.ops_flow_spine_instance_events", "instance_id", SPINE),
    (f"{OPS}.ops_fuhrpark_rechnungen", "fahrzeug_id", VEHICLE),
)
PARENTS = (CONTRACT, LINE, PROJECT, PLANT, SPINE, VEHICLE)
KEYS = {CONTRACT: "contract_id", LINE: "line_id"}
CHILDREN = tuple(dict.fromkeys(child for child, _, _ in LINKS))
DEFAULT_TO_CONTEXT = (
    f"{OPS}.edi_nachrichten", f"{OPS}.ops_flow_spine_instances", f"{OPS}.ops_flow_spine_instance_events",
    f"{OPS}.ops_flow_spine_instance_documents", f"{OPS}.ops_projekte", f"{OPS}.ops_projekt_aufgaben",
    f"{OPS}.ops_tank_bestand", f"{OPS}.ops_verladungen", f"{OPS}.ops_versicherungen", f"{OPS}.ops_wartung_anlagen",
    f"{OPS}.ops_wartungs_protokolle", f"{OPS}.ops_zapfungen", f"{OPS}.ops_pcn_meldungen", VEHICLE,
    f"{OPS}.ops_fuhrpark_ausgehende_dokumente", f"{OPS}.ops_fuhrpark_rechnungen", f"{OPS}.ops_fuhrpark_terminarten",
)
PER_TENANT_UNIQUE = (
    (f"{OPS}.ops_tank_bestand", "artikel"),
    (f"{OPS}.ops_versicherungen", "vertragsnummer"),
    (f"{OPS}.edi_partner", "gln"),
    (f"{OPS}.edi_nachrichten", "nachricht_id"),
)


def _key(conn, table: str) -> str:
    return KEYS.get(table) or support.primary_key(conn, table)


def _links_of(table: str):
    return [(column, parent) for child, column, parent in LINKS if child == table]


@pytest.fixture(scope="module")
def probe():
    tables = tuple(dict.fromkeys(ISOLATED + PARENTS + CHILDREN + tuple(t for t, _ in PER_TENANT_UNIQUE)))
    with support.probe(tables) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            for table in tuple(dict.fromkeys(PARENTS + ISOLATED + CHILDREN)):
                links = {column: rows[parent, tenant] for column, parent in _links_of(table) if (parent, tenant) in rows}
                full = support.seed_row(conn, table, tenant, **links)
                rows["full", table, tenant] = full
                rows[table, tenant] = str(full[_key(conn, table)])
        for parent in PARENTS:
            links = {column: rows[p, B] for column, p in _links_of(parent)}
            rows["spare", parent] = str(support.seed_row(conn, parent, B, **links)[_key(conn, parent)])
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
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM], key=_key(conn, table))


def _other_references(conn, rows, child: str, column: str) -> dict:
    full = rows["full", child, A]
    columns = {c for _, cols, parent, _ in conn.execute(sa.text(support.FKS_SQL), {"t": child})
               for c in cols if parent != "domain_shared.tenants"}
    return {c: full[c] for c in columns - {column, "tenant_id"} if full.get(c) is not None}


@pytest.mark.parametrize("child,column,parent", LINKS, ids=[f"{c.split('.')[1]}.{col}" for c, col, _ in LINKS])
def test_kein_verweis_auf_fremden_eltern(db, child, column, parent):
    conn, rows = db
    foreign = rows["spare", parent]
    constraint = f"fk_{child.split('.')[1]}_{column}_tenant"[:63]
    with tenant_scope(A, "test"):
        message = support.rejected_insert_with(conn, child, A, _key(conn, child), **{column: foreign},
                                               **_other_references(conn, rows, child, column))
        assert constraint in message, message
        message = support.rejected(conn, f"UPDATE {child} SET {column} = :p WHERE {_key(conn, child)} = :i",
                                   {"p": foreign, "i": rows[child, A]})
    assert constraint in message, message


def test_eltern_mit_verweisen_behaelt_seinen_mandanten(db):
    conn, rows = db
    for parent in PARENTS:
        message = support.as_owner_rejected(conn, f"UPDATE {parent} SET tenant_id = :b WHERE {_key(conn, parent)} = :i",
                                            {"b": B, "i": rows[parent, A]})
        assert "foreign key constraint" in message and "_tena" in message, (parent, message)


def test_vorgabe_ist_der_kontext_nicht_default(db):
    """'default' bzw. 'legacy-unassigned' als Vorgabe von tenant_id; jetzt der Mandant des Kontexts."""
    conn, _ = db
    for table in DEFAULT_TO_CONTEXT:
        default = conn.execute(sa.text(
            "SELECT pg_get_expr(d.adbin, d.adrelid) FROM pg_attrdef d JOIN pg_attribute a "
            "ON a.attrelid = d.adrelid AND a.attnum = d.adnum WHERE d.adrelid = to_regclass(:t) "
            "AND a.attname = 'tenant_id'"), {"t": table}).scalar()
        assert default == "rls_current_tenant()", (table, default)


@pytest.mark.parametrize("table,column", PER_TENANT_UNIQUE, ids=[f"{t.split('.')[1]}.{c}" for t, c in PER_TENANT_UNIQUE])
def test_eindeutig_je_mandant_nicht_systemweit(db, table, column):
    conn, rows = db
    wert = f"gleich-{column}"[:20]
    for tenant in (A, B):
        with tenant_scope(tenant, "test"):
            support.insert_row(conn, table, tenant, _key(conn, table), **{column: wert})
    with tenant_scope(A, "test"):
        message = support.rejected_insert_with(conn, table, A, _key(conn, table), **{column: wert})
    assert f"uq_{table.split('.')[1]}_tenant_{column}" in message, message


def test_kontextwechsel_savepoint_hintergrund(db):
    conn, rows = db
    support.assert_context_switch_and_savepoint(conn, CONTRACT, rows[CONTRACT, A], rows[CONTRACT, B], key="contract_id")
    support.assert_background_needs_explicit_context(conn, CONTRACT, rows[CONTRACT, A], rows[CONTRACT, B], key="contract_id")
