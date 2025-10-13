"""add_l3_target_tables

Revision ID: a489a6a4a212
Revises: 1368e3f15650
Create Date: 2025-10-13 11:10:11.080064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'a489a6a4a212'
down_revision: Union[str, None] = '1368e3f15650'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create l3_staging schema for raw import
    op.execute("CREATE SCHEMA IF NOT EXISTS l3_staging")

    # Domain Finance tables
    op.create_table('period_closure',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('fiscal_year', sa.Integer(), nullable=False),
        sa.Column('fiscal_period', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('dim_cost_center', sa.String(length=100), nullable=False),
        sa.Column('dim_profit_center', sa.String(length=100), nullable=False),
        sa.Column('dim_account_line', sa.String(length=100), nullable=True),
        sa.Column('dim_project_tag', sa.String(length=100), nullable=True),
        sa.Column('dim_region', sa.String(length=100), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_finance'
    )

    op.create_table('sales_order',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('fx_rate', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('fx_rate_ts', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('amount_txn', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('amount_base', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_finance'
    )

    # Domain CRM tables
    op.create_table('cancellation_reason',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('cancel_reason_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cancel_reason_id'),
        schema='domain_crm'
    )

    op.create_table('opportunity',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('stage', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('cancel_reason_id', sa.Integer(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['cancel_reason_id'], ['domain_crm.cancellation_reason.cancel_reason_id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_crm'
    )

    # Domain Inventory tables
    op.create_table('stock_item',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('uom_base', sa.String(length=20), nullable=False),
        sa.Column('lot_id', sa.String(length=100), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_inventory'
    )

    op.create_table('stock_movement',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('quantity', sa.Numeric(precision=15, scale=4), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_inventory'
    )

    # Domain HR tables
    op.create_table('person',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('person_id'),
        schema='domain_hr'
    )

    op.create_table('employment',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('person_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('employment_start', sa.Date(), nullable=False),
        sa.Column('employment_end', sa.Date(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['person_id'], ['domain_hr.person.person_id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_hr'
    )

    # Domain Manufacturing tables
    op.create_table('bill_of_material',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('bom_id', sa.Integer(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('bom_id'),
        schema='domain_mfg'
    )

    op.create_table('production_order',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('routing_id', sa.Integer(), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('routing_id'),
        schema='domain_mfg'
    )

    op.create_table('production_event',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tenant_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_ts', postgresql.TIMESTAMP(timezone=True), nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['domain_shared.tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        schema='domain_mfg'
    )

    # Create indexes for performance
    op.create_index('idx_period_closure_fiscal_year', 'period_closure', ['fiscal_year'], schema='domain_finance')
    op.create_index('idx_sales_order_currency', 'sales_order', ['currency_code'], schema='domain_finance')
    op.create_index('idx_opportunity_stage', 'opportunity', ['stage'], schema='domain_crm')
    op.create_index('idx_stock_movement_quantity', 'stock_movement', ['quantity'], schema='domain_inventory')
    op.create_index('idx_employment_dates', 'employment', ['employment_start', 'employment_end'], schema='domain_hr')
    op.create_index('idx_production_event_ts', 'production_event', ['event_ts'], schema='domain_mfg')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_production_event_ts', schema='domain_mfg')
    op.drop_index('idx_employment_dates', schema='domain_hr')
    op.drop_index('idx_stock_movement_quantity', schema='domain_inventory')
    op.drop_index('idx_opportunity_stage', schema='domain_crm')
    op.drop_index('idx_sales_order_currency', schema='domain_finance')
    op.drop_index('idx_period_closure_fiscal_year', schema='domain_finance')

    # Drop tables
    op.drop_table('production_event', schema='domain_mfg')
    op.drop_table('production_order', schema='domain_mfg')
    op.drop_table('bill_of_material', schema='domain_mfg')
    op.drop_table('employment', schema='domain_hr')
    op.drop_table('person', schema='domain_hr')
    op.drop_table('stock_movement', schema='domain_inventory')
    op.drop_table('stock_item', schema='domain_inventory')
    op.drop_table('opportunity', schema='domain_crm')
    op.drop_table('cancellation_reason', schema='domain_crm')
    op.drop_table('sales_order', schema='domain_finance')
    op.drop_table('period_closure', schema='domain_finance')

    # Drop staging schema
    op.execute("DROP SCHEMA IF EXISTS l3_staging CASCADE")
