"""Row-level security for the inventory master data and stock documents (RLS domain slice inventory).

Separate policies per command, named like P3/P5/P6 (docs/architecture/rls-domaenen-entscheidungsmatrix.md,
§3): articles, warehouses with zones, bins and stock, stock movements, counts, lots, preparation lists,
shipping units and EPCIS events belong to one tenant; no shared 'system' rows are readable.

Not part of this slice: the silo and material flow tables (``silos``, ``silo_cells``, ``silo_lots``,
``silo_lot_movements``, ``silo_systems``, ``material_flow_*``; open lead claim on the material flow SQL),
``agrar_contracts`` and ``weighing_tickets`` (agrar domain) and the tables of the inventory service
``public.inventory_*`` (service identity first). Their references to articles and warehouses keep their
single-column keys until their slice.

Children hang under their parent over ``(parent key, tenant_id)``: FK checks bypass RLS, so only the
key stops a row under or pointing at a parent of another tenant, also when re-pointing, and a parent
with children cannot change tenant. ``article_suppliers``, ``stock_locations``, the drying rule rows
and the harvest acceptance lines and positions had no tenant; they take it from their parent
(backfilled, NOT NULL, default from the context). Tables already under RLS (P5) that point at these
parents only get the key, their policies stay as they are. ON DELETE behaviour is kept; SET NULL only
clears the reference column (PG15), never the tenant.

Rows without a tenant or with a placeholder ('', 'default', 'system') and rows pointing at a parent of
another tenant block the migration.
"""
from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision = "rls_domain_inventory_20261027"
down_revision = "rls_domain_crm_20261027"
branch_labels = None
depends_on = None

INV = "domain_inventory"
ARTICLES, WAREHOUSES = f"{INV}.articles", f"{INV}.warehouses"
ZONES, BINS, AISLES = f"{INV}.warehouse_zones", f"{INV}.warehouse_bins", f"{INV}.warehouse_aisles"
LOCATIONS, MOVEMENTS = f"{INV}.stock_locations", f"{INV}.inventory_stock_movements"
COUNTS, PREP_LISTS = f"{INV}.inventory_counts", f"{INV}.preparation_lists"
DRYING_RULES, HARVEST = f"{INV}.drying_rule_sets", f"{INV}.harvest_acceptances"
PARTNERS = "domain_crm.business_partners"

POLICY_TABLES = tuple(f"{INV}.{name}" for name in (
    "articles", "article_batches", "article_documents", "article_selections", "article_suppliers",
    "warehouses", "warehouse_zones", "warehouse_bins", "bin_stock", "stock_locations",
    "stock_item", "stock_movement", "stock_movements", "inventory_stock_movements",
    "inventory_counts", "inventory_count_lines", "inventory_lots", "inventory_lot_movements",
    "preparation_lists", "preparation_list_lines", "shipping_units", "epcis_events",
    "nawaro_print_notifications", "drying_rule_factor_ranges", "drying_rule_lookup_rows",
    "harvest_acceptance_lines", "harvest_acceptance_positions",
))
# Kinder ohne Mandant: tenant_id kommt vom ersten Eltern in LINKS.
NEW_TENANT_COLUMN = tuple(f"{INV}.{name}" for name in (
    "article_suppliers", "stock_locations", "drying_rule_factor_ranges", "drying_rule_lookup_rows",
    "harvest_acceptance_lines", "harvest_acceptance_positions",
))
NULLABLE_TENANT = tuple(f"{INV}.{name}" for name in (
    "articles", "warehouses", "stock_item", "stock_movement", "stock_movements",
    "inventory_lot_movements", "nawaro_print_notifications",
))


def _link(child: str, column: str, parent: str, key: str = "id", on_delete: str = "NO ACTION"):
    return (child if "." in child else f"{INV}.{child}", column, parent, key, on_delete)


