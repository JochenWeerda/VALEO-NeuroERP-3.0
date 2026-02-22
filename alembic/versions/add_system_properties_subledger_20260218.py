"""add_system_properties_subledger_20260218

Revision ID: add_sysprops_20260218
Revises: add_vat_modes_20260217
Create Date: 2026-02-18 12:00:00.000000

Systemeigenschaften für Subledger-Workflow, Konten-Mapping (1400/1415), Stichtags-Umgliederung.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "add_sysprops_20260218"
down_revision: Union[str, None] = "add_vat_modes_20260217"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    op.create_table(
        "system_properties",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("tenant_id", sa.String(), sa.ForeignKey("domain_shared.tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("property_key", sa.String(100), nullable=False, comment="z.B. SUBLEDGER_AR_ACCOUNT"),
        sa.Column("property_value", sa.Text(), nullable=True),
        sa.Column("property_type", sa.String(20), server_default="string", nullable=True, comment="string / number / boolean / json"),
        sa.Column("category", sa.String(50), server_default="subledger", nullable=True, comment="subledger / year_end / harvest"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("tenant_id", "property_key", name="uq_system_properties_tenant_key"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_system_properties_tenant_key",
        "system_properties",
        ["tenant_id", "property_key"],
        unique=False,
        schema="domain_shared",
    )

    # Seed default Subledger-Systemeigenschaften (idempotent via ON CONFLICT)
    op.execute(
        f"""
        INSERT INTO domain_shared.system_properties (id, tenant_id, property_key, property_value, property_type, category, description)
        VALUES
          (gen_random_uuid()::text, '{DEFAULT_TENANT_ID}', 'SUBLEDGER_AR_ACCOUNT', '1400', 'string', 'subledger', 'Debitoren-Sammelkonto (Forderungen)'),
          (gen_random_uuid()::text, '{DEFAULT_TENANT_ID}', 'SUBLEDGER_CREDITOR_DEBITOR_ACCOUNT', '1415', 'string', 'subledger', 'Erhaltene Anzahlungen / Guthaben (kreditorische Debitoren)'),
          (gen_random_uuid()::text, '{DEFAULT_TENANT_ID}', 'SUBLEDGER_STORAGE_ACCOUNT', '3300', 'string', 'subledger', 'Fremdware Lager'),
          (gen_random_uuid()::text, '{DEFAULT_TENANT_ID}', 'SUBLEDGER_AP_PRODUCER_ACCOUNT', '1600', 'string', 'subledger', 'Verbindlichkeiten Rohwaren'),
          (gen_random_uuid()::text, '{DEFAULT_TENANT_ID}', 'SUBLEDGER_INTEREST_ACCOUNT', '2690', 'string', 'subledger', 'Zinsen'),
          (gen_random_uuid()::text, '{DEFAULT_TENANT_ID}', 'STICHTAG_UMGLIEDERUNG_ENABLED', 'true', 'boolean', 'year_end', 'Stichtags-Umgliederung aktiv'),
          (gen_random_uuid()::text, '{DEFAULT_TENANT_ID}', 'STICHTAG_UMGLIEDERUNG_AUTO_REVERSAL', 'false', 'boolean', 'year_end', 'Rückbuchung 01.01. automatisch'),
          (gen_random_uuid()::text, '{DEFAULT_TENANT_ID}', 'ACCEPTANCE_MODE_DEFAULT', 'PURCHASE_AT_DELIVERY_PTBF', 'string', 'harvest', 'Default Geschäftsmodell Ernte-Annahme')
        ON CONFLICT (tenant_id, property_key) DO NOTHING;
        """
    )


def downgrade() -> None:
    op.drop_index("ix_system_properties_tenant_key", table_name="system_properties", schema="domain_shared")
    op.drop_table("system_properties", schema="domain_shared")
