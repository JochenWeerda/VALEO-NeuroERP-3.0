"""add ownership/consignment fields to inventory_stock_movements

Revision ID: inventory_stock_movements_consignment_ownership_20260215
Revises: articles_master_fields_gap_83_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "inventory_stock_movements_consignment_ownership_20260215"
down_revision = "articles_master_fields_gap_83_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_inventory.inventory_stock_movements
            ADD COLUMN IF NOT EXISTS ownership_type VARCHAR(20) NOT NULL DEFAULT 'owned',
            ADD COLUMN IF NOT EXISTS owner_partner_id VARCHAR(64),
            ADD COLUMN IF NOT EXISTS agrar_contract_id VARCHAR(64),
            ADD COLUMN IF NOT EXISTS weighing_ticket_id VARCHAR(64),
            ADD COLUMN IF NOT EXISTS storage_fee_relevant BOOLEAN NOT NULL DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS storage_fee_start_date DATE,
            ADD COLUMN IF NOT EXISTS storage_fee_monthly_rate NUMERIC(12,4),
            ADD COLUMN IF NOT EXISTS storage_fee_last_charged_until DATE;
        """
    )

    op.execute(
        """
        ALTER TABLE domain_inventory.inventory_stock_movements
            DROP CONSTRAINT IF EXISTS chk_inventory_stock_movements_ownership_type,
            ADD CONSTRAINT chk_inventory_stock_movements_ownership_type
                CHECK (ownership_type IN ('owned', 'consigned'));
        """
    )

    op.execute(
        """
        ALTER TABLE domain_inventory.inventory_stock_movements
            DROP CONSTRAINT IF EXISTS chk_inventory_stock_movements_consigned_owner_required,
            ADD CONSTRAINT chk_inventory_stock_movements_consigned_owner_required
                CHECK (
                    ownership_type <> 'consigned'
                    OR owner_partner_id IS NOT NULL
                );
        """
    )

    op.execute(
        """
        ALTER TABLE domain_inventory.inventory_stock_movements
            DROP CONSTRAINT IF EXISTS chk_inventory_stock_movements_storage_fee_rate_non_negative,
            ADD CONSTRAINT chk_inventory_stock_movements_storage_fee_rate_non_negative
                CHECK (
                    storage_fee_monthly_rate IS NULL
                    OR storage_fee_monthly_rate >= 0
                );
        """
    )

    op.create_index(
        "ix_inventory_stock_movements_tenant_ownership_type",
        "inventory_stock_movements",
        ["tenant_id", "ownership_type"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_inventory_stock_movements_owner_partner_id",
        "inventory_stock_movements",
        ["owner_partner_id"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_inventory_stock_movements_agrar_contract_id",
        "inventory_stock_movements",
        ["agrar_contract_id"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_inventory_stock_movements_weighing_ticket_id",
        "inventory_stock_movements",
        ["weighing_ticket_id"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_inventory_stock_movements_weighing_ticket_id",
        table_name="inventory_stock_movements",
        schema="domain_inventory",
    )
    op.drop_index(
        "ix_inventory_stock_movements_agrar_contract_id",
        table_name="inventory_stock_movements",
        schema="domain_inventory",
    )
    op.drop_index(
        "ix_inventory_stock_movements_owner_partner_id",
        table_name="inventory_stock_movements",
        schema="domain_inventory",
    )
    op.drop_index(
        "ix_inventory_stock_movements_tenant_ownership_type",
        table_name="inventory_stock_movements",
        schema="domain_inventory",
    )

    op.execute(
        """
        ALTER TABLE domain_inventory.inventory_stock_movements
            DROP CONSTRAINT IF EXISTS chk_inventory_stock_movements_ownership_type,
            DROP CONSTRAINT IF EXISTS chk_inventory_stock_movements_consigned_owner_required,
            DROP CONSTRAINT IF EXISTS chk_inventory_stock_movements_storage_fee_rate_non_negative;
        """
    )

    op.execute(
        """
        ALTER TABLE domain_inventory.inventory_stock_movements
            DROP COLUMN IF EXISTS storage_fee_last_charged_until,
            DROP COLUMN IF EXISTS storage_fee_monthly_rate,
            DROP COLUMN IF EXISTS storage_fee_start_date,
            DROP COLUMN IF EXISTS storage_fee_relevant,
            DROP COLUMN IF EXISTS weighing_ticket_id,
            DROP COLUMN IF EXISTS agrar_contract_id,
            DROP COLUMN IF EXISTS owner_partner_id,
            DROP COLUMN IF EXISTS ownership_type;
        """
    )
