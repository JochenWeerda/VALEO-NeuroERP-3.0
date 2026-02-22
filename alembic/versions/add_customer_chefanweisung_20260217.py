"""Add chefanweisung field to customers table.

Revision ID: add_customer_chefanweisung_20260217
Revises: add_customer_address_generated_columns_20260217
Create Date: 2026-02-17 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_customer_chefanweisung_20260217'
down_revision: Union[str, Sequence[str], None] = 'customer_address_generated_cols'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add chefanweisung (executive note) field to customers table
    op.add_column(
        'customers',
        sa.Column(
            'chefanweisung',
            sa.Text(),
            nullable=True,
            comment='Chefanweisung (Executive Note) - Special instructions for this customer'
        ),
        schema='domain_crm'
    )


def downgrade() -> None:
    # Remove chefanweisung field
    op.drop_column('customers', 'chefanweisung', schema='domain_crm')

