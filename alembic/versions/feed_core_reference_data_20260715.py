"""Versioned feeding nutrient and unit reference data (FEED-CORE-017).

Revision ID: feed_core_reference_data_20260715
Revises: feed_core_groups_20260715
"""
from alembic import op

revision = "feed_core_reference_data_20260715"
down_revision = "feed_core_groups_20260715"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_unit_definitions (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR REFERENCES domain_shared.tenants(id),
      code VARCHAR(40) NOT NULL,
      display_name VARCHAR(160) NOT NULL,
      dimension VARCHAR(40) NOT NULL,
      factor_to_base NUMERIC(30,15) NOT NULL CHECK (factor_to_base > 0),
      precision INTEGER NOT NULL CHECK (precision BETWEEN 0 AND 12),
      revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
      source VARCHAR(120) NOT NULL,
      active BOOLEAN NOT NULL DEFAULT TRUE,
      created_by VARCHAR(160) NOT NULL DEFAULT 'migration',
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_by VARCHAR(160) NOT NULL DEFAULT 'migration',
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("""CREATE UNIQUE INDEX IF NOT EXISTS uq_feeding_unit_scope_code
      ON domain_agrar.feeding_unit_definitions (COALESCE(tenant_id,''),code)""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_nutrient_definitions (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR REFERENCES domain_shared.tenants(id),
      code VARCHAR(60) NOT NULL,
      display_name VARCHAR(160) NOT NULL,
      canonical_unit_code VARCHAR(40) NOT NULL,
      default_basis VARCHAR(30) NOT NULL CHECK (default_basis IN ('fresh_matter','dry_matter')),
      value_kind VARCHAR(30) NOT NULL CHECK (value_kind IN ('quantity','concentration')),
      minimum_value NUMERIC(30,12),
      maximum_value NUMERIC(30,12),
      sort_order INTEGER NOT NULL DEFAULT 0,
      revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
      source VARCHAR(120) NOT NULL,
      active BOOLEAN NOT NULL DEFAULT TRUE,
      created_by VARCHAR(160) NOT NULL DEFAULT 'migration',
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_by VARCHAR(160) NOT NULL DEFAULT 'migration',
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT ck_feeding_nutrient_range CHECK
        (minimum_value IS NULL OR maximum_value IS NULL OR maximum_value >= minimum_value)
    )""")
    op.execute("""CREATE UNIQUE INDEX IF NOT EXISTS uq_feeding_nutrient_scope_code
      ON domain_agrar.feeding_nutrient_definitions (COALESCE(tenant_id,''),code)""")
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_reference_revisions (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR REFERENCES domain_shared.tenants(id),
      entity_type VARCHAR(30) NOT NULL CHECK (entity_type IN ('unit','nutrient')),
      entity_id VARCHAR NOT NULL,
      code VARCHAR(60) NOT NULL,
      revision INTEGER NOT NULL CHECK (revision > 0),
      snapshot JSONB NOT NULL,
      reason VARCHAR(500) NOT NULL,
      changed_by VARCHAR(160) NOT NULL,
      changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("""CREATE UNIQUE INDEX IF NOT EXISTS uq_feeding_reference_revision
      ON domain_agrar.feeding_reference_revisions
      (COALESCE(tenant_id,''),entity_type,entity_id,revision)""")

    op.execute("""INSERT INTO domain_agrar.feeding_unit_definitions
      (id,code,display_name,dimension,factor_to_base,precision,source)
      VALUES
      ('feed-unit-kg','kg','Kilogramm','mass',1,3,'VALEO canonical'),
      ('feed-unit-g','g','Gramm','mass',0.001,1,'VALEO canonical'),
      ('feed-unit-mg','mg','Milligramm','mass',0.000001,2,'VALEO canonical'),
      ('feed-unit-mj','MJ','Megajoule','energy',1,2,'VALEO canonical'),
      ('feed-unit-percent','percent','Prozent','ratio',0.01,2,'VALEO canonical'),
      ('feed-unit-g-kg','g_per_kg','Gramm je Kilogramm','mass_concentration',1,2,'VALEO canonical'),
      ('feed-unit-mg-kg','mg_per_kg','Milligramm je Kilogramm','mass_concentration',0.001,3,'VALEO canonical'),
      ('feed-unit-mj-kg','MJ_per_kg','Megajoule je Kilogramm','energy_concentration',1,2,'VALEO canonical')
      ON CONFLICT DO NOTHING""")
    op.execute("""INSERT INTO domain_agrar.feeding_nutrient_definitions
      (id,code,display_name,canonical_unit_code,default_basis,value_kind,minimum_value,maximum_value,sort_order,source)
      VALUES
      ('feed-nutrient-dm','dry_matter','Trockenmasse','percent','fresh_matter','concentration',0,100,10,'VALEO/DLG'),
      ('feed-nutrient-me','metabolizable_energy','Umsetzbare Energie','MJ_per_kg','dry_matter','concentration',0,NULL,20,'VALEO/DLG'),
      ('feed-nutrient-nel','net_energy_lactation','Nettoenergie Laktation','MJ_per_kg','dry_matter','concentration',0,NULL,30,'VALEO/DLG'),
      ('feed-nutrient-cp','crude_protein','Rohprotein','g_per_kg','dry_matter','concentration',0,1000,40,'VALEO/DLG'),
      ('feed-nutrient-nxp','utilizable_crude_protein','Nutzbares Rohprotein','g_per_kg','dry_matter','concentration',0,1000,50,'VALEO/DLG'),
      ('feed-nutrient-rnb','ruminal_n_balance','Ruminale Stickstoffbilanz','g_per_kg','dry_matter','concentration',-100,100,60,'VALEO/DLG'),
      ('feed-nutrient-fibre','crude_fibre','Rohfaser','g_per_kg','dry_matter','concentration',0,1000,70,'VALEO/DLG'),
      ('feed-nutrient-ndf','ndf','NDF','g_per_kg','dry_matter','concentration',0,1000,80,'VALEO/DLG'),
      ('feed-nutrient-adf','adf','ADF','g_per_kg','dry_matter','concentration',0,1000,90,'VALEO/DLG'),
      ('feed-nutrient-starch','starch','Staerke','g_per_kg','dry_matter','concentration',0,1000,100,'VALEO/DLG'),
      ('feed-nutrient-sugar','sugar','Zucker','g_per_kg','dry_matter','concentration',0,1000,110,'VALEO/DLG'),
      ('feed-nutrient-ca','calcium','Calcium','g_per_kg','dry_matter','concentration',0,1000,120,'VALEO/DLG'),
      ('feed-nutrient-p','phosphorus','Phosphor','g_per_kg','dry_matter','concentration',0,1000,130,'VALEO/DLG'),
      ('feed-nutrient-mycotoxin','mycotoxin','Mykotoxin','mg_per_kg','dry_matter','concentration',0,NULL,900,'VALEO extensible')
      ON CONFLICT DO NOTHING""")
    op.execute("""INSERT INTO domain_agrar.feeding_reference_revisions
      (id,tenant_id,entity_type,entity_id,code,revision,snapshot,reason,changed_by,changed_at)
      SELECT 'revision-' || id,tenant_id,'unit',id,code,revision,to_jsonb(u),
             'Initialer Referenzdatenstand',created_by,created_at
      FROM domain_agrar.feeding_unit_definitions u ON CONFLICT DO NOTHING""")
    op.execute("""INSERT INTO domain_agrar.feeding_reference_revisions
      (id,tenant_id,entity_type,entity_id,code,revision,snapshot,reason,changed_by,changed_at)
      SELECT 'revision-' || id,tenant_id,'nutrient',id,code,revision,to_jsonb(n),
             'Initialer Referenzdatenstand',created_by,created_at
      FROM domain_agrar.feeding_nutrient_definitions n ON CONFLICT DO NOTHING""")
    op.execute("""CREATE OR REPLACE FUNCTION domain_agrar.guard_immutable_feeding_reference_revision()
      RETURNS trigger LANGUAGE plpgsql AS $$
      BEGIN RAISE EXCEPTION 'feeding_reference_revisions are immutable'; END;
      $$""")
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_reference_revision ON domain_agrar.feeding_reference_revisions")
    op.execute("""CREATE TRIGGER trg_immutable_feeding_reference_revision
      BEFORE UPDATE OR DELETE ON domain_agrar.feeding_reference_revisions
      FOR EACH ROW EXECUTE FUNCTION domain_agrar.guard_immutable_feeding_reference_revision()""")


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_immutable_feeding_reference_revision ON domain_agrar.feeding_reference_revisions")
    op.execute("DROP FUNCTION IF EXISTS domain_agrar.guard_immutable_feeding_reference_revision()")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_reference_revisions")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_nutrient_definitions")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_unit_definitions")
