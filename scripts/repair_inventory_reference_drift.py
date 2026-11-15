"""Restore two already-migrated inventory references on an existing database.

Default: read-only plan. Explicit --anwenden applies; --anwenden --rollback
executes and verifies the same DDL but rolls back. URLs come only from the named
environment variable (default DATABASE_URL). Never stamps or runs migrations.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SCHEMA = "domain_inventory"
BINS, AISLES = "warehouse_bins", "warehouse_aisles"
QUEUE, ARTICLES = "lkw_annahme_queue", "articles"
TABLES = (BINS, AISLES, QUEUE, ARTICLES)
FK, TENANT_FK, INDEX = "fk_wb_aisle", "fk_warehouse_bins_aisle_id_tenant", "idx_wb_aisle"
WMS_REV = "wms_warehouse_aisles_20260612"
QUEUE_REV = "lkw_annahme_queue_article_reference_20260328"
RLS_REV = "rls_domain_inventory_20261027"
APP_NAME = "agent:codex-inventory-reference-drift"


@dataclass(frozen=True)
class Reference:
    child: str
    column: str
    parent: str
    sql_type: str
    catalog_type: str
    fk: str
    tenant_fk: str
    index: str
    delete_code: str
    delete_sql: str

    def additions(self) -> tuple[str, str, str]:
        return (
            f"ALTER TABLE {SCHEMA}.{self.child} ADD COLUMN {self.column} {self.sql_type} NULL",
            f"ALTER TABLE {SCHEMA}.{self.child} ADD CONSTRAINT {self.fk} FOREIGN KEY ({self.column}) "
            f"REFERENCES {SCHEMA}.{self.parent} (id){self.delete_sql}",
            f"CREATE INDEX {self.index} ON {SCHEMA}.{self.child} ({self.column})",
        )


# Closed list: no caller-supplied identifiers, types, SQL or additional references.
REFERENCES = (
    Reference(BINS, "aisle_id", AISLES, "VARCHAR(36)", "character varying(36)", FK, TENANT_FK, INDEX, "a", ""),
    Reference(QUEUE, "article_id", ARTICLES, "VARCHAR", "character varying", "fk_lkw_annahme_queue_article_id",
              "fk_lkw_annahme_queue_article_id_tenant", "ix_lkw_annahme_queue_article_id", "n", " ON DELETE SET NULL"),
)


class RepairError(ValueError):
    """A bounded, credential-free diagnostic safe for CLI output."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RepairError(message)


def revision_has_inventory(revision: str) -> bool:
    """Use the repository DAG, not dates or string ordering, for repair eligibility."""
    from alembic.script import ScriptDirectory

    script = ScriptDirectory(str(ROOT / "alembic"))
    seen: set[str] = set()
    pending = [revision]
    while pending:
        item = pending.pop()
        if item in seen:
            continue
        node = script.get_revision(item)
        require(node is not None, "Unbekannte Repository-Revision")
        seen.add(node.revision)
        parents = node.down_revision
        pending.extend((parents,) if isinstance(parents, str) else parents or ())
    require(WMS_REV in seen, "Revision liegt vor dem kanonischen WMS-Vertrag")
    require(QUEUE_REV in seen, "Revision liegt vor dem kanonischen LKW-Artikelvertrag")
    return RLS_REV in seen


