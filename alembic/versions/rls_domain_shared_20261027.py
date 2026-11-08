"""Row-level security for tenant tables in domain_shared (RLS domain slice shared).

Separate policies per command, named like P3/P5/P6 (docs/architecture/rls-domaenen-entscheidungsmatrix.md,
§3): branches, master data, dispatchers, farmers, calendar items, internal messages, direct debit items,
feed master data (single and compound feed, recipes, production orders, ground feed analyses) and the
small condition tables belong to one tenant; no shared 'system' rows are readable. The live data holds no
'system' row in any of them, and the code reads none (the "shared" hits in the matrix concern nutrient
definitions and articles, not these tables).

Children without a tenant (recipe components, thread audit items, job artifacts, commission scales and
their lines, surcharge conditions) take it from their parent (backfilled, NOT NULL, default from the
context). Children hang under their parent over ``(parent key, tenant_id)``: FK checks bypass RLS, so
only the key stops a row under or pointing at a parent of another tenant, also when re-pointing. Tables
already under RLS (P5 and other domains) only get the key. ``public.number_series`` defaulted
``tenant_id`` to 'default' and now defaults to the tenant of the context.

Not here: identity tables (users, API keys, ICS tokens), outbox events (the publisher reads across
tenants), audit logs and policy rules (rows without or with a shared tenant; origin to be settled).

Rows without a tenant or with a placeholder ('', 'default', 'system') and rows pointing at a parent of
another tenant block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_shared_20261027"
down_revision = "rls_domain_einkauf_20261027"
branch_labels = None
depends_on = None

SH = "domain_shared"
BRANCHES, SINGLE_FEED, COMPOUND_FEED = f"{SH}.branches", f"{SH}.futtermittel_einzelfutter", f"{SH}.futtermittel_mischfutter"
RECIPES, ANALYSES = f"{SH}.futtermittel_rezepte", f"{SH}.grundfutter_analysen"
SCALES = f"{SH}.vertreter_provisionsstaffeln"

POLICY_TABLES = (
    f"{SH}.agrar_sorten", f"{SH}.artikel_sperren", BRANCHES, f"{SH}.calendar_items",
    f"{SH}.calendar_team_memberships", f"{SH}.direct_debit_items", f"{SH}.dispatchers", f"{SH}.farmers",
    f"{SH}.feeding_feed_analysis_findings", f"{SH}.feeding_feed_analysis_revisions",
    f"{SH}.feeding_feed_analysis_values", SINGLE_FEED, COMPOUND_FEED, f"{SH}.futtermittel_produktionsauftraege",
    RECIPES, ANALYSES, f"{SH}.internal_messages", f"{SH}.logistik_frachttabellen", f"{SH}.master_data_entries",
    f"{SH}.rations_zugang", "public.number_series",
    # Kinder ohne Mandant
    f"{SH}.channel_thread_audit_items", f"{SH}.futtermittel_rezept_komponenten", f"{SH}.job_artifacts",
    SCALES, f"{SH}.vertreter_staffel_zeilen", f"{SH}.zu_abschlag_konditionen",
)
# Kinder ohne Mandant: tenant_id kommt vom ersten Eltern in LINKS (Staffelzeilen ueber die Staffel).
NEW_TENANT_COLUMN = (
    f"{SH}.channel_thread_audit_items", f"{SH}.futtermittel_rezept_komponenten", f"{SH}.job_artifacts",
    SCALES, f"{SH}.vertreter_staffel_zeilen", f"{SH}.zu_abschlag_konditionen",
)
NULLABLE_TENANT = ("public.number_series",)
# Spaltenvorgabe 'default' -> Kontext.
DEFAULT_TO_CONTEXT = ("public.number_series",)

# child, column, parent, parent key, ON DELETE
LINKS = (
    # Kinder ohne Mandant (der Mandant kommt vom ersten Eintrag; die Staffel vor ihren Zeilen)
    (f"{SH}.channel_thread_audit_items", "thread_id", f"{SH}.channel_process_threads", "thread_id", "CASCADE"),
    (f"{SH}.futtermittel_rezept_komponenten", "rezept_id", RECIPES, "id", "CASCADE"),
    (f"{SH}.job_artifacts", "job_id", f"{SH}.jobs", "id", "CASCADE"),
    (SCALES, "gruppe_id", f"{SH}.vertreter_provisionsgruppen", "id", "NO ACTION"),
    (f"{SH}.vertreter_staffel_zeilen", "staffel_id", SCALES, "id", "NO ACTION"),
    (f"{SH}.zu_abschlag_konditionen", "gruppe_id", f"{SH}.zu_abschlaggruppen", "id", "NO ACTION"),
    # weitere Verweise dieses Slices
    (f"{SH}.zu_abschlag_konditionen", "klasse_id", f"{SH}.zu_abschlagklassen", "id", "NO ACTION"),
    (f"{SH}.futtermittel_rezept_komponenten", "einzelfutter_id", SINGLE_FEED, "id", "NO ACTION"),
    (RECIPES, "mischfutter_id", COMPOUND_FEED, "id", "NO ACTION"),
    (f"{SH}.futtermittel_produktionsauftraege", "rezept_id", RECIPES, "id", "NO ACTION"),
    (ANALYSES, "feed_id", SINGLE_FEED, "id", "RESTRICT"),
    (f"{SH}.feeding_feed_analysis_findings", "analysis_id", ANALYSES, "id", "CASCADE"),
    (f"{SH}.feeding_feed_analysis_revisions", "analysis_id", ANALYSES, "id", "RESTRICT"),
    (f"{SH}.feeding_feed_analysis_values", "analysis_id", ANALYSES, "id", "CASCADE"),
    # Tabellen anderer Domains: nur der Schluessel, Policies unveraendert
    ("domain_sales.delivery_notes", "branch_id", BRANCHES, "id", "SET NULL"),
    ("domain_inventory.harvest_acceptances", "branch_id", BRANCHES, "id", "NO ACTION"),
    ("domain_agrar.feeding_feed_products", "feed_id", SINGLE_FEED, "id", "NO ACTION"),
    ("domain_agrar.feeding_feed_reference_values", "feed_id", SINGLE_FEED, "id", "NO ACTION"),
    ("domain_agrar.feeding_feed_revisions", "feed_id", SINGLE_FEED, "id", "NO ACTION"),
)
OWN = "tenant_id = public.rls_current_tenant()"
POLICIES = tuple(f"tenant_isolation_{kind}" for kind in ("select", "insert", "update", "delete"))


def _exists(bind, table: str) -> bool:
    return bind.execute(sa.text("SELECT to_regclass(:t)"), {"t": table}).scalar() is not None


def _name(table: str) -> str:
    return table.split(".")[1]


def _tenant_type(bind, table: str) -> str:
    return bind.execute(sa.text(
        "SELECT format_type(atttypid, atttypmod) FROM pg_attribute "
        "WHERE attrelid = to_regclass(:t) AND attname = 'tenant_id' AND NOT attisdropped"), {"t": table}).scalar()


def _single_fk(bind, child: str, column: str, parent: str) -> str | None:
    return bind.execute(sa.text(
        "SELECT k.conname FROM pg_constraint k JOIN pg_attribute a ON a.attrelid = k.conrelid "
        "AND a.attnum = k.conkey[1] WHERE k.contype = 'f' AND k.conrelid = to_regclass(:c) "
        "AND k.confrelid = to_regclass(:p) AND cardinality(k.conkey) = 1 AND a.attname = :col"),
        {"c": child, "p": parent, "col": column}).scalar()


def _has_unique(bind, parent: str, key: str) -> bool:
    return bind.execute(sa.text(
        "SELECT 1 FROM pg_constraint k WHERE k.conrelid = to_regclass(:p) AND k.contype IN ('u', 'p') "
        "AND (SELECT array_agg(a.attname::text ORDER BY a.attname) FROM pg_attribute a "
        "     WHERE a.attrelid = k.conrelid AND a.attnum = ANY(k.conkey)) = ARRAY[:k, 'tenant_id']::text[]"),
        {"p": parent, "k": key}).scalar() is not None


def _on_delete(column: str, on_delete: str) -> str:
    # Ein Verbund-FK mit SET NULL leert sonst auch tenant_id (NOT NULL); PG15 leert nur die Verweisspalte.
    return f"SET NULL ({column})" if on_delete == "SET NULL" else on_delete


def _enable(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"CREATE POLICY tenant_isolation_select ON {table} FOR SELECT USING ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_insert ON {table} FOR INSERT WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_update ON {table} FOR UPDATE USING ({OWN}) WITH CHECK ({OWN})")
    op.execute(f"CREATE POLICY tenant_isolation_delete ON {table} FOR DELETE USING ({OWN})")


def _disable(table: str) -> None:
    for name in POLICIES:
        op.execute(f"DROP POLICY IF EXISTS {name} ON {table}")
    op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")


def upgrade() -> None:
    bind = op.get_bind()
    links = [link for link in LINKS if _exists(bind, link[0]) and _exists(bind, link[2])]
    present = [t for t in POLICY_TABLES if _exists(bind, t)]
    defaults = [t for t in DEFAULT_TO_CONTEXT if _exists(bind, t)]
    locked = sorted(set(present) | set(defaults) | {link[0] for link in links} | {link[2] for link in links})
    op.execute(f"LOCK TABLE {', '.join(locked)} IN ACCESS EXCLUSIVE MODE")

    backfilled = set()
    for child, column, parent, key, _ in links:
        if child in NEW_TENANT_COLUMN and child not in backfilled:
            backfilled.add(child)
            op.execute(f"ALTER TABLE {child} ADD COLUMN tenant_id {_tenant_type(bind, parent)}")
            op.execute(f"UPDATE {child} c SET tenant_id = p.tenant_id FROM {parent} p WHERE p.{key} = c.{column}")

    for table in present:
        unclear = bind.execute(sa.text(
            f"SELECT count(*) FROM {table} WHERE tenant_id IS NULL OR tenant_id IN ('', 'default', 'system')"
        )).scalar()
        if unclear:
            raise RuntimeError(
                f"{table}: {unclear} Zeilen ohne eindeutigen Mandanten; Herkunft klaeren, "
                "nicht pauschal zuordnen (rls-domaenen-entscheidungsmatrix.md)"
            )
    for table in NEW_TENANT_COLUMN + NULLABLE_TENANT:
        if table in present:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET NOT NULL")
    for table in NEW_TENANT_COLUMN + tuple(defaults):
        if table in present or table in defaults:
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT public.rls_current_tenant()")

    for child, column, parent, key, _ in links:
        foreign = bind.execute(sa.text(
            f"SELECT count(*) FROM {child} c JOIN {parent} p ON p.{key} = c.{column} "
            "WHERE p.tenant_id IS DISTINCT FROM c.tenant_id")).scalar()
        if foreign:
            raise RuntimeError(f"{child}.{column}: {foreign} Zeilen verweisen auf {parent} eines anderen Mandanten")
    for parent, key in sorted({(link[2], link[3]) for link in links}):
        if not _has_unique(bind, parent, key):
            op.execute(f"ALTER TABLE {parent} ADD CONSTRAINT uq_{_name(parent)}_{key}_tenant UNIQUE ({key}, tenant_id)")
    for child, column, parent, key, on_delete in links:
        old = _single_fk(bind, child, column, parent)
        if old:
            op.execute(f"ALTER TABLE {child} DROP CONSTRAINT {old}")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT fk_{_name(child)}_{column}_tenant FOREIGN KEY ({column}, tenant_id) "
            f"REFERENCES {parent} ({key}, tenant_id) ON DELETE {_on_delete(column, on_delete)}"
        )

    for table in present:
        _enable(table)


def downgrade() -> None:
    bind = op.get_bind()
    for table in POLICY_TABLES:
        if _exists(bind, table):
            _disable(table)
    for child, column, parent, key, on_delete in LINKS:
        if not (_exists(bind, child) and _exists(bind, parent)):
            continue
        op.execute(f"ALTER TABLE {child} DROP CONSTRAINT IF EXISTS fk_{_name(child)}_{column}_tenant")
        op.execute(
            f"ALTER TABLE {child} ADD CONSTRAINT {_name(child)}_{column}_fkey FOREIGN KEY ({column}) "
            f"REFERENCES {parent} ({key}) ON DELETE {on_delete}"
        )
    for parent, key in sorted({(link[2], link[3]) for link in LINKS}):
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS uq_{_name(parent)}_{key}_tenant")
    for table in NEW_TENANT_COLUMN:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id")
    for table in NULLABLE_TENANT:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP NOT NULL")
    for table in DEFAULT_TO_CONTEXT:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id SET DEFAULT 'default'")
