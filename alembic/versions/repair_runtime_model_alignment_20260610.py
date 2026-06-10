"""Align fresh installations with current CRM and article runtime models.

Revision ID: repair_model_alignment_20260610
Revises: repair_runtime_cols_20260610
"""

from alembic import op
from sqlalchemy import text


revision = "repair_model_alignment_20260610"
down_revision = "repair_runtime_cols_20260610"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        text(
            """
            ALTER TABLE domain_crm.business_partners
              ADD COLUMN IF NOT EXISTS street VARCHAR(120),
              ADD COLUMN IF NOT EXISTS house_number VARCHAR(40),
              ADD COLUMN IF NOT EXISTS postal_code VARCHAR(20),
              ADD COLUMN IF NOT EXISTS city VARCHAR(120),
              ADD COLUMN IF NOT EXISTS country VARCHAR(2) DEFAULT 'DE',
              ADD COLUMN IF NOT EXISTS state VARCHAR(80),
              ADD COLUMN IF NOT EXISTS language VARCHAR(10) DEFAULT 'de',
              ADD COLUMN IF NOT EXISTS is_customer BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS is_supplier BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS is_carrier BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS is_employee BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS is_service_provider BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS phone VARCHAR(60),
              ADD COLUMN IF NOT EXISTS mobile VARCHAR(60),
              ADD COLUMN IF NOT EXISTS email VARCHAR(255),
              ADD COLUMN IF NOT EXISTS website VARCHAR(255),
              ADD COLUMN IF NOT EXISTS fax VARCHAR(60),
              ADD COLUMN IF NOT EXISTS iban VARCHAR(34),
              ADD COLUMN IF NOT EXISTS bic VARCHAR(20),
              ADD COLUMN IF NOT EXISTS bank_name VARCHAR(120),
              ADD COLUMN IF NOT EXISTS sepa_mandate_reference VARCHAR(120),
              ADD COLUMN IF NOT EXISTS sepa_mandate_signed_at TIMESTAMPTZ,
              ADD COLUMN IF NOT EXISTS debtor_account VARCHAR(40),
              ADD COLUMN IF NOT EXISTS creditor_account VARCHAR(40),
              ADD COLUMN IF NOT EXISTS tax_number VARCHAR(60),
              ADD COLUMN IF NOT EXISTS vat_id VARCHAR(60),
              ADD COLUMN IF NOT EXISTS tax_type VARCHAR(40) DEFAULT 'standard',
              ADD COLUMN IF NOT EXISTS edifact_desadv BOOLEAN NOT NULL DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS webshop_customer_number VARCHAR(80),
              ADD COLUMN IF NOT EXISTS webshop_description VARCHAR(255);

            ALTER TABLE domain_inventory.articles
              ADD COLUMN IF NOT EXISTS kennzeichnung_bio VARCHAR(50),
              ADD COLUMN IF NOT EXISTS kennzeichnung_vegan VARCHAR(10),
              ADD COLUMN IF NOT EXISTS kennzeichnung_vegetarisch VARCHAR(10),
              ADD COLUMN IF NOT EXISTS kennzeichnung_allergene TEXT,
              ADD COLUMN IF NOT EXISTS kennzeichnung_herkunft VARCHAR(100),
              ADD COLUMN IF NOT EXISTS lager_min_temperatur NUMERIC(5,1),
              ADD COLUMN IF NOT EXISTS lager_max_temperatur NUMERIC(5,1),
              ADD COLUMN IF NOT EXISTS lager_lagerdauer_tage INTEGER,
              ADD COLUMN IF NOT EXISTS lager_zentral BOOLEAN DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS lager_silo BOOLEAN DEFAULT FALSE,
              ADD COLUMN IF NOT EXISTS analyse_protein NUMERIC(5,2),
              ADD COLUMN IF NOT EXISTS analyse_feuchtigkeit NUMERIC(5,2),
              ADD COLUMN IF NOT EXISTS analyse_schadex NUMERIC(5,2),
              ADD COLUMN IF NOT EXISTS analyse_fremdstoffe NUMERIC(5,2),
              ADD COLUMN IF NOT EXISTS analyse_sonstiges TEXT;
            """
        )
    )


def downgrade() -> None:
    # Master data must survive application rollback.
    pass