def inspect_catalog(conn) -> dict:
    table_rows = conn.execute(text("""
        SELECT c.relname, c.relkind, pg_get_userbyid(c.relowner) AS owner,
               c.relrowsecurity AS rls, c.relforcerowsecurity AS force_rls
        FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = :schema AND c.relname = ANY(:tables)
    """), {"schema": SCHEMA, "tables": list(TABLES)}).mappings()
    tables = {r["relname"]: dict(r) for r in table_rows}
    columns = conn.execute(text("""
        SELECT c.relname, a.attname, format_type(a.atttypid, a.atttypmod) AS type,
               a.attnotnull AS not_null, a.attgenerated AS generated,
               pg_get_expr(d.adbin, d.adrelid) AS default_value
        FROM pg_attribute a JOIN pg_class c ON c.oid = a.attrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        LEFT JOIN pg_attrdef d ON d.adrelid = a.attrelid AND d.adnum = a.attnum
        WHERE n.nspname = :schema AND c.relname = ANY(:tables)
          AND a.attnum > 0 AND NOT a.attisdropped
    """), {"schema": SCHEMA, "tables": list(TABLES)}).mappings()
    constraints = conn.execute(text("""
        SELECT c.relname AS table_name, k.conname AS name, k.contype AS kind,
               ARRAY(SELECT a.attname::text FROM unnest(k.conkey) WITH ORDINALITY x(num, pos)
                     JOIN pg_attribute a ON a.attrelid=k.conrelid AND a.attnum=x.num ORDER BY x.pos) AS columns,
               pn.nspname AS parent_schema, p.relname AS parent,
               ARRAY(SELECT a.attname::text FROM unnest(k.confkey) WITH ORDINALITY x(num, pos)
                     JOIN pg_attribute a ON a.attrelid=k.confrelid AND a.attnum=x.num ORDER BY x.pos) AS parent_columns,
               k.convalidated AS validated, k.condeferrable AS deferrable,
               ARRAY(SELECT a.attname::text FROM unnest(k.confdelsetcols) WITH ORDINALITY x(num, pos)
                     JOIN pg_attribute a ON a.attrelid=k.conrelid AND a.attnum=x.num ORDER BY x.pos) AS delete_columns,
               k.confdeltype AS on_delete, k.confupdtype AS on_update, k.confmatchtype AS match
        FROM pg_constraint k JOIN pg_class c ON c.oid=k.conrelid
        JOIN pg_namespace n ON n.oid=c.relnamespace
        LEFT JOIN pg_class p ON p.oid=k.confrelid LEFT JOIN pg_namespace pn ON pn.oid=p.relnamespace
        WHERE n.nspname=:schema AND c.relname=ANY(:tables)
        ORDER BY c.relname, k.conname
    """), {"schema": SCHEMA, "tables": list(TABLES)}).mappings()
    indexes = conn.execute(text("""
        SELECT ic.relname AS name, tc.relname AS table_name, am.amname AS method,
               i.indisvalid AS valid, i.indisready AS ready, i.indisunique AS unique,
               i.indnatts AS attributes, i.indnkeyatts AS keys,
               pg_get_expr(i.indpred,i.indrelid) AS predicate,
               pg_get_indexdef(ic.oid,1,true) AS first_column,
               pg_get_indexdef(ic.oid) AS definition
        FROM pg_class ic JOIN pg_namespace n ON n.oid=ic.relnamespace
        LEFT JOIN pg_index i ON i.indexrelid=ic.oid LEFT JOIN pg_class tc ON tc.oid=i.indrelid
        LEFT JOIN pg_am am ON am.oid=ic.relam
        WHERE n.nspname=:schema AND ic.relname=ANY(:names)
    """), {"schema": SCHEMA, "names": [ref.index for ref in REFERENCES]}).mappings()
    policies = conn.execute(text("""
        SELECT tablename, policyname, permissive, roles, cmd, qual, with_check
        FROM pg_policies WHERE schemaname=:schema AND tablename=ANY(:tables)
        ORDER BY tablename,policyname
    """), {"schema": SCHEMA, "tables": list(TABLES)}).mappings()
    return {"tables": tables, "columns": {(r["relname"], r["attname"]): dict(r) for r in columns},
            "constraints": [dict(r) for r in constraints], "indexes": [dict(r) for r in indexes],
            "policies": [dict(r) for r in policies]}


def repair_plan(catalog: dict, *, inventory_applied: bool) -> list[str]:
    tables, columns, constraints = catalog["tables"], catalog["columns"], catalog["constraints"]
    for table in TABLES:
        require(table in tables and tables[table]["relkind"] == "r", "WMS-Elterntabellen fehlen oder sind keine normalen Tabellen")
        require(tables[table]["owner"] == "valeo_owner", "WMS-Tabellen gehoeren nicht valeo_owner")
        names = ("id", "tenant_id", "zone_id", "warehouse_id") if table in (BINS, AISLES) else ("id", "tenant_id")
        for name in names:
            col = columns.get((table, name))
            expected_type = ("character varying" if table in (QUEUE, ARTICLES) else
                             "character varying(64)" if name == "tenant_id" else "character varying(36)")
            require(col is not None and col["type"] == expected_type and col["not_null"]
                    and not col["generated"], f"Unvereinbarer WMS-Schluesselvertrag: {table}.{name}")
        require(any(c["table_name"] == table and c["kind"] == "p" and c["columns"] == ["id"]
                    for c in constraints), f"Primaerschluessel fehlt: {table}.id")
    return [statement for ref in REFERENCES for statement in reference_plan(catalog, ref, inventory_applied)]


