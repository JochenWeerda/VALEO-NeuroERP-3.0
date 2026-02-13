"""Add farmer declaration fields to PSM

Revision ID: 4601a09c0fc1
Revises: add_inventory_entities_stock_movements_and_inventory_counts
Create Date: 2025-10-14 18:08:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '4601a09c0fc1'
down_revision: Union[str, None] = 'add_inv_ent'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # This table may be owned by another service/domain and not exist in a fresh DB.
    conn = op.get_bind()
    exists = conn.execute(text("SELECT to_regclass('domain_agrar.agrar_psm')")).scalar()
    if not exists:
        return

    # Add farmer declaration fields to PSM table
    op.add_column(
        "agrar_psm",
        sa.Column("ausgangsstoff_explosivstoffe", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        schema="domain_agrar",
    )
    op.add_column(
        "agrar_psm",
        sa.Column("erklaerung_landwirt_erforderlich", sa.Boolean(), nullable=True, server_default=sa.text("false")),
        schema="domain_agrar",
    )
    op.add_column(
        "agrar_psm",
        sa.Column("erklaerung_landwirt_status", sa.String(length=20), nullable=True),
        schema="domain_agrar",
    )


def downgrade() -> None:
    conn = op.get_bind()
    exists = conn.execute(text("SELECT to_regclass('domain_agrar.agrar_psm')")).scalar()
    if not exists:
        return

    # Remove farmer declaration fields from PSM table
    op.drop_column("agrar_psm", "erklaerung_landwirt_status", schema="domain_agrar")
    op.drop_column("agrar_psm", "erklaerung_landwirt_erforderlich", schema="domain_agrar")
    op.drop_column("agrar_psm", "ausgangsstoff_explosivstoffe", schema="domain_agrar")
