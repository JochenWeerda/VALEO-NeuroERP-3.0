"""Add tenant_id to business_partners table for multi-tenant isolation.

Revision ID: add_business_partners_tenant_id_20260219
Revises: add_nutrient_compositions_20260219
Create Date: 2026-02-19 17:30:00.000000

CRITICAL: This migration is required for multi-tenant security.
Business partners must be isolated per tenant to prevent data leakage.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'add_business_partners_tenant_id_20260219'
down_revision = 'add_nutrient_compositions_20260219'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    tenant_column_exists = conn.execute(
        text(
            """
            SELECT 1
            FROM information_schema.columns
            WHERE table_schema = 'domain_crm'
              AND table_name = 'business_partners'
              AND column_name = 'tenant_id'
            """
        )
    ).scalar() is not None

    if not tenant_column_exists:
        op.add_column(
            'business_partners',
            sa.Column(
                'tenant_id',
                sa.String(),
                sa.ForeignKey('domain_shared.tenants.id'),
                nullable=False,
                comment='Tenant ID for multi-tenant isolation'
            ),
            schema='domain_crm'
        )

    op.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS ix_business_partners_tenant_id
            ON domain_crm.business_partners (tenant_id)
            """
        )
    )

    # First-install fallback from an earlier migration created a global unique
    # index on partner_number. Replace that with the intended tenant-scoped
    # uniqueness so multi-tenant bootstrap matches the target model.
    op.execute(text("DROP INDEX IF EXISTS domain_crm.uq_domain_crm_bp_partner_number"))
    op.execute(
        text(
            """
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM pg_constraint
                    WHERE conname = 'uq_business_partners_tenant_partner_number'
                      AND conrelid = 'domain_crm.business_partners'::regclass
                ) THEN
                    ALTER TABLE domain_crm.business_partners
                    ADD CONSTRAINT uq_business_partners_tenant_partner_number
                    UNIQUE (tenant_id, partner_number);
                END IF;
            END
            $$;
            """
        )
    )


def downgrade() -> None:
    # Drop unique constraint
    op.drop_constraint(
        'uq_business_partners_tenant_partner_number',
        'business_partners',
        schema='domain_crm'
    )
    
    # Drop index
    op.drop_index(
        'ix_business_partners_tenant_id',
        'business_partners',
        schema='domain_crm'
    )
    
    # Drop tenant_id column
    op.drop_column('business_partners', 'tenant_id', schema='domain_crm')