def reference_plan(catalog: dict, ref: Reference, inventory_applied: bool) -> list[str]:
    column = catalog["columns"].get((ref.child, ref.column))
    related = [c for c in catalog["constraints"] if c["table_name"] == ref.child and
               (c["name"] in (ref.fk, ref.tenant_fk) or ref.column in c["columns"])]
    index = [i for i in catalog["indexes"] if i["name"] == ref.index]
    add_column, add_fk, add_index = ref.additions()
    if column is None:
        require(not inventory_applied, "Fehlende Spalte nach Inventory-RLS: gesonderte Ursachenpruefung erforderlich")
        require(not related and not index, "Fehlende Spalte mit widerspruechlichen FK-/Indexobjekten")
        return [add_column, add_fk, add_index]
    require(column["type"] == ref.catalog_type and not column["not_null"]
            and not column["generated"] and column["default_value"] is None,
            f"{ref.child}.{ref.column} entspricht nicht dem kanonischen Vertrag")
    expected_name = ref.tenant_fk if inventory_applied else ref.fk
    expected_columns = [ref.column, "tenant_id"] if inventory_applied else [ref.column]
    expected_parent = ["id", "tenant_id"] if inventory_applied else ["id"]
    for fk in related:
        require(fk["kind"] == "f" and fk["name"] == expected_name
                and fk["columns"] == expected_columns and fk["parent_columns"] == expected_parent
                and fk["parent_schema"] == SCHEMA and fk["parent"] == ref.parent
                and fk["validated"] and not fk["deferrable"] and fk["on_delete"] == ref.delete_code
                and fk["delete_columns"] == ([ref.column] if inventory_applied and ref.delete_code == "n" else [])
                and fk["on_update"] == "a" and fk["match"] == "s", f"Unvereinbarer {ref.column}-Fremdschluessel")
    require(len(related) <= 1 and (related or not inventory_applied), "Inventory-Verbund-FK fehlt oder ist mehrdeutig")
    if index:
        require(len(index) == 1, "Indexname ist mehrdeutig")
        i = index[0]
        require(i["table_name"] == ref.child and i["method"] == "btree" and i["valid"] and i["ready"]
                and not i["unique"] and i["attributes"] == i["keys"] == 1
                and i["predicate"] is None and i["first_column"] == ref.column, f"Unvereinbarer {ref.index}")
    return ([] if related else [add_fk]) + ([] if index else [add_index])


def check_identity(conn, expected_database: str, expected_revision: str, *, apply: bool) -> None:
    require(expected_database in ("valeo_neuro_erp", "valeo_probe"), "Datenbank ist nicht fuer diese Reparatur zugelassen")
    row = conn.execute(text("SELECT current_database(), session_user, current_user, rolsuper, rolbypassrls "
                            "FROM pg_roles WHERE rolname = session_user")).one()
    require(row[0] == expected_database, "Tatsaechliche Datenbank weicht vom erwarteten Ziel ab")
    revisions = list(conn.execute(text("SELECT version_num FROM public.alembic_version")).scalars())
    require(revisions == [expected_revision], "Alembic-Stand weicht von der erwarteten Einzelrevision ab")
    if apply:
        require(row[1] == "valeo_migrator" and row[2] == "valeo_owner", "Anwendung erfordert Login valeo_migrator und aktive Rolle valeo_owner")
        require(not row[3] and not row[4], "Migrator-Login darf weder Superuser noch BYPASSRLS besitzen")


