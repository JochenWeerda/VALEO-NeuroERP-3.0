"""Customer recipe cycle: recipes, versions, orders, deliveries (FEED-RECIPE-052).

Revision ID: feed_recipes_20260717
Revises: feed_rbac_audit_20260717
"""

from alembic import op

revision = "feed_recipes_20260717"
down_revision = "feed_rbac_audit_20260717"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Kundenrezeptur: eigene Artikelnummer je Kunde eindeutig.
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_customer_recipes (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      customer_ref VARCHAR(160) NOT NULL,
      artikel_nr VARCHAR(80) NOT NULL,
      name VARCHAR(200) NOT NULL,
      source_ration_ref VARCHAR(120),
      approved_version_id VARCHAR,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_customer_recipe_artikel UNIQUE (tenant_id, customer_ref, artikel_nr)
    )""")

    # Append-only Versionen (Optimal-Rezeptur je Freigabe).
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_recipe_versions (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      recipe_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_customer_recipes(id),
      version_no INTEGER NOT NULL CHECK (version_no > 0),
      components JSONB NOT NULL,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_recipe_version_no UNIQUE (tenant_id, recipe_id, version_no)
    )""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_recipe_version()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN RAISE EXCEPTION 'recipe versions are append-only'; END; $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_recipe_version ON domain_agrar.feeding_recipe_versions")
    op.execute("""CREATE TRIGGER trg_immutable_recipe_version
      BEFORE UPDATE OR DELETE ON domain_agrar.feeding_recipe_versions
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_recipe_version()""")

    # Bestellungen fixieren die freigegebene Version (Drift-Schutz).
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_recipe_orders (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      recipe_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_customer_recipes(id),
      recipe_version_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_recipe_versions(id),
      menge_t NUMERIC(18,3) NOT NULL CHECK (menge_t > 0),
      soll_components JSONB NOT NULL,
      idempotency_key VARCHAR(160) NOT NULL,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_recipe_order_idem UNIQUE (tenant_id, idempotency_key)
    )""")

    # Ruecklauf: Ist-Lieferung + Nachkalkulation, append-only, je Bestellung eine.
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_recipe_deliveries (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      order_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_recipe_orders(id),
      source VARCHAR(30) NOT NULL CHECK (source IN ('mixer','manual','import')),
      nachkalkulation JSONB NOT NULL,
      idempotency_key VARCHAR(160) NOT NULL,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_recipe_delivery_idem UNIQUE (tenant_id, idempotency_key),
      CONSTRAINT uq_recipe_delivery_order UNIQUE (tenant_id, order_id)
    )""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_recipe_delivery()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN RAISE EXCEPTION 'recipe deliveries are append-only'; END; $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_recipe_delivery ON domain_agrar.feeding_recipe_deliveries")
    op.execute("""CREATE TRIGGER trg_immutable_recipe_delivery
      BEFORE UPDATE OR DELETE ON domain_agrar.feeding_recipe_deliveries
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_recipe_delivery()""")

    op.execute("""CREATE INDEX IF NOT EXISTS ix_customer_recipes_customer
      ON domain_agrar.feeding_customer_recipes (tenant_id, customer_ref, name)""")
    op.execute("""CREATE INDEX IF NOT EXISTS ix_recipe_orders_recipe
      ON domain_agrar.feeding_recipe_orders (tenant_id, recipe_id, created_at DESC)""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_recipe_delivery ON domain_agrar.feeding_recipe_deliveries")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_recipe_delivery()")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_recipe_deliveries")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_recipe_orders_recipe")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_recipe_orders")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_recipe_version ON domain_agrar.feeding_recipe_versions")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_recipe_version()")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_recipe_versions")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_customer_recipes_customer")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_customer_recipes")
