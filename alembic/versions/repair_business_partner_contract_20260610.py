"""Complete the canonical business-partner runtime contract.

Revision ID: repair_bp_contract_20260610
Revises: repair_model_alignment_20260610
"""

from alembic import op
from sqlalchemy import text


revision = "repair_bp_contract_20260610"
down_revision = "repair_model_alignment_20260610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        text(
            """
            ALTER TABLE domain_crm.business_partners
              ADD COLUMN IF NOT EXISTS payment_terms_id VARCHAR(36),
              ADD COLUMN IF NOT EXISTS credit_limit NUMERIC(14,2),
              ADD COLUMN IF NOT EXISTS dunning_level INTEGER DEFAULT 0,
              ADD COLUMN IF NOT EXISTS farm_number VARCHAR(80),
              ADD COLUMN IF NOT EXISTS eu_farm_id VARCHAR(80),
              ADD COLUMN IF NOT EXISTS harvest_year_default INTEGER,
              ADD COLUMN IF NOT EXISTS qs_certificate_number VARCHAR(80),
              ADD COLUMN IF NOT EXISTS qs_valid_until TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS bio_certified BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS bio_certificate_valid_until TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS contract_group VARCHAR(80),
              ADD COLUMN IF NOT EXISTS default_silo_location VARCHAR(120),
              ADD COLUMN IF NOT EXISTS default_route_id VARCHAR(36),
              ADD COLUMN IF NOT EXISTS preferred_carrier_id VARCHAR(36),
              ADD COLUMN IF NOT EXISTS loading_requirements TEXT,
              ADD COLUMN IF NOT EXISTS email_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS email_opt_in_timestamp TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS sms_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS sms_opt_in_timestamp TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS whatsapp_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS whatsapp_opt_in_timestamp TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS newsletter_opt_in BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS newsletter_language VARCHAR(10),
              ADD COLUMN IF NOT EXISTS flyer_subscription BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS flyer_delivery_type VARCHAR(20),
              ADD COLUMN IF NOT EXISTS marketing_segment VARCHAR(80),
              ADD COLUMN IF NOT EXISTS privacy_policy_accepted BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS privacy_policy_version VARCHAR(40),
              ADD COLUMN IF NOT EXISTS privacy_policy_accepted_at TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS data_processing_agreement_signed BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS data_retention_until TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS contact_block_reason VARCHAR(255),
              ADD COLUMN IF NOT EXISTS anonymized_at TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS created_by VARCHAR(36),
              ADD COLUMN IF NOT EXISTS updated_by VARCHAR(36),
              ADD COLUMN IF NOT EXISTS tab_23 JSONB;
            """
        )
    )


def downgrade() -> None:
    # Master data and consent evidence must survive application rollback.
    pass
