"""extend inventory_stock_movements with l3 migration fields

Revision ID: inventory_stock_movements_l3_fields_20260214
Revises: seed_default_tenant_20260214
Create Date: 2026-02-14 11:20:00.000000
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "inventory_stock_movements_l3_fields_20260214"
down_revision: Union[str, Sequence[str], None] = "seed_default_tenant_20260214"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_inventory.inventory_stock_movements
            ADD COLUMN IF NOT EXISTS movement_number VARCHAR(64),
            ADD COLUMN IF NOT EXISTS movement_date DATE,
            ADD COLUMN IF NOT EXISTS movement_time TIME,
            ADD COLUMN IF NOT EXISTS unit VARCHAR(10),
            ADD COLUMN IF NOT EXISTS warehouse_location VARCHAR(120),
            ADD COLUMN IF NOT EXISTS charge VARCHAR(64),
            ADD COLUMN IF NOT EXISTS booking_user VARCHAR(100),
            ADD COLUMN IF NOT EXISTS auto_created BOOLEAN DEFAULT FALSE,
            ADD COLUMN IF NOT EXISTS linked_order_id UUID,
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ DEFAULT now();
        """
    )

    op.execute(
        """
        UPDATE domain_inventory.inventory_stock_movements
        SET
            movement_number = COALESCE(movement_number, 'MOV-' || substring(id::text, 1, 8)),
            movement_date = COALESCE(movement_date, (created_at AT TIME ZONE 'UTC')::date),
            movement_time = COALESCE(movement_time, (created_at AT TIME ZONE 'UTC')::time),
            unit = COALESCE(unit, 'kg'),
            auto_created = COALESCE(auto_created, FALSE),
            updated_at = COALESCE(updated_at, created_at, now());
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS ix_inventory_stock_movements_movement_number
        ON domain_inventory.inventory_stock_movements (movement_number);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS domain_inventory.ix_inventory_stock_movements_movement_number;
        """
    )
    op.execute(
        """
        ALTER TABLE domain_inventory.inventory_stock_movements
            DROP COLUMN IF EXISTS movement_number,
            DROP COLUMN IF EXISTS movement_date,
            DROP COLUMN IF EXISTS movement_time,
            DROP COLUMN IF EXISTS unit,
            DROP COLUMN IF EXISTS warehouse_location,
            DROP COLUMN IF EXISTS charge,
            DROP COLUMN IF EXISTS booking_user,
            DROP COLUMN IF EXISTS auto_created,
            DROP COLUMN IF EXISTS linked_order_id,
            DROP COLUMN IF EXISTS updated_at;
        """
    )
