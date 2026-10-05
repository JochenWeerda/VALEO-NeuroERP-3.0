"""Tabellen fuer Masken-Bruecken, die bisher ins Leere zeigten.

Revision ID: mask_frontend_bridges_20260917
Revises: sales_beleg_druck_buchung_20260917
"""

from alembic import op

revision = "mask_frontend_bridges_20260917"
down_revision = "sales_beleg_druck_buchung_20260917"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_agrar")
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_inventory")
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_hr")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_agrar.seed_orders (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR NOT NULL,
          payload JSONB NOT NULL DEFAULT '{}'::jsonb,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_seed_orders_tenant ON domain_agrar.seed_orders (tenant_id)"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_inventory.epcis_events (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR NOT NULL,
          event_type VARCHAR(40) NOT NULL,
          event_time TIMESTAMPTZ NOT NULL,
          biz_step VARCHAR(128),
          read_point VARCHAR(128),
          lot_id VARCHAR,
          sku VARCHAR(64),
          quantity NUMERIC(16, 3),
          extensions JSONB,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_epcis_events_tenant_time "
        "ON domain_inventory.epcis_events (tenant_id, event_time DESC)"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_hr.work_plan_assignments (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR NOT NULL,
          datum DATE NOT NULL,
          employee_ref VARCHAR NOT NULL,
          label VARCHAR(255) NOT NULL,
          start_time VARCHAR(16),
          end_time VARCHAR(16),
          role_code VARCHAR(64),
          notes TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_work_plan_assignments_tenant_datum "
        "ON domain_hr.work_plan_assignments (tenant_id, datum)"
    )
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_finance")
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_shared")
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_crm")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_agrar.waagen_vorlagen (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR NOT NULL,
          name VARCHAR(200) NOT NULL,
          waage_id VARCHAR NOT NULL DEFAULT 'default',
          kontrakt_nr VARCHAR,
          lieferant_nr VARCHAR,
          fahrer_name VARCHAR,
          kfz_kennzeichen VARCHAR,
          lager_id VARCHAR,
          silo_id VARCHAR,
          sorte_nr VARCHAR,
          artikel_nr VARCHAR,
          charge_nr VARCHAR,
          ist_aktiv BOOLEAN NOT NULL DEFAULT TRUE,
          verwendungen_count INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_finance.fixed_assets (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR NOT NULL,
          asset_number VARCHAR NOT NULL,
          description TEXT,
          asset_class VARCHAR(20) NOT NULL DEFAULT 'MASCHINE',
          acquisition_date DATE,
          acquisition_cost NUMERIC(14, 2) NOT NULL DEFAULT 0,
          useful_life_years INTEGER NOT NULL DEFAULT 1,
          residual_value NUMERIC(14, 2) NOT NULL DEFAULT 0,
          current_book_value NUMERIC(14, 2) NOT NULL DEFAULT 0,
          accumulated_depreciation NUMERIC(14, 2) NOT NULL DEFAULT 0,
          depreciation_method VARCHAR(20) NOT NULL DEFAULT 'LINEAR',
          is_active BOOLEAN NOT NULL DEFAULT TRUE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_shared.direct_debit_items (
          id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
          run_id VARCHAR NOT NULL,
          debitor_name VARCHAR,
          iban VARCHAR,
          bic VARCHAR,
          mandate_id VARCHAR,
          amount NUMERIC(14, 2) NOT NULL DEFAULT 0,
          verwendungszweck VARCHAR,
          status VARCHAR(32) NOT NULL DEFAULT 'pending',
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_direct_debit_items_run "
        "ON domain_shared.direct_debit_items (run_id)"
    )
    # Bereits gestempelte crm_consents_20260917-Fassung: Kontaktzeilen umziehen.
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_crm.crm_contact_consents (
          id VARCHAR PRIMARY KEY,
          tenant_id VARCHAR NOT NULL,
          contact_id VARCHAR NOT NULL,
          channel VARCHAR(20) NOT NULL,
          consent_type VARCHAR(20) NOT NULL,
          status VARCHAR(20) NOT NULL DEFAULT 'pending',
          source VARCHAR(20) NOT NULL DEFAULT 'manual',
          granted_at TIMESTAMPTZ,
          denied_at TIMESTAMPTZ,
          revoked_at TIMESTAMPTZ,
          double_opt_in_token VARCHAR UNIQUE,
          double_opt_in_confirmed_at TIMESTAMPTZ,
          ip_address VARCHAR(45),
          user_agent TEXT,
          expires_at TIMESTAMPTZ,
          created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          created_by VARCHAR(255),
          updated_by VARCHAR(255)
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_contact_consents_tenant_contact "
        "ON domain_crm.crm_contact_consents (tenant_id, contact_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_contact_consents_tenant_status "
        "ON domain_crm.crm_contact_consents (tenant_id, status)"
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_crm.crm_contact_consent_history (
          id VARCHAR PRIMARY KEY,
          consent_id VARCHAR NOT NULL REFERENCES domain_crm.crm_contact_consents(id) ON DELETE CASCADE,
          action VARCHAR(20) NOT NULL,
          old_status VARCHAR(20),
          new_status VARCHAR(20) NOT NULL,
          reason TEXT,
          changed_by VARCHAR(255) NOT NULL,
          changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          ip_address VARCHAR(45),
          user_agent TEXT
        )
        """
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_crm_contact_consent_history_consent "
        "ON domain_crm.crm_contact_consent_history (consent_id)"
    )
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_schema = 'domain_crm'
              AND table_name = 'crm_consents'
              AND column_name = 'contact_id'
          ) THEN
            INSERT INTO domain_crm.crm_contact_consents (
              id, tenant_id, contact_id, channel, consent_type, status, source,
              granted_at, denied_at, revoked_at, double_opt_in_token,
              double_opt_in_confirmed_at, ip_address, user_agent, expires_at,
              created_at, updated_at, created_by, updated_by
            )
            SELECT
              id, tenant_id, contact_id, channel, consent_type, status, source,
              granted_at, denied_at, revoked_at, double_opt_in_token,
              double_opt_in_confirmed_at, ip_address, user_agent, expires_at,
              created_at, updated_at, created_by, updated_by
            FROM domain_crm.crm_consents
            ON CONFLICT (id) DO NOTHING;
          END IF;
        END $$;
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_shared.direct_debit_items")
    op.execute("DROP TABLE IF EXISTS domain_finance.fixed_assets")
    op.execute("DROP TABLE IF EXISTS domain_agrar.waagen_vorlagen")
    op.execute("DROP TABLE IF EXISTS domain_hr.work_plan_assignments")
    op.execute("DROP TABLE IF EXISTS domain_inventory.epcis_events")
    op.execute("DROP TABLE IF EXISTS domain_agrar.seed_orders")
