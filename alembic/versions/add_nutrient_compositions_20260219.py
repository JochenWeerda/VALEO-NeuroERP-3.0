"""Add nutrient compositions table and article linkage

Revision ID: add_nutrient_compositions_20260219
Revises: add_weighing_ticket_article_notes_20260219
Create Date: 2026-02-19 16:35:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_nutrient_compositions_20260219'
down_revision = 'add_wt_article_notes_20260219'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create nutrient_compositions table in domain_agrar schema
    op.create_table(
        'nutrient_compositions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('tenant_id', sa.String(), sa.ForeignKey('domain_shared.tenants.id'), nullable=False),
        sa.Column('lfd_nr', sa.String(20), nullable=True),
        sa.Column('bezeichnung', sa.String(255), nullable=False),
        sa.Column('beschreibung', sa.Text(), nullable=True),
        # Nutrient values (kg/t)
        sa.Column('stickstoff_gesamt', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('ts_gehalt', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('n_anteil', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('ammonium_n', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('phosphat_p2o5', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('kalium_k2o', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('magnesium_mgo', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('calcium_cao', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('schwefel_s', sa.DECIMAL(10, 2), nullable=True),
        sa.Column('natrium_na2o', sa.DECIMAL(10, 2), nullable=True),
        # Additional fields
        sa.Column('basis', sa.String(50), nullable=True),
        sa.Column('wirtschaftsduenger', sa.Boolean(), default=False, nullable=True),
        sa.Column('composition_type', sa.String(50), nullable=True),
        # Laborwert reference
        sa.Column('laborwert_id', sa.String(), nullable=True),
        sa.Column('laborwert_name', sa.String(255), nullable=True),
        # Status
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        schema='domain_agrar'
    )
    
    # Add index on tenant_id
    op.create_index('ix_nutrient_compositions_tenant_id', 'nutrient_compositions', ['tenant_id'], schema='domain_agrar')
    
    # Add index on bezeichnung for search
    op.create_index('ix_nutrient_compositions_bezeichnung', 'nutrient_compositions', ['bezeichnung'], schema='domain_agrar')
    
    # Add nutrient composition linkage to articles table
    op.add_column(
        'articles',
        sa.Column('duengemittel_inhalte_id', sa.String(), sa.ForeignKey('domain_agrar.nutrient_compositions.id'), nullable=True),
        schema='domain_inventory'
    )
    
    op.add_column(
        'articles',
        sa.Column('duengemittel_inhalte_bezeichnung', sa.String(255), nullable=True),
        schema='domain_inventory'
    )


def downgrade() -> None:
    # Drop columns from articles
    op.drop_column('articles', 'duengemittel_inhalte_bezeichnung', schema='domain_inventory')
    op.drop_column('articles', 'duengemittel_inhalte_id', schema='domain_inventory')
    
    # Drop indexes
    op.drop_index('ix_nutrient_compositions_bezeichnung', table_name='nutrient_compositions', schema='domain_agrar')
    op.drop_index('ix_nutrient_compositions_tenant_id', table_name='nutrient_compositions', schema='domain_agrar')
    
    # Drop table
    op.drop_table('nutrient_compositions', schema='domain_agrar')
