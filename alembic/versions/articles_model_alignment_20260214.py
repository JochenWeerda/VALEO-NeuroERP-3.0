"""align domain_inventory.articles with Article model

Revision ID: articles_model_alignment_20260214
Revises: ops_chargen_qs_fields_20260214
Create Date: 2026-02-14 11:40:00.000000
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "articles_model_alignment_20260214"
down_revision: Union[str, Sequence[str], None] = "ops_chargen_qs_fields_20260214"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_inventory.articles
            ADD COLUMN IF NOT EXISTS subcategory VARCHAR(50),
            ADD COLUMN IF NOT EXISTS barcode VARCHAR(50),
            ADD COLUMN IF NOT EXISTS supplier_number VARCHAR(50),
            ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'EUR',
            ADD COLUMN IF NOT EXISTS min_stock NUMERIC(10,2),
            ADD COLUMN IF NOT EXISTS max_stock NUMERIC(10,2),
            ADD COLUMN IF NOT EXISTS weight NUMERIC(8,2),
            ADD COLUMN IF NOT EXISTS dimensions VARCHAR(50),
            ADD COLUMN IF NOT EXISTS reserved_stock NUMERIC(10,2) DEFAULT 0,
            ADD COLUMN IF NOT EXISTS available_stock NUMERIC(10,2) DEFAULT 0,
            ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMPTZ;
        """
    )

    op.execute(
        """
        UPDATE domain_inventory.articles
        SET
            min_stock = COALESCE(min_stock, minimum_stock),
            max_stock = COALESCE(max_stock, maximum_stock),
            currency = COALESCE(currency, 'EUR'),
            reserved_stock = COALESCE(reserved_stock, 0),
            available_stock = COALESCE(available_stock, current_stock)
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE domain_inventory.articles
            DROP COLUMN IF EXISTS subcategory,
            DROP COLUMN IF EXISTS barcode,
            DROP COLUMN IF EXISTS supplier_number,
            DROP COLUMN IF EXISTS currency,
            DROP COLUMN IF EXISTS min_stock,
            DROP COLUMN IF EXISTS max_stock,
            DROP COLUMN IF EXISTS weight,
            DROP COLUMN IF EXISTS dimensions,
            DROP COLUMN IF EXISTS reserved_stock,
            DROP COLUMN IF EXISTS available_stock,
            DROP COLUMN IF EXISTS deleted_at;
        """
    )