def execute_repair(conn, expected_database: str, expected_revision: str, *, apply=False, rollback=False) -> list[str]:
    require(not rollback or apply, "--rollback benoetigt --anwenden")
    inventory_applied = revision_has_inventory(expected_revision)
    tx = conn.begin()
    try:
        if not apply:
            conn.execute(text("SET TRANSACTION READ ONLY"))
        conn.execute(text("SET LOCAL lock_timeout = '5s'"))
        conn.execute(text("SET LOCAL statement_timeout = '30s'"))
        check_identity(conn, expected_database, expected_revision, apply=apply)
        if apply:
            conn.execute(text("LOCK TABLE " + ", ".join(f"{SCHEMA}.{t}" for t in sorted(TABLES)) + " IN ACCESS EXCLUSIVE MODE"))
            conn.execute(text("LOCK TABLE public.alembic_version IN SHARE MODE"))
            check_identity(conn, expected_database, expected_revision, apply=True)
        before = inspect_catalog(conn)
        plan = repair_plan(before, inventory_applied=inventory_applied)
        if apply:
            counts = {t: conn.execute(text(f"SELECT count(*) FROM {SCHEMA}.{t}")).scalar_one() for t in TABLES}
            for statement in plan:
                conn.execute(text(statement))
            after = inspect_catalog(conn)
            require(not repair_plan(after, inventory_applied=inventory_applied), "Nachpruefung: Reparatur unvollstaendig")
            require(before["tables"] == after["tables"] and before["policies"] == after["policies"], "RLS-/Eigentumsvertrag hat sich geaendert")
            require(all(c in after["constraints"] for c in before["constraints"]), "Vorhandene Schluessel wurden geaendert")
            require(all(after["columns"].get(k) == v for k, v in before["columns"].items()), "Vorhandene Spalten wurden geaendert")
            require(all(conn.execute(text(f"SELECT count(*) FROM {SCHEMA}.{t}")).scalar_one() == n
                        for t, n in counts.items()), "Zeilenzahlen haben sich geaendert")
        if not apply or rollback:
            tx.rollback()
        else:
            tx.commit()
        return plan
    except BaseException:
        if tx.is_active:
            tx.rollback()
        raise


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expected-database", required=True, choices=("valeo_neuro_erp", "valeo_probe"))
    parser.add_argument("--expected-revision", required=True)
    parser.add_argument("--url-env", default="DATABASE_URL")
    parser.add_argument("--anwenden", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args(argv)
    engine = None
    try:
        require(not args.rollback or args.anwenden, "--rollback benoetigt --anwenden")
        raw = os.environ.get(args.url_env)
        require(bool(raw), "Verbindungsvariable fehlt")
        url = make_url(raw)
        require(url.get_backend_name() == "postgresql" and url.database == args.expected_database,
                "Verbindungsziel ist keine passende PostgreSQL-Datenbank")
        require(url.host in ("localhost", "127.0.0.1", "::1", "postgres") and (url.port or 5432) == 5432,
                "Nur der bestehende lokale PostgreSQL-Pruefstand auf Port 5432 ist zugelassen")
        require(not set(url.query).intersection({"host", "hostaddr", "port", "dbname", "user", "service", "servicefile"}),
                "Verbindungsparameter duerfen das gepruefte Ziel nicht ueberschreiben")
        if args.anwenden:
            require(url.username == "valeo_migrator", "Schreibverbindung muss valeo_migrator verwenden")
        engine = create_engine(url, connect_args={"application_name": APP_NAME, "connect_timeout": 5}, hide_parameters=True)
        with engine.connect() as conn:
            plan = execute_repair(conn, args.expected_database, args.expected_revision,
                                  apply=args.anwenden, rollback=args.rollback)
        print("PLAN" if not args.anwenden else "ZURUECKGEROLLT" if args.rollback else "ANGEWENDET")
        for statement in plan:
            print(statement)
        if not plan:
            print("Kanonischer Vertrag bereits vorhanden; keine Aenderung.")
        return 0
    except RepairError as exc:
        print(f"Abgebrochen: {exc}", file=sys.stderr)
        return 1
    except Exception:
        # Driver errors can contain URLs, SQL parameters or business data.
        print("Abgebrochen: Verbindungs-, Katalog- oder Transaktionsfehler; keine Zugangsdaten ausgegeben.", file=sys.stderr)
        return 1
    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    raise SystemExit(main())
