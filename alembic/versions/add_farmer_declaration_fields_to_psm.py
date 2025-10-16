"""Add farmer declaration fields to PSM

Revision ID: add_farmer_declaration_fields_to_psm
Revises: add_inventory_entities_stock_movements_and_inventory_counts
Create Date: 2025-10-14 18:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_farmer_declaration_fields_to_psm'
down_revision: Union[str, None] = 'add_inv_ent'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add farmer declaration fields to PSM table
    op.add_column('domain_agrar.agrar_psm', sa.Column('ausgangsstoff_explosivstoffe', sa.Boolean(), nullable=True, default=False))
    op.add_column('domain_agrar.agrar_psm', sa.Column('erklaerung_landwirt_erforderlich', sa.Boolean(), nullable=True, default=False))
    op.add_column('domain_agrar.agrar_psm', sa.Column('erklaerung_landwirt_status', sa.String(length=20), nullable=True))


def downgrade() -> None:
    # Remove farmer declaration fields from PSM table
    op.drop_column('domain_agrar.agrar_psm', 'erklaerung_landwirt_status')
    op.drop_column('domain_agrar.agrar_psm', 'erklaerung_landwirt_erforderlich')
    op.drop_column('domain_agrar.agrar_psm', 'ausgangsstoff_explosivstoffe')