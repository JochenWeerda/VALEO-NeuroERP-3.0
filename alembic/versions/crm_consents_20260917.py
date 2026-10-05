"""Kontakt-Einwilligungen (DSGVO Double-Opt-in) neben dem Partner-Stamm.

``domain_crm.crm_consents`` gehoert dem Partnerweg (DSGVO Art. 6/7,
``app/crm/router.py``: partner_id, purpose, granted). CREATE TABLE IF NOT EXISTS
auf denselben Namen und danach ein Index auf ``contact_id`` bricht auf
Bestandsinstallationen ab und wuerde zwei Fachmodelle in eine Tabelle legen.

Revision ID: crm_consents_20260917
Revises: screen_definition_drafts_20260916
"""

from alembic import op

revision = "crm_consents_20260917"
down_revision = "screen_definition_drafts_20260916"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS domain_crm")
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
    # Frische DBs, die die erste Fassung schon mit contact_id in crm_consents
    # angelegt haben: Daten retten, Partner-Tabelle nicht anfassen.
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
    op.execute("DROP TABLE IF EXISTS domain_crm.crm_contact_consent_history")
    op.execute("DROP TABLE IF EXISTS domain_crm.crm_contact_consents")
