"""Feeding businesses, farm sites, herds and business grants (FEED-CORE-015).

Revision ID: feed_core_business_20260715
Revises: feed_advice_controlling_20260714
"""

from alembic import op

revision = "feed_core_business_20260715"
down_revision = "feed_advice_controlling_20260714"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_businesses (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      business_partner_id VARCHAR(64),
      name VARCHAR(240) NOT NULL,
      production_type VARCHAR(80),
      husbandry_form VARCHAR(80),
      feeding_system VARCHAR(40),
      milking_system VARCHAR(80),
      advisory_status VARCHAR(40) NOT NULL DEFAULT 'none',
      last_consultation_at TIMESTAMPTZ,
      preferences JSONB NOT NULL DEFAULT '{}'::jsonb,
      active BOOLEAN NOT NULL DEFAULT TRUE,
      created_by VARCHAR(160) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_by VARCHAR(160) NOT NULL, updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_feeding_business_partner UNIQUE (tenant_id, business_partner_id)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_feeding_businesses_tenant ON domain_agrar.feeding_businesses (tenant_id, active, name)")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.farm_sites (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      business_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_businesses(id),
      name VARCHAR(240) NOT NULL,
      address VARCHAR(400),
      active BOOLEAN NOT NULL DEFAULT TRUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_farm_site_name UNIQUE (tenant_id, business_id, name)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_farm_sites_business ON domain_agrar.farm_sites (tenant_id, business_id, active)")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.herds (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      business_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_businesses(id),
      site_id VARCHAR REFERENCES domain_agrar.farm_sites(id),
      name VARCHAR(240) NOT NULL,
      animal_type VARCHAR(40) NOT NULL DEFAULT 'dairy_cow',
      active BOOLEAN NOT NULL DEFAULT TRUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
      CONSTRAINT uq_herd_name UNIQUE (tenant_id, business_id, name)
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_herds_business ON domain_agrar.herds (tenant_id, business_id, active)")

    op.execute("""CREATE TABLE IF NOT EXISTS domain_agrar.feeding_business_grants (
      id VARCHAR PRIMARY KEY,
      tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
      business_id VARCHAR NOT NULL REFERENCES domain_agrar.feeding_businesses(id),
      subject VARCHAR(160) NOT NULL,
      scope VARCHAR(16) NOT NULL CHECK (scope IN ('read','write','approve','admin')),
      valid_from TIMESTAMPTZ NOT NULL DEFAULT now(),
      valid_until TIMESTAMPTZ,
      granted_by VARCHAR(160) NOT NULL,
      revoked_by VARCHAR(160),
      revoked_at TIMESTAMPTZ,
      revoke_reason TEXT,
      created_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")
    op.execute("CREATE INDEX IF NOT EXISTS ix_business_grants_subject ON domain_agrar.feeding_business_grants (tenant_id, subject)")
    op.execute("""CREATE UNIQUE INDEX IF NOT EXISTS uq_active_business_grant
      ON domain_agrar.feeding_business_grants (tenant_id,business_id,subject,scope)
      WHERE revoked_at IS NULL""")

    # Additive Brücke: bestehende Tiergruppen bleiben gültig (NULL = noch keinem
    # Betrieb zugeordnet; Backfill erzeugt je Tenant den Default-Betrieb).
    op.execute("ALTER TABLE domain_agrar.feeding_groups ADD COLUMN IF NOT EXISTS business_id VARCHAR REFERENCES domain_agrar.feeding_businesses(id)")
    op.execute("ALTER TABLE domain_agrar.feeding_groups ADD COLUMN IF NOT EXISTS herd_id VARCHAR REFERENCES domain_agrar.herds(id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_feeding_groups_business ON domain_agrar.feeding_groups (tenant_id, business_id)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_groups_business")
    op.execute("ALTER TABLE domain_agrar.feeding_groups DROP COLUMN IF EXISTS herd_id")
    op.execute("ALTER TABLE domain_agrar.feeding_groups DROP COLUMN IF EXISTS business_id")
    op.execute("DROP INDEX IF EXISTS domain_agrar.uq_active_business_grant")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_business_grants_subject")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_business_grants")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_herds_business")
    op.execute("DROP TABLE IF EXISTS domain_agrar.herds")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_farm_sites_business")
    op.execute("DROP TABLE IF EXISTS domain_agrar.farm_sites")
    op.execute("DROP INDEX IF EXISTS domain_agrar.ix_feeding_businesses_tenant")
    op.execute("DROP TABLE IF EXISTS domain_agrar.feeding_businesses")
