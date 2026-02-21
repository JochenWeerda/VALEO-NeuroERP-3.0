"""Add tenant_id to business_partners table for multi-tenant isolation.

Revision ID: add_business_partners_tenant_id_20260219
Revises: add_nutrient_compositions_20260219
Create Date: 2026-02-19 17:30:00.000000

CRITICAL: This migration is required for multi-tenant security.
Business partners must be isolated per tenant to prevent data leakage.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_business_partners_tenant_id_20260219'
down_revision = 'add_nutrient_compositions_20260219'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add tenant_id column to business_partners table
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
    
    # Create index on tenant_id for query performance
    op.create_index(
        'ix_business_partners_tenant_id',
        'business_partners',
        ['tenant_id'],
        schema='domain_crm'
    )
    
    # Add unique constraint on (tenant_id, partner_number) 
    # since partner_number was previously globally unique
    op.create_unique_constraint(
        'uq_business_partners_tenant_partner_number',
        'business_partners',
        ['tenant_id', 'partner_number'],
        schema='domain_crm'
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
