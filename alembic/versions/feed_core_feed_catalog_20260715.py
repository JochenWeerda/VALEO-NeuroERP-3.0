"""Canonical feed catalog, products, values and revisions (FEED-CORE-018).

Revision ID: feed_core_feed_catalog_20260715
Revises: feed_core_reference_data_20260715
"""
from alembic import op

revision = "feed_core_feed_catalog_20260715"
down_revision = "feed_core_reference_data_20260715"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""ALTER TABLE domain_shared.futtermittel_einzelfutter
      ADD COLUMN IF NOT EXISTS feed_kind VARCHAR(30) NOT NULL DEFAULT 'other',
      ADD COLUMN IF NOT EXISTS species_scope VARCHAR(80),
      ADD COLUMN IF NOT EXISTS conservation_method VARCHAR(80),
      ADD COLUMN IF NOT EXISTS approval_status VARCHAR(30) NOT NULL DEFAULT 'draft',
      ADD COLUMN IF NOT EXISTS valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
      ADD COLUMN IF NOT EXISTS valid_until DATE,
      ADD COLUMN IF NOT EXISTS revision INTEGER NOT NULL DEFAULT 1,
      ADD COLUMN IF NOT EXISTS created_by VARCHAR(160) NOT NULL DEFAULT 'migration',
      ADD COLUMN IF NOT EXISTS updated_by VARCHAR(160) NOT NULL DEFAULT 'migration'""")
    op.execute("""UPDATE domain_shared.futtermittel_einzelfutter SET
      feed_kind=CASE
        WHEN lower(art) SIMILAR TO '%(grundfutter|silage|heu)%' THEN 'forage'
        WHEN lower(art) LIKE '%mineral%' THEN 'mineral'
        WHEN lower(art) LIKE '%nebenprodukt%' THEN 'byproduct'
        ELSE 'concentrate' END,
      approval_status=CASE WHEN aktiv THEN 'approved' ELSE 'retired' END
      WHERE feed_kind='other'""")
    op.execute("""ALTER TABLE domain_shared.futtermittel_einzelfutter
      ADD CONSTRAINT ck_feed_catalog_kind CHECK (feed_kind IN
        ('forage','concentrate','mineral','additive','byproduct','liquid','other')),
      ADD CONSTRAINT ck_feed_catalog_approval CHECK (approval_status IN ('draft','approved','blocked','retired')),
      ADD CONSTRAINT ck_feed_catalog_validity CHECK (valid_until IS NULL OR valid_until >= valid_from),
      ADD CONSTRAINT ck_feed_catalog_revision CHECK (revision > 0)""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_feed_products (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      feed_id VARCHAR NOT NULL REFERENCES domain_shared.futtermittel_einzelfutter(id),
      supplier_partner_id VARCHAR,
      sku VARCHAR(80) NOT NULL,
      display_name VARCHAR(240) NOT NULL,
      packaging_unit VARCHAR(30) NOT NULL DEFAULT 't',
      package_size NUMERIC(18,6) NOT NULL DEFAULT 1 CHECK (package_size > 0),
      minimum_order_qty NUMERIC(18,6) CHECK (minimum_order_qty IS NULL OR minimum_order_qty >= 0),
      price_eur_t NUMERIC(18,6) CHECK (price_eur_t IS NULL OR price_eur_t >= 0),
      freight_eur_t NUMERIC(18,6) NOT NULL DEFAULT 0 CHECK (freight_eur_t >= 0),
      valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
      valid_until DATE,
      active BOOLEAN NOT NULL DEFAULT TRUE,
      revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
      created_by VARCHAR(160) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_by VARCHAR(160) NOT NULL,
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_feeding_feed_product UNIQUE (tenant_id,feed_id,sku),
      CONSTRAINT ck_feeding_feed_product_validity CHECK (valid_until IS NULL OR valid_until >= valid_from)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_feeding_feed_products_lookup ON domain_agrar.feeding_feed_products (tenant_id,feed_id,active)")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_feed_reference_values (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      feed_id VARCHAR NOT NULL REFERENCES domain_shared.futtermittel_einzelfutter(id),
      nutrient_code VARCHAR(60) NOT NULL,
      value NUMERIC(30,12) NOT NULL,
      unit_code VARCHAR(40) NOT NULL,
      basis VARCHAR(30) NOT NULL CHECK (basis IN ('fresh_matter','dry_matter')),
      value_status VARCHAR(30) NOT NULL DEFAULT 'reference' CHECK (value_status IN ('reference','estimated','analyzed')),
      source_type VARCHAR(40) NOT NULL,
      source_ref VARCHAR(160),
      valid_from DATE NOT NULL DEFAULT CURRENT_DATE,
      valid_until DATE,
      priority INTEGER NOT NULL DEFAULT 0,
      revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
      created_by VARCHAR(160) NOT NULL,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT ck_feeding_feed_value_validity CHECK (valid_until IS NULL OR valid_until >= valid_from)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_feeding_feed_values_effective ON domain_agrar.feeding_feed_reference_values (tenant_id,feed_id,nutrient_code,valid_from DESC,priority DESC)")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_feed_revisions (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      feed_id VARCHAR NOT NULL REFERENCES domain_shared.futtermittel_einzelfutter(id),
      revision INTEGER NOT NULL CHECK (revision > 0),
      snapshot JSONB NOT NULL,
      reason VARCHAR(500) NOT NULL,
      changed_by VARCHAR(160) NOT NULL,
      changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_feeding_feed_revision UNIQUE (tenant_id,feed_id,revision)
    )""")
    op.execute("""INSERT INTO domain_agrar.feeding_feed_revisions
      (id,tenant_id,feed_id,revision,snapshot,reason,changed_by,changed_at)
      SELECT id || '-revision-1',tenant_id,id,1,to_jsonb(f),'Bestandsuebernahme',
             created_by,COALESCE(created_at,now())
      FROM domain_shared.futtermittel_einzelfutter f ON CONFLICT DO NOTHING""")
    op.execute("""INSERT INTO domain_agrar.feeding_nutrient_definitions
      (id,code,display_name,canonical_unit_code,default_basis,value_kind,minimum_value,maximum_value,sort_order,source)
      VALUES
      ('feed-nutrient-fat','crude_fat','Rohfett','g_per_kg','dry_matter','concentration',0,1000,115,'VALEO/DLG'),
      ('feed-nutrient-na','sodium','Natrium','g_per_kg','dry_matter','concentration',0,1000,140,'VALEO/DLG'),
      ('feed-nutrient-mg','magnesium','Magnesium','g_per_kg','dry_matter','concentration',0,1000,150,'VALEO/DLG'),
      ('feed-nutrient-k','potassium','Kalium','g_per_kg','dry_matter','concentration',0,1000,160,'VALEO/DLG'),
      ('feed-nutrient-sidp','sidp','Duenndarmverdauliches Protein','g_per_kg','dry_matter','concentration',0,1000,170,'VALEO/GfE')
      ON CONFLICT DO NOTHING""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_feeding_feed_revision()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN RAISE EXCEPTION 'feeding_feed_revisions are immutable'; END; $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_feed_revision ON domain_agrar.feeding_feed_revisions")
    op.execute("""CREATE TRIGGER trg_immutable_feeding_feed_revision BEFORE UPDATE OR DELETE
      ON domain_agrar.feeding_feed_revisions FOR EACH ROW
      EXECUTE FUNCTION domain_agrar.guard_immutable_feeding_feed_revision()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_feed_revision ON domain_agrar.feeding_feed_revisions")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_feeding_feed_revision()")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_feed_revisions")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_feed_reference_values")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_feed_products")
    for column in ("updated_by","created_by","revision","valid_until","valid_from","approval_status","conservation_method","species_scope","feed_kind"):
        op.execute(f"ALTER TABLE domain_shared.futtermittel_einzelfutter DROP COLUMN IF EXISTS {column}")  # noqa: S608 -- fixed allowlist
