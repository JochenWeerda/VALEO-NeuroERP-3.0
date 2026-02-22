"""Add missing delivery note position fields.

Revision ID: add_delivery_note_position_fields_20260217
Revises: add_article_search_fields_20260217
Create Date: 2026-02-17 14:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_delivery_note_position_fields_20260217'
down_revision: Union[str, Sequence[str], None] = 'add_article_search_fields_20260217'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing fields to delivery_note_positions table
    op.add_column(
        'delivery_note_positions',
        sa.Column(
            'gef_punkt',
            sa.String(length=80),
            nullable=True,
            comment='Gefahrpunkt (Danger point / Hazard classification)'
        ),
        schema='domain_sales'
    )
    
    op.add_column(
        'delivery_note_positions',
        sa.Column(
            'na_bio',
            sa.String(length=80),
            nullable=True,
            comment='Nachhaltigkeits-/Bio-Kennzeichnung (Sustainability/Bio label)'
        ),
        schema='domain_sales'
    )
    
    op.add_column(
        'delivery_note_positions',
        sa.Column(
            'muster_nr',
            sa.String(length=80),
            nullable=True,
            comment='Muster-Nummer (Sample number)'
        ),
        schema='domain_sales'
    )
    
    op.add_column(
        'delivery_note_positions',
        sa.Column(
            'strecke',
            sa.String(length=80),
            nullable=True,
            comment='Strecke (Route/Line)'
        ),
        schema='domain_sales'
    )
    
    op.add_column(
        'delivery_note_positions',
        sa.Column(
            'zus_beleg',
            sa.String(length=80),
            nullable=True,
            comment='Zusatzbeleg (Additional document)'
        ),
        schema='domain_sales'
    )
    
    op.add_column(
        'delivery_note_positions',
        sa.Column(
            'anerken',
            sa.String(length=80),
            nullable=True,
            comment='Anerkennung (Recognition/Acknowledgment)'
        ),
        schema='domain_sales'
    )


def downgrade() -> None:
    # Drop columns
    op.drop_column('delivery_note_positions', 'anerken', schema='domain_sales')
    op.drop_column('delivery_note_positions', 'zus_beleg', schema='domain_sales')
    op.drop_column('delivery_note_positions', 'strecke', schema='domain_sales')
    op.drop_column('delivery_note_positions', 'muster_nr', schema='domain_sales')
    op.drop_column('delivery_note_positions', 'na_bio', schema='domain_sales')
    op.drop_column('delivery_note_positions', 'gef_punkt', schema='domain_sales')