# child, column, parent, parent key, ON DELETE
LINKS = (
    # Kinder ohne Mandant (der Mandant kommt vom ersten Eintrag)
    _link("article_suppliers", "article_id", ARTICLES),
    _link("stock_locations", "warehouse_id", WAREHOUSES),
    _link("drying_rule_factor_ranges", "rule_set_id", DRYING_RULES),
    _link("drying_rule_lookup_rows", "rule_set_id", DRYING_RULES),
    _link("harvest_acceptance_lines", "harvest_acceptance_id", HARVEST, on_delete="CASCADE"),
    _link("harvest_acceptance_positions", "harvest_acceptance_id", HARVEST, on_delete="CASCADE"),
    # Tabellen dieses Slices
    _link("article_suppliers", "partner_id", PARTNERS, "partner_id"),
    _link("article_batches", "article_id", ARTICLES),
    _link("article_batches", "warehouse_id", WAREHOUSES),
    _link("article_documents", "article_id", ARTICLES),
    _link("article_selections", "article_id", ARTICLES),
    _link("warehouse_zones", "warehouse_id", WAREHOUSES),
    _link("warehouse_bins", "warehouse_id", WAREHOUSES),
    _link("warehouse_bins", "zone_id", ZONES),
    _link("warehouse_bins", "aisle_id", AISLES),
    _link("bin_stock", "bin_id", BINS),
    _link("stock_movements", "article_id", ARTICLES),
    _link("stock_movements", "location_id", LOCATIONS),
    _link("stock_movements", "warehouse_id", WAREHOUSES),
    _link("inventory_stock_movements", "article_id", ARTICLES),
    _link("inventory_stock_movements", "bin_id", BINS),
    _link("inventory_stock_movements", "warehouse_id", WAREHOUSES),
    _link("inventory_counts", "warehouse_id", WAREHOUSES),
    _link("inventory_count_lines", "inventory_count_id", COUNTS),
    _link("inventory_count_lines", "article_id", ARTICLES),
    _link("inventory_count_lines", "warehouse_id", WAREHOUSES),
    _link("preparation_lists", "warehouse_id", WAREHOUSES),
    _link("preparation_list_lines", "list_id", PREP_LISTS),
    _link("preparation_list_lines", "article_id", ARTICLES),
    _link("harvest_acceptance_positions", "article_id", ARTICLES),
    # P5-Tabellen: nur der Schluessel, Policies unveraendert
    _link("article_price_thresholds", "article_id", ARTICLES, on_delete="CASCADE"),
    _link("daily_prices", "article_id", ARTICLES, on_delete="SET NULL"),
    _link("price_adjustment_rules", "article_id", ARTICLES),
    _link("weighing_ticket_lines", "article_id", ARTICLES),
    _link("warehouse_transfer_lines", "article_id", ARTICLES),
    _link("stock_correction_lines", "article_id", ARTICLES),
    _link("pick_list_lines", "article_id", ARTICLES),
    _link("pick_list_lines", "bin_id", BINS),
    _link("lkw_annahme_queue", "article_id", ARTICLES, on_delete="SET NULL"),
    _link("nawaro_raps_profiles", "article_id", ARTICLES),
    _link("harvest_acceptances", "article_id", ARTICLES),
    _link("harvest_acceptances", "warehouse_id", WAREHOUSES),
    _link("harvest_acceptances", "stock_movement_id", MOVEMENTS),
    _link("harvest_acceptances", "forwarder_id", PARTNERS, "partner_id"),
    _link("harvest_acceptances", "intermediate_dealer_id", PARTNERS, "partner_id"),
    _link("bin_locations", "warehouse_id", WAREHOUSES),
    _link("warehouse_aisles", "warehouse_id", WAREHOUSES),
    _link("warehouse_aisles", "zone_id", ZONES),
    _link("warehouse_transfers", "from_warehouse_id", WAREHOUSES),
    _link("warehouse_transfers", "to_warehouse_id", WAREHOUSES),
    _link("stock_corrections", "warehouse_id", WAREHOUSES),
    _link("charge_lineage_links", "source_movement_id", MOVEMENTS, on_delete="SET NULL"),
    _link("charge_lineage_links", "target_movement_id", MOVEMENTS, on_delete="SET NULL"),
    _link("domain_sales.delivery_note_positions", "artikel_id", ARTICLES, on_delete="SET NULL"),
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
    locked = sorted(set(present) | {link[0] for link in links} | {link[2] for link in links})
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
    for table in NEW_TENANT_COLUMN:
        if table in present:
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
    # uq_business_partners_partner_id_tenant gehoert rls_domain_crm_20261027 und bleibt.
    for parent, key in sorted({(link[2], link[3]) for link in LINKS if link[2] != PARTNERS}):
        if _exists(bind, parent):
            op.execute(f"ALTER TABLE {parent} DROP CONSTRAINT IF EXISTS uq_{_name(parent)}_{key}_tenant")
    for table in NEW_TENANT_COLUMN:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} DROP COLUMN IF EXISTS tenant_id")
    for table in NULLABLE_TENANT:
        if _exists(bind, table):
            op.execute(f"ALTER TABLE {table} ALTER COLUMN tenant_id DROP NOT NULL")
